#!/usr/bin/env python3
"""
Lettore della tabella LARN - Studio Nutrizionale Taglialatela

Restituisce i riferimenti LARN degli 8 micronutrienti tracciati dal motore,
scelti per sesso, eta' e condizione fisiologica.

Fonte: LARN V revisione, SINU 2024 - tabelle riassuntive pubblicate da SINU
(sinu.it/larn/, "Tabelle riassuntive"). Valori PRI o AI su base giornaliera,
trascritti in larn.csv il 19/09/2026.

Regola del nucleo: mai valori di default sui dati clinici. Se sesso, eta' o
condizione non sono noti il modulo SOLLEVA un errore, non riempie da solo.
"""

import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
TABELLA = os.path.join(BASE, "larn.csv")

COLONNE_LARN = [
    "larn_calcio_mg", "larn_ferro_mg", "larn_vitamina_d_ug", "larn_folati_ug",
    "larn_vitamina_b12_ug", "larn_zinco_mg", "larn_magnesio_mg",
    "larn_vitamina_c_mg",
]

CONDIZIONI = ("nessuna", "menopausa", "gravidanza", "allattamento")


def _righe():
    with open(TABELLA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _numero(testo):
    v = float(testo)
    return int(v) if v == int(v) else v


def riferimenti(sesso, eta_anni, condizione="nessuna"):
    """Riferimenti LARN per un paziente.

    sesso: 'M' o 'F'. eta_anni: intero. condizione: una di CONDIZIONI.
    Restituisce (valori, nota): valori e' il dizionario delle 8 colonne
    larn_* pronte per target.csv, nota e' il testo della riga usata.
    """
    if sesso is None or str(sesso).upper() not in ("M", "F"):
        raise ValueError("sesso deve essere 'M' o 'F': dato obbligatorio, "
                         "nessun default (nucleo, sezione 6)")
    if eta_anni is None:
        raise ValueError("eta_anni e' obbligatoria: nessun default")
    sesso = str(sesso).upper()
    eta = int(eta_anni)
    if condizione not in CONDIZIONI:
        raise ValueError(f"condizione deve essere una tra: {list(CONDIZIONI)}")
    if condizione != "nessuna" and sesso != "F":
        raise ValueError(f"condizione '{condizione}' incompatibile con sesso M")

    candidate = [r for r in _righe()
                 if r["sesso"] == sesso
                 and r["condizione"] == condizione
                 and int(r["eta_min"]) <= eta <= int(r["eta_max"])]
    if not candidate:
        raise ValueError(
            f"nessuna riga LARN per sesso={sesso}, eta={eta}, "
            f"condizione={condizione}. La tabella copre da 11 anni in su: "
            f"per l'eta' pediatrica servono i LARN dei bambini, non ancora "
            f"caricati.")
    if len(candidate) > 1:
        raise ValueError(f"{len(candidate)} righe LARN sovrapposte per "
                         f"sesso={sesso}, eta={eta}, condizione={condizione}: "
                         f"larn.csv va corretto")
    riga = candidate[0]
    valori = {c: _numero(riga[c]) for c in COLONNE_LARN}
    return valori, riga.get("nota", "")


if __name__ == "__main__":
    casi = [("M", 36, "nessuna"), ("F", 34, "nessuna"), ("F", 58, "menopausa"),
            ("F", 31, "gravidanza"), ("M", 78, "nessuna")]
    for sesso, eta, cond in casi:
        v, nota = riferimenti(sesso, eta, cond)
        print(f"{sesso} {eta} anni ({cond}): Ca {v['larn_calcio_mg']} mg, "
              f"Fe {v['larn_ferro_mg']} mg, B12 {v['larn_vitamina_b12_ug']} ug, "
              f"vit.D {v['larn_vitamina_d_ug']} ug"
              + (f" - {nota}" if nota else ""))
