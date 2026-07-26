#!/usr/bin/env python3
"""
Motore di calcolo - Studio Nutrizionale Taglialatela
Calcolatrice deterministica: legge database alimenti (CSV) + composizione
piano (CSV) + target/LARN paziente (CSV), produce totali per pasto e per
giorno con confronto rispetto a target e riferimenti LARN.

SCHEMA CONGELATO - non modificare le colonne senza aggiornare questo commento
e tutti i file dati esistenti.

alimenti.csv:
  food_id, nome, categoria, fonte, codice_fonte, data_verifica,
  kcal_100g, proteine_g, carboidrati_g, grassi_g, fibra_g,
  calcio_mg, ferro_mg, vitamina_d_ug, folati_ug, vitamina_b12_ug,
  zinco_mg, magnesio_mg, vitamina_c_mg
  (tutti i valori nutrizionali riferiti a 100g di parte edibile)

piano.csv:
  giorno, pasto, food_id, grammi
  (pasto ammessi: colazione | pranzo | spuntino | cena)

target.csv:
  parametro, valore
  chiavi attese: kcal_target, proteine_pct_target, carboidrati_pct_target,
  grassi_pct_target, fibra_g_target, larn_calcio_mg, larn_ferro_mg,
  larn_vitamina_d_ug, larn_folati_ug, larn_vitamina_b12_ug, larn_zinco_mg,
  larn_magnesio_mg, larn_vitamina_c_mg

Regole cliniche applicate (da protocollo Studio Taglialatela):
  - kcal lette da fonte (CREA/BDA/USDA), mai ricalcolate con 4/4/9
  - tolleranza +/-5% su kcal totali e % macro rispetto al target
  - flag warning (sotto 80% del riferimento) sui micronutrienti
"""

import csv
import sys
from collections import defaultdict

NUTRIENTI_PER_100G = [
    "kcal_100g", "proteine_g", "carboidrati_g", "grassi_g", "fibra_g",
    "calcio_mg", "ferro_mg", "vitamina_d_ug", "folati_ug",
    "vitamina_b12_ug", "zinco_mg", "magnesio_mg", "vitamina_c_mg",
]

MICRONUTRIENTI_LARN = {
    "calcio_mg": "larn_calcio_mg",
    "ferro_mg": "larn_ferro_mg",
    "vitamina_d_ug": "larn_vitamina_d_ug",
    "folati_ug": "larn_folati_ug",
    "vitamina_b12_ug": "larn_vitamina_b12_ug",
    "zinco_mg": "larn_zinco_mg",
    "magnesio_mg": "larn_magnesio_mg",
    "vitamina_c_mg": "larn_vitamina_c_mg",
}

TOLLERANZA_PCT = 5.0  # +/-5% su kcal totali e % macro, da protocollo studio


def carica_alimenti(path):
    db = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fid = row["food_id"]
            db[fid] = {k: float(row[k]) for k in NUTRIENTI_PER_100G}
            db[fid]["nome"] = row["nome"]
    return db


def carica_piano(path):
    righe = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            righe.append({
                "giorno": row["giorno"],
                "pasto": row["pasto"],
                "food_id": row["food_id"],
                "grammi": float(row["grammi"]),
            })
    return righe


def carica_target(path):
    t = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t[row["parametro"]] = float(row["valore"])
    return t


def calcola_riga(alimento, grammi):
    fattore = grammi / 100.0
    return {n: alimento[n] * fattore for n in NUTRIENTI_PER_100G}


def somma_nutrienti(lista_dict):
    tot = {n: 0.0 for n in NUTRIENTI_PER_100G}
    for d in lista_dict:
        for n in NUTRIENTI_PER_100G:
            tot[n] += d[n]
    return tot


def formatta_num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if "." in f"{v:.2f}" else f"{v:.2f}"


def report(alimenti_path, piano_path, target_path):
    db = carica_alimenti(alimenti_path)
    piano = carica_piano(piano_path)
    target = carica_target(target_path)

    per_pasto = defaultdict(list)
    for riga in piano:
        chiave = (riga["giorno"], riga["pasto"])
        alimento = db.get(riga["food_id"])
        if alimento is None:
            print(f"ERRORE: food_id sconosciuto: {riga['food_id']}")
            sys.exit(1)
        per_pasto[chiave].append(calcola_riga(alimento, riga["grammi"]))

    giorni = sorted(set(g for g, _ in per_pasto))
    for giorno in giorni:
        print(f"\n{'='*60}\nGIORNO {giorno}\n{'='*60}")
        pasti_del_giorno = [(g, p) for (g, p) in per_pasto if g == giorno]
        # ordine standard dei pasti
        ordine = {"colazione": 0, "pranzo": 1, "spuntino": 2, "cena": 3}
        pasti_del_giorno.sort(key=lambda gp: ordine.get(gp[1], 99))

        tot_giorno = []
        for chiave in pasti_del_giorno:
            righe = per_pasto[chiave]
            tot_pasto = somma_nutrienti(righe)
            tot_giorno.extend(righe)
            print(f"\n-- {chiave[1].upper()} --")
            print(f"  kcal: {formatta_num(tot_pasto['kcal_100g'])}  "
                  f"P: {formatta_num(tot_pasto['proteine_g'])}g  "
                  f"C: {formatta_num(tot_pasto['carboidrati_g'])}g  "
                  f"F: {formatta_num(tot_pasto['grassi_g'])}g  "
                  f"Fibra: {formatta_num(tot_pasto['fibra_g'])}g")

        tot = somma_nutrienti(tot_giorno)
        kcal = tot["kcal_100g"]
        prot_kcal = tot["proteine_g"] * 4
        carb_kcal = tot["carboidrati_g"] * 4
        gras_kcal = tot["grassi_g"] * 9
        prot_pct = prot_kcal / kcal * 100
        carb_pct = carb_kcal / kcal * 100
        gras_pct = gras_kcal / kcal * 100

        print(f"\n{'-'*60}\nTOTALE GIORNO {giorno}")
        print(f"  kcal totali: {formatta_num(kcal)}")
        print(f"  Proteine: {formatta_num(tot['proteine_g'])}g ({formatta_num(prot_pct)}%)")
        print(f"  Carboidrati: {formatta_num(tot['carboidrati_g'])}g ({formatta_num(carb_pct)}%)")
        print(f"  Grassi: {formatta_num(tot['grassi_g'])}g ({formatta_num(gras_pct)}%)")
        print(f"  Fibra: {formatta_num(tot['fibra_g'])}g")

        # confronto kcal vs target, tolleranza +/-5%
        if "kcal_target" in target:
            kt = target["kcal_target"]
            scarto_pct = (kcal - kt) / kt * 100
            stato = "OK" if abs(scarto_pct) <= TOLLERANZA_PCT else "FUORI TOLLERANZA (+/-5%)"
            print(f"\n  Target kcal: {formatta_num(kt)} | scostamento: {formatta_num(scarto_pct)}% -> {stato}")

        # confronto macro % vs target, tolleranza +/-5 punti percentuali
        for nome_pct, valore_calc, chiave_target in [
            ("Proteine", prot_pct, "proteine_pct_target"),
            ("Carboidrati", carb_pct, "carboidrati_pct_target"),
            ("Grassi", gras_pct, "grassi_pct_target"),
        ]:
            if chiave_target in target:
                tgt = target[chiave_target]
                scarto = valore_calc - tgt
                stato = "OK" if abs(scarto) <= TOLLERANZA_PCT else "FUORI TOLLERANZA (+/-5 punti %)"
                print(f"  {nome_pct} target: {formatta_num(tgt)}% | scostamento: {formatta_num(scarto)} punti -> {stato}")

        # fibra vs target
        if "fibra_g_target" in target:
            ft = target["fibra_g_target"]
            print(f"  Fibra target: {formatta_num(ft)}g | attuale: {formatta_num(tot['fibra_g'])}g")

        # micronutrienti vs LARN, flag sotto 80%
        print(f"\n  MICRONUTRIENTI vs LARN:")
        for nutriente, chiave_larn in MICRONUTRIENTI_LARN.items():
            if chiave_larn in target:
                larn = target[chiave_larn]
                valore = tot[nutriente]
                pct = valore / larn * 100 if larn else 0
                flag = " ⚠️ SOTTO 80% LARN" if pct < 80 else ""
                unita = nutriente.split("_")[-1]
                print(f"    {nutriente}: {formatta_num(valore)}{unita} "
                      f"({formatta_num(pct)}% del riferimento {formatta_num(larn)}{unita}){flag}")


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    report(
        os.path.join(base, "alimenti_test.csv"),
        os.path.join(base, "piano_test.csv"),
        os.path.join(base, "target_test.csv"),
    )
