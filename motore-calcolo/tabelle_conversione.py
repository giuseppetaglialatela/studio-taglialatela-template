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
  scambi_carni.csv        stesso schema (decisione del nutrizionista, 11/11/2026): carni e
                          affettati, grammi equivalenti a 100 g di petto di pollo, a parita'
                          di proteine, arrotondati a 5 g. Gli affettati (ruolo salume) sono
                          segnati nella scheda con la nota sul sale: il motore non calcola
                          il sodio.
  scambi_verdure.csv      food_id, nome_riferimento, uso (crude|cotte|entrambe), stato.
                          A parita' di peso; patate e legumi esclusi.
  Stato: 'confermato' = compare come alternativa; 'da_confermare' = compare solo come
  riga, se e' nel piano, finche' il nutrizionista non lo conferma; 'solo_piano' =
  decisione del nutrizionista: compare solo se e' nel piano, mai come alternativa
  (quinoa e piadina, 04/11/2026: a parita' di carboidrati oltre 100 kcal in piu').

Filtro di sicurezza (decisione del 04/11/2026, delegata dal nutrizionista): uno scambio
compare solo se 1) lo scarto non supera il 2,5% delle kcal del target, cosi' due scambi
nello stesso giorno restano entro il 5%; 2) in ogni giorno in cui la voce compare, sommando
lo scambio e un secondo scambio uguale, nessuno scenario supera il +/-10%.
Verdure: a parita' di peso si dividono in fasce di energia, per gruppo; una fascia con una
verdura del piano non resta mai vuota in silenzio.

Esclusioni del singolo piano (04/11/2026): file JSON facoltativo, fuori dal repository e
dai metadati, con le chiavi escludi_food_id, massimo_g_a_pasto e verdure_crude_ammesse
(carica_esclusioni). Toglie dalle tabelle cio' che quella dieta vieta.

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
RIF_CARNI = ("106500", 100.0)          # petto di pollo
SOGLIA_CARBOIDRATI_VERDURA = 5.0       # g/100 g: oltre, la verdura si segnala
SOGLIA_FIBRA_VERDURA = 5.0             # g/100 g: oltre, la verdura si segnala
RUOLI_AMMESSI = {"carboidrati": {"cereale", "patate"}, "pesce": {"pesce", "molluschi_crostacei"},
                 "carni": {"carne", "salume"}, "verdure": {"verdura"}}
# tabelle a grammature ricalcolate: file, riferimento (food_id, grammi), nutriente
TABELLE_GRAMMI = {"scambi_carboidrati.csv": (RIF_CARBOIDRATI, "carboidrati_g"),
                  "scambi_pesce.csv": (RIF_PESCE, "proteine_g"),
                  "scambi_carni.csv": (RIF_CARNI, "proteine_g")}
USI_VERDURE = {"crude", "cotte", "entrambe"}
STATI = {"confermato", "da_confermare", "solo_piano"}
PASTI_PRINCIPALI = ("pranzo", "cena")
QUOTA_SCAMBIO = 0.025                  # dello scarto ammesso sul target giornaliero
LIMITE_GIORNO = 0.10                   # limite di sicurezza del nucleo, principio 8


CHIAVI_ESCLUSIONI = ("escludi_food_id", "massimo_g_a_pasto", "verdure_crude_ammesse")


def carica_esclusioni(path, db):
    """Legge e valida il file. ValueError su campo non previsto, food_id sconosciuto o
    valore non valido: chi lo usa si ferma."""
    import json
    with open(path, encoding="utf-8") as f:
        dati = json.load(f)
    if not isinstance(dati, dict):
        raise ValueError(f"{path}: serve un oggetto JSON")
    estranei = sorted(set(dati) - set(CHIAVI_ESCLUSIONI))
    if estranei:
        raise ValueError(f"{path}: campi non previsti: {', '.join(estranei)}")
    vieti = dati.get("escludi_food_id", {})
    massimi = dati.get("massimo_g_a_pasto", {})
    crude = dati.get("verdure_crude_ammesse")
    if not isinstance(vieti, dict) or not isinstance(massimi, dict) or \
            not (crude is None or isinstance(crude, list)):
        raise ValueError(f"{path}: formato non valido")
    sconosciuti = sorted(f for f in [*vieti, *massimi, *(crude or [])] if f not in db)
    if sconosciuti:
        raise ValueError(f"{path}: food_id sconosciuti: {', '.join(map(str, sconosciuti))}")
    for f, g in massimi.items():
        if isinstance(g, bool) or not isinstance(g, (int, float)) or g <= 0:
            raise ValueError(f"{path}: massimo non valido per {f}: {g}")
    return {"vieti": set(vieti), "massimi": {f: float(g) for f, g in massimi.items()},
            "crude": None if crude is None else set(crude)}


def controlla_esclusioni(piano, esc):
    """Una voce vietata non puo' stare nel piano: e' una contraddizione."""
    return sorted({r["food_id"] for r in piano if r["food_id"] in esc["vieti"]})


class Filtro:
    """Decide se uno scambio resta in tabella, sui giorni reali del piano."""

    def __init__(self, piano, db, target_kcal):
        self.target = float(target_kcal)
        self.limite = QUOTA_SCAMBIO * self.target
        pasti, self.dove = {}, {}
        for r in piano:
            k = (r["giorno"], r["pasto"])
            o = r.get("opzione", "")
            pasti.setdefault(k, {}).setdefault(o, 0.0)
            pasti[k][o] += kcal(r["food_id"], float(r["grammi"]), db)
            self.dove.setdefault((r["food_id"], float(r["grammi"])), set()).add(r["giorno"])
        self.giorni = {}
        for (g, _p), opz in pasti.items():
            fisso = opz.get("", 0.0)
            scelte = [v for o, v in opz.items() if o] or [0.0]
            lo, hi = self.giorni.get(g, (0.0, 0.0))
            self.giorni[g] = (lo + fisso + min(scelte), hi + fisso + max(scelte))

    def ammesso(self, fid, grammi, scarto):
        if abs(scarto) > self.limite:
            return False
        for g in self.dove.get((fid, float(grammi)), ()):
            lo, hi = self.giorni[g]
            if hi + 2 * max(scarto, 0) > (1 + LIMITE_GIORNO) * self.target:
                return False
            if lo + 2 * min(scarto, 0) < (1 - LIMITE_GIORNO) * self.target:
                return False
        return True


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


def _tabella(piano, db, scambi, campo, filtro=None, esc=None):
    """Righe = voci del piano (pranzo e cena) presenti nell'elenco; colonne = voci
    confermate. Ogni cella: grammi equivalenti e scarto in kcal."""
    tolte_voci = sum(s["food_id"] in esc["vieti"] for s in scambi) if esc else 0
    if esc:
        scambi = [s for s in scambi if s["food_id"] not in esc["vieti"]]
    elenco = {s["food_id"]: s["nome_riferimento"] for s in scambi}
    colonne = [s for s in scambi if s["stato"] == "confermato"]
    massimi = esc["massimi"] if esc else {}
    tolte_celle = 0
    viste = sorted({(r["food_id"], float(r["grammi"])) for r in piano
                    if r["pasto"] in PASTI_PRINCIPALI and r["food_id"] in elenco},
                   key=lambda x: (list(elenco).index(x[0]), -x[1]))
    righe, esclusi = [], 0
    for fid, g in viste:
        celle = []
        for c in colonne:
            alt = c["food_id"]
            if alt == fid:
                celle.append(None)
                continue
            ga = equivalente(g, fid, alt, campo, db)
            if alt in massimi and ga > massimi[alt]:
                celle.append(None)
                tolte_celle += 1
                continue
            scarto = kcal(alt, ga, db) - kcal(fid, g, db)
            if filtro is not None and not filtro.ammesso(fid, g, scarto):
                celle.append(None)
                esclusi += 1
                continue
            celle.append({"grammi": ga, "scarto_kcal": round(scarto)})
        righe.append({"food_id": fid, "nome": elenco[fid], "grammi": g, "celle": celle})
    # un'alternativa senza nessuno scambio ammesso non si mostra
    vive = [i for i in range(len(colonne)) if any(r["celle"][i] for r in righe)]
    for r in righe:
        r["celle"] = [r["celle"][i] for i in vive]
    return {"colonne": [colonne[i]["nome_riferimento"] for i in vive], "righe": righe,
            "esclusi": esclusi, "da_file": {"voci": tolte_voci, "celle": tolte_celle}}


def tabella_carboidrati(piano, db, base=None, filtro=None, esc=None):
    return _tabella(piano, db, carica_scambi("scambi_carboidrati.csv", base), "carboidrati_g", filtro, esc)


def tabella_pesce(piano, db, base=None, filtro=None, esc=None):
    return _tabella(piano, db, carica_scambi("scambi_pesce.csv", base), "proteine_g", filtro, esc)


def tabella_carni(piano, db, base=None, filtro=None, esc=None):
    return _tabella(piano, db, carica_scambi("scambi_carni.csv", base), "proteine_g", filtro, esc)


def _fasce(voci, grammi, limite):
    """voci: [(kcal/100 g, nome, food_id)] in ordine. Fasce in cui due voci qualsiasi, a
    quel peso, differiscono al massimo di 'limite' kcal."""
    fasce = []
    for v in voci:
        if fasce and (v[0] - fasce[-1][0][0]) * grammi / 100 <= limite:
            fasce[-1].append(v)
        else:
            fasce.append([v])
    return fasce


def tabella_verdure(piano, db, base=None, filtro=None, esc=None):
    """Per ogni gruppo (crude, cotte) le fasce di verdure scambiabili tra loro. Con il
    filtro restano le fasce con una verdura del piano e, in queste, le voci che il piano
    regge; la verdura del piano non si toglie mai. Le verdure del piano senza scambio si
    riportano in 'senza_scambio', non spariscono in silenzio."""
    scambi = carica_scambi("scambi_verdure.csv", base)
    conf = [s for s in scambi if s["stato"] == "confermato"]
    gruppi, senza, esclusi = {}, [], 0
    tolte = 0
    for u in ("crude", "cotte"):
        tutte = [s for s in conf if s["uso"] in (u, "entrambe")]
        ammesse = [s for s in tutte if not esc or s["food_id"] not in esc["vieti"]]
        if esc and u == "crude" and esc["crude"] is not None:
            ammesse = [s for s in ammesse if s["food_id"] in esc["crude"]]
        tolte += len(tutte) - len(ammesse)
        voci = sorted((float(db[s["food_id"]]["kcal_100g"]), s["nome_riferimento"], s["food_id"])
                      for s in ammesse)
        if filtro is None:
            gruppi[u] = [[v[1] for v in voci]]
            continue
        del_piano = {}
        for r in piano:
            if r["pasto"] in PASTI_PRINCIPALI and any(v[2] == r["food_id"] for v in voci):
                del_piano.setdefault(r["food_id"], []).append(float(r["grammi"]))
        if not del_piano:
            gruppi[u] = []
            continue
        peso = max(g for gg in del_piano.values() for g in gg)
        gruppi[u] = []
        for fascia in _fasce(voci, peso, filtro.limite):
            nel_piano = [v for v in fascia if v[2] in del_piano]
            if not nel_piano:
                continue
            tenute = [v for v in fascia if v[2] in del_piano or all(
                filtro.ammesso(f[2], g, (v[0] - f[0]) * g / 100)
                for f in nel_piano for g in del_piano[f[2]])]
            esclusi += len(fascia) - len(tenute)
            if len(tenute) > 1:
                gruppi[u].append([v[1] for v in tenute])
            else:
                senza.append(tenute[0][1])
    mostrate = {n for fasce in gruppi.values() for f in fasce for n in f}
    segnalate = []
    for s in conf:
        if s["nome_riferimento"] not in mostrate:
            continue
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
    return {"gruppi": gruppi, "segnalate": segnalate, "fuori_elenco": fuori, "esclusi": esclusi,
            "senza_scambio": sorted(set(senza) - mostrate), "da_file": {"voci": tolte, "celle": 0}}


def attese(nome, base=None, db=None):
    """grammi_porzione ricalcolati da alimenti.csv."""
    db = db or carica_db(base)
    (rif, g), campo = TABELLE_GRAMMI[nome]
    return {s["food_id"]: equivalente(g, rif, s["food_id"], campo, db)
            for s in carica_scambi(nome, base)}


def controlla(base=None):
    """Per il collaudo: elenco dei problemi, vuoto se tutto e' coerente."""
    problemi = []
    db = carica_db(base)
    ruoli = {r["food_id"]: r["ruolo"] for r in _righe("ruoli_alimenti.csv", base)}
    for nome, tipo in (("scambi_carboidrati.csv", "carboidrati"), ("scambi_pesce.csv", "pesce"),
                       ("scambi_carni.csv", "carni"), ("scambi_verdure.csv", "verdure")):
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
    for nome in TABELLE_GRAMMI:
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
