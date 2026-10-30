#!/usr/bin/env python3
"""
metadati_piano.py - Studio Nutrizionale Taglialatela

Controlli sui metadati del piano e sul verdetto della pipeline, condivisi da
pipeline.py e genera_zona_piano.py (tappa 2, «disciplina nel codice», 30/10/2026).

Ogni controllo traduce in codice un errore di processo gia' successo su un piano
reale: le regole erano scritte nei moduli, ma la loro applicazione dipendeva da
chi lavorava. Il motore ora si ferma da solo.

1. TERAPIA ASSENTE CONFERMATA (decisione del 30/10/2026, blocco).
   Il 28/10 la terapia di un paziente e' stata dedotta da una scheda invece di
   essere confermata. «Nessuna terapia» vale solo con la formula fissa, nel campo
   `terapia` dei metadati:
       nessuna terapia, confermato dal nutrizionista il GG/MM/AAAA (fonte: colloquio)
   con fonte = colloquio, Form A o fascicolo (piu' un dettaglio facoltativo dopo
   una virgola). Data valida e non futura. Qualsiasi altro testo ferma la pipeline.

2. ASSUNZIONI DI COMPOSIZIONE (decisione del 30/10/2026, blocco).
   Il 28/10 tre assunzioni (pranzo a casa, pesce a pranzo, sostituzione della
   verdura) sono entrate nel piano senza conferma e hanno causato il
   rifacimento dei pranzi. Campo `assunzioni`, obbligatorio per l'anteprima:
       [{"testo": "pranzo a casa nei giorni lavorativi", "stato": "confermata"}, ...]
   stato = confermata | da_confermare. Lista vuota = nessuna assunzione (scritto
   apposta). Una sola «da_confermare» blocca.

3. ALIMENTI DESIDERATI (decisione del 30/10/2026, avviso).
   Il 28/10 gli alimenti mancanti dal database sono emersi a piano finito.
   Campo `alimenti_desiderati`, obbligatorio per l'anteprima: i nomi (o i
   food_id) degli alimenti che paziente o nutrizionista vogliono nel piano, da
   fascicolo e Form B. Si confrontano col database all'apertura
   (python3 metadati_piano.py --desiderati ...); i mancanti tornano come avviso
   nel verdetto della pipeline. Lista vuota = nessuna richiesta.

4. CAMPO `drive` (30/10/2026). E' l'unico campo fuori dall'impronta: puo' contenere
   solo riferimenti a file (chiavi note, nomi di file o ID di Drive). Una frase
   scritta li' non passerebbe dall'approvazione: ferma lo script.

5. VERDETTO DELLA PIPELINE (decisione del 30/10/2026, blocco).
   L'anteprima rilasciava l'impronta anche su un piano che la pipeline dichiarava
   non presentabile. Ora pipeline.py --out-verdetto scrive il verdetto con
   l'impronta dei dati che ha valutato (piano, target, metadati: contenuto, non
   byte, perche' il passaggio da Drive puo' cambiare i fine riga); l'anteprima lo
   richiede, si ferma se i dati non coincidono, se c'e' un bloccante o se il
   collaudo e' stato saltato, e riporta le attenzioni nel testo approvato.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

VERSIONE_VERDETTO = 2   # 2 (30/10/2026): impronta del registro dei riferimenti

# ─── 1. terapia assente ────────────────────────────────────────────
FONTI_TERAPIA = ("colloquio", "form a", "fascicolo")
FORMULA_TERAPIA = ("nessuna terapia, confermato dal nutrizionista il GG/MM/AAAA "
                   "(fonte: colloquio | Form A | fascicolo)")
_RE_NESSUNA = re.compile(
    r"^nessuna terapia, confermat[oa] dal nutrizionista il "
    r"(\d{1,2})/(\d{1,2})/(\d{4}) \(fonte: (colloquio|form a|fascicolo)(?:[,;] [^()]+)?\)\.?$",
    re.IGNORECASE)


def _normalizza(t):
    t = unicodedata.normalize("NFKC", t).replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def dichiara_nessuna_terapia(terapia):
    """True se il campo `terapia` comincia come una dichiarazione di assenza
    (formula giusta o no): serve a riconoscere la contraddizione con i file."""
    return isinstance(terapia, str) and _normalizza(terapia).lower().startswith("nessun")


def valida_nessuna_terapia(terapia, oggi=None):
    """(True, testo) se `terapia` e' la formula fissa con data valida e non futura;
    altrimenti (False, motivo)."""
    if not isinstance(terapia, str) or not terapia.strip():
        return False, ("nei metadati manca il campo 'terapia' con la conferma: "
                       f"«{FORMULA_TERAPIA}»")
    t = _normalizza(terapia)
    m = _RE_NESSUNA.match(t)
    if not m:
        return False, (f"il campo 'terapia' vale «{terapia}», che non e' la conferma "
                       f"registrata. Formula: «{FORMULA_TERAPIA}»")
    g, me, a = (int(x) for x in m.group(1, 2, 3))
    try:
        data = datetime.date(a, me, g)
    except ValueError:
        return False, f"data della conferma non valida ({g}/{me}/{a})"
    if data > (oggi or datetime.date.today()):
        return False, f"data della conferma nel futuro ({data:%d/%m/%Y})"
    return True, t


# ─── 2. assunzioni ─────────────────────────────────────────────────
STATI_ASSUNZIONE = ("confermata", "da_confermare")


def leggi_assunzioni(meta):
    """(assunzioni, errore). assunzioni = lista di (testo, stato) oppure None se il
    campo manca; errore = None o la descrizione del difetto di forma."""
    if "assunzioni" not in meta:
        return None, None
    v = meta["assunzioni"]
    if not isinstance(v, list):
        return None, "'assunzioni' deve essere una lista (vuota se non ce ne sono)"
    out = []
    for i, a in enumerate(v, 1):
        if not isinstance(a, dict) or set(a) != {"testo", "stato"}:
            return None, (f"assunzione {i}: servono esattamente le chiavi 'testo' e "
                          f"'stato' ({a!r})")
        testo, stato = a["testo"], a["stato"]
        if not isinstance(testo, str) or not any(c.isalnum() for c in testo):
            return None, f"assunzione {i}: 'testo' vuoto o non testuale ({testo!r})"
        if stato not in STATI_ASSUNZIONE:
            return None, (f"assunzione {i} («{testo}»): stato «{stato}» non ammesso "
                          f"({' | '.join(STATI_ASSUNZIONE)})")
        out.append((testo.strip(), stato))
    return out, None


# ─── 3. alimenti desiderati ────────────────────────────────────────
def _token(testo):
    t = unicodedata.normalize("NFKD", testo.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return [w for w in re.split(r"[^a-z0-9]+", t) if w]


def _radice(w):
    # singolare e plurale italiani: «zucchina/zucchine», «uovo/uova», «pomodoro/i»
    return w[:-1] if len(w) > 3 and not w.isdigit() else w


PAROLE_VUOTE = {"di", "da", "del", "della", "dei", "delle", "al", "alla", "allo", "con",
                "in", "e", "il", "la", "lo", "le", "gli", "i", "a", "per", "tipo"}


def carica_nomi_database(alimenti_p=None, nomi_p=None):
    """{food_id: [nome alimenti.csv, nome paziente]}"""
    out = {}
    with open(alimenti_p or os.path.join(QUI, "alimenti.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["food_id"], []).append(r["nome"])
    p = nomi_p or os.path.join(QUI, "nomi_paziente.csv")
    if os.path.isfile(p):
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["food_id"] in out:
                    out[r["food_id"]].append(r["nome_paziente"])
    return out


def cerca_desiderato(nome, nomi_db):
    """food_id del database che corrispondono a `nome`: un food_id esatto, oppure
    le voci il cui nome contiene tutte le parole significative di `nome`
    (singolare o plurale, parola intera: «pasta» non trova «pastorizzato»).
    Lista vuota = assente dal database. Nel dubbio meglio un falso «assente»
    (si vede e si controlla) che un falso «presente» (nasconde un alimento
    mancante)."""
    nome = nome.strip()
    if nome in nomi_db:
        return [nome]
    parole = [_radice(w) for w in _token(nome) if w not in PAROLE_VUOTE]
    if not parole:
        return []
    trovati = []
    for fid, nomi in nomi_db.items():
        for n in nomi:
            voce = [_radice(w) for w in _token(n)]
            if all(p in voce for p in parole):
                trovati.append(fid)
                break
    return sorted(trovati)


def leggi_desiderati(meta):
    """(lista di nomi, errore); lista None se il campo manca."""
    if "alimenti_desiderati" not in meta:
        return None, None
    v = meta["alimenti_desiderati"]
    if not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v):
        return None, ("'alimenti_desiderati' deve essere una lista di nomi o food_id "
                      "(vuota se non ce ne sono)")
    return [x.strip() for x in v], None


def confronta_desiderati(nomi, nomi_db):
    """{nome: [food_id...]} per ogni nome richiesto."""
    return {n: cerca_desiderato(n, nomi_db) for n in nomi}


# ─── 4. campo drive ────────────────────────────────────────────────
CHIAVI_DRIVE = ("cartella_id", "piano_csv", "fascicolo", "metadati", "verdetto",
                "altri_file")
_RE_FILE = re.compile(r"^[\w\-. ()àèéìòùÀÈÉÌÒÙ']{1,120}\.[A-Za-z0-9]{1,5}$")
_RE_ID = re.compile(r"^[A-Za-z0-9_\-]{10,80}$")


def _riferimento_file(v):
    return isinstance(v, str) and (_RE_FILE.match(v.strip()) or _RE_ID.match(v.strip()))


def errore_drive(meta):
    """None se `drive` manca o contiene solo riferimenti a file; altrimenti il motivo."""
    if "drive" not in meta:
        return None
    d = meta["drive"]
    if not isinstance(d, dict):
        return "'drive' deve essere un oggetto con i riferimenti ai file"
    for k, v in d.items():
        if k not in CHIAVI_DRIVE:
            return (f"'drive' contiene la chiave «{k}»: ammesse solo "
                    f"{', '.join(CHIAVI_DRIVE)}. Un testo scritto qui resterebbe fuori "
                    f"dall'approvazione")
        valori = v if k == "altri_file" else [v]
        if k == "altri_file" and not isinstance(v, list):
            return "'drive.altri_file' deve essere una lista di nomi di file"
        for x in valori:
            if x in (None, ""):
                continue
            if not _riferimento_file(x):
                return (f"'drive.{k}' vale «{x}»: ammessi solo nomi di file con "
                        f"estensione o ID di Drive, non testo libero")
    return None


# ─── 5. impronta dei dati e verdetto ───────────────────────────────
CAMPI_FUORI_DATI = ("drive", "impronta_approvata")


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()[:16]


def impronta_piano(path):
    from scelte_multiple import carica_piano_esteso
    righe = carica_piano_esteso(path)
    return _sha([{k: r[k] for k in sorted(r)} for r in righe])


def impronta_target(path):
    from calcolatore import carica_target
    return _sha(carica_target(path))


def impronta_registro():
    """Impronta del registro dei riferimenti (riferimenti.csv), None se illeggibile:
    un registro cambiato dopo la pipeline rende il verdetto non piu' valido."""
    import riferimenti
    try:
        return riferimenti.impronta(riferimenti.carica())
    except riferimenti.ErroreRiferimenti:
        return None


def impronta_metadati(meta):
    return _sha({k: v for k, v in meta.items() if k not in CAMPI_FUORI_DATI})


def scrivi_verdetto(path, rilievi, piano_p, target_p, meta):
    v = {
        "versione": VERSIONE_VERDETTO,
        "scritto": datetime.datetime.now().isoformat(timespec="seconds"),
        "collaudo": ("saltato" if any(c == "COLLAUDO_SALTATO" for _, c, _ in rilievi.attenzioni)
                     else "superato"),
        "dati": {"piano": impronta_piano(piano_p), "target": impronta_target(target_p),
                 "metadati": impronta_metadati(meta) if meta is not None else None,
                 "riferimenti": impronta_registro()},
        "bloccanti": [list(x) for x in rilievi.bloccanti],
        "attenzioni": [list(x) for x in rilievi.attenzioni],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=1)
    return v


class VerdettoNonValido(Exception):
    pass


def controlla_verdetto(path, piano_p, target_p, meta, accetta_collaudo_saltato=False):
    """Restituisce il verdetto se vale per QUESTI dati ed e' presentabile; altrimenti
    VerdettoNonValido con il motivo. `accetta_collaudo_saltato` esiste solo per gli
    autotest (il collaudo non puo' rieseguire se stesso): la riga di comando non lo
    espone."""
    if not path:
        raise VerdettoNonValido(
            "manca --verdetto: l'anteprima si fa solo su un piano valutato. Eseguire "
            "pipeline.py ... --metadati <metadati> --out-verdetto verdetto_vN.json")
    try:
        with open(path, encoding="utf-8") as f:
            v = json.load(f)
    except (OSError, ValueError) as e:
        raise VerdettoNonValido(f"verdetto non leggibile ({path}): {e}")
    if not isinstance(v, dict) or v.get("versione") != VERSIONE_VERDETTO:
        raise VerdettoNonValido(f"{path} non e' un verdetto di pipeline.py (versione "
                                f"{VERSIONE_VERDETTO})")
    if v.get("bloccanti"):
        el = "; ".join(f"{c}" for _, c, _ in v["bloccanti"])
        raise VerdettoNonValido(f"la pipeline ha rilievi bloccanti ({el}): il piano non e' "
                                f"presentabile per l'approvazione (principio 1)")
    if v.get("collaudo") != "superato" and not accetta_collaudo_saltato:
        raise VerdettoNonValido("il verdetto e' stato prodotto con --salta-collaudo: "
                                "rieseguire la pipeline con il collaudo (principio 7)")
    d = v.get("dati") or {}
    if d.get("metadati") is None:
        raise VerdettoNonValido("verdetto prodotto senza --metadati: rieseguire la pipeline "
                                "con gli stessi metadati dell'anteprima")
    diversi = [n for n, a, b in (("piano", d.get("piano"), impronta_piano(piano_p)),
                                 ("target", d.get("target"), impronta_target(target_p)),
                                 ("metadati", d.get("metadati"), impronta_metadati(meta)),
                                 ("registro dei riferimenti", d.get("riferimenti"),
                                  impronta_registro()))
               if a != b]
    if diversi:
        raise VerdettoNonValido(f"il verdetto non riguarda questi dati ({', '.join(diversi)} "
                                f"cambiati dopo la pipeline): rieseguire la pipeline")
    return v


# ─── autotest (nel collaudo dal 30/10/2026) ────────────────────────
def autotest():
    """Restituisce (numero di prove, elenco dei fallimenti). Ogni regola con la sua
    prova al contrario: cio' che deve passare passa, cio' che deve fermarsi si ferma."""
    oggi = datetime.date(2026, 10, 30)
    prove, ko = 0, []

    def atteso(etichetta, ottenuto, voluto):
        nonlocal prove
        prove += 1
        if ottenuto != voluto:
            ko.append(f"{etichetta}: {ottenuto!r} invece di {voluto!r}")

    buone = ["nessuna terapia, confermato dal nutrizionista il 23/10/2026 (fonte: colloquio)",
             "Nessuna terapia, confermata dal nutrizionista il 1/2/2026 (fonte: Form A)",
             "nessuna terapia, confermato dal nutrizionista il 30/10/2026 (fonte: fascicolo, "
             "pagina 2).",
             "nessuna  terapia,  confermato dal nutrizionista il 23/10/2026 (fonte: colloquio)"]
    cattive = ["nessuna terapia", "nessuna terapia (Form A del 23/10/2026)", "x", "", "   ",
               None, 0, False, ["nessuna terapia"],
               "nessuna terapia, confermato dal nutrizionista il 31/10/2026 (fonte: colloquio)",
               "nessuna terapia, confermato dal nutrizionista il 30/02/2026 (fonte: colloquio)",
               "nessuna terapia, confermato dal nutrizionista il 23/10/2026 (fonte: scheda)",
               "nessuna terapia, dedotta dalla scheda il 23/10/2026 (fonte: colloquio)",
               "nessuna terapia, confermato dal nutrizionista il 23/10/2026 (fonte: colloquio) "
               "salvo metformina"]
    for t in buone:
        atteso(f"formula accettata «{t}»", valida_nessuna_terapia(t, oggi)[0], True)
    for t in cattive:
        atteso(f"formula respinta «{t}»", valida_nessuna_terapia(t, oggi)[0], False)
    atteso("dichiarazione di assenza riconosciuta", dichiara_nessuna_terapia("Nessun farmaco"), True)
    atteso("principi attivi non sono un'assenza", dichiara_nessuna_terapia("metformina 500 mg"),
           False)

    atteso("assunzioni assenti", leggi_assunzioni({}), (None, None))
    atteso("assunzioni vuote", leggi_assunzioni({"assunzioni": []}), ([], None))
    atteso("assunzione valida", leggi_assunzioni({"assunzioni": [
        {"testo": "pranzo a casa", "stato": "da_confermare"}]})[0],
        [("pranzo a casa", "da_confermare")])
    for cattiva in ("pranzo a casa", [{"testo": "x"}], [{"testo": "x", "stato": "si"}],
                    [{"testo": " ", "stato": "confermata"}],
                    [{"testo": "x", "stato": "confermata", "nota": "y"}]):
        atteso(f"assunzioni respinte {cattiva!r}",
               leggi_assunzioni({"assunzioni": cattiva})[1] is not None, True)

    nomi_db = {"000800": ["Pasta di semola cruda", "Pasta"],
               "135030": ["Latte di vacca pastorizzato scremato", "Latte scremato"],
               "349": ["Zucchine", "Zucchine"], "1800": ["Uovo di gallina intero", "Uovo"],
               "101120": ["Macinato di manzo magro", "Macinato"]}
    atteso("pasta non trova il latte pastorizzato", cerca_desiderato("pasta", nomi_db), ["000800"])
    atteso("plurale e singolare", cerca_desiderato("zucchina", nomi_db), ["349"])
    atteso("uova trova uovo", cerca_desiderato("uova", nomi_db), ["1800"])
    atteso("parole vuote ignorate", cerca_desiderato("macinato di manzo", nomi_db), ["101120"])
    atteso("food_id esatto", cerca_desiderato("349", nomi_db), ["349"])
    atteso("hamburger assente", cerca_desiderato("hamburger", nomi_db), [])
    atteso("birra assente", cerca_desiderato("birra", nomi_db), [])
    atteso("desiderati non lista", leggi_desiderati({"alimenti_desiderati": "pasta"})[1]
           is not None, True)

    for d in ({"piano_csv": "piano_v2.csv", "altri_file": ["orari_pasti.csv"]},
              {"cartella_id": "15IE06RHwtW4XwpCs1n1OFRTVpN8QGHxv", "fascicolo": "Fascicolo P01.docx"},
              {"altri_file": []}, {}):
        atteso(f"drive accettato {d!r}", errore_drive({"drive": d}), None)
    for d in ({"nota": "x.csv"}, {"fascicolo": "assume warfarin"}, "piano_v2.csv",
              {"altri_file": "orari.csv"}, {"altri_file": ["vedi nota: assume warfarin"]}):
        atteso(f"drive respinto {d!r}", errore_drive({"drive": d}) is not None, True)
    return prove, ko


# ─── riga di comando: alimenti desiderati all'apertura ─────────────
def main():
    ap = argparse.ArgumentParser(description="Alimenti desiderati contro il database "
                                             "(apertura della chat A)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--desiderati", nargs="+", metavar="NOME",
                   help="nomi o food_id, tra virgolette se di piu' parole")
    g.add_argument("--metadati", help="legge 'alimenti_desiderati' dai metadati")
    a = ap.parse_args()
    if a.metadati:
        with open(a.metadati, encoding="utf-8") as f:
            nomi, err = leggi_desiderati(json.load(f))
        if err or nomi is None:
            print(f"FERMO: {err or 'manca alimenti_desiderati nei metadati'}")
            return 1
    else:
        nomi = a.desiderati
    db = carica_nomi_database()
    esiti = confronta_desiderati(nomi, db)
    mancanti = [n for n, f in esiti.items() if not f]
    print("ALIMENTI DESIDERATI CONTRO IL DATABASE")
    for n, fids in esiti.items():
        if fids:
            voci = ", ".join(f"{x} {db[x][0]}" for x in fids[:4])
            altro = f" (+{len(fids) - 4})" if len(fids) > 4 else ""
            print(f"  [OK ] {n}: {voci}{altro}")
        else:
            print(f"  [-- ] {n}: ASSENTE dal database")
    print(f"\n{len(nomi) - len(mancanti)} presenti, {len(mancanti)} assenti."
          + (" Gli assenti si dichiarano subito al nutrizionista: si aggiungono (M6, "
             "sessione col repository) o si sostituiscono, prima di comporre."
             if mancanti else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
