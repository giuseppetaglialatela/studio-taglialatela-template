#!/usr/bin/env python3
"""
Combinazioni reali dei pasti a scelta - Studio Nutrizionale Taglialatela
Tappa 1 del piano operativo del 28/10/2026 (approvata il 28/10/2026).

PERCHE'
Fino al 29/10/2026 le percentuali dei macro dei giorni a scelta si calcolavano
come grammi minimi / kcal minime e grammi massimi / kcal massime, con minimi e
massimi presi nutriente per nutriente. Un rapporto non ha gli estremi dove li
hanno numeratore e denominatore: una giornata reale poteva uscire
dall'intervallo dichiarato (caso 06: carboidrati -6,26 punti con colazione S2 e
spuntino SPrA, dichiarati -4,69; piano reale v5: -9,3 contro -7,65).

COSA FA
- Giorno: elenca TUTTE le giornate realmente componibili (un'alternativa per
  ogni gruppo di scelta, colazione x spuntino x secondo spuntino x ...),
  rispettando l'abbinamento colazione -> spuntino dei metadati se c'e'.
  Kcal, nutrienti e percentuali dei macro si leggono su queste giornate: gli
  estremi sono giornate vere, con le scelte che le producono.
- Settimana: la media settimanale di un macro e' un rapporto di somme
  (somma grammi x kcal/g) / (somma kcal) su una scelta per ogni giorno. Il
  massimo e il minimo esatti si trovano con il metodo di Dinkelbach: per un
  lambda fissato la somma si separa giorno per giorno; si itera finche' la
  scelta non cambia. Il risultato e' la settimana reale peggiore, giorno per
  giorno.
- Kcal settimanali e nutrienti singoli sono somme: il minimo e' la somma dei
  minimi giornalieri, gia' esatto (lo si ricalcola qui per coerenza).

VERIFICA
  python3 combinazioni.py --autotest
confronta giorno e settimana con il calcolo di tutte le combinazioni una per
una (forza bruta) su casi casuali piccoli, a seme fisso: zero differenze
ammesse. Gira dentro regressione.py.
"""

import itertools
import sys
from collections import OrderedDict

from scelte_multiple import NUTRIENTI, _contributo

# (nome, campo, kcal per grammo, chiave del target)
MACRO = [("Proteine", "proteine_g", 4, "proteine_pct_target"),
         ("Carboidrati", "carboidrati_g", 4, "carboidrati_pct_target"),
         ("Grassi", "grassi_g", 9, "grassi_pct_target")]

# oltre questo numero di giornate componibili in un giorno ci si ferma: un
# piano reale ne ha decine, non migliaia
LIMITE_COMBINAZIONI_GIORNO = 20000

# confronto in virgola mobile tra il calcolo esatto e la forza bruta
EPS = 1e-9


class ErroreCombinazioni(ValueError):
    pass


def carica_abbinamento(meta):
    """Da metadati: {opzione_colazione: [opzioni_spuntino]} oppure None
    («non concordato» o assente). Stessa lettura di genera_zona_piano.py."""
    if not meta:
        return None
    ab = meta.get("abbinamento_spuntino", "non concordato")
    if ab in (None, "", "non concordato"):
        return None
    if not isinstance(ab, dict):
        raise ErroreCombinazioni("metadati: 'abbinamento_spuntino' deve essere un oggetto "
                                 "{opzione_colazione: opzione_spuntino} oppure "
                                 "\"non concordato\"")
    return {str(c): [str(x) for x in (s if isinstance(s, list) else [s])]
            for c, s in ab.items()}


def _somma(a, b):
    return {n: a[n] + b[n] for n in NUTRIENTI}


def struttura_giorno(righe_giorno, db):
    """(base, gruppi): base = totale degli alimenti fissi; gruppi = lista
    ordinata di ((pasto, gruppo_scelta), [(opzione, totale_opzione), ...])."""
    base = {n: 0.0 for n in NUTRIENTI}
    gruppi = OrderedDict()
    for r in righe_giorno:
        c = _contributo(db, r["food_id"], r["grammi"])
        if not r["gruppo_scelta"]:
            base = _somma(base, c)
            continue
        opz = gruppi.setdefault((r["pasto"], r["gruppo_scelta"]), OrderedDict())
        opz[r["opzione"]] = _somma(opz.get(r["opzione"], {n: 0.0 for n in NUTRIENTI}), c)
    return base, [(k, list(v.items())) for k, v in gruppi.items()]


def _ammessa(scelte, abbin):
    if not abbin:
        return True
    col = [o for (pasto, _), o in scelte if pasto == "colazione"]
    spu = [o for (pasto, _), o in scelte if pasto == "spuntino"]
    for oc in col:
        if oc not in abbin:
            raise ErroreCombinazioni(f"abbinamento_spuntino: manca la colazione {oc}")
        for os_ in spu:
            if os_ not in abbin[oc]:
                return False
    return True


def combinazioni_giorno(righe_giorno, db, abbin=None):
    """Tutte le giornate componibili del giorno: lista di dict
    {"scelte": ((pasto, gruppo), opzione)..., "tot": {nutriente: valore}}.
    Un giorno senza scelte ha una sola giornata."""
    base, gruppi = struttura_giorno(righe_giorno, db)
    n = 1
    for _, opz in gruppi:
        n *= len(opz)
    if n > LIMITE_COMBINAZIONI_GIORNO:
        raise ErroreCombinazioni(f"{n} giornate componibili in un giorno: oltre il limite "
                                 f"di {LIMITE_COMBINAZIONI_GIORNO}")
    chiavi = [k for k, _ in gruppi]
    out = []
    for prodotto in itertools.product(*[opz for _, opz in gruppi]):
        scelte = tuple((k, o) for k, (o, _) in zip(chiavi, prodotto))
        if not _ammessa(scelte, abbin):
            continue
        tot = dict(base)
        for _, t in prodotto:
            tot = _somma(tot, t)
        out.append({"scelte": scelte, "tot": tot})
    if not out:
        raise ErroreCombinazioni("abbinamento_spuntino esclude tutte le combinazioni del giorno")
    return out


def pct(tot, campo, kc):
    k = tot["kcal_100g"]
    return tot[campo] * kc / k * 100 if k else None


def estremi_giorno(combos):
    """Estremi su giornate reali. Restituisce
    (minimi, massimi, macro) con minimi/massimi per nutriente e
    macro[campo] = ((pct_min, combo), (pct_max, combo))."""
    minimi = {n: min(c["tot"][n] for c in combos) for n in NUTRIENTI}
    massimi = {n: max(c["tot"][n] for c in combos) for n in NUTRIENTI}
    macro = {}
    for _, campo, kc, _ in MACRO:
        valide = [(pct(c["tot"], campo, kc), c) for c in combos if c["tot"]["kcal_100g"]]
        if not valide:
            continue
        lo = min(valide, key=lambda x: x[0])
        hi = max(valide, key=lambda x: x[0])
        macro[campo] = (lo, hi)
    return minimi, massimi, macro


def _dinkelbach(giorni, segno):
    """giorni: lista (per giorno) di liste di coppie (a, b), b > 0.
    Massimizza segno * (somma a) / (somma b) scegliendo una coppia per giorno.
    Restituisce (rapporto, indici scelti). Esatto: si ferma quando la scelta
    ottima per il lambda corrente non migliora piu' il rapporto."""
    scelta = [0] * len(giorni)

    def rapporto(sc):
        A = sum(giorni[i][j][0] for i, j in enumerate(sc))
        B = sum(giorni[i][j][1] for i, j in enumerate(sc))
        return segno * A / B

    lam = rapporto(scelta)
    for _ in range(10000):
        nuova = []
        for i, opz in enumerate(giorni):
            valori = [segno * a - lam * b for a, b in opz]
            m = max(valori)
            # a parita' si tiene la scelta corrente: niente oscillazioni
            j = scelta[i] if valori[scelta[i]] >= m - EPS * (1 + abs(m)) else valori.index(m)
            nuova.append(j)
        nuovo_lam = rapporto(nuova)
        if nuovo_lam <= lam + EPS * (1 + abs(lam)):
            return segno * max(lam, nuovo_lam), (scelta if lam >= nuovo_lam else nuova)
        scelta, lam = nuova, nuovo_lam
    raise ErroreCombinazioni("Dinkelbach: nessuna convergenza in 10000 iterazioni")


def estremi_settimana(combos_per_giorno):
    """combos_per_giorno: lista (un elemento per giorno, nell'ordine del piano)
    di liste di combinazioni. Restituisce dict con:
      kcal_media: (min, max) della media giornaliera
      macro[campo]: ((pct_min, [indice combinazione per giorno]),
                     (pct_max, [indici]))
    Le percentuali sono quelle della media settimanale (somma su somma)."""
    n = len(combos_per_giorno)
    k_min = sum(min(c["tot"]["kcal_100g"] for c in g) for g in combos_per_giorno) / n
    k_max = sum(max(c["tot"]["kcal_100g"] for c in g) for g in combos_per_giorno) / n
    out = {"kcal_media": (k_min, k_max), "macro": {}}
    for _, campo, kc, _ in MACRO:
        coppie = [[(c["tot"][campo] * kc * 100, c["tot"]["kcal_100g"]) for c in g]
                  for g in combos_per_giorno]
        if any(b <= 0 for g in coppie for _, b in g):
            continue
        hi, sc_hi = _dinkelbach(coppie, +1)
        lo, sc_lo = _dinkelbach(coppie, -1)
        out["macro"][campo] = ((lo, sc_lo), (hi, sc_hi))
    return out


def estremi_pct_settimana(combos_per_giorno, campo, kc):
    """Come estremi_settimana per un solo campo qualsiasi (es. saturi_g, 9 kcal/g):
    ((pct_min, indici), (pct_max, indici)) della media settimanale, oppure None
    se una giornata ha kcal nulle. Stesso metodo esatto (Dinkelbach)."""
    coppie = [[(c["tot"][campo] * kc * 100, c["tot"]["kcal_100g"]) for c in g]
              for g in combos_per_giorno]
    if any(b <= 0 for g in coppie for _, b in g):
        return None
    return _dinkelbach(coppie, -1), _dinkelbach(coppie, +1)


def descrivi_scelte(combo):
    """'colazione S2 + spuntino SPrA' (vuoto per un giorno senza scelte)."""
    return " + ".join(f"{pasto} {o}" for (pasto, _), o in combo["scelte"])


# --------------------------------------------------------------------------
# Forza bruta e autotest
# --------------------------------------------------------------------------

def _forza_bruta_settimana(combos_per_giorno, campo, kc):
    lo = hi = None
    for prodotto in itertools.product(*combos_per_giorno):
        A = sum(c["tot"][campo] * kc * 100 for c in prodotto)
        B = sum(c["tot"]["kcal_100g"] for c in prodotto)
        r = A / B
        lo = r if lo is None else min(lo, r)
        hi = r if hi is None else max(hi, r)
    return lo, hi


def _db_casuale(rnd, n):
    db = {}
    for i in range(n):
        p, c, g = rnd.uniform(0, 30), rnd.uniform(0, 80), rnd.uniform(0, 40)
        if p + c + g < 1:
            c += 5
        al = {k: rnd.uniform(0, 50) for k in NUTRIENTI}
        al.update({"proteine_g": p, "carboidrati_g": c, "grassi_g": g,
                   "kcal_100g": max(1.0, 4 * p + 4 * c + 9 * g + rnd.uniform(-5, 5))})
        db[f"F{i}"] = al
    return db


def _piano_casuale(rnd, db, n_giorni):
    ids = list(db)
    righe = []
    pasti_scelta = [("colazione", "colazione_principale"), ("spuntino", "spuntino_principale"),
                    ("spuntino2", "spuntino_secondo"), ("pranzo", "pranzo_scelta")]
    for g in range(1, n_giorni + 1):
        for pasto in ("pranzo", "cena"):
            for _ in range(rnd.randint(1, 3)):
                righe.append({"giorno": str(g), "pasto": pasto, "food_id": rnd.choice(ids),
                              "grammi": rnd.uniform(10, 200), "gruppo_scelta": "", "opzione": ""})
        for pasto, gruppo in rnd.sample(pasti_scelta, rnd.randint(0, 3)):
            for o in range(rnd.randint(1, 4)):
                for _ in range(rnd.randint(1, 3)):
                    righe.append({"giorno": str(g), "pasto": pasto, "food_id": rnd.choice(ids),
                                  "grammi": rnd.uniform(5, 250), "gruppo_scelta": gruppo,
                                  "opzione": f"O{o}"})
    return righe


def autotest(n_casi=300, seme=20261029, verboso=False):
    """Confronto con la forza bruta. Restituisce (casi, differenze)."""
    import random
    rnd = random.Random(seme)
    differenze = 0
    for caso in range(n_casi):
        db = _db_casuale(rnd, 12)
        n_giorni = rnd.randint(1, 4)
        righe = _piano_casuale(rnd, db, n_giorni)
        abbin = None
        cols = sorted({r["opzione"] for r in righe if r["pasto"] == "colazione" and r["gruppo_scelta"]})
        spus = sorted({r["opzione"] for r in righe if r["pasto"] == "spuntino" and r["gruppo_scelta"]})
        if cols and spus and rnd.random() < 0.4:
            abbin = {c: rnd.sample(spus, rnd.randint(1, len(spus))) for c in cols}
            # nei casi casuali le opzioni cambiano da un giorno all'altro: un
            # abbinamento che svuota un giorno non e' un piano possibile
            try:
                for g in range(1, n_giorni + 1):
                    combinazioni_giorno([r for r in righe if r["giorno"] == str(g)], db, abbin)
            except ErroreCombinazioni:
                abbin = None
        per_giorno = []
        for g in range(1, n_giorni + 1):
            rg = [r for r in righe if r["giorno"] == str(g)]
            combos = combinazioni_giorno(rg, db, abbin)
            per_giorno.append(combos)
            # giorno: estremi contro l'elenco esplicito delle percentuali
            _, _, macro = estremi_giorno(combos)
            for _, campo, kc, _ in MACRO:
                valori = [pct(c["tot"], campo, kc) for c in combos]
                (lo, clo), (hi, chi) = macro[campo]
                if abs(lo - min(valori)) > 1e-9 or abs(hi - max(valori)) > 1e-9 \
                        or abs(pct(clo["tot"], campo, kc) - lo) > 1e-12 \
                        or abs(pct(chi["tot"], campo, kc) - hi) > 1e-12:
                    differenze += 1
                    if verboso:
                        print(f"  caso {caso}, giorno {g}, {campo}: differenza")
            # abbinamento: nessuna combinazione esclusa compare
            if abbin:
                for c in combos:
                    if not _ammessa(c["scelte"], abbin):
                        differenze += 1
        sett = estremi_settimana(per_giorno)
        for _, campo, kc, _ in MACRO:
            blo, bhi = _forza_bruta_settimana(per_giorno, campo, kc)
            (lo, slo), (hi, shi) = sett["macro"][campo]
            # gli indici restituiti devono produrre davvero il valore dichiarato
            def ricalcola(sc):
                A = sum(per_giorno[i][j]["tot"][campo] * kc * 100 for i, j in enumerate(sc))
                B = sum(per_giorno[i][j]["tot"]["kcal_100g"] for i, j in enumerate(sc))
                return A / B
            if abs(lo - blo) > 1e-9 or abs(hi - bhi) > 1e-9 \
                    or abs(ricalcola(slo) - lo) > 1e-9 or abs(ricalcola(shi) - hi) > 1e-9:
                differenze += 1
                if verboso:
                    print(f"  caso {caso}, settimana, {campo}: esatto {lo:.6f}/{hi:.6f}, "
                          f"forza bruta {blo:.6f}/{bhi:.6f}")
        # saturi in % dell'energia (riferimenti, 31/10/2026): stesso metodo esatto
        blo, bhi = _forza_bruta_settimana(per_giorno, "saturi_g", 9)
        (lo, _), (hi, _) = estremi_pct_settimana(per_giorno, "saturi_g", 9)
        if abs(lo - blo) > 1e-9 or abs(hi - bhi) > 1e-9:
            differenze += 1
            if verboso:
                print(f"  caso {caso}, settimana, saturi_g: esatto {lo:.6f}/{hi:.6f}, "
                      f"forza bruta {blo:.6f}/{bhi:.6f}")
    return n_casi, differenze


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        casi, diff = autotest(verboso=True)
        print(f"combinazioni.py --autotest: {casi} casi casuali, giorno e settimana contro "
              f"la forza bruta: {diff} differenze")
        sys.exit(0 if diff == 0 else 1)
    print(__doc__)
