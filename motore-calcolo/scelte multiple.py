#!/usr/bin/env python3
"""
Modulo pasti a scelta multipla - Studio Nutrizionale Taglialatela

Gestisce i pasti in cui il paziente sceglie tra alternative
(es. "a pranzo: pollo OPPURE pesce OPPURE legumi").

SCHEMA ESTESO di piano.csv (retrocompatibile: le due colonne sono opzionali,
i file esistenti senza di esse continuano a funzionare come prima):

  giorno, pasto, food_id, grammi, gruppo_scelta, opzione

  - gruppo_scelta vuoto  -> alimento FISSO, sempre presente nel pasto
  - gruppo_scelta valorizzato -> il pasto contiene alternative; tutte le righe
    con lo stesso gruppo_scelta e la stessa opzione formano UNA alternativa,
    e il paziente ne sceglie esattamente una per gruppo.

METODO DI CALCOLO - lettura obbligatoria:
Il minimo e il massimo sono calcolati per OGNI NUTRIENTE SEPARATAMENTE,
scegliendo di volta in volta l'alternativa che minimizza o massimizza quel
singolo nutriente. Il risultato e' quindi un INTERVALLO DI GARANZIA
(limite inferiore e superiore certi), NON un menu' realmente componibile:
nessuna giornata reale avra' contemporaneamente tutti i minimi.

Questa scelta e' voluta ed e' quella clinicamente prudente: se anche nello
scenario piu' favorevole un micronutriente resta sotto soglia, la carenza e'
strutturale e non dipende dalla scelta del paziente. Se invece la soglia e'
superata solo nello scenario massimo, la copertura dipende da quale
alternativa il paziente sceglie davvero - e va detto a lui, non dato per
acquisito.
"""

from collections import defaultdict

NUTRIENTI = ["kcal_100g", "proteine_g", "carboidrati_g", "grassi_g", "fibra_g",
             "calcio_mg", "ferro_mg", "vitamina_d_ug", "folati_ug",
             "vitamina_b12_ug", "zinco_mg", "magnesio_mg", "vitamina_c_mg"]


def carica_piano_esteso(path):
    """Legge piano.csv con le colonne opzionali gruppo_scelta e opzione."""
    import csv
    righe = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            righe.append({
                "giorno": row["giorno"].strip(),
                "pasto": row["pasto"].strip(),
                "food_id": row["food_id"].strip(),
                "grammi": float(row["grammi"]),
                "gruppo_scelta": (row.get("gruppo_scelta") or "").strip(),
                "opzione": (row.get("opzione") or "").strip(),
            })
    return righe


def _contributo(db, food_id, grammi):
    al = db[food_id]
    f = grammi / 100.0
    return {n: al[n] * f for n in NUTRIENTI}


def calcola_intervallo_giorno(righe_giorno, db):
    """
    Restituisce (minimi, massimi, dettaglio_gruppi).
    minimi/massimi: dict nutriente -> valore.
    """
    fissi = [r for r in righe_giorno if not r["gruppo_scelta"]]
    variabili = [r for r in righe_giorno if r["gruppo_scelta"]]

    base = {n: 0.0 for n in NUTRIENTI}
    for r in fissi:
        c = _contributo(db, r["food_id"], r["grammi"])
        for n in NUTRIENTI:
            base[n] += c[n]

    # raggruppa: (pasto, gruppo_scelta) -> opzione -> lista contributi
    gruppi = defaultdict(lambda: defaultdict(list))
    for r in variabili:
        gruppi[(r["pasto"], r["gruppo_scelta"])][r["opzione"]].append(r)

    minimi = dict(base)
    massimi = dict(base)
    dettaglio = []

    for (pasto, gruppo), opzioni in gruppi.items():
        # totale di ciascuna opzione
        tot_opzioni = {}
        for nome_opz, righe in opzioni.items():
            tot = {n: 0.0 for n in NUTRIENTI}
            for r in righe:
                c = _contributo(db, r["food_id"], r["grammi"])
                for n in NUTRIENTI:
                    tot[n] += c[n]
            tot_opzioni[nome_opz] = tot

        dettaglio.append({
            "pasto": pasto, "gruppo": gruppo,
            "n_opzioni": len(tot_opzioni),
            "opzioni": list(tot_opzioni.keys()),
        })

        # per ogni nutriente, scegli l'opzione che minimizza / massimizza
        for n in NUTRIENTI:
            valori = [t[n] for t in tot_opzioni.values()]
            minimi[n] += min(valori)
            massimi[n] += max(valori)

    return minimi, massimi, dettaglio


def stampa_report_scelte(righe_piano, db, target, micro_larn):
    print(f"\n{'='*60}\nPASTI A SCELTA MULTIPLA - INTERVALLI MIN/MAX\n{'='*60}")

    per_giorno = defaultdict(list)
    for r in righe_piano:
        per_giorno[r["giorno"]].append(r)

    for giorno in sorted(per_giorno):
        righe = per_giorno[giorno]
        if not any(r["gruppo_scelta"] for r in righe):
            print(f"\n  Giorno {giorno}: nessuna scelta multipla "
                  f"(valore unico, vedi report principale).")
            continue

        minimi, massimi, dettaglio = calcola_intervallo_giorno(righe, db)

        print(f"\n  --- GIORNO {giorno} ---")
        for d in dettaglio:
            print(f"    Gruppo '{d['gruppo']}' ({d['pasto']}): "
                  f"{d['n_opzioni']} alternative -> {', '.join(d['opzioni'])}")

        print(f"\n    kcal:        {minimi['kcal_100g']:.0f} - {massimi['kcal_100g']:.0f}")
        print(f"    Proteine:    {minimi['proteine_g']:.1f} - {massimi['proteine_g']:.1f} g")
        print(f"    Carboidrati: {minimi['carboidrati_g']:.1f} - {massimi['carboidrati_g']:.1f} g")
        print(f"    Grassi:      {minimi['grassi_g']:.1f} - {massimi['grassi_g']:.1f} g")
        print(f"    Fibra:       {minimi['fibra_g']:.1f} - {massimi['fibra_g']:.1f} g")

        if "kcal_target" in target:
            kt = target["kcal_target"]
            s_min = (minimi["kcal_100g"] - kt) / kt * 100
            s_max = (massimi["kcal_100g"] - kt) / kt * 100
            print(f"\n    Scostamento kcal vs target {kt:.0f}: "
                  f"{s_min:+.1f}% / {s_max:+.1f}%")
            if abs(s_min) > 5 or abs(s_max) > 5:
                print("      ⚠️ almeno uno degli estremi e' fuori tolleranza +/-5%")

        print(f"\n    MICRONUTRIENTI (min - max vs LARN):")
        for nutriente, chiave in micro_larn.items():
            if chiave not in target:
                continue
            larn = target[chiave]
            vmin, vmax = minimi[nutriente], massimi[nutriente]
            pmin = vmin / larn * 100 if larn else 0
            pmax = vmax / larn * 100 if larn else 0
            if pmax < 80:
                flag = " ⚠️ CARENZA STRUTTURALE (sotto 80% anche nel best case)"
            elif pmin < 80:
                flag = " ⚠️ dipende dalla scelta del paziente (min sotto 80%)"
            else:
                flag = ""
            print(f"      {nutriente}: {vmin:.1f} - {vmax:.1f} "
                  f"({pmin:.0f}% - {pmax:.0f}% del LARN){flag}")

        print("\n    NOTA METODOLOGICA: min e max sono calcolati per ogni")
        print("    nutriente separatamente. Sono limiti garantiti, NON una")
        print("    giornata realmente componibile.")
