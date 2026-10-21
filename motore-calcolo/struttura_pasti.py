#!/usr/bin/env python3
"""
Catalogo delle colazioni e degli spuntini - Studio Nutrizionale Taglialatela

COSA E'
Il protocollo struttura pasti prevede 4 colazioni (2 salate, 2 dolci) e 2
spuntini, uguali per tutti i giorni strutturati del piano, in due livelli:
'standard' e 'rinforzata_calcio'. La scelta del livello e' UNA SOLA DECISIONE
PER L'INTERO PIANO, mai giorno per giorno.

Questo modulo legge il catalogo e permette di RICONOSCERE a quale livello
appartengono la colazione e lo spuntino di un piano - non solo di verificare
che siano uniformi tra i giorni.

PERCHE' IL CATALOGO NON CONTIENE PIU' I VALORI NUTRIZIONALI
La prima versione del file portava kcal, macro, calcio e vitamina D
precalcolati accanto agli ingredienti. Il 28/07/2026 il ricalcolo col motore
ha trovato 71 valori su 72 corretti e uno sbagliato: l'alternativa S1
dichiarava 0.20 ug di vitamina D contro 2.10 reali, un fattore dieci sul
nutriente che e' gia' il limite noto della dieta, e nella direzione che fa
sembrare coperto cio' che non lo e'. Il dato a monte era sano (uovo intero,
1.75 ug/100 g da BDA-IEO, coerente con i 2.0 di USDA): l'errore stava nel
derivato.

Un valore derivato che nessuno ricontrolla diverge prima o poi dalla fonte.
Il catalogo dichiara quindi SOLO gli ingredienti; kcal e nutrienti si
ricalcolano sempre da alimenti.csv, che e' la fonte. La leggibilita' a occhio
si ottiene con 'python3 struttura_pasti.py', che ristampa la tabella
aggiornata: cosi' e' sempre fresca invece di essere congelata e sbagliata.

SCHEMA - file affiancato, non fa parte dello schema congelato
colazioni_spuntini.csv
  alternativa_id, livello, tipo, ingredienti_food_id_grammi, nota
  livello: standard | rinforzata_calcio
  tipo:    salata | dolce | spuntino
  ingredienti: "food_id:grammi;food_id:grammi;..."
"""

import csv
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CATALOGO_DEFAULT = os.path.join(BASE, "colazioni_spuntini.csv")

TIPI_COLAZIONE = ("salata", "dolce")


def carica_catalogo(path=None):
    path = path or CATALOGO_DEFAULT
    if not os.path.isfile(path):
        return []
    voci = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            voci.append({
                "alternativa_id": row["alternativa_id"].strip(),
                "livello": row["livello"].strip(),
                "tipo": row["tipo"].strip(),
                "ingredienti": _parse_ingredienti(row["ingredienti_food_id_grammi"]),
                "nota": (row.get("nota") or "").strip(),
            })
    return voci


def _parse_ingredienti(testo):
    """'1800:120;000550:60' -> [('1800', 120.0), ('000550', 60.0)]"""
    fuori = []
    for pezzo in testo.split(";"):
        pezzo = pezzo.strip()
        if not pezzo:
            continue
        fid, _, grammi = pezzo.partition(":")
        fuori.append((fid.strip(), float(grammi)))
    return fuori


def firma(ingredienti):
    """Firma confrontabile di un'alternativa: insieme di (food_id, grammi).

    Insieme e non lista, perche' l'ordine degli ingredienti nel CSV e
    nel piano non deve contare.
    """
    return frozenset((fid, round(g, 3)) for fid, g in ingredienti)


def valori(db, ingredienti):
    """Ricalcola i nutrienti di un'alternativa da alimenti.csv."""
    from calcolatore import calcola_riga, somma_nutrienti
    return somma_nutrienti([calcola_riga(db[fid], g) for fid, g in ingredienti])


def food_id_mancanti(catalogo, db):
    """food_id del catalogo assenti dal database: il catalogo e' un file
    affiancato e puo' disallinearsi da alimenti.csv senza che nulla lo veda."""
    mancanti = []
    for voce in catalogo:
        for fid, _ in voce["ingredienti"]:
            if fid not in db:
                mancanti.append((voce["alternativa_id"], fid))
    return mancanti


def livelli_disponibili(catalogo):
    return sorted({v["livello"] for v in catalogo})


def identifica_livello(firme_piano, catalogo, pasto):
    """Riconosce a quale livello del catalogo appartengono le alternative
    trovate nel piano per un dato pasto.

    firme_piano: insieme di firme (una per alternativa offerta dal piano)
    pasto: "colazione" | "spuntino" | "spuntino2"
           (il secondo spuntino si confronta con gli spuntini del catalogo:
           stesse regole dello spuntino, decisione del 30/09/2026)

    Restituisce (livello, esito, dettaglio) dove esito e':
      "esatto"      tutte le alternative del piano sono di quel livello E
                    sono tutte quelle previste dal livello
      "parziale"    tutte di quel livello, ma non tutte quelle previste
                    (o alcune ripetute): il paziente ha meno scelta del
                    protocollo
      "misto"       alternative appartenenti a livelli diversi -> incoerenza
      "fuori"       nessuna corrispondenza: alternative personalizzate

    'misto' e' il caso che questo modulo esiste per intercettare: colazione
    del livello standard e spuntino del rinforzato (o viceversa) e' una
    combinazione che il controllo di sola uniformita' tra giorni non vede,
    perche' ogni giorno e' identico all'altro.
    """
    if pasto == "colazione":
        tipi = TIPI_COLAZIONE
    elif pasto in ("spuntino", "spuntino2"):
        tipi = ("spuntino",)
    else:
        raise ValueError(f"identifica_livello: pasto '{pasto}' non soggetto "
                         f"al catalogo colazioni_spuntini.csv")
    per_livello = {}
    for voce in catalogo:
        if voce["tipo"] not in tipi:
            continue
        per_livello.setdefault(voce["livello"], {})[firma(voce["ingredienti"])] = \
            voce["alternativa_id"]

    if not per_livello:
        return None, "fuori", "catalogo privo di alternative per questo pasto"

    # a quale livello appartiene ciascuna firma del piano
    appartenenza = {}
    for f in firme_piano:
        trovati = [liv for liv, m in per_livello.items() if f in m]
        appartenenza[f] = trovati[0] if trovati else None

    livelli_visti = {liv for liv in appartenenza.values() if liv}
    non_riconosciute = [f for f, liv in appartenenza.items() if liv is None]

    if len(livelli_visti) > 1:
        riepilogo = []
        for liv in sorted(livelli_visti):
            ids = sorted(per_livello[liv][f] for f, l in appartenenza.items()
                         if l == liv)
            riepilogo.append(f"{liv}: {', '.join(ids)}")
        return None, "misto", " / ".join(riepilogo)

    if not livelli_visti:
        return None, "fuori", (f"{len(firme_piano)} alternativa/e non presente/i "
                               f"nel catalogo")

    livello = next(iter(livelli_visti))
    attese = set(per_livello[livello])
    trovate = {f for f, l in appartenenza.items() if l == livello}
    ids_trovate = sorted(per_livello[livello][f] for f in trovate)

    if non_riconosciute:
        return livello, "misto", (
            f"{len(trovate)} alternativa/e del livello {livello} "
            f"({', '.join(ids_trovate)}) piu' {len(non_riconosciute)} "
            f"non presente/i nel catalogo")

    if trovate == attese:
        return livello, "esatto", ", ".join(ids_trovate)

    mancanti = sorted(per_livello[livello][f] for f in attese - trovate)
    return livello, "parziale", (
        f"presenti {', '.join(ids_trovate)} - mancano dal piano "
        f"{', '.join(mancanti)} (il protocollo ne prevede {len(attese)})")


def stampa_tabella(path=None, path_alimenti=None):
    """Ristampa il catalogo con i valori RICALCOLATI dal database.

    Sostituisce i valori precalcolati che il file conteneva prima: la tabella
    e' leggibile come allora, ma non puo' divergere da alimenti.csv perche'
    viene prodotta al momento.
    """
    from calcolatore import carica_alimenti

    path_alimenti = path_alimenti or os.path.join(BASE, "alimenti.csv")
    catalogo = carica_catalogo(path)
    if not catalogo:
        print("Catalogo non trovato o vuoto.")
        return 1
    db = carica_alimenti(path_alimenti)

    mancanti = food_id_mancanti(catalogo, db)
    if mancanti:
        print("ERRORE: food_id del catalogo assenti da alimenti.csv:")
        for aid, fid in mancanti:
            print(f"  {aid}: {fid}")
        return 1

    print("=" * 78)
    print("CATALOGO COLAZIONI E SPUNTINI - valori ricalcolati da alimenti.csv")
    print("=" * 78)
    print("I valori NON sono memorizzati nel catalogo: sono ricalcolati a ogni")
    print("esecuzione. Il catalogo dichiara solo gli ingredienti.\n")

    for livello in livelli_disponibili(catalogo):
        print(f"\n--- LIVELLO {livello.upper()} ---")
        print(f"  {'ID':<6} {'tipo':<9} {'kcal':>6} {'P':>6} {'C':>6} {'G':>6} "
              f"{'Ca mg':>7} {'vitD':>6}  nota")
        for voce in catalogo:
            if voce["livello"] != livello:
                continue
            t = valori(db, voce["ingredienti"])
            print(f"  {voce['alternativa_id']:<6} {voce['tipo']:<9} "
                  f"{t['kcal_100g']:>6.0f} {t['proteine_g']:>6.1f} "
                  f"{t['carboidrati_g']:>6.1f} {t['grassi_g']:>6.1f} "
                  f"{t['calcio_mg']:>7.0f} {t['vitamina_d_ug']:>6.2f}  "
                  f"{voce['nota']}")

        colazioni = [v for v in catalogo
                     if v["livello"] == livello and v["tipo"] in TIPI_COLAZIONE]
        if colazioni:
            kcal = [valori(db, v["ingredienti"])["kcal_100g"] for v in colazioni]
            print(f"\n  Colazioni: {len(colazioni)} alternative, "
                  f"{min(kcal):.0f}-{max(kcal):.0f} kcal "
                  f"(scarto {max(kcal) - min(kcal):.0f})")
            if max(kcal) - min(kcal) > 60:
                print("    ATTENZIONE: le 4 colazioni vanno tenute il piu' vicine")
                print("    possibile tra loro, perche' la scelta del paziente non")
                print("    sposti il bilancio della giornata.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(stampa_tabella())
