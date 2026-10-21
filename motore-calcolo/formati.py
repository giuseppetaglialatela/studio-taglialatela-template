#!/usr/bin/env python3
"""
Modulo formati confezione - Studio Nutrizionale Taglialatela

Traduce in controllo automatico la regola "mai sprechi" (nucleo M0, sezione 5):
le quantita' dei prodotti a confezione o a unita devono essere una confezione
intera o un multiplo esatto del formato, entro la tolleranza dichiarata.

DATI
  formati_confezione.csv  food_id, nome_riferimento, unita_g (lista separata
                          da '|'), tolleranza_g, fonte, stato.
                          Un alimento PRESENTE nel file e' vincolato.
                          Un alimento ASSENTE e' a porzione libera (al banco,
                          non deperibile o consumabile in famiglia).
  scambi_frutta.csv       food_id, nome_riferimento, grammi_porzione, stato.
                          Porzioni di frutta equivalenti in energia
                          (riferimento: banana 100 g), usate per la tabella di
                          scambio nel PDF e nel documento di spiegazione.

Il controllo SEGNALA, non blocca (decisione del nutrizionista, 29/09/2026).
Il documento Word su Drive e' archivio: valgono questi CSV.
"""
import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAX_MULTIPLO = 6


def carica_formati(path=None):
    path = path or os.path.join(BASE, "formati_confezione.csv")
    formati = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            formati[r["food_id"]] = {
                "nome": r["nome_riferimento"],
                "unita": [float(u) for u in r["unita_g"].split("|")],
                "tolleranza": float(r["tolleranza_g"]),
                "stato": r["stato"],
            }
    return formati


def carica_scambi_frutta(path=None):
    path = path or os.path.join(BASE, "scambi_frutta.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return [{"food_id": r["food_id"], "nome": r["nome_riferimento"],
                 "grammi": float(r["grammi_porzione"]), "stato": r["stato"]}
                for r in csv.DictReader(f)]


def quantita_valida(grammi, fmt):
    """True se grammi = k * unita (k = 1..MAX_MULTIPLO) entro tolleranza."""
    for u in fmt["unita"]:
        for k in range(1, MAX_MULTIPLO + 1):
            if abs(grammi - k * u) <= fmt["tolleranza"]:
                return True
    return False


def formati_suggeriti(fmt):
    """Quantita' ammesse, per il messaggio di segnalazione."""
    valori = sorted({int(u * k) if (u * k) == int(u * k) else u * k
                     for u in fmt["unita"] for k in range(1, 4)})
    return ", ".join(f"{v} g" for v in valori)


def controlla_piano(piano, formati):
    """piano: righe con giorno, pasto, food_id, grammi. Restituisce le
    violazioni uniche (food_id, grammi) con i pasti in cui compaiono."""
    trovate = {}
    for r in piano:
        fid = r["food_id"]
        if fid not in formati:
            continue
        g = float(r["grammi"])
        if not quantita_valida(g, formati[fid]):
            trovate.setdefault((fid, g), []).append(f"g{r['giorno']} {r['pasto']}")
    return [{"food_id": fid, "grammi": g, "nome": formati[fid]["nome"],
             "dove": sorted(set(dove)),
             "ammesse": formati_suggeriti(formati[fid])}
            for (fid, g), dove in sorted(trovate.items())]


def valida_file(db_ids):
    """Per il collaudo: file presenti, parsabili, food_id esistenti."""
    problemi = []
    try:
        formati = carica_formati()
    except Exception as e:
        return [f"formati_confezione.csv non leggibile: {e}"]
    for fid, f in formati.items():
        if fid not in db_ids:
            problemi.append(f"formati_confezione.csv: food_id {fid} assente da alimenti.csv")
        if not f["unita"] or f["tolleranza"] < 0:
            problemi.append(f"formati_confezione.csv: riga {fid} con unita/tolleranza non valide")
    try:
        scambi = carica_scambi_frutta()
    except Exception as e:
        return problemi + [f"scambi_frutta.csv non leggibile: {e}"]
    for s in scambi:
        if s["food_id"] not in db_ids:
            problemi.append(f"scambi_frutta.csv: food_id {s['food_id']} assente da alimenti.csv")
        if s["grammi"] <= 0:
            problemi.append(f"scambi_frutta.csv: grammi non validi per {s['food_id']}")
    return problemi
