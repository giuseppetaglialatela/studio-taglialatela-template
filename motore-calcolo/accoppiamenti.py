"""
Controllo degli accoppiamenti nello stesso pasto - Studio Taglialatela

COSA FA
Segnala i pasti in cui compaiono insieme due alimenti di ruoli che il
nutrizionista ha dichiarato da non accoppiare (es. latte e yogurt, carne e
pesce). Decisione del 21/10/2026: la violazione si SEGNALA, non blocca.

FILE (affiancati, lo schema di alimenti.csv resta congelato)
  ruoli_alimenti.csv        food_id,ruolo - un ruolo per ogni voce del database
  accoppiamenti_vietati.csv regola_id,ruoli_a,ruoli_b,motivo,data_decisione[,pasti]
                            ruoli_a e ruoli_b accettano piu' voci separate da |;
                            ogni voce e' un RUOLO (es. pesce) oppure un food_id
                            preciso (es. 1313 merluzzo) - dal 21/10/2026, per
                            regole come "merluzzo + pasta" che non valgono per
                            tutto il ruolo (pasta con alici o pesce spada si').
                            pasti (facoltativa): pasti in cui la regola vale,
                            separati da |; vuota = tutti. Nella libreria un
                            blocco 'spuntino' vale per spuntino e spuntino2.

Una regola con lo stesso ruolo sui due lati (es. formaggio + formaggio)
segnala due alimenti DIVERSI di quel ruolo; lo stesso alimento non fa coppia
con se stesso.

Le coppie vietate crescono man mano che si presentano: una riga nuova nel
file, nessuna modifica al codice.

COME SI VALUTANO LE SCELTE
Un pasto con alternative (gruppo_scelta/opzione) si controlla scenario per
scenario: righe fisse + una opzione per ogni gruppo. Due opzioni dello stesso
gruppo non si mangiano insieme, quindi non formano un accoppiamento.

USO
  python3 accoppiamenti.py --piano piano.csv      controlla un piano
  python3 accoppiamenti.py --libreria             controlla la libreria dei blocchi
"""

import argparse
import csv
import itertools
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

RUOLI_AMMESSI = {
    "carne", "salume", "pesce", "molluschi_crostacei", "uova", "legumi",
    "latte", "yogurt", "formaggio", "cereale", "patate", "verdura", "frutta",
    "frutta_secca", "condimento", "dolce",
}

FILE_LIBRERIA = ("moduli_pasto.csv", "moduli_colazione.csv")

PASTI_AMMESSI = {"colazione", "spuntino", "pranzo", "spuntino2", "cena"}


def carica_ruoli(path=None):
    path = path or os.path.join(BASE, "ruoli_alimenti.csv")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {r["food_id"].strip(): r["ruolo"].strip() for r in csv.DictReader(f)}


def carica_regole(path=None):
    path = path or os.path.join(BASE, "accoppiamenti_vietati.csv")
    regole = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            regole.append({
                "id": r["regola_id"].strip(),
                "a": {x.strip() for x in r["ruoli_a"].split("|") if x.strip()},
                "b": {x.strip() for x in r["ruoli_b"].split("|") if x.strip()},
                "motivo": r["motivo"].strip(),
                "pasti": {x.strip() for x in (r.get("pasti") or "").split("|") if x.strip()},
            })
    return regole


def _corrisponde(food_id, lato, ruoli):
    """Un alimento sta su un lato della regola se il lato nomina il suo ruolo
    oppure il suo food_id."""
    return food_id in lato or ruoli.get(food_id) in lato


def _vale_nel_pasto(reg, pasti):
    """pasti: insieme dei pasti a cui appartiene l'insieme controllato (None =
    non noto, la regola vale). Regola senza pasti = vale ovunque."""
    if not reg.get("pasti") or pasti is None:
        return True
    return bool(reg["pasti"] & set(pasti))


def violazioni_insieme(food_ids, ruoli, regole, pasti=None):
    """food_ids: insieme di alimenti mangiati insieme; pasti: insieme dei pasti
    in cui li si mangia. Restituisce [(regola, food_id_a, food_id_b)] per ogni
    coppia vietata trovata."""
    trovate = []
    for reg in regole:
        if not _vale_nel_pasto(reg, pasti):
            continue
        lato_a = sorted(f for f in food_ids if _corrisponde(f, reg["a"], ruoli))
        lato_b = sorted(f for f in food_ids if _corrisponde(f, reg["b"], ruoli))
        coppie = [(x, y) for x in lato_a for y in lato_b if x != y]
        if coppie:
            trovate.append((reg, lato_a, lato_b))
    return trovate


def scenari_pasto(righe):
    """righe di un solo (giorno, pasto). Restituisce [(etichetta, {food_id})]."""
    fissi = {r["food_id"] for r in righe if not r.get("gruppo_scelta")}
    gruppi = {}
    for r in righe:
        g = r.get("gruppo_scelta")
        if g:
            gruppi.setdefault(g, {}).setdefault(r["opzione"], set()).add(r["food_id"])
    if not gruppi:
        return [("", fissi)]
    nomi = sorted(gruppi)
    scenari = []
    for combo in itertools.product(*[sorted(gruppi[g]) for g in nomi]):
        insieme = set(fissi)
        for g, opz in zip(nomi, combo):
            insieme |= gruppi[g][opz]
        etichetta = ", ".join(f"{g}={o}" for g, o in zip(nomi, combo))
        scenari.append((etichetta, insieme))
    return scenari


def controlla_piano(righe_estese, ruoli, regole):
    """Restituisce le violazioni raggruppate: una voce per (regola, pasto,
    alimenti coinvolti, scenario), con l'elenco dei giorni in cui compare."""
    per_pasto = {}
    for r in righe_estese:
        per_pasto.setdefault((r["giorno"], r["pasto"]), []).append(r)
    raccolta = {}
    for (giorno, pasto), righe in per_pasto.items():
        for etichetta, insieme in scenari_pasto(righe):
            for reg, a, b in violazioni_insieme(insieme, ruoli, regole, {pasto}):
                chiave = (reg["id"], pasto, tuple(a), tuple(b), etichetta)
                voce = raccolta.setdefault(chiave, {
                    "regola": reg["id"], "motivo": reg["motivo"], "pasto": pasto,
                    "alimenti_a": a, "alimenti_b": b, "scenario": etichetta,
                    "giorni": []})
                if giorno not in voce["giorni"]:
                    voce["giorni"].append(giorno)
    return sorted(raccolta.values(), key=lambda v: (v["regola"], v["pasto"], v["scenario"]))


def _parse_ingredienti(testo):
    return {p.split(":")[0].strip() for p in testo.split(";") if p.strip()}


def controlla_libreria(ruoli, regole):
    """Ogni blocco della libreria dev'essere un accoppiamento valido."""
    problemi = []
    for nome_file in FILE_LIBRERIA:
        path = os.path.join(BASE, nome_file)
        if not os.path.isfile(path):
            continue
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                insieme = _parse_ingredienti(r["ingredienti_food_id_grammi"])
                cat = r.get("categoria", "").strip()
                pasti = {"spuntino", "spuntino2"} if cat == "spuntino" else ({cat} if cat else None)
                for reg, a, b in violazioni_insieme(insieme, ruoli, regole, pasti):
                    problemi.append(f"{nome_file} {r['modulo_id']}: viola {reg['id']} "
                                    f"({', '.join(a)} + {', '.join(b)})")
    return problemi


def valida_file(ids_alimenti):
    """Per il collaudo: ruoli completi e validi, regole coerenti, libreria
    senza accoppiamenti vietati e senza food_id sconosciuti."""
    problemi = []
    try:
        with open(os.path.join(BASE, "ruoli_alimenti.csv"), newline="",
                  encoding="utf-8-sig") as f:
            righe = list(csv.DictReader(f))
    except Exception as e:
        return [f"ruoli_alimenti.csv non leggibile: {e}"]
    visti = set()
    for r in righe:
        fid, ruolo = r["food_id"].strip(), (r["ruolo"] or "").strip()
        if fid in visti:
            problemi.append(f"ruoli_alimenti.csv: food_id duplicato {fid}")
        visti.add(fid)
        if ruolo not in RUOLI_AMMESSI:
            problemi.append(f"ruoli_alimenti.csv: ruolo non ammesso '{ruolo}' per {fid}")
    senza = sorted(set(ids_alimenti) - visti)
    orfani = sorted(visti - set(ids_alimenti))
    if senza:
        problemi.append(f"{len(senza)} food_id senza ruolo: {', '.join(senza[:5])}")
    if orfani:
        problemi.append(f"ruoli_alimenti.csv: {len(orfani)} food_id assenti da "
                        f"alimenti.csv: {', '.join(orfani[:5])}")
    try:
        regole = carica_regole()
    except Exception as e:
        return problemi + [f"accoppiamenti_vietati.csv non leggibile: {e}"]
    for reg in regole:
        ignoti = (reg["a"] | reg["b"]) - RUOLI_AMMESSI - set(ids_alimenti)
        if ignoti or not reg["a"] or not reg["b"]:
            problemi.append(f"regola {reg['id']}: voci che non sono ne' ruoli ne' "
                            f"food_id del database {sorted(ignoti)}")
        pasti_ignoti = reg["pasti"] - PASTI_AMMESSI
        if pasti_ignoti:
            problemi.append(f"regola {reg['id']}: pasti non ammessi {sorted(pasti_ignoti)}")
    for nome_file in FILE_LIBRERIA:
        path = os.path.join(BASE, nome_file)
        if not os.path.isfile(path):
            continue
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                ignoti = _parse_ingredienti(r["ingredienti_food_id_grammi"]) - set(ids_alimenti)
                if ignoti:
                    problemi.append(f"{nome_file} {r['modulo_id']}: food_id "
                                    f"sconosciuti {', '.join(sorted(ignoti))}")
    if not problemi:
        problemi += controlla_libreria(carica_ruoli(), regole)
    return problemi


def _nomi(db_path=None):
    db_path = db_path or os.path.join(BASE, "alimenti.csv")
    with open(db_path, newline="", encoding="utf-8") as f:
        return {r["food_id"]: r["nome"] for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser(description="Controllo accoppiamenti nello stesso pasto")
    ap.add_argument("--piano")
    ap.add_argument("--libreria", action="store_true")
    args = ap.parse_args()
    ruoli, regole = carica_ruoli(), carica_regole()
    nomi = _nomi()
    if args.libreria:
        problemi = controlla_libreria(ruoli, regole)
        print("libreria: nessun accoppiamento vietato" if not problemi else "\n".join(problemi))
        return 1 if problemi else 0
    if not args.piano:
        ap.error("indicare --piano oppure --libreria")
    sys.path.insert(0, BASE)
    from scelte_multiple import carica_piano_esteso
    viol = controlla_piano(carica_piano_esteso(args.piano), ruoli, regole)
    if not viol:
        print("nessun accoppiamento vietato")
    for v in viol:
        a = " + ".join(nomi.get(x, x) for x in v["alimenti_a"])
        b = " + ".join(nomi.get(x, x) for x in v["alimenti_b"])
        sc = f" [{v['scenario']}]" if v["scenario"] else ""
        print(f"{v['regola']} {v['pasto']}{sc}, giorni {','.join(v['giorni'])}: {a} / {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
