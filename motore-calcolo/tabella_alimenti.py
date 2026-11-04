#!/usr/bin/env python3
"""
Tabella di tutti gli alimenti del motore, pronta alla lettura (04/11/2026).

Unisce alimenti.csv, lipidi.csv, gap.csv e nomi_paziente.csv. Non contiene dati propri: i
valori e le fonti restano nei CSV. Un dato mancante compare come «n.d.», mai come zero.

USO
  python3 tabella_alimenti.py --genera-pagina   riscrive TABELLA_ALIMENTI.md
  python3 tabella_alimenti.py --json FILE       i dati per la pagina di consultazione

Il collaudo (controllo 12) si ferma se TABELLA_ALIMENTI.md non coincide con i CSV.
"""
import argparse
import csv
import json
import os

QUI = os.path.dirname(os.path.abspath(__file__))
FILE_PAGINA = os.path.join(QUI, "TABELLA_ALIMENTI.md")
MACRO = (("kcal_100g", "kcal"), ("proteine_g", "Prot g"), ("carboidrati_g", "Carb g"),
         ("grassi_g", "Grassi g"), ("fibra_g", "Fibra g"))
MICRO = (("calcio_mg", "Ca mg"), ("ferro_mg", "Fe mg"), ("vitamina_d_ug", "Vit D µg"),
         ("folati_ug", "Folati µg"), ("vitamina_b12_ug", "B12 µg"), ("zinco_mg", "Zn mg"),
         ("magnesio_mg", "Mg mg"), ("vitamina_c_mg", "Vit C mg"))
LIPIDI = (("saturi_g", "Saturi g"), ("monoinsaturi_g", "Mono g"), ("polinsaturi_g", "Poli g"),
          ("epa_g", "EPA g"), ("dha_g", "DHA g"), ("colesterolo_mg", "Col mg"))
GRUPPI = (("Energia e macronutrienti", MACRO), ("Micronutrienti", MICRO), ("Lipidi", LIPIDI))


def _righe(nome):
    with open(os.path.join(QUI, nome), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def voci():
    """Una voce per alimento, nell'ordine di categoria e nome."""
    lipidi = {r["food_id"]: r for r in _righe("lipidi.csv")}
    gap = {}
    for r in _righe("gap.csv"):
        gap.setdefault(r["food_id"], {})[r["nutriente"]] = r["motivo"]
    out = []
    for a in _righe("alimenti.csv"):
        fid = a["food_id"]
        lip = lipidi.get(fid, {})
        valori, manca = {}, gap.get(fid, {})
        for chiave, _ in MACRO + MICRO + LIPIDI:
            v = a[chiave] if chiave in a else lip.get(chiave, "")
            valori[chiave] = None if chiave in manca or v in ("", None) else float(v)
        out.append({"food_id": fid, "nome": a["nome"], "categoria": a["categoria"],
                    "fonte": a["fonte"], "codice": a["codice_fonte"], "verifica": a["data_verifica"],
                    "fonte_lipidi": lip.get("fonte", ""), "codice_lipidi": lip.get("codice_fonte", ""),
                    "metodo_lipidi": lip.get("metodo", ""), "valori": valori, "mancanti": manca})
    return sorted(out, key=lambda x: (x["categoria"], x["nome"].lower()))


def _cifra(v):
    return "n.d." if v is None else f"{v:g}".replace(".", ",")


def testo_pagina():
    tutte = voci()
    con_gap = [v for v in tutte if v["mancanti"]]
    L = ["# Tabella degli alimenti", "",
         "Generata da `tabella_alimenti.py --genera-pagina` dai CSV del motore: non si modifica a "
         "mano. Valori per 100 g di parte edibile. «n.d.» = dato mancante, dichiarato in `gap.csv`: "
         "non è uno zero.", "",
         f"**{len(tutte)} alimenti**, {sum(len(v['mancanti']) for v in tutte)} valori mancanti su "
         f"{len(con_gap)} alimenti.", ""]
    L += ["## Valori mancanti", "", "| Alimento | Nutriente | Motivo |", "|---|---|---|"]
    for v in con_gap:
        L += [f"| {v['nome']} | {n} | {m} |" for n, m in sorted(v["mancanti"].items())]
    for cat in sorted({v["categoria"] for v in tutte}):
        L += ["", f"## {cat.capitalize()}"]
        righe = [v for v in tutte if v["categoria"] == cat]
        for titolo, cols in GRUPPI:
            L += ["", f"### {titolo}", "", "| Alimento | " + " | ".join(c[1] for c in cols) + " |",
                  "|---|" + "---:|" * len(cols)]
            L += ["| " + v["nome"] + " | " + " | ".join(_cifra(v["valori"][c[0]]) for c in cols) + " |"
                  for v in righe]
        L += ["", "### Fonti", "", "| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |",
              "|---|---|---|---|---|---|"]
        L += [f"| {v['nome']} | {v['food_id']} | {v['fonte']} | {v['codice']} | {v['verifica']} | "
              f"{v['fonte_lipidi']} {v['codice_lipidi']} |" for v in righe]
    return "\n".join(L) + "\n"


def controlla():
    try:
        with open(FILE_PAGINA, encoding="utf-8") as f:
            return f.read() == testo_pagina()
    except OSError:
        return False


if __name__ == "__main__":
    a = argparse.ArgumentParser(description="Tabella degli alimenti")
    a.add_argument("--genera-pagina", action="store_true")
    a.add_argument("--json")
    o = a.parse_args()
    if o.genera_pagina:
        with open(FILE_PAGINA, "w", encoding="utf-8") as f:
            f.write(testo_pagina())
    if o.json:
        with open(o.json, "w", encoding="utf-8") as f:
            json.dump({"voci": voci(), "gruppi": [[t, c] for t, c in GRUPPI]}, f, ensure_ascii=False)
