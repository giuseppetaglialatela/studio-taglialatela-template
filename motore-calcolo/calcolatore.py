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
  (pasto ammessi: colazione | spuntino | pranzo | spuntino2 | cena)
  Struttura a 5 posti (decisione del 30/09/2026): un pasto senza righe
  semplicemente non esiste in quel piano. Elenco e ordine vivono SOLO in
  PASTI_AMMESSI e ordine_pasti() qui sotto: pipeline.py e
  genera_zona_piano.py li importano, non li riscrivono.

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
import os
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

# Pasti ammessi in piano.csv: al massimo 5 (decisione clinica del 30/09/2026).
PASTI_AMMESSI = ("colazione", "spuntino", "pranzo", "spuntino2", "cena")

# Ordine dei pasti, deciso a livello di PIANO (non di giorno):
# - piano a 4 pasti: lo spuntino e' quello del pomeriggio, dopo il pranzo
#   (ordine storico, invariato: i piani gia' consegnati restano identici);
# - piano con spuntino2 in almeno un giorno: lo spuntino passa a meta'
#   mattina e il secondo spuntino sta tra pranzo e cena.
# Se ci sono gli orari, il PDF segue gli orari (genera_zona_piano.py).
_ORDINE_4 = {"colazione": 0, "pranzo": 1, "spuntino": 2, "cena": 3}
_ORDINE_5 = {"colazione": 0, "spuntino": 1, "pranzo": 2, "spuntino2": 3, "cena": 4}


def ordine_pasti(pasti_presenti):
    """Dizionario pasto -> posizione, per l'insieme dei pasti del PIANO."""
    return dict(_ORDINE_5 if "spuntino2" in set(pasti_presenti) else _ORDINE_4)


def pasti_non_ammessi(piano):
    """Coppie (giorno, pasto) con un valore di pasto fuori da PASTI_AMMESSI.
    Un refuso ('spuntino 2', 'Spuntino') verrebbe sommato nei totali ma
    scartato dal PDF: va fermato prima."""
    return sorted({(r["giorno"], r["pasto"]) for r in piano
                   if r["pasto"] not in PASTI_AMMESSI})


def entro_tolleranza(scarto, tolleranza=TOLLERANZA_PCT):
    """Vero se lo scostamento (kcal % o punti percentuali macro) rientra
    nella tolleranza. Confine INCLUSO: uno scarto esattamente uguale alla
    tolleranza e' OK, non fuori. Estratta da report() perche' la suite di
    regressione possa verificare il verdetto stesso, non solo i grammi da
    cui deriva."""
    return abs(scarto) <= tolleranza


def carica_alimenti(path):
    db = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fid = row["food_id"]
            db[fid] = {k: float(row[k]) for k in NUTRIENTI_PER_100G}
            db[fid]["nome"] = row["nome"]
    return db


COLONNE_ALIMENTI = ["food_id", "nome", "categoria", "fonte", "codice_fonte",
                    "data_verifica"] + NUTRIENTI_PER_100G


def carica_eccezioni_etichetta(path, db_ufficiale):
    """Voci da etichetta, SOLO su richiesta esplicita del nutrizionista (21/10/2026).

    I valori di un'etichetta non entrano mai nel database ufficiale: si passano
    per il singolo piano in un file a parte, con le colonne di alimenti.csv.
    Restituisce {food_id: valori} come carica_alimenti.
    Si ferma (ValueError) se: mancano colonne di alimenti.csv; una riga ha campi
    in piu' o in meno; food_id, nome o fonte sono vuoti; un valore non e' un
    numero finito e non negativo; un food_id e' duplicato o e' gia' una voce
    del database ufficiale (un'eccezione non sovrascrive un dato verificato).
    db_ufficiale deve essere il database del motore, non una copia.
    """
    import math
    with open(path, newline="", encoding="utf-8-sig") as f:
        lettore = csv.DictReader(f)
        mancanti = [c for c in COLONNE_ALIMENTI if c not in (lettore.fieldnames or [])]
        if mancanti:
            raise ValueError(f"{path}: colonne mancanti {', '.join(mancanti)} "
                             f"(servono tutte le colonne di alimenti.csv)")
        righe = list(lettore)
    if not righe:
        raise ValueError(f"{path}: nessuna voce")
    voci = {}
    for n, row in enumerate(righe, start=2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"{path}, riga {n}: numero di campi diverso dall'intestazione")
        fid = row["food_id"].strip()
        for campo in ("food_id", "nome", "fonte"):
            if not row[campo].strip():
                raise ValueError(f"{path}, riga {n}: campo '{campo}' vuoto")
        if fid in db_ufficiale:
            raise ValueError(f"{path}: {fid} esiste gia' nel database ufficiale: "
                             f"un'eccezione non sovrascrive un dato verificato")
        if fid in voci:
            raise ValueError(f"{path}: food_id duplicato {fid}")
        valori = {}
        for k in NUTRIENTI_PER_100G:
            try:
                v = float(row[k])
            except ValueError:
                raise ValueError(f"{path}, riga {n}: {k} = '{row[k]}' non e' un numero")
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"{path}, riga {n}: {k} = '{row[k]}' non valido "
                                 f"(serve un numero finito e non negativo)")
            valori[k] = v
        valori["nome"] = row["nome"].strip()
        voci[fid] = valori
    return voci


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


def carica_gap(path):
    """FASE 2 - file affiancato gap.csv: distingue lo zero biologico dal dato mancante.

    Lo schema di alimenti.csv e' congelato e non ha modo di rappresentare
    "dato non disponibile": un nutriente non pubblicato dalla fonte finisce a 0
    e viene sommato come un'assenza reale. Il totale giornaliero risulta piu'
    basso del vero e il confronto LARN produce un allarme di carenza che non
    esiste - errore gia' occorso (vitamina D delle sardine, 5.8% LARN
    apparente su una giornata che ne conteneva sette volte tanto).

    gap.csv (food_id, nome, nutriente, motivo) elenca le celle il cui zero e'
    un dato mancante. Restituisce {food_id: {nutriente: motivo}}.
    Se il file non esiste restituisce {} e il motore lavora come prima, ma
    senza alcuna garanzia sui gap: e' una perdita di informazione, non un
    funzionamento normale.
    """
    gap = {}
    if not os.path.isfile(path):
        return gap
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gap.setdefault(row["food_id"], {})[row["nutriente"]] = row["motivo"]
    return gap


def nutrienti_sottostimati(piano, gap):
    """Nutrienti il cui totale e' sottostimato, con le voci che li causano.

    Restituisce {nutriente: [(food_id, motivo), ...]} considerando solo gli
    alimenti effettivamente presenti nel piano: un gap su un alimento non
    usato non sporca il report.
    """
    sottostime = {}
    for riga in piano:
        for nutriente, motivo in gap.get(riga["food_id"], {}).items():
            sottostime.setdefault(nutriente, [])
            if riga["food_id"] not in [f for f, _ in sottostime[nutriente]]:
                sottostime[nutriente].append((riga["food_id"], motivo))
    return sottostime


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


def report(alimenti_path, piano_path, target_path, gap_path=None):
    db = carica_alimenti(alimenti_path)
    piano = carica_piano(piano_path)
    target = carica_target(target_path)
    if gap_path is None:
        gap_path = os.path.join(os.path.dirname(os.path.abspath(alimenti_path)), "gap.csv")
    gap = carica_gap(gap_path)
    sottostime = nutrienti_sottostimati(piano, gap)

    for giorno, pasto in pasti_non_ammessi(piano):
        print(f"ERRORE: giorno {giorno}, pasto non ammesso: '{pasto}' "
              f"(ammessi: {' | '.join(PASTI_AMMESSI)})")
    if pasti_non_ammessi(piano):
        sys.exit(1)
    ordine = ordine_pasti(r["pasto"] for r in piano)

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
        # ordine dei pasti: deciso sul piano intero (ordine_pasti)
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
            stato = "OK" if entro_tolleranza(scarto_pct) else "FUORI TOLLERANZA (+/-5%)"
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
                stato = "OK" if entro_tolleranza(scarto) else "FUORI TOLLERANZA (+/-5 punti %)"
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
                if nutriente in sottostime:
                    flag += " ⛔ TOTALE SOTTOSTIMATO (dati mancanti)"
                unita = nutriente.split("_")[-1]
                print(f"    {nutriente}: {formatta_num(valore)}{unita} "
                      f"({formatta_num(pct)}% del riferimento {formatta_num(larn)}{unita}){flag}")

        if sottostime:
            print("\n  ⛔ GAP DICHIARATI - i totali seguenti sono SOTTOSTIMATI.")
            print("     Un valore sotto soglia qui NON e' una carenza accertata:")
            print("     puo' derivare da un dato che la fonte non pubblica.")
            for nutriente in sorted(sottostime):
                print(f"     {nutriente}:")
                for fid, motivo in sottostime[nutriente]:
                    nome = db[fid]["nome"] if fid in db else fid
                    print(f"        - {nome}: {motivo}")


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    report(
        os.path.join(base, "alimenti_test.csv"),
        os.path.join(base, "piano_test.csv"),
        os.path.join(base, "target_test.csv"),
    )
