#!/usr/bin/env python3
"""
Interrogazione della cache CREA - Studio Nutrizionale Taglialatela

COSA FA
Legge `crea_cache.zip` (o `crea_cache.csv`): copia locale delle 832 schede delle
Tabelle di composizione degli alimenti CREA 2019, scaricata dal sito il
20/09/2026. Per ogni alimento riporta i valori dello schema di alimenti.csv
con il CODICE DI ORIGINE di ciascun valore, cosi' si vede cosa e' misurato e
cosa e' imputato.

Tre modi:
  ricerca  - dati uno o piu' nomi, elenca le schede che li contengono
             (tutte le parole devono comparire nel nome CREA)
  estrai   - dato un codice CREA, riporta i nutrienti dello schema con origine
  verifica - confronta kcal, macro e fibra delle righe CREA di alimenti.csv con
             la cache (audit: nessuna modifica)

PERCHE' ESISTE
Il passo 5 del protocollo di estrazione (M6) leggeva le schede CREA dal sito
tramite un fetch che passa da un riassunto di modello: non e' una copia, e un
valore trascritto male non lascia traccia. Qui la lettura e' deterministica e
ripetibile. Il 01/10/2026 il confronto con la cache ha trovato 7 kcal di
alimenti.csv diverse da CREA (poi allineate): senza questo strumento non
sarebbero emerse.

CODICI DI ORIGINE (cosi' come compaiono nella cache, senza reinterpretarli)
  A        valore con metodo analitico dichiarato
  C        valore calcolato (energia Southgate, carboidrati disponibili...)
  ZL, S    valore IMPUTATO (metodica "Imputation"): non e' una misura
  B        metodica non dichiarata nella scheda
Uno zero con origine ZL/S e' un'assunzione, non un dato: stessa trappola dello
"zero assunto" USDA (M1, sezione 7). Lo strumento lo segnala.

REGOLE APPLICATE (le stesse del protocollo)
  valore numerico    -> si riporta
  "tr" (traccia)     -> NON si scrive zero: la cache CREA non porta la soglia,
                        va deciso (BDA-IEO la pubblica come vltraccia)
  valore assente     -> NON e' uno zero: scendere a BDA-IEO (cerca_cache.py) e
                        poi a USDA; solo se manca ovunque, riga in gap.csv

COSA NON FA
Non scrive niente in alimenti.csv. Le kcal e i macro restano quelli CREA
(gerarchia fonti, M1); i micronutrienti mancanti si cercano nei livelli
successivi.

USO
  python3 cerca_crea.py ricerca "yogurt greco" "ravanelli"
  python3 cerca_crea.py estrai 150030
  python3 cerca_crea.py verifica
  python3 cerca_crea.py --autotest
"""

import csv
import io
import os
import sys
import zipfile
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

# colonna di alimenti.csv -> nome del nutriente nella cache CREA
SCHEMA = [
    ("kcal_100g", "Energia (kcal)"),
    ("proteine_g", "Proteine (g)"),
    ("carboidrati_g", "Carboidrati disponibili (g)"),
    ("grassi_g", "Lipidi (g)"),
    ("fibra_g", "Fibra totale (g)"),
    ("calcio_mg", "Calcio (mg)"),
    ("ferro_mg", "Ferro (mg)"),
    ("vitamina_d_ug", "Vitamina D (μg)"),
    ("folati_ug", "Folati (μg)"),
    ("vitamina_b12_ug", "Vitamina B12 (μg)"),
    ("zinco_mg", "Zinco (mg)"),
    ("magnesio_mg", "Magnesio (mg)"),
    ("vitamina_c_mg", "Vitamina C (mg)"),
]
COLONNE_VERIFICA = ["kcal_100g", "proteine_g", "carboidrati_g", "grassi_g",
                    "fibra_g"]
IMPUTATI = {"ZL", "S"}
TOLLERANZA_VERIFICA = 0.051  # arrotondamento a 1 decimale


def _norma(nome):
    # nella cache esistono sia la mu greca (U+03BC) sia il micro (U+00B5)
    return nome.replace("µ", "μ")


def carica():
    """Restituisce {codice: {"nome", "edibile", "nutr": {nome: (valore, origine)}}}."""
    csv_path = os.path.join(BASE, "crea_cache.csv")
    zip_path = os.path.join(BASE, "crea_cache.zip")
    if os.path.exists(csv_path):
        testo = open(csv_path, encoding="utf-8", newline="").read()
    elif os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path) as z:
            testo = z.read("crea_cache.csv").decode("utf-8")
    else:
        sys.exit("crea_cache.zip non trovata accanto a cerca_crea.py. Scaricala "
                 "dalla cartella motore-calcolo del repository (stessa cartella "
                 "di alimenti.csv).")
    db = {}
    for r in csv.DictReader(io.StringIO(testo, newline="")):
        voce = db.setdefault(r["codice_crea"], {
            "nome": r["nome_crea"], "edibile": r["parte_edibile"], "nutr": {}})
        voce["nutr"][_norma(r["nutriente"])] = (r["valore_100g"],
                                                r["origine_dato"])
    return db


def _numero(testo):
    try:
        return float(testo.replace(",", "."))
    except ValueError:
        return None


def ricerca(db, nomi):
    for q in nomi:
        parole = q.lower().split()
        trovati = [(c, v["nome"], v["edibile"]) for c, v in sorted(db.items())
                   if all(p in v["nome"].lower() for p in parole)]
        print(f"\n  '{q}'")
        if not trovati:
            print("     nessuna corrispondenza in cache CREA")
            continue
        for c, n, e in trovati[:15]:
            print(f"     {c:8s} {n}   [parte edibile {e}]")
        if len(trovati) > 15:
            print(f"     ... e altri {len(trovati) - 15}")


def estrai(db, codice):
    codice = codice.zfill(6)
    if codice not in db:
        sys.exit(f"codice {codice} non presente nella cache CREA")
    v = db[codice]
    print("=" * 72)
    print(f"{v['nome']}\ncodice CREA {codice}   parte edibile {v['edibile']}")
    print("=" * 72)
    print("Valori per 100 g di parte edibile.\n")
    assenti, imputati, tracce = [], [], []
    for colonna, nutriente in SCHEMA:
        dato = v["nutr"].get(nutriente)
        if dato is None:
            print(f"  {colonna:16s} ASSENTE in CREA")
            assenti.append(colonna)
            continue
        valore, origine = dato
        nota = ""
        if valore.strip().lower() == "tr":
            nota = "  TRACCIA: non scrivere 0, soglia da BDA-IEO"
            tracce.append(colonna)
        elif origine in IMPUTATI:
            nota = "  IMPUTATO (non misurato)"
            imputati.append(colonna)
        print(f"  {colonna:16s} {valore:8s} origine {origine}{nota}")
    print()
    if assenti:
        print("Campi assenti: scendere a BDA-IEO (cerca_cache.py), poi USDA con la "
              "verifica di derivazione (M1). Solo se mancano ovunque: gap.csv.")
        print("  " + ", ".join(assenti))
    if imputati:
        print("Valori imputati: verifica che gli zeri siano biologici (es. fibra in "
              "un alimento animale) e non assenze di dato: uno zero imputato non "
              "e' uno zero misurato.")
        print("  " + ", ".join(imputati))
    if tracce:
        print("Tracce: " + ", ".join(tracce))
    if v["edibile"].strip() not in ("100 %", "100%"):
        print(f"Parte edibile {v['edibile']}: i valori sono per 100 g di PARTE "
              "EDIBILE. Il peso nel piano (osso, buccia, scarto) va convertito.")


def verifica(db, path_alimenti):
    righe = list(csv.DictReader(open(path_alimenti, encoding="utf-8",
                                     newline="")))
    confrontate, differenze, fuori_cache = 0, [], []
    for r in righe:
        if "CREA" not in r["fonte"]:
            continue
        codice = r["codice_fonte"].split("+")[0].zfill(6)
        if codice not in db:
            fuori_cache.append((r["food_id"], r["nome"]))
            continue
        confrontate += 1
        for colonna in COLONNE_VERIFICA:
            nutriente = dict(SCHEMA)[colonna]
            dato = db[codice]["nutr"].get(nutriente)
            if dato is None:
                continue
            crea, mio = _numero(dato[0]), _numero(r[colonna])
            if crea is None or mio is None:
                continue
            if abs(crea - mio) > TOLLERANZA_VERIFICA:
                differenze.append((r["food_id"], r["nome"], colonna, mio, crea))
    print(f"Righe con fonte CREA confrontate con la cache: {confrontate}")
    if fuori_cache:
        print(f"Codice non trovato in cache ({len(fuori_cache)}): {fuori_cache}")
    if differenze:
        print(f"DIFFERENZE: {len(differenze)}")
        for fid, nome, col, mio, crea in differenze:
            print(f"  {fid:8s} {nome:34s} {col:14s} database {mio:g}  CREA {crea:g}")
    else:
        print("Nessuna differenza su kcal, macro e fibra.")
    return 1 if (differenze or fuori_cache) else 0


def autotest(db):
    """Fissa alcuni valori noti della cache: se cambiano, la cache non e' quella."""
    attesi = [
        ("009010", "Energia (kcal)", "625"),
        ("009010", "Magnesio (mg)", "18"),      # incoerente con le altre fonti
        ("150030", "Energia (kcal)", "51"),
        ("150030", "Lipidi (g)", "0"),
        ("135030", "Fibra totale (g)", "0"),
    ]
    ok = True
    for codice, nutriente, atteso in attesi:
        dato = db.get(codice, {}).get("nutr", {}).get(nutriente)
        esito = dato is not None and dato[0] == atteso
        ok &= esito
        print(f"  [{'OK ' if esito else 'XX '}] {codice} {nutriente}: "
              f"atteso {atteso}, trovato {dato[0] if dato else None}")
    n = len(db)
    esito = n == 832
    ok &= esito
    print(f"  [{'OK ' if esito else 'XX '}] schede in cache: {n} (attese 832)")
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    db = carica()
    modo = argv[1]
    if modo == "ricerca" and len(argv) > 2:
        ricerca(db, argv[2:])
        return 0
    if modo == "estrai" and len(argv) == 3:
        estrai(db, argv[2])
        return 0
    if modo == "verifica":
        return verifica(db, os.path.join(BASE, "alimenti.csv"))
    if modo == "--autotest":
        return autotest(db)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
