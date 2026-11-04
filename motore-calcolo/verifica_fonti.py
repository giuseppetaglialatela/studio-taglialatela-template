#!/usr/bin/env python3
"""
Controllo di ogni valore del database contro le schede delle fonti (04/11/2026).

Per ogni cella di alimenti.csv cerca il valore nelle schede CREA e BDA-IEO dell'alimento,
trovate da codice_fonte, food_id e dalla scheda dichiarata in lipidi.csv. Tre esiti:
  verificata       coincide con una scheda (entro l'arrotondamento);
  diversa          ci sono schede ma nessuna coincide;
  senza scheda     la fonte non e' in cache (USDA, INSA): si riporta, non si inventa.
Lo stesso per lipidi.csv quando la scheda e' dichiarata e i grassi coincidono.

Le differenze gia' note stanno in differenze_note.csv: alcune sono legittime (proxy,
USDA, INSA), altre da esaminare. Il collaudo si ferma su ogni differenza NON elencata.

USO  python3 verifica_fonti.py [--elenco] [--scrivi-note]
"""
import csv
import io
import json
import os
import re
import sys
import zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
BDA = {"kcal_100g": "Energia, Ric con fibra", "proteine_g": "Proteine totali",
       "carboidrati_g": "Carboidrati disponibili (MSE)", "grassi_g": "Lipidi totali",
       "fibra_g": "Fibra alimentare totale", "calcio_mg": "Calcio", "ferro_mg": "Ferro",
       "vitamina_d_ug": "Vitamina D", "folati_ug": "Folati totali",
       "vitamina_b12_ug": "Vitamina B12", "zinco_mg": "Zinco", "magnesio_mg": "Magnesio",
       "vitamina_c_mg": "Vitamina C"}
CREA = {"kcal_100g": "Energia (kcal)", "calcio_mg": "Calcio (mg)", "ferro_mg": "Ferro (mg)",
        "vitamina_d_ug": "Vitamina D (μg)", "folati_ug": "Folati (μg)",
        "vitamina_b12_ug": "Vitamina B12 (μg)", "zinco_mg": "Zinco (mg)",
        "magnesio_mg": "Magnesio (mg)", "vitamina_c_mg": "Vitamina C (mg)"}
MACRO = ("kcal_100g", "proteine_g", "carboidrati_g", "grassi_g", "fibra_g")
LIP = {"saturi_g": "Acidi grassi saturi totali", "monoinsaturi_g": "Acidi grassi monoinsaturi totali",
       "polinsaturi_g": "Acidi grassi polinsaturi totali", "colesterolo_mg": "Colesterolo"}


def _num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def uguale(a, b):
    """Coincidono entro l'arrotondamento a una cifra in meno."""
    return abs(a - b) <= max(0.0051, 0.006 * abs(b)) or round(a) == round(b) and abs(b) >= 10


def schede_bda():
    z = zipfile.ZipFile(os.path.join(QUI, "cache.zip"))
    return z, {os.path.basename(n)[:-5] for n in z.namelist()
               if n.endswith(".json") and n.startswith("cache/")}


def _bda(z, codice, cache={}):
    if codice not in cache:
        d = json.loads(z.read(f"cache/{codice}.json"))
        r = {}
        for f in d["components"]["foodComponents"]:
            for k in f["components"]:
                if k["dscomp"].startswith("Energia") and k["cnum"] != "kcal":
                    continue
                r.setdefault(k["dscomp"], k["valore"])
        cache[codice] = r
    return cache[codice]


def esamina():
    with open(os.path.join(QUI, "alimenti.csv"), newline="", encoding="utf-8") as f:
        alimenti = list(csv.DictReader(f))
    with open(os.path.join(QUI, "lipidi.csv"), newline="", encoding="utf-8") as f:
        lipidi = {r["food_id"]: r for r in csv.DictReader(f)}
    with open(os.path.join(QUI, "gap.csv"), newline="", encoding="utf-8") as f:
        gap = {(r["food_id"], r["nutriente"]) for r in csv.DictReader(f)}
    z, nomi = schede_bda()
    testo = zipfile.ZipFile(os.path.join(QUI, "crea_cache.zip")).read("crea_cache.csv").decode("utf-8")
    crea = {}
    for r in csv.DictReader(io.StringIO(testo, newline="")):
        crea.setdefault(r["codice_crea"], {})[r["nutriente"]] = r["valore_100g"]
    esito = {"verificata": 0, "diversa": [], "senza_scheda": []}
    for a in alimenti:
        codici = set(re.split(r"[+\s]", a["codice_fonte"])) | {a["food_id"]}
        lip = lipidi.get(a["food_id"], {})
        codici |= set(lip.get("codice_fonte", "").split("+"))
        bda = [c2 for c in codici for c2 in (c, c + "_2", c + "_1") if c2 in nomi]
        cr = [c for c in codici if c in crea or c.zfill(6) in crea]
        for col in BDA:
            if (a["food_id"], col) in gap:
                continue
            v = float(a[col])
            # kcal e macro delle righe CREA: solo la scheda CREA della riga (non quella
            # BDA, che per legumi cotti e simili riguarda un altro stato dell'alimento)
            macro_crea = a["fonte"].startswith("CREA") and col in MACRO
            if macro_crea:
                continue                    # coperte da cerca_crea.py verifica, nel collaudo
            trovati = [_num(_bda(z, c).get(BDA[col])) for c in bda]
            for c in cr:
                s = crea.get(c) or crea.get(c.zfill(6))
                trovati.append(_num(s.get(CREA.get(col, ""), None)))
            trovati = [t for t in trovati if t is not None]
            if not trovati:
                esito["senza_scheda"].append((a["nome"], col, v, a["fonte"]))
            elif any(uguale(v, t) for t in trovati):
                esito["verificata"] += 1
            else:
                esito["diversa"].append((a["nome"], col, v, trovati, a["fonte"]))
        if lip and "coincidenti" in lip.get("metodo", ""):
            cod = lip["codice_fonte"].split("+")[0]
            if cod in nomi:
                for col, nome in LIP.items():
                    if lip[col] == "":
                        continue
                    t = _num(_bda(z, cod).get(nome))
                    if t is None:
                        esito["senza_scheda"].append((a["nome"], col, float(lip[col]), lip["fonte"]))
                    elif uguale(float(lip[col]), t):
                        esito["verificata"] += 1
                    else:
                        esito["diversa"].append((a["nome"], col, float(lip[col]), [t], lip["fonte"]))
    return esito


FILE_NOTE = os.path.join(QUI, "differenze_note.csv")


def _chiave(x):
    return (x[0], x[1], f"{x[2]:g}")


def nuove():
    """Differenze non elencate tra le note: per il collaudo."""
    with open(FILE_NOTE, newline="", encoding="utf-8") as f:
        note = {(r["alimento"], r["colonna"], r["valore"]) for r in csv.DictReader(f)}
    return [x for x in esamina()["diversa"] if _chiave(x) not in note]


def scrivi_note(e):
    with open(FILE_NOTE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["alimento", "colonna", "valore", "schede", "fonte", "stato"])
        for x in e["diversa"]:
            w.writerow([*_chiave(x), "|".join(f"{t:g}" for t in x[3]), x[4], "da_esaminare"])


if __name__ == "__main__":
    e = esamina()
    print(f"verificate {e['verificata']}, diverse {len(e['diversa'])}, senza scheda {len(e['senza_scheda'])}")
    if "--scrivi-note" in sys.argv:
        scrivi_note(e)
    if "--elenco" in sys.argv:
        for x in e["diversa"]:
            print("DIVERSA", x)
