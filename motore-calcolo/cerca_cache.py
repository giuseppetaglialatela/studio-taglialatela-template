#!/usr/bin/env python3
"""
Interrogazione della cache BDA-IEO - Studio Nutrizionale Taglialatela

COSA FA
Trasforma in comando il PASSO 4 del protocollo di estrazione ("cerca PRIMA
nella cache locale, interrogala in blocco su tutti i nomi"), che finora era
una procedura a memoria.

Due modi:
  ricerca  - dato un elenco di nomi, dice quali sono in cache e con quale
             idFood, e quali mancano davvero
  estrai   - dato un idFood, riporta i nutrienti dello schema di alimenti.csv
             con la fonte citata per ciascuno

PERCHE' ESISTE
La cache contiene 1.109 alimenti. Cercarli uno a uno con ricerche web e' lento
e fragile, ed e' il passo che il protocollo indica come quello che fa
risparmiare piu' tempo se fatto in blocco. Farlo a mano significa anche
decidere a occhio, ogni volta, come trattare un valore "tr" o un campo
assente: le due cose che confuse producono falsi allarmi di carenza.

REGOLE APPLICATE - le stesse del protocollo, qui in codice
  valore numerico   -> si riporta
  "tr" (traccia)    -> si riporta il valore di soglia (vltraccia), NON zero
  valore assente    -> NON e' uno zero. Va segnalato come DA CERCARE ALTROVE
                       (livello 3 USDA) e, se manca ovunque, va scritto in
                       gap.csv con il motivo. Non basta segnalarlo a voce: se
                       non e' in gap.csv, il motore lo somma come zero reale.

COSA NON FA
Non scrive niente in alimenti.csv e non decide nulla. Riporta cosa la cache
contiene e con quale fonte, perche' la trascrizione resti una scelta
consapevole. Le kcal in particolare NON vengono proposte: si leggono da CREA,
mai da BDA-IEO ne' ricalcolate con 4/4/9.

USO
  python3 cerca_cache.py ricerca "sgombro" "cavolo nero" "farro"
  python3 cerca_cache.py ricerca --file nomi.txt
  python3 cerca_cache.py estrai 1300_2
"""

import json
import os
import sys
import unicodedata
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_DEFAULT = os.path.join(BASE, "cache.zip")

# Nutrienti dello schema congelato di alimenti.csv che BDA-IEO puo' coprire.
# L'energia e i macronutrienti sono ESCLUSI di proposito: per quelli la fonte
# e' CREA (gerarchia congelata), e prenderli da qui sarebbe un salto di livello.
MAPPA_NUTRIENTI = {
    "calcio_mg": ("Calcio", "mg"),
    "ferro_mg": ("Ferro", "mg"),
    "vitamina_d_ug": ("Vitamina D", "ug"),
    "folati_ug": ("Folati totali", "ug"),
    "vitamina_b12_ug": ("Vitamina B12", "ug"),
    "zinco_mg": ("Zinco", "mg"),
    "magnesio_mg": ("Magnesio", "mg"),
    "vitamina_c_mg": ("Vitamina C", "mg"),
}


def _normalizza(testo):
    """Minuscolo e senza accenti: 'PERÒ' e 'pero' devono incontrarsi."""
    testo = unicodedata.normalize("NFKD", str(testo).lower())
    return "".join(c for c in testo if not unicodedata.combining(c)).strip()


def apri_cache(path=None):
    path = path or CACHE_DEFAULT
    if not os.path.isfile(path):
        print(f"ERRORE: {os.path.basename(path)} non trovato.")
        print("La cache si scarica da GitHub, cartella motore-calcolo, e non")
        print("e' necessaria per calcolare un piano: serve solo per ampliare")
        print("il database alimenti.")
        return None
    return zipfile.ZipFile(path)


def carica_indice(z):
    """Elenco (idFood, descrizione) dall'indice _foods.json.

    Cercare nell'indice evita di aprire 1.109 file: e' la ragione per cui
    l'indice esiste.
    """
    dati = json.loads(z.read("cache/_foods.json"))
    return [(v["idFood"], v.get("description", "").strip())
            for v in dati.get("foods", [])]


def _percorso_voce(z, id_food):
    nome = f"cache/{id_food}.json"
    return nome if nome in z.namelist() else None


def ricerca(nomi, path=None):
    """Cerca un blocco di nomi nell'indice. Un solo passaggio per tutti."""
    z = apri_cache(path)
    if z is None:
        return 1
    indice = carica_indice(z)
    indice_norm = [(i, d, _normalizza(d)) for i, d in indice]

    print("=" * 72)
    print(f"RICERCA IN CACHE BDA-IEO - {len(indice)} alimenti indicizzati")
    print("=" * 72)

    trovati_tot, mancanti = 0, []
    for nome in nomi:
        chiave = _normalizza(nome)
        parole = chiave.split()
        esiti = [(i, d) for i, d, dn in indice_norm
                 if all(p in dn for p in parole)]
        print(f"\n  '{nome}'")
        if not esiti:
            print("     nessuna corrispondenza in cache")
            mancanti.append(nome)
            continue
        trovati_tot += 1
        for i, d in esiti[:12]:
            print(f"     {i:<12} {d}")
        if len(esiti) > 12:
            print(f"     ... e altri {len(esiti) - 12}")

    print("\n" + "=" * 72)
    print(f"{trovati_tot} nomi con almeno una corrispondenza, "
          f"{len(mancanti)} senza")
    if mancanti:
        print(f"Da cercare su CREA (livello 1) o USDA (livello 3): "
              f"{', '.join(mancanti)}")
    print("Un nome trovato NON significa che il dato sia utilizzabile:")
    print("controllare con 'estrai' quali campi la voce copre davvero.")
    print("=" * 72)
    return 0


def estrai(id_food, path=None):
    """Riporta i nutrienti utili di una voce, con fonte e casi speciali."""
    z = apri_cache(path)
    if z is None:
        return 1
    percorso = _percorso_voce(z, id_food)
    if percorso is None:
        print(f"ERRORE: idFood '{id_food}' non presente in cache.")
        print("Gli idFood si ottengono con 'cerca_cache.py ricerca'.")
        return 1

    dati = json.loads(z.read(percorso))
    info = dati["info"]["foodInfo"]

    # appiattisce le famiglie in un unico indice per nome componente
    componenti = {}
    for famiglia in dati["components"]["foodComponents"]:
        for c in famiglia.get("components", []):
            componenti.setdefault(_normalizza(c.get("dscomp") or ""), c)

    print("=" * 72)
    print(f"{info['description'].strip()}")
    print(f"idFood {info['idFood']}   (BDA-IEO)")
    if info.get("note"):
        print(f"nota: {info['note'].strip()[:200]}")
    print("=" * 72)
    print("Valori per 100 g di parte edibile. Energia e macronutrienti non")
    print("sono riportati: per quelli la fonte e' CREA (gerarchia congelata).\n")

    da_cercare_altrove = []
    for colonna, (nome_bda, unita) in MAPPA_NUTRIENTI.items():
        c = componenti.get(_normalizza(nome_bda))
        if c is None:
            print(f"  {colonna:<18} --        componente non presente nella voce")
            da_cercare_altrove.append(colonna)
            continue

        valore = c.get("valore")
        if valore is None or str(valore).strip() == "":
            print(f"  {colonna:<18} --        DATO ASSENTE -> scendere al "
                  f"livello 3 (USDA)")
            da_cercare_altrove.append(colonna)
            continue

        if c.get("flTr") or str(valore).lower() == "tr":
            soglia = c.get("vltraccia")
            if soglia is None:
                print(f"  {colonna:<18} tr        traccia senza soglia "
                      f"dichiarata: verificare a mano")
                da_cercare_altrove.append(colonna)
            else:
                print(f"  {colonna:<18} {soglia:<9} TRACCIA: si scrive la "
                      f"soglia {soglia} {unita}, non zero")
            continue

        fonte = (c.get("dsfonte") or "").strip()
        print(f"  {colonna:<18} {valore:<9} {unita}")
        if fonte:
            print(f"  {'':<18} fonte: {fonte[:90]}")

    print()
    if da_cercare_altrove:
        print("DA NON LASCIARE A ZERO - questi campi la cache non li copre:")
        print(f"  {', '.join(da_cercare_altrove)}")
        print("Interrogare USDA (livello 3). Cio' che manca anche li' va")
        print("scritto in gap.csv con il motivo: uno zero non dichiarato viene")
        print("sommato come assenza reale e produce un falso allarme di carenza.")
    else:
        print("La voce copre tutti i nutrienti dello schema coperti da BDA-IEO.")
    print("Attenzione agli alimenti fortificati negli USA (latte, cereali,")
    print("farine, bevande vegetali): il dato USDA non e' trasferibile.")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip().split("USO")[-1].strip())
        return 1
    modo = sys.argv[1]
    argomenti = sys.argv[2:]

    if modo == "ricerca":
        if argomenti[:1] == ["--file"]:
            if len(argomenti) < 2:
                print("--file richiede il percorso di un file di nomi, uno per riga")
                return 1
            with open(argomenti[1], encoding="utf-8") as f:
                nomi = [r.strip() for r in f if r.strip()]
        else:
            nomi = argomenti
        if not nomi:
            print("Nessun nome da cercare.")
            return 1
        return ricerca(nomi)

    if modo == "estrai":
        if not argomenti:
            print("estrai richiede un idFood (es. 1300_2)")
            return 1
        return estrai(argomenti[0])

    print(f"Modo sconosciuto: {modo}. Usare 'ricerca' o 'estrai'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
