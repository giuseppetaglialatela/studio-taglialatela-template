#!/usr/bin/env python3
"""
Tabelle di conversione di ogni dieta (richiesta del nutrizionista, 03/11/2026).

Nessun valore scritto a mano: le grammature si ricalcolano da alimenti.csv.

DATI
  scambi_carboidrati.csv  food_id, nome_riferimento, grammi_porzione, stato.
                          grammi_porzione = grammi equivalenti a 80 g di pasta cruda,
                          a parita' di carboidrati, arrotondati a 5 g.
  scambi_pesce.csv        stesso schema: grammi equivalenti a 100 g di merluzzo, a
                          parita' di proteine, arrotondati a 5 g.
  scambi_verdure.csv      food_id, nome_riferimento, uso (crude|cotte|entrambe), stato.
                          A parita' di peso; patate e legumi esclusi.
  Stato: 'confermato' = compare come alternativa; 'da_confermare' = compare solo come
  riga, se e' nel piano, finche' il nutrizionista non lo conferma.

La colonna grammi_porzione e' controllata dal collaudo (controllo 13): se alimenti.csv
cambia, il collaudo si ferma finche' non si esegue --rigenera.

USO
  python3 tabelle_conversione.py --controlla
  python3 tabelle_conversione.py --rigenera
"""
import csv
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PASSO_G = 5
RIF_CARBOIDRATI = ("000800", 80.0)     # pasta cruda
RIF_PESCE = ("1313", 100.0)            # merluzzo
SOGLIA_CARBOIDRATI_VERDURA = 5.0       # g/100 g: oltre, la verdura si segnala
SOGLIA_FIBRA_VERDURA = 5.0             # g/100 g: oltre, la verdura si segnala
RUOLI_AMMESSI = {"carboidrati": {"cereale", "patate"}, "pesce": {"pesce", "molluschi_crostacei"},
                 "verdure": {"verdura"}}
USI_VERDURE = {"crude", "cotte", "entrambe"}
STATI = {"confermato", "da_confermare"}
PASTI_PRINCIPALI = ("pranzo", "cena")


def arrotonda(g):
    """Al multiplo di 5 g piu' vicino; il mezzo va verso l'alto."""
    return int(g / PASSO_G + 0.5) * PASSO_G


def _righe(nome, base=None):
    with open(os.path.join(base or BASE, nome), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def carica_db(base=None):
    return {r["food_id"]: r for r in _righe("alimenti.csv", base)}


def carica_scambi(nome, base=None):
    return _righe(nome, base)


def equivalente(grammi, da, a, campo, db):
    """Grammi di 'a' con lo stesso contenuto di 'campo' di 'grammi' di 'da'."""
    return arrotonda(grammi * float(db[da][campo]) / float(db[a][campo]))


def kcal(fid, grammi, db):
    return grammi * float(db[fid]["kcal_100g"]) / 100


def _tabella(piano, db, scambi, campo):
    """Righe = voci del piano (pranzo e cena) presenti nell'elenco; colonne = voci
    confermate. Ogni cella: grammi equivalenti e scarto in kcal."""
    elenco = {s["food_id"]: s["nome_riferimento"] for s in scambi}
    colonne = [s for s in scambi if s["stato"] == "confermato"]
    viste = sorted({(r["food_id"], float(r["grammi"])) for r in piano
                    if r["pasto"] in PASTI_PRINCIPALI and r["food_id"] in elenco},
                   key=lambda x: (list(elenco).index(x[0]), -x[1]))
    righe = []
    for fid, g in viste:
        celle = []
        for c in colonne:
            alt = c["food_id"]
            if alt == fid:
                celle.append(None)
                continue
            ga = equivalente(g, fid, alt, campo, db)
            celle.append({"grammi": ga, "scarto_kcal": round(kcal(alt, ga, db) - kcal(fid, g, db))})
        righe.append({"food_id": fid, "nome": elenco[fid], "grammi": g, "celle": celle})
    return {"colonne": [c["nome_riferimento"] for c in colonne], "righe": righe}


def tabella_carboidrati(piano, db, base=None):
    return _tabella(piano, db, carica_scambi("scambi_carboidrati.csv", base), "carboidrati_g")


def tabella_pesce(piano, db, base=None):
    return _tabella(piano, db, carica_scambi("scambi_pesce.csv", base), "proteine_g")


def tabella_verdure(piano, db, base=None):
    """Gruppi crude e cotte, voci che si discostano, verdure del piano fuori elenco."""
    scambi = carica_scambi("scambi_verdure.csv", base)
    conf = [s for s in scambi if s["stato"] == "confermato"]
    gruppi = {u: [s["nome_riferimento"] for s in conf if s["uso"] in (u, "entrambe")]
              for u in ("crude", "cotte")}
    segnalate = []
    for s in conf:
        d = db[s["food_id"]]
        if float(d["carboidrati_g"]) >= SOGLIA_CARBOIDRATI_VERDURA:
            segnalate.append(f"{s['nome_riferimento']}: più carboidrati ({float(d['carboidrati_g']):g} g/100 g)")
        if float(d["fibra_g"]) >= SOGLIA_FIBRA_VERDURA:
            segnalate.append(f"{s['nome_riferimento']}: più fibre ({float(d['fibra_g']):g} g/100 g)")
    ruoli = {r["food_id"]: r["ruolo"] for r in _righe("ruoli_alimenti.csv", base)}
    elenco = {s["food_id"] for s in scambi}
    fuori = sorted({db[r["food_id"]]["nome"] for r in piano
                    if ruoli.get(r["food_id"]) == "verdura" and r["pasto"] in PASTI_PRINCIPALI
                    and r["food_id"] not in elenco})
    return {"gruppi": gruppi, "segnalate": segnalate, "fuori_elenco": fuori}


def attese(nome, base=None, db=None):
    """grammi_porzione ricalcolati da alimenti.csv."""
    db = db or carica_db(base)
    rif, g, campo = ((*RIF_CARBOIDRATI, "carboidrati_g") if nome == "scambi_carboidrati.csv"
                     else (*RIF_PESCE, "proteine_g"))
    return {s["food_id"]: equivalente(g, rif, s["food_id"], campo, db)
            for s in carica_scambi(nome, base)}


def controlla(base=None):
    """Per il collaudo: elenco dei problemi, vuoto se tutto e' coerente."""
    problemi = []
    db = carica_db(base)
    ruoli = {r["food_id"]: r["ruolo"] for r in _righe("ruoli_alimenti.csv", base)}
    for nome, tipo in (("scambi_carboidrati.csv", "carboidrati"), ("scambi_pesce.csv", "pesce"),
                       ("scambi_verdure.csv", "verdure")):
        righe = carica_scambi(nome, base)
        visti = set()
        for s in righe:
            fid = s["food_id"]
            if fid in visti:
                problemi.append(f"{nome}: {fid} ripetuto")
            visti.add(fid)
            if fid not in db:
                problemi.append(f"{nome}: food_id {fid} assente da alimenti.csv")
                continue
            if ruoli.get(fid) not in RUOLI_AMMESSI[tipo]:
                problemi.append(f"{nome}: {fid} ha ruolo {ruoli.get(fid)}, non ammesso qui")
            if s["stato"] not in STATI:
                problemi.append(f"{nome}: {fid} stato '{s['stato']}' non valido")
            if tipo == "verdure" and s["uso"] not in USI_VERDURE:
                problemi.append(f"{nome}: {fid} uso '{s['uso']}' non valido")
        if tipo != "verdure" and not any(p.endswith("assente da alimenti.csv") for p in problemi):
            att = attese(nome, base, db)
            for s in righe:
                if float(s["grammi_porzione"]) != att[s["food_id"]]:
                    problemi.append(f"{nome}: {s['nome_riferimento']} {s['grammi_porzione']} g, "
                                    f"ricalcolato {att[s['food_id']]} g (--rigenera)")
    return problemi


def rigenera(base=None):
    """Riscrive grammi_porzione dai dati di alimenti.csv."""
    for nome in ("scambi_carboidrati.csv", "scambi_pesce.csv"):
        att = attese(nome, base)
        righe = carica_scambi(nome, base)
        with open(os.path.join(base or BASE, nome), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(righe[0]), lineterminator="\n")
            w.writeheader()
            for s in righe:
                w.writerow(dict(s, grammi_porzione=att[s["food_id"]]))


if __name__ == "__main__":
    if "--rigenera" in sys.argv:
        rigenera()
    trovati = controlla()
    print("\n".join(trovati) or "Tabelle di conversione coerenti con alimenti.csv.")
    sys.exit(1 if trovati else 0)
