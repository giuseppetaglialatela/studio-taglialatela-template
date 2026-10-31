#!/usr/bin/env python3
"""
riferimenti.py - Studio Nutrizionale Taglialatela

Registro dei riferimenti clinici per profilo (decisione del 30/10/2026: tappa 5,
registro delle fonti, con l'ossatura dei profili della tappa 7, anticipate).

PERCHE'
Le soglie cliniche vivevano nella scheda «Estrazione linee guida» e nella memoria
della chat: ogni dieta ripartiva dalla ricerca, e il 30/10/2026 i valori sui saturi
per l'ipercolesterolemia, gia' estratti il 24/10, non sono stati usati. Ora stanno
in un file che il motore legge (riferimenti.csv), con documento, posizione e frase
originale per ogni valore, e che si aggiorna quando le evidenze cambiano senza
toccare il codice.

COME FUNZIONA
- riferimenti.csv: una riga per profilo e parametro (valore_min e/o valore_max),
  oppure un'indicazione senza numero (parametro = indicazione), che si mostra e
  non si controlla.
- Il profilo lo sceglie il nutrizionista nei metadati del piano
  ("profili": ["ipercolesterolemia"], [] = solo il profilo generale): mai dedotto.
- Si controllano SOLO i parametri dei profili scelti (decisione del 31/10/2026:
  «i controlli devono scattare solo nelle apposite diete»): un piano senza profili,
  o un parametro che sta solo nel profilo «generale», non da' avvisi. Il valore del
  generale (LARN) resta il termine di confronto: il valore di un profilo lo
  sostituisce solo se e' PIU' RESTRITTIVO (regola del 24/10/2026), a parita' si cita
  il profilo; tra piu' profili vale il piu' restrittivo. Le righe con regola
  «sostituisce» (popolazioni, es. over65) sostituiscono il generale comunque.
- Parametri calcolati dal motore: verificati sulla MEDIA SETTIMANALE (principio 8),
  nella settimana reale peggiore. Gli altri: dichiarati «non verificabili».
- Avviso, mai blocco (decisione del 30/10/2026).
- Evidenze nuove: si aggiunge la riga nuova «attivo» e la vecchia diventa
  «superato» con sostituito_da; niente si cancella. Una riga «da_verificare» non
  si usa mai.

USO
  python3 riferimenti.py --profili ipercolesterolemia [altri]   (apertura chat A)
  python3 riferimenti.py --genera-pagina      (riscrive RIFERIMENTI.md)
  python3 riferimenti.py --autotest
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
FILE_REGISTRO = os.path.join(QUI, "riferimenti.csv")
FILE_PAGINA = os.path.join(QUI, "RIFERIMENTI.md")

COLONNE = ["id", "profilo", "parametro", "valore_min", "valore_max", "unita", "regola",
           "documento", "posizione", "frase", "evidenza", "popolazione", "data_verifica",
           "stato", "sostituito_da", "note"]

PROFILI = {
    "generale": "popolazione adulta sana (LARN): termine di confronto, da solo non da' avvisi",
    "over65": "65 anni e oltre (sostituisce i valori generali)",
    "ipercolesterolemia": "ipercolesterolemia / LDL elevato",
    "ipertrigliceridemia": "trigliceridi elevati",
    "ipertensione": "pressione elevata o ipertensione",
    "masld": "steatosi epatica metabolica (MASLD)",
    "diabete_t2": "diabete tipo 2",
    "obesita": "obesità",
}
NOTE_PROFILO = {
    "obesita": "linea guida SIO/ISS 2026 (Eat Weight Disord 2026;31:9) non ancora letta: "
               "nessun riferimento caricato",
}

# parametro -> (unita, descrizione, come si calcola dal motore o None)
# calcolo: ("somma", campo) = media settimanale di grammi; ("pct", campo, kcal/g)
PARAMETRI = {
    "fibra_g": ("g_die", "fibra totale", ("somma", "fibra_g")),
    "proteine_pct": ("pct_energia", "proteine", ("pct", "proteine_g", 4)),
    "carboidrati_pct": ("pct_energia", "carboidrati", ("pct", "carboidrati_g", 4)),
    "grassi_pct": ("pct_energia", "grassi totali", ("pct", "grassi_g", 9)),
    "saturi_pct": ("pct_energia", "acidi grassi saturi", None),
    "trans_pct": ("pct_energia", "acidi grassi trans", None),
    "colesterolo_mg": ("mg_die", "colesterolo alimentare", None),
    "fibra_solubile_g": ("g_die", "fibra solubile", None),
    "zuccheri_totali_pct": ("pct_energia", "zuccheri totali", None),
    "zuccheri_aggiunti_pct": ("pct_energia", "zuccheri aggiunti", None),
    "zuccheri_liberi_pct": ("pct_energia", "zuccheri liberi", None),
    "fruttosio_pct": ("pct_energia", "fruttosio", None),
    "epa_dha_mg": ("mg_die", "EPA + DHA", None),
    "sodio_mg": ("mg_die", "sodio", None),
    "potassio_mg": ("mg_die", "potassio", None),
    "alcol_g_die": ("g_die", "alcol", None),
    "alcol_g_settimana": ("g_settimana", "alcol", None),
}
UNITA_LEGGIBILE = {"g_die": "g/die", "mg_die": "mg/die", "pct_energia": "% dell'energia",
                   "g_settimana": "g/settimana"}
STATI = ("attivo", "superato", "da_verificare")
REGOLE = ("", "piu_restrittivo", "sostituisce")


class ErroreRiferimenti(ValueError):
    pass


def _num(v):
    v = (v or "").strip()
    return float(v.replace(",", ".")) if v else None


def carica(path=None):
    path = path or FILE_REGISTRO
    try:
        with open(path, newline="", encoding="utf-8") as f:
            lettore = csv.DictReader(f)
            if lettore.fieldnames != COLONNE:
                raise ErroreRiferimenti(f"{os.path.basename(path)}: colonne {lettore.fieldnames}, "
                                        f"attese {COLONNE}")
            righe = []
            for n, r in enumerate(lettore, 2):
                if None in r or any(v is None for v in r.values()):
                    raise ErroreRiferimenti(f"riga {n}: numero di campi diverso dalle colonne")
                r = {k: (v or "").strip() for k, v in r.items()}
                try:
                    r["min"], r["max"] = _num(r["valore_min"]), _num(r["valore_max"])
                except ValueError:
                    raise ErroreRiferimenti(f"riga {n} ({r['id']}): valore non numerico")
                r["_riga"] = n
                righe.append(r)
    except OSError as e:
        raise ErroreRiferimenti(f"registro non leggibile ({path}): {e}")
    return righe


def problemi(righe, oggi=None):
    """Elenco dei difetti del registro (vuoto = registro valido). Usato dal collaudo."""
    oggi = oggi or datetime.date.today()
    out, ids, attivi = [], set(), {}
    for r in righe:
        rid = r["id"] or f"riga {r['_riga']}"
        if not r["id"]:
            out.append(f"riga {r['_riga']}: id vuoto")
        elif r["id"] in ids:
            out.append(f"{rid}: id duplicato")
        ids.add(r["id"])
        if r["profilo"] not in PROFILI:
            out.append(f"{rid}: profilo «{r['profilo']}» sconosciuto")
        if r["stato"] not in STATI:
            out.append(f"{rid}: stato «{r['stato']}» non ammesso ({' | '.join(STATI)})")
        if r["regola"] not in REGOLE:
            out.append(f"{rid}: regola «{r['regola']}» non ammessa")
        if r["regola"] == "sostituisce" and r["profilo"] == "generale":
            out.append(f"{rid}: il profilo generale non puo' «sostituire» se stesso")
        ind = r["parametro"] == "indicazione"
        if not ind and r["parametro"] not in PARAMETRI:
            out.append(f"{rid}: parametro «{r['parametro']}» sconosciuto")
        elif ind:
            if r["min"] is not None or r["max"] is not None or r["unita"]:
                out.append(f"{rid}: un'indicazione non ha valori ne' unita'")
            if not r["note"]:
                out.append(f"{rid}: indicazione senza argomento nella colonna note")
        else:
            if r["min"] is None and r["max"] is None:
                out.append(f"{rid}: parametro numerico senza valore_min ne' valore_max")
            if r["min"] is not None and r["max"] is not None and r["min"] > r["max"]:
                out.append(f"{rid}: valore_min maggiore di valore_max")
            if r["unita"] != PARAMETRI[r["parametro"]][0]:
                out.append(f"{rid}: unita' «{r['unita']}», attesa "
                           f"«{PARAMETRI[r['parametro']][0]}»")
        if r["stato"] == "attivo":
            for c in ("documento", "posizione", "frase", "data_verifica"):
                if not r[c]:
                    out.append(f"{rid}: riga attiva senza «{c}» (ogni valore ha la sua fonte)")
            if r["data_verifica"]:
                try:
                    d = datetime.date.fromisoformat(r["data_verifica"])
                    if d > oggi:
                        out.append(f"{rid}: data_verifica nel futuro")
                except ValueError:
                    out.append(f"{rid}: data_verifica non in formato AAAA-MM-GG")
            if not ind and r["parametro"] in PARAMETRI:
                chiave = (r["profilo"], r["parametro"])
                if chiave in attivi:
                    out.append(f"{rid}: due righe attive per {chiave[0]} / {chiave[1]} "
                               f"({attivi[chiave]} e {rid}): una diventa «superato»")
                attivi[chiave] = rid
        if r["stato"] == "superato" and not r["sostituito_da"]:
            out.append(f"{rid}: riga superata senza sostituito_da")
        if r["stato"] != "superato" and r["sostituito_da"]:
            out.append(f"{rid}: sostituito_da compilato su una riga non superata")
    for r in righe:
        if r["sostituito_da"] and r["sostituito_da"] not in ids:
            out.append(f"{r['id']}: sostituito_da «{r['sostituito_da']}» non esiste")
    return out


def impronta(righe):
    """Impronta del contenuto del registro (12 caratteri): va nel verdetto e
    quindi nell'impronta dell'anteprima approvata."""
    dati = [{k: r[k] for k in COLONNE} for r in righe]
    return hashlib.sha256(json.dumps(dati, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()[:12]


def valida_profili(valore):
    """(lista di profili, errore)."""
    if not isinstance(valore, list) or not all(isinstance(p, str) for p in valore):
        return None, "'profili' deve essere una lista di nomi ([] = solo il profilo generale)"
    sconosciuti = [p for p in valore if p not in PROFILI]
    if sconosciuti:
        return None, (f"profili sconosciuti: {', '.join(sconosciuti)} (ammessi: "
                      f"{', '.join(PROFILI)})")
    return [p for p in valore if p != "generale"], None


def applicabili(righe, profili):
    """Limiti che valgono per il piano. Restituisce (limiti, indicazioni, avvertenze):
    limiti[parametro] = {"min": riga|None, "max": riga|None}, SOLO per i parametri
    che compaiono nei profili scelti (31/10/2026); indicazioni = righe dei profili
    scelti; avvertenze = testi (es. profilo senza riferimenti)."""
    attive = [r for r in righe if r["stato"] == "attivo"]
    limiti, indicazioni, avvertenze = {}, [], []

    def lato(r, s):
        return r["min"] if s == "min" else r["max"]

    generale = {}
    for r in attive:
        if r["profilo"] == "generale" and r["parametro"] != "indicazione":
            g = generale.setdefault(r["parametro"], {"min": None, "max": None})
            for s in ("min", "max"):
                if lato(r, s) is not None:
                    g[s] = r
    richiesti = {(r["parametro"], s) for r in attive
                 if r["profilo"] in profili and r["parametro"] != "indicazione"
                 for s in ("min", "max") if lato(r, s) is not None}
    for par, s in richiesti:
        lim = limiti.setdefault(par, {"min": None, "max": None})
        lim[s] = generale.get(par, {}).get(s)
    sostituiti = {}
    for p in profili:
        proprie = [r for r in attive if r["profilo"] == p]
        if not proprie:
            avvertenze.append(f"profilo {p}: nessun riferimento attivo nel registro"
                              + (f" ({NOTE_PROFILO[p]})" if p in NOTE_PROFILO else ""))
        for r in proprie:
            if r["parametro"] == "indicazione":
                indicazioni.append(r)
                continue
            lim = limiti.setdefault(r["parametro"], {"min": None, "max": None})
            for s in ("min", "max"):
                v = lato(r, s)
                if v is None:
                    continue
                if r["regola"] == "sostituisce":
                    chiave = (r["parametro"], s)
                    if chiave in sostituiti and sostituiti[chiave]["profilo"] != p:
                        raise ErroreRiferimenti(
                            f"{r['parametro']}: due profili scelti sostituiscono lo stesso "
                            f"valore ({sostituiti[chiave]['id']} e {r['id']})")
                    sostituiti[chiave] = r
                    lim[s] = r
                    continue
                cur = lim[s]
                if cur is None:
                    lim[s] = r
                elif cur["profilo"] == "generale" and v == lato(cur, s):
                    lim[s] = r          # a parita' si cita il profilo che chiede il controllo
                elif s == "min" and v > lato(cur, s):
                    lim[s] = r
                elif s == "max" and v < lato(cur, s):
                    lim[s] = r
    return limiti, indicazioni, avvertenze


def _settimana_somma(combos_per_giorno, campo):
    n = len(combos_per_giorno)
    idx_min = [min(range(len(g)), key=lambda j: g[j]["tot"][campo]) for g in combos_per_giorno]
    idx_max = [max(range(len(g)), key=lambda j: g[j]["tot"][campo]) for g in combos_per_giorno]
    lo = sum(g[j]["tot"][campo] for g, j in zip(combos_per_giorno, idx_min)) / n
    hi = sum(g[j]["tot"][campo] for g, j in zip(combos_per_giorno, idx_max)) / n
    return (lo, idx_min), (hi, idx_max)


def valuta(limiti, combos_per_giorno):
    """Esiti per parametro: lista di dict(parametro, lato, riga, verificabile,
    valore (media settimanale peggiore), indici (scelte per giorno), ok)."""
    import combinazioni as mod_comb
    esiti = []
    sett = None
    for par in sorted(limiti):
        calcolo = PARAMETRI[par][2]
        for s in ("min", "max"):
            r = limiti[par][s]
            if r is None:
                continue
            soglia = r["min"] if s == "min" else r["max"]
            if calcolo is None:
                esiti.append(dict(parametro=par, lato=s, riga=r, soglia=soglia,
                                  verificabile=False, valore=None, indici=None, ok=None))
                continue
            if calcolo[0] == "somma":
                (lo, ilo), (hi, ihi) = _settimana_somma(combos_per_giorno, calcolo[1])
            else:
                if sett is None:
                    sett = mod_comb.estremi_settimana(combos_per_giorno)
                if calcolo[1] not in sett["macro"]:
                    continue
                (lo, ilo), (hi, ihi) = sett["macro"][calcolo[1]]
            valore, indici = (lo, ilo) if s == "min" else (hi, ihi)
            ok = valore >= soglia - 1e-9 if s == "min" else valore <= soglia + 1e-9
            esiti.append(dict(parametro=par, lato=s, riga=r, soglia=soglia, verificabile=True,
                              valore=valore, indici=indici, ok=ok))
    return esiti


def _fmt(v):
    return f"{v:g}".replace(".", ",")


def descrivi_limite(r, s=None):
    un = UNITA_LEGGIBILE.get(r["unita"], r["unita"])
    if s == "min" or (s is None and r["min"] is not None and r["max"] is None):
        return f"≥ {_fmt(r['min'])} {un}"
    if s == "max" or (s is None and r["max"] is not None and r["min"] is None):
        return f"≤ {_fmt(r['max'])} {un}"
    return f"{_fmt(r['min'])}-{_fmt(r['max'])} {un}"


def fonte(r):
    return f"{r['documento']}, {r['posizione']} ({r['id']}, verificato il {r['data_verifica']})"


def testo_apertura(righe, profili):
    """Tabella per l'apertura della chat A: cosa vale per questi profili e da dove."""
    limiti, indicazioni, avvertenze = applicabili(righe, profili)
    L = [f"RIFERIMENTI PER I PROFILI: generale" + (" + " + ", ".join(profili) if profili else ""),
         f"Registro {impronta(righe)}", ""]
    if limiti:
        L.append("| Parametro | Limite | Verificato dal motore | Profilo | Fonte | Frase | Evidenza |")
        L.append("|---|---|---|---|---|---|---|")
    for par in sorted(limiti):
        for s in ("min", "max"):
            r = limiti[par][s]
            if r is None:
                continue
            calc = "sì" if PARAMETRI[par][2] else "NO: si dichiara come limite"
            L.append(f"| {PARAMETRI[par][1]} | {descrivi_limite(r, s)} | {calc} | {r['profilo']} "
                     f"| {r['documento']}, {r['posizione']} ({r['id']}) | {r['frase']} "
                     f"| {r['evidenza']} |")
    if not profili:
        L.insert(3, "Nessun profilo clinico scelto: nessun riferimento da verificare.")
    info = [r for r in righe if r["stato"] == "attivo" and r["profilo"] == "generale"
            and r["parametro"] != "indicazione" and r["parametro"] not in limiti]
    if info:
        L += ["", "Riferimenti generali (LARN), solo informativi: nessun avviso senza un "
                  "profilo che li richieda:"]
        L += [f"- {PARAMETRI[r['parametro']][1]} {descrivi_limite(r)} ({r['id']})" for r in info]
    if indicazioni:
        L += ["", "Indicazioni senza numero (non verificate dal motore):"]
        for r in indicazioni:
            L.append(f"- {r['note']} [{r['profilo']}]: {r['frase']} — {r['documento']}, "
                     f"{r['posizione']} ({r['id']}); popolazione: {r['popolazione']}")
    for a in avvertenze:
        L.append(f"ATTENZIONE: {a}")
    da_ver = [r for r in righe if r["stato"] == "da_verificare"
              and r["profilo"] in (["generale"] + profili)]
    for r in da_ver:
        L.append(f"NON USATO (da verificare): {r['id']} {r['profilo']} {r['parametro']} — {r['note']}")
    return "\n".join(L) + "\n"


def testo_pagina(righe):
    """RIFERIMENTI.md: tutto il registro, leggibile anche dal telefono su GitHub."""
    L = ["# Registro dei riferimenti clinici", "",
         "Generato da `riferimenti.py --genera-pagina` da `riferimenti.csv`: non si modifica "
         "a mano (il collaudo controlla che coincida). Ogni valore con documento, posizione "
         "e frase originale. Si controllano solo i parametri dei profili scelti nel piano: "
         "il profilo «generale» (LARN) da solo non dà avvisi, è il termine di confronto, e un "
         "profilo lo sostituisce solo se più restrittivo (salvo le righe «sostituisce»). "
         "Avvisi, mai blocchi.", "",
         f"Impronta del registro: `{impronta(righe)}`", ""]
    for p, descr in PROFILI.items():
        proprie = [r for r in righe if r["profilo"] == p]
        L += [f"## {p} — {descr}", ""]
        if p in NOTE_PROFILO:
            L += [NOTE_PROFILO[p], ""]
        if not proprie:
            L += ["Nessuna riga.", ""]
            continue
        for r in proprie:
            if r["parametro"] == "indicazione":
                cosa = f"**{r['note']}** (indicazione)"
            else:
                cosa = (f"**{PARAMETRI.get(r['parametro'], (0, r['parametro']))[1]}** "
                        f"{descrivi_limite(r)}")
            stato = "" if r["stato"] == "attivo" else f" — **{r['stato'].upper()}**" + (
                f" da {r['sostituito_da']}" if r["sostituito_da"] else "")
            L.append(f"- `{r['id']}` {cosa}{stato}")
            L.append(f"  - {r['documento']}, {r['posizione']}; evidenza: {r['evidenza']}; "
                     f"popolazione: {r['popolazione']}; verificato: {r['data_verifica'] or '—'}")
            if r["frase"]:
                L.append(f"  - {r['frase']}")
            if r["note"] and r["parametro"] != "indicazione":
                L.append(f"  - nota: {r['note']}")
        L.append("")
    return "\n".join(L)


# ─── autotest ──────────────────────────────────────────────────────
def autotest():
    """(prove, fallimenti): regola del piu' restrittivo, sostituzione, valutazione
    settimanale e validazione del registro, ognuna con la prova al contrario."""
    prove, ko = 0, []

    def atteso(etichetta, ottenuto, voluto):
        nonlocal prove
        prove += 1
        if ottenuto != voluto:
            ko.append(f"{etichetta}: {ottenuto!r} invece di {voluto!r}")

    def riga(i, prof, par, mn="", mx="", **kw):
        base = dict(id=i, profilo=prof, parametro=par, valore_min=mn, valore_max=mx,
                    unita=PARAMETRI[par][0] if par in PARAMETRI else "", regola="",
                    documento="Doc", posizione="p. 1", frase="«frase»", evidenza="—",
                    popolazione="—", data_verifica="2026-10-30", stato="attivo",
                    sostituito_da="", note="argomento" if par == "indicazione" else "")
        base.update(kw)
        base["min"], base["max"] = _num(base["valore_min"]), _num(base["valore_max"])
        base["_riga"] = 0
        return base

    reg = [riga("G1", "generale", "fibra_g", mn="25"),
           riga("G2", "generale", "saturi_pct", mx="10"),
           riga("G3", "generale", "sodio_mg", mx="2000"),
           riga("P1", "ipercolesterolemia", "saturi_pct", mx="7"),
           riga("P2", "ipercolesterolemia", "fibra_g", mn="20", mx="40"),
           riga("P3", "diabete_t2", "fibra_g", mn="35"),
           riga("P4", "diabete_t2", "saturi_pct", mx="10"),
           riga("O1", "over65", "sodio_mg", mx="2200", regola="sostituisce"),
           riga("X1", "ipertensione", "sodio_mg", mx="1500", stato="da_verificare"),
           riga("I1", "masld", "indicazione")]
    atteso("registro di prova valido", problemi(reg), [])
    lim, ind, avv = applicabili(reg, [])
    atteso("senza profili nessun controllo (31/10/2026)", (lim, ind), ({}, []))
    lim, _, _ = applicabili(reg, ["ipercolesterolemia"])
    atteso("parametro solo generale non controllato (sodio)", "sodio_mg" in lim, False)
    lim, _, _ = applicabili(reg, ["diabete_t2"])
    atteso("a parita' si cita il profilo (saturi 10 = 10)", lim["saturi_pct"]["max"]["id"], "P4")
    lim, _, _ = applicabili(reg, ["ipercolesterolemia"])
    atteso("profilo piu' restrittivo sostituisce (saturi 7 < 10)", lim["saturi_pct"]["max"]["id"], "P1")
    atteso("profilo meno restrittivo NON sostituisce (fibra 20 < 25)", lim["fibra_g"]["min"]["id"], "G1")
    atteso("lato nuovo del profilo si aggiunge (fibra max 40)", lim["fibra_g"]["max"]["id"], "P2")
    lim, _, _ = applicabili(reg, ["ipercolesterolemia", "diabete_t2"])
    atteso("tra due profili vale il piu' restrittivo (fibra 35)", lim["fibra_g"]["min"]["id"], "P3")
    atteso("tra due profili vale il piu' restrittivo (saturi 7)", lim["saturi_pct"]["max"]["id"], "P1")
    lim, _, _ = applicabili(reg, ["over65"])
    atteso("riga «sostituisce» vale anche se meno restrittiva", lim["sodio_mg"]["max"]["id"], "O1")
    lim, _, avv = applicabili(reg, ["ipertensione"])
    atteso("riga da_verificare non si usa", ("sodio_mg" in lim, len(avv)), (False, 1))
    _, ind, avv = applicabili(reg, ["masld", "obesita"])
    atteso("indicazioni del profilo mostrate", [r["id"] for r in ind], ["I1"])
    atteso("profilo senza righe segnalato", len(avv), 1)

    # valutazione settimanale: due giorni, il secondo con due giornate
    def c(fibra, p, cc, g):
        k = 4 * p + 4 * cc + 9 * g
        return {"tot": {"kcal_100g": k, "proteine_g": p, "carboidrati_g": cc, "grassi_g": g,
                        "fibra_g": fibra}, "scelte": ()}
    cp = [[c(30, 20, 50, 10)], [c(10, 20, 50, 10), c(40, 20, 50, 10)]]
    lim, _, _ = applicabili(reg, ["diabete_t2"])
    es = {(e["parametro"], e["lato"]): e for e in valuta(lim, cp)}
    atteso("fibra: media della settimana peggiore (30+10)/2 = 20", round(es[("fibra_g", "min")]["valore"], 6), 20.0)
    atteso("fibra 20 sotto 35: fuori", es[("fibra_g", "min")]["ok"], False)
    atteso("saturi: non verificabile oggi", es[("saturi_pct", "max")]["verificabile"], False)
    cp_ok = [[c(36, 20, 50, 10)], [c(35, 20, 50, 10), c(40, 20, 50, 10)]]
    es = {(e["parametro"], e["lato"]): e for e in valuta(lim, cp_ok)}
    atteso("prova al contrario: fibra 35,5 dentro", es[("fibra_g", "min")]["ok"], True)
    reg_m = reg + [riga("P5", "diabete_t2", "proteine_pct", mn="10", mx="20")]
    lim, _, _ = applicabili(reg_m, ["diabete_t2"])
    es = {(e["parametro"], e["lato"]): e for e in valuta(lim, [[c(30, 30, 50, 10)]])}
    p_pct = 30 * 4 / (4 * 30 + 4 * 50 + 90) * 100
    atteso("proteine in % dell'energia della settimana", round(es[("proteine_pct", "max")]["valore"], 6),
           round(p_pct, 6))
    atteso("proteine 29% oltre 20%: fuori", es[("proteine_pct", "max")]["ok"], False)

    # validazione: ogni difetto noto si ferma
    def con(i, **kw):
        r = [dict(x) for x in reg]
        r[i].update(kw)
        r[i]["min"], r[i]["max"] = _num(r[i]["valore_min"]), _num(r[i]["valore_max"])
        return problemi(r)
    for etichetta, i, kw, attesa in (
            ("riga attiva senza frase", 0, {"frase": ""}, "frase"),
            ("riga attiva senza documento", 0, {"documento": ""}, "documento"),
            ("riga attiva senza data", 0, {"data_verifica": ""}, "data_verifica"),
            ("data futura", 0, {"data_verifica": "2999-01-01"}, "futuro"),
            ("profilo sconosciuto", 0, {"profilo": "celiachia"}, "profilo"),
            ("parametro sconosciuto", 0, {"parametro": "omega9_pct"}, "parametro"),
            ("unita' sbagliata", 0, {"unita": "mg_die"}, "unita"),
            ("min > max", 4, {"valore_min": "50"}, "maggiore"),
            ("superato senza sostituto", 0, {"stato": "superato"}, "sostituito_da"),
            ("indicazione con valore", 9, {"valore_max": "3"}, "indicazione"),
            ("seconda riga attiva per lo stesso parametro", 2, {"profilo": "generale",
                                                               "parametro": "saturi_pct",
                                                               "valore_max": "9"}, "due righe")):
        trovati = con(i, **kw)
        atteso(f"validazione: {etichetta}", any(attesa in t for t in trovati), True)
    r_sup = [dict(x) for x in reg] + [riga("G9", "generale", "fibra_g", mn="30",
                                           stato="superato", sostituito_da="G1")]
    atteso("prova al contrario: riga superata con sostituto valida", problemi(r_sup), [])
    lim, _, _ = applicabili(r_sup, ["ipercolesterolemia"])
    atteso("riga superata non si usa", lim["fibra_g"]["min"]["id"], "G1")
    atteso("profili non lista respinti", valida_profili("ipercolesterolemia")[1] is not None, True)
    atteso("profilo sconosciuto respinto", valida_profili(["celiachia"])[1] is not None, True)
    atteso("profilo generale ammesso e assorbito", valida_profili(["generale"]), ([], None))
    return prove, ko


def main():
    ap = argparse.ArgumentParser(description="Registro dei riferimenti clinici per profilo")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--profili", nargs="*", metavar="PROFILO")
    g.add_argument("--genera-pagina", action="store_true")
    g.add_argument("--autotest", action="store_true")
    a = ap.parse_args()
    if a.autotest:
        n, ko = autotest()
        for k in ko:
            print(f"  KO {k}")
        print(f"riferimenti.py --autotest: {n} prove, {len(ko)} fallite")
        return 1 if ko else 0
    try:
        righe = carica()
    except ErroreRiferimenti as e:
        print(f"FERMO: {e}")
        return 1
    errori = problemi(righe)
    if errori:
        print("FERMO: registro non valido:\n  " + "\n  ".join(errori))
        return 1
    if a.genera_pagina:
        with open(FILE_PAGINA, "w", encoding="utf-8") as f:
            f.write(testo_pagina(righe))
        print(f"Scritto {FILE_PAGINA}")
        return 0
    profili, err = valida_profili(a.profili)
    if err:
        print(f"FERMO: {err}")
        return 1
    print(testo_apertura(righe, profili), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
