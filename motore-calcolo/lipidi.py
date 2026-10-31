#!/usr/bin/env python3
"""
lipidi.py - Studio Nutrizionale Taglialatela

File affiancato lipidi.csv (decisione del nutrizionista del 31/10/2026): acidi
grassi saturi, monoinsaturi, polinsaturi, EPA, DHA e colesterolo per 100 g di
parte edibile, senza toccare lo schema congelato di alimenti.csv.

PERCHE'
Il riferimento sui saturi per l'ipercolesterolemia (R020, < 7% dell'energia) e
quello sul colesterolo (R021, < 300 mg/die) erano «non verificabili»: il dato non
c'era. La cache CREA non ha acidi grassi; la cache BDA-IEO si'. Ogni riga dice da
quale scheda viene il valore e con quale metodo (stessa scheda, proporzione sui
grassi di alimenti.csv, zero per decisione, USDA).

REGOLE
- lipidi.csv: food_id, saturi_g, monoinsaturi_g, polinsaturi_g, epa_g, dha_g,
  colesterolo_mg, fonte, codice_fonte, origine_dato, metodo, data_verifica.
  origine_dato descrive i saturi (analitico, calcolato da BDA su un alimento
  simile o sullo stesso alimento, zero per decisione...).
- Cella vuota = dato mancante, e solo cosi': deve avere la sua riga in gap.csv
  (nutriente = nome della colonna). Uno zero e' uno zero vero (biologico, tracce,
  decisione). Un food_id senza riga in lipidi.csv deve avere in gap.csv tutte e
  sei le colonne. Lo controlla il collaudo (controllo 12).
- Nel calcolo un dato mancante vale 0 e il totale esce SOTTOSTIMATO (gap.csv), come
  per i micronutrienti: mai un valore inventato.
- Il dato si mostra in tutti i piani; gli avvisi solo nei profili che lo chiedono
  (regola del 31/10/2026, riferimenti.py).

USO
  python3 lipidi.py --autotest
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
FILE_LIPIDI = os.path.join(QUI, "lipidi.csv")

CAMPI = ["saturi_g", "monoinsaturi_g", "polinsaturi_g", "epa_g", "dha_g", "colesterolo_mg"]
COLONNE = (["food_id"] + CAMPI
           + ["fonte", "codice_fonte", "origine_dato", "metodo", "data_verifica"])


class ErroreLipidi(ValueError):
    pass


def carica(path=None):
    """{food_id: {campo: float o None}}. None = cella vuota = dato mancante."""
    path = path or FILE_LIPIDI
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        lettore = csv.DictReader(f)
        if lettore.fieldnames != COLONNE:
            raise ErroreLipidi(f"{os.path.basename(path)}: colonne {lettore.fieldnames}, "
                               f"attese {COLONNE}")
        for n, r in enumerate(lettore, 2):
            if None in r or any(v is None for v in r.values()):
                raise ErroreLipidi(f"riga {n}: numero di campi diverso dalle colonne")
            fid = r["food_id"].strip()
            if fid in out:
                raise ErroreLipidi(f"riga {n}: food_id {fid} duplicato")
            valori = {}
            for c in CAMPI:
                v = r[c].strip()
                if v == "":
                    valori[c] = None
                    continue
                try:
                    valori[c] = float(v)
                except ValueError:
                    raise ErroreLipidi(f"riga {n} ({fid}): {c} non numerico ({v!r})")
                if valori[c] < 0:
                    raise ErroreLipidi(f"riga {n} ({fid}): {c} negativo")
            for c in ("fonte", "metodo", "data_verifica"):
                if not r[c].strip():
                    raise ErroreLipidi(f"riga {n} ({fid}): {c} vuoto")
            out[fid] = valori
    return out


def arricchisci(db, lipidi):
    """Aggiunge i campi lipidici a ogni voce del database (sul posto). Dato
    mancante o voce assente = 0.0: la sottostima la dichiara gap.csv."""
    for fid, voce in db.items():
        riga = lipidi.get(fid, {})
        for c in CAMPI:
            v = riga.get(c)
            voce[c] = v if v is not None else 0.0
    return db


def carica_se_presente(path=None):
    """Come carica(), ma {} se il file manca (il collaudo ne segnala l'assenza)."""
    path = path or FILE_LIPIDI
    if not os.path.exists(path):
        return {}
    return carica(path)


def problemi(lipidi, food_ids, gap, grassi=None):
    """Difetti di copertura (vuoto = coerente). gap: {food_id: {nutriente: motivo}}.
    grassi: {food_id: grassi_g} per il controllo di plausibilita'."""
    out = []
    for fid in sorted(set(lipidi) - set(food_ids)):
        out.append(f"{fid}: in lipidi.csv ma non in alimenti.csv")
    for fid in food_ids:
        riga = lipidi.get(fid)
        g = gap.get(fid, {})
        for c in CAMPI:
            v = None if riga is None else riga.get(c)
            if v is None and c not in g:
                out.append(f"{fid}: {c} senza valore e senza riga in gap.csv")
            elif v is not None and c in g:
                out.append(f"{fid}: {c} ha un valore ma anche un gap dichiarato")
        if riga and grassi and fid in grassi:
            fa = sum(riga[c] or 0.0 for c in ("saturi_g", "monoinsaturi_g", "polinsaturi_g"))
            if fa > grassi[fid] * 1.05 + 0.05:
                out.append(f"{fid}: saturi+mono+poli {fa:g} g oltre i grassi totali "
                           f"{grassi[fid]:g} g")
    return out


def autotest():
    import tempfile
    ko, n = [], 0

    def atteso(etichetta, ottenuto, voluto):
        nonlocal n
        n += 1
        if ottenuto != voluto:
            ko.append(f"lipidi autotest «{etichetta}»: {ottenuto!r} invece di {voluto!r}")

    testa = ",".join(COLONNE) + "\n"
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "l.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(testa + "A,1,2,3,0,0,10,BDA-IEO,1_2,analitico,scheda,2026-10-31\n"
                            "B,,0.5,0.5,,,0,BDA-IEO,2_2,analitico,scheda,2026-10-31\n")
        lip = carica(p)
        atteso("vuoto = None", lip["B"]["saturi_g"], None)
        atteso("zero = 0.0", lip["B"]["colesterolo_mg"], 0.0)
        db = {"A": {}, "B": {}, "C": {}}
        arricchisci(db, lip)
        atteso("mancante vale 0 nel calcolo", db["B"]["saturi_g"], 0.0)
        atteso("voce assente vale 0", db["C"]["colesterolo_mg"], 0.0)
        gap = {"B": {"saturi_g": "x", "epa_g": "x", "dha_g": "x"},
               "C": {c: "x" for c in CAMPI}}
        atteso("copertura completa", problemi(lip, ["A", "B", "C"], gap), [])
        atteso("vuoto senza gap", len(problemi(lip, ["A", "B", "C"],
                                               {"B": {"saturi_g": "x"}, "C": gap["C"]})), 2)
        atteso("valore con gap", len(problemi(lip, ["A", "B", "C"],
                                              dict(gap, A={"saturi_g": "x"}))), 1)
        atteso("voce senza riga e senza gap", len(problemi(lip, ["A", "B", "C"],
                                                           {"B": gap["B"]})), 6)
        atteso("riga orfana", len(problemi(lip, ["B", "C"], gap)), 1)
        atteso("acidi grassi oltre i grassi", len(problemi(lip, ["A", "B", "C"], gap,
                                                           {"A": 4.0, "B": 1.0})), 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(testa + "A,x,2,3,0,0,10,BDA-IEO,1_2,analitico,scheda,2026-10-31\n")
        try:
            carica(p)
            atteso("valore non numerico blocca", False, True)
        except ErroreLipidi:
            atteso("valore non numerico blocca", True, True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(testa + "A,1,2,3,0,0,10,,1_2,analitico,scheda,2026-10-31\n")
        try:
            carica(p)
            atteso("fonte vuota blocca", False, True)
        except ErroreLipidi:
            atteso("fonte vuota blocca", True, True)
    return n, ko


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        n, ko = autotest()
        for k in ko:
            print("XX", k)
        print(f"{n - len(ko)}/{n} prove superate")
        sys.exit(1 if ko else 0)
    print(__doc__)
