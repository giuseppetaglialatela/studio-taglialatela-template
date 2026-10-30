#!/usr/bin/env python3
"""
genera_zona_piano.py - Studio Nutrizionale Taglialatela

Compila la ZONA DATI del template piano alimentare v5 a partire da:
  piano.csv, alimenti.csv, nomi_paziente.csv, target.csv,
  metadati_piano_vN.json, [orari_pasti.csv]

e produce:
  - il .py del paziente (template v5 con la sola zona dati sostituita:
    il motore grafico e' copiato byte per byte dal template);
  - il PDF, eseguendo quel .py.

REGOLE (nucleo M0 e M3):
  - nessuna kcal scritta a mano: tutte vengono da calcolatore.calcola_riga;
  - nessun testo clinico inventato: intestazione, avvertenze, titoli dei
    piatti, indicazioni del giorno libero e abbinamento vengono SOLO dai
    metadati approvati in chat A. Se un campo manca lo script si ferma e
    lo nomina: la chat B non decide.
  - le lettere A, B, C... nel PDF seguono l'ordine della colonna `opzione`
    di piano.csv.

Decisioni cliniche recepite (19/09/2026):
  - box target: target kcal da target.csv, deficit = TDEE confermato -
    target, perdita attesa = deficit x 7 / 7700 kg/settimana;
  - giorno libero: colazione e spuntino = le stesse alternative dei giorni
    strutturati; pranzo e cena liberi, con le indicazioni dei metadati;
    totale = range_kcal_libero dei metadati.

Struttura a 5 posti (30/09/2026):
  - pasti ammessi e ordine da calcolatore.py (PASTI_AMMESSI, ordine_pasti);
    un pasto senza righe non compare; un valore non ammesso ferma lo script;
  - piano con spuntino2: SPUNTINO a meta' mattina, SECONDO SPUNTINO tra
    pranzo e cena; se tutti i pasti del giorno hanno un orario, vale l'orario;
  - il secondo spuntino usa la chiave emoji "spuntino" (template intatto);
  - "N pasti" nell'intestazione e' contato dai dati;
  - le kcal di un pasto a scelta diverso da colazione/spuntino entrano nel
    totale del giorno (min e max); il giorno libero riporta il secondo
    spuntino dei giorni strutturati.

USO
  python3 genera_zona_piano.py --piano piano_vN.csv --target target.csv
      --metadati metadati_piano_vN.json --template TEMPLATE_..._v5.py
      --out-py CognomeNome_piano_vN.py --out-pdf CognomeNome_piano_vN.pdf
      [--orari orari_pasti.csv] [--mese "Settembre 2026"]

  python3 genera_zona_piano.py --anteprima --piano piano_vN.csv --target target.csv
      --metadati metadati_piano_vN.json [--orari ...] [--out-anteprima anteprima.md]
      (PASSO 6: anteprima completa e impronta; senza template e senza PDF)

  python3 genera_zona_piano.py --verifica-impronta --piano ... --target ... --metadati ...
      (prima del documento di spiegazione: solo il controllo dell'impronta)

  python3 genera_zona_piano.py --autotest --template TEMPLATE_..._v5.py

IMPRONTA (23/10/2026): la generazione del PDF si ferma se i metadati non hanno
'impronta_approvata' o se non coincide con l'impronta dell'anteprima di oggi
(piano, testi o valori cambiati dopo l'approvazione). Fuori dall'impronta solo
'drive' e il mese.
"""
import argparse, csv, datetime, json, os, re, subprocess, sys, tempfile, unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from calcolatore import (entro_tolleranza, carica_alimenti, carica_eccezioni_etichetta, carica_target, calcola_riga,
                         PASTI_AMMESSI, ordine_pasti, pasti_non_ammessi)
from scelte_multiple import carica_piano_esteso
import combinazioni as mod_comb
import metadati_piano as mod_meta

KCAL_PER_KG = 7700          # convenzione clinica decisa il 19/09/2026
# Struttura a 5 posti (30/09/2026): elenco e ordine da calcolatore.py.
# Un pasto senza righe in piano.csv non compare nel PDF.
ETICHETTE = {"colazione": "COLAZIONE", "pranzo": "PRANZO",
             "spuntino": "SPUNTINO", "spuntino2": "SECONDO SPUNTINO",
             "cena": "CENA"}
# Il template v5 ammette 4 chiavi emoji: il secondo spuntino usa l'icona
# dello spuntino. Il motore grafico non si tocca.
CHIAVE_EMOJI = {"spuntino2": "spuntino"}
NOMI_GIORNO = {"lun": "Lunedì", "mar": "Martedì", "mer": "Mercoledì",
               "gio": "Giovedì", "ven": "Venerdì", "sab": "Sabato",
               "dom": "Domenica"}
MESI = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

MARCA_INIZIO = "import os, sys, base64, tempfile\n"
MARCA_FINE = ("# ═══════════════════════════════════════════════════════════════════\n"
              "#  ═══ MOTORE GRAFICO")


class Fermo(Exception):
    """Dato mancante o incoerente: ci si ferma e lo si nomina."""


# ─── formattazione ────────────────────────────────────────────────
def _migliaia(n):
    return f"{int(n):,}".replace(",", ".")


def _kcal(v):
    return f"~{_migliaia(round(v / 10) * 10)} kcal"


def _grammi(g):
    return f"{g:g}".replace(".", ",")


# ─── lettura ──────────────────────────────────────────────────────
def carica_nomi(path):
    nomi = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nomi[r["food_id"].strip()] = (r["nome_paziente"].strip(),
                                          (r.get("nota_peso") or "").strip())
    return nomi


def carica_orari(path):
    if not path:
        return {}
    orari = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            orari[(r["giorno"].strip(), r["pasto"].strip())] = r["orario"].strip()
    return orari


def _campo(meta, chiave):
    if chiave not in meta or meta[chiave] in (None, "", [], {}):
        raise Fermo(f"metadati: manca il campo '{chiave}' (va scritto in chat A)")
    return meta[chiave]


# Testi che finiscono nel PDF del paziente: devono essere testo vero. «non
# concordato» e' ammesso negli altri metadati (M2), qui no; lo stesso vale per
# ogni altro segnaposto («da concordare», «N/D», «—», «?»...), per un campo di
# soli spazi e per un valore che non e' testo. Prima la regola viveva solo nel
# testo di M2 e lo script stampava «Obiettivo: non concordato» (22/10/2026).
# Il controllo riguarda il campo INTERO: una frase che contiene le stesse
# parole («obiettivo non concordato con il cardiologo») passa.
CAMPI_PAZIENTE = ("obiettivo_intestazione", "criterio_rivalutazione", "avvertenze_box")
# il campo INTERO coincide con un segnaposto (dopo la normalizzazione)
_SEGNAPOSTO = re.compile(
    r"non (ancora )?((e|è|e') )?(stat[oa] )?concordat[oaie]( ancora)?|nonconcordat[oaie]"
    r"|da (concordar(e|si)|definir(e|si)|stabilir(e|si)|decider(e|si)|compilare"
    r"|valutare|inserire|completare)"
    r"|non (ancora )?(definit[oaie]|applicabil[ei]|disponibil[ei]|indicat[oaie])"
    r"|in attesa"
    r"|n ?/ ?[da]|tbd|tba|tbc|to ?do|null|none|nil|undefined"
    # segnaposto numerici del template («XX kg», «XX anni»): solo da soli o con
    # un'unita', perche' «XX settimana» o «46,XX» sono testi clinici veri
    r"|x+ (kg|anni|mesi|g|kcal|cm)|x{2,}")
# «n.d.» e «n.a.» solo in minuscolo: «N.D.» puo' essere un paio di iniziali
_SIGLA_MINUSCOLA = re.compile(r"n\. ?[da]\.?")
# testi di esempio della zona dati del template v5 (errore di copia e incolla)
_TESTI_TEMPLATE = re.compile(
    r"nome cognome|descrizione (della )?condizione clinica"
    r"|da rivalutare dopo [nx] sett(imane)?"
    r"|indicare qui allergie( accertate( e qualsiasi esclusione obbligatoria)?)?"
    r"|titolo approvato")  # «titolo approvato»: valore d'esempio dello schema in M2
_INVISIBILI = dict.fromkeys(map(ord, "\u00ad\u200b\u200c\u200d\u2060\ufeff"))
_INVISIBILI.update({0x2019: "'", 0x2018: "'"})  # apostrofo tipografico
_BORDI = " ,;:!?…'\"«»()[]{}*~#•.-–—−‐‒―/\\_"


def _testo_paziente(valore, dove):
    """Un testo che finisce nel PDF del paziente deve essere testo vero.

    Si ferma (Fermo, mai crash) se il valore non e' una stringa, se e' vuoto o
    fatto solo di spazi e simboli, se coincide con un testo di esempio del
    template («Nome Cognome», «XX kg») o con un segnaposto
    (_SEGNAPOSTO, sul campo intero). Sigle e nomi brevi («NA», «Nan», «N.D.»)
    passano: sono ammessi come iniziali, nomi o sigle cliniche.
    """
    if not isinstance(valore, str):
        raise Fermo(f"metadati: '{dove}' finisce nel PDF del paziente e deve essere "
                    f"un testo, non {type(valore).__name__} ({valore!r})")
    grezzo = unicodedata.normalize("NFKC", valore).translate(_INVISIBILI).strip()
    norm = re.sub(r"\s+", " ", grezzo.lower()).strip(_BORDI).strip()
    piatto = re.sub(r"[\s.\-–—−‐‒―_]+", " ", norm).strip()
    if (not any(c.isalnum() for c in norm)
            or _TESTI_TEMPLATE.fullmatch(piatto)
            or _SEGNAPOSTO.fullmatch(piatto)
            or _SIGLA_MINUSCOLA.fullmatch(grezzo.strip(" ,;:!?()[]{}«»\"'"))):
        raise Fermo(f"metadati: '{dove}' vale «{valore}», ma finisce nel PDF del "
                    f"paziente: serve il testo vero, da chiedere al PASSO 6 e "
                    f"scrivere in chat A (M2)")
    return valore


_VERSIONE = re.compile(r"\s*(?:v|versione)?\s*\.?\s*([0-9]+(?:\.[0-9]+)*[a-z]?)\s*\.?\s*",
                       re.IGNORECASE)


def _versione(meta):
    """Numero di versione per le note dell'intestazione del PDF.

    Facoltativa (lo script non si ferma se manca). Se c'e', il formato e' fisso:
    un intero, oppure un numero con o senza «v»/«versione» davanti («v3», «3»,
    «versione 2», «v1.0», «2b»). Qualunque altra forma ferma lo script: meglio
    di qualunque pulizia, che su forme impreviste stampava testo spezzato
    («versione 2» usciva «ersione 2»).
    """
    v = meta.get("versione_piano", "")
    if v == "":
        return ""
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    m = _VERSIONE.fullmatch(v) if isinstance(v, str) else None
    if not m:
        raise Fermo(f"metadati: 'versione_piano' vale «{v}»: formato atteso «v3», "
                    f"«3» o «versione 3»")
    return m.group(1)


def _oggetto(meta, chiave):
    valore = _campo(meta, chiave)
    if not isinstance(valore, dict):
        raise Fermo(f"metadati: '{chiave}' deve essere un oggetto con le sue voci, "
                    f"non {type(valore).__name__} ({valore!r})")
    return valore


def _campo_paziente(meta, chiave):
    return _testo_paziente(_campo(meta, chiave), chiave)


# ─── costruzione dei pasti ────────────────────────────────────────
def _dettaglio(righe, nomi):
    parti = []
    for r in righe:
        if r["food_id"] not in nomi:
            raise Fermo(f"food_id {r['food_id']} senza nome in nomi_paziente.csv")
        nome, nota = nomi[r["food_id"]]
        parti.append(f"{nome} {_grammi(r['grammi'])} g" + (f" ({nota})" if nota else ""))
    return " · ".join(parti)


def _kcal_righe(righe, db):
    tot = 0.0
    for r in righe:
        if r["food_id"] not in db:
            raise Fermo(f"food_id {r['food_id']} assente da alimenti.csv")
        tot += calcola_riga(db[r["food_id"]], r["grammi"])["kcal_100g"]
    return tot


def _titolo(titoli, giorno, pasto, opzione):
    for k in (f"{giorno}|{pasto}|{opzione}", f"*|{pasto}|{opzione}"):
        if k in titoli:
            return _testo_paziente(titoli[k], f"titoli_piatti[{k}]")
    raise Fermo(f"metadati: manca il titolo del piatto '{giorno}|{pasto}|{opzione}'")


def costruisci_pasto(giorno, pasto, righe, db, nomi, titoli):
    """Restituisce (tipo, dati, kcal_possibili, lettere) dove tipo e'
    'fisso' o 'alternative'."""
    gruppi = {r["gruppo_scelta"] for r in righe if r["gruppo_scelta"]}
    fisse = [r for r in righe if not r["gruppo_scelta"]]
    if not gruppi:
        k = _kcal_righe(righe, db)
        return ("fisso", (_titolo(titoli, giorno, pasto, ""), _dettaglio(righe, nomi),
                          _kcal(k)), [k], {})
    if len(gruppi) > 1 or fisse:
        raise Fermo(f"giorno {giorno}, {pasto}: alimenti fissi insieme ad alternative, "
                    "o piu' gruppi di scelta nello stesso pasto: formato non gestito "
                    "dal template, serve una decisione prima di generare")
    opzioni = sorted({r["opzione"] for r in righe})
    alt, kcal, lettere = [], [], {}
    for i, op in enumerate(opzioni):
        rr = [r for r in righe if r["opzione"] == op]
        k = _kcal_righe(rr, db)
        lettere[op] = "ABCDEFGH"[i]
        alt.append([_titolo(titoli, giorno, pasto, op), _dettaglio(rr, nomi), _kcal(k), None])
        kcal.append((op, k))
    return ("alternative", alt, kcal, lettere)


def _abbinamenti(meta):
    ab = meta.get("abbinamento_spuntino", "non concordato")
    if ab == "non concordato":
        return None
    if not isinstance(ab, dict):
        raise Fermo("metadati: 'abbinamento_spuntino' deve essere un oggetto "
                    "{opzione_colazione: opzione_spuntino} oppure \"non concordato\"")
    return {c: (s if isinstance(s, list) else [s]) for c, s in ab.items()}


def _ordina_pasti_giorno(pasti, ordine, orari, giorno):
    """Ordine dei pasti di un giorno. Se TUTTI i pasti del giorno hanno un
    orario, vale l'orario (uno spuntino alle 22:30 va dopo la cena);
    altrimenti l'ordine fisso del piano (decisione del 30/09/2026)."""
    fisso = sorted(pasti, key=lambda p: ordine[p])
    if pasti and all((giorno, p) in orari for p in pasti):
        def minuti(p):
            try:
                h, m = orari[(giorno, p)].split(":")
                return int(h) * 60 + int(m)
            except ValueError:
                raise Fermo(f"orari_pasti.csv: orario non valido per giorno "
                            f"{giorno}, {p}: '{orari[(giorno, p)]}' (atteso HH:MM)")
        return sorted(fisso, key=minuti)
    return fisso


def _range_giorno(kc_col, kc_spu, fissi, abbin):
    """Kcal min e max del giorno sulle combinazioni ammesse."""
    combos = []
    col = kc_col or [(None, 0.0)]
    spu = kc_spu or [(None, 0.0)]
    for oc, kc in col:
        for os_, ks in spu:
            if abbin and oc is not None and os_ is not None and os_ not in abbin.get(oc, []):
                continue
            combos.append(kc + ks)
    if not combos:
        raise Fermo("abbinamento_spuntino esclude tutte le combinazioni del giorno")
    return min(combos) + fissi, max(combos) + fissi


# ─── costruzione della zona dati ──────────────────────────────────
def costruisci_dati(piano, db, nomi, target, meta, orari, mese):
    giorni_meta = _oggetto(meta, "giorni")
    lavorativi = _campo(giorni_meta, "lavorativi") if isinstance(giorni_meta, dict) else None
    libero = giorni_meta.get("libero")
    titoli = _oggetto(meta, "titoli_piatti")
    inte = _oggetto(meta, "intestazione")
    for k in ("nome", "eta", "condizione"):
        _testo_paziente(_campo(inte, k), f"intestazione.{k}")
    tdee = float(_campo(meta, "tdee_confermato_kcal"))
    kcal_target = float(target["kcal_target"])
    abbin = _abbinamenti(meta)

    num_giorni = sorted({r["giorno"] for r in piano}, key=int)
    if len(num_giorni) != len(lavorativi):
        raise Fermo(f"piano.csv ha {len(num_giorni)} giorni, i metadati ne dichiarano "
                    f"{len(lavorativi)} lavorativi")
    non_ammessi = pasti_non_ammessi(piano)
    if non_ammessi:
        raise Fermo("piano.csv: valori di pasto non ammessi ("
                    + ", ".join(f"giorno {g} '{p}'" for g, p in non_ammessi)
                    + f"); ammessi: {' | '.join(PASTI_AMMESSI)}")
    ordine = ordine_pasti(r["pasto"] for r in piano)
    # numero di pasti contato dai dati, non scritto fisso (30/09/2026)
    n_pasti = len({r["pasto"] for r in piano})

    giorni_out, alt_col, alt_spu = [], None, None
    altri_lib = {}   # pasti oltre i 4 storici da riportare nel giorno libero
    for g, sigla in zip(num_giorni, lavorativi):
        righe_g = [r for r in piano if r["giorno"] == g]
        pasti_out, kc_col, kc_spu, fissi = [], None, None, 0.0
        extra_lo = extra_hi = 0.0   # altri pasti a scelta: scelta indipendente
        for pasto in _ordina_pasti_giorno({r["pasto"] for r in righe_g}, ordine, orari, g):
            rr = [r for r in righe_g if r["pasto"] == pasto]
            tipo, dati, kc, lettere = costruisci_pasto(g, pasto, rr, db, nomi, titoli)
            label = ETICHETTE[pasto] + (f" — ore {orari[(g, pasto)]}" if (g, pasto) in orari else "")
            if tipo == "fisso":
                fissi += kc[0]
                pasti_out.append((pasto, label, dati[0], dati[1], dati[2], None))
                if pasto == "spuntino2":
                    altri_lib.setdefault(pasto, (pasto, ETICHETTE[pasto], dati[0],
                                                 dati[1], dati[2], None))
            else:
                if pasto == "colazione":
                    kc_col = kc
                    if abbin:
                        for op, alt in zip([o for o, _ in kc], dati):
                            if op not in abbin:
                                raise Fermo(f"abbinamento_spuntino: manca la colazione {op}")
                            lett_spu = abbin[op]
                            alt[3] = ("da abbinare allo spuntino "
                                      + " o ".join(lett_spu))  # lettere risolte sotto
                    alt_col = alt_col or dati
                elif pasto == "spuntino":
                    kc_spu = kc
                    alt_spu = alt_spu or dati
                else:
                    # Pasto a scelta diverso da colazione e spuntino (es. secondo
                    # spuntino): entra nel totale con la sua alternativa minima e
                    # massima. Prima del 30/09/2026 queste kcal restavano FUORI
                    # dal totale del giorno.
                    extra_lo += min(k for _, k in kc)
                    extra_hi += max(k for _, k in kc)
                    if pasto == "spuntino2":
                        altri_lib.setdefault(pasto, (pasto, ETICHETTE[pasto], dati,
                                                     None, None, None))
                pasti_out.append((pasto, label, dati, None, None, None, lettere))
        lo, hi = _range_giorno(kc_col, kc_spu, fissi, abbin)
        lo, hi = lo + extra_lo, hi + extra_hi
        altre_scelte = any(len(p) == 7 and p[0] not in ("colazione", "spuntino")
                           for p in pasti_out)
        motivo = ("secondo le alternative scelte" if altre_scelte
                  else "secondo la colazione e lo spuntino scelti")
        tot = (f"Totale giornata: {_kcal(lo)}" if round(lo / 10) == round(hi / 10) else
               f"Totale giornata: ~{_migliaia(round(lo/10)*10)}–{_migliaia(round(hi/10)*10)} kcal "
               + motivo)
        # giornate realmente componibili (tappa 1, 29/10/2026): solo per
        # l'anteprima; la zona dati del PDF non le legge
        try:
            combos = mod_comb.combinazioni_giorno(righe_g, db, abbin)
        except mod_comb.ErroreCombinazioni as e:
            raise Fermo(str(e))
        giorni_out.append({"num": g, "nome": NOMI_GIORNO.get(sigla, sigla),
                           "pasti": pasti_out, "totale": tot, "_combos": combos,
                           "_target": target})

    # lettere dell'abbinamento: da opzione di piano.csv a lettera del PDF
    if abbin and alt_spu is not None:
        lett_spu = next(p[6] for gg in giorni_out for p in gg["pasti"]
                        if p[0] == "spuntino" and len(p) == 7)
        for gg in giorni_out:
            for p in gg["pasti"]:
                if p[0] == "colazione" and len(p) == 7:
                    for alt in p[2]:
                        if alt[3]:
                            ops = alt[3].replace("da abbinare allo spuntino ", "").split(" o ")
                            if any(o not in lett_spu for o in ops):
                                raise Fermo(f"abbinamento_spuntino: spuntino {ops} inesistente")
                            alt[3] = "da abbinare allo spuntino " + " o ".join(lett_spu[o] for o in ops)

    # giorno libero
    if libero:
        ind = _oggetto(meta, "indicazioni_giorno_libero")
        rng = _campo(giorni_meta, "range_kcal_libero")
        if alt_col is None or alt_spu is None:
            raise Fermo("giorno libero: servono colazione e spuntino a scelta nei giorni "
                        "strutturati (decisione del 19/09/2026)")
        per_pasto_lib = {
            "colazione": ("colazione", "COLAZIONE", alt_col, None, None, None),
            "pranzo": ("pranzo", "PRANZO", "Pasto libero", _testo_paziente(_campo(ind, "pranzo"), "indicazioni_giorno_libero.pranzo"), None, None),
            "spuntino": ("spuntino", "SPUNTINO", alt_spu, None, None, None),
            "cena": ("cena", "CENA", "Pasto libero", _testo_paziente(_campo(ind, "cena"), "indicazioni_giorno_libero.cena"), None, None),
        }
        # secondo spuntino: come lo spuntino, lo stesso dei giorni strutturati
        per_pasto_lib.update(altri_lib)
        pasti_lib = [per_pasto_lib[p] for p in sorted(per_pasto_lib, key=lambda p: ordine[p])]
        giorni_out.append({"num": str(len(giorni_out) + 1),
                           "nome": f"{NOMI_GIORNO.get(libero, libero)} — Giorno libero",
                           "libero": True, "pasti": pasti_lib,
                           "totale": f"Totale giornata indicativo: ~{_migliaia(rng[0])}–"
                                     f"{_migliaia(rng[1])} kcal"})

    # box target
    deficit = tdee - kcal_target
    if deficit > 0:
        perdita = f"{deficit * 7 / KCAL_PER_KG:.1f}".replace(".", ",")
        box_t = (f"⭐  Target: ~{_migliaia(kcal_target)} kcal/die  ·  deficit "
                 f"~{_migliaia(round(deficit / 10) * 10)} kcal  ·  perdita attesa "
                 f"{perdita} kg/sett")
    else:
        box_t = (f"⭐  Target: ~{_migliaia(kcal_target)} kcal/die  ·  "
                 f"{'surplus' if deficit < 0 else 'bilancio'} "
                 f"~{_migliaia(round(abs(deficit) / 10) * 10)} kcal rispetto al fabbisogno")

    n_strut = len(num_giorni)
    note = (f"Struttura su {n_strut + (1 if libero else 0)} giorni"
            + (f" ({n_strut} + 1 libero)" if libero else "")
            + f" · {n_pasti} pasti · versione {_versione(meta)}")
    paziente = {"nome": inte["nome"], "eta": inte["eta"], "condizione": inte["condizione"],
                "obiettivo": _campo_paziente(meta, "obiettivo_intestazione"), "note_piano": note,
                "mese": mese, "rivalutare": _campo_paziente(meta, "criterio_rivalutazione")}
    box = {"target": box_t, "allergie": "🚫  " + _campo_paziente(meta, "avvertenze_box")}
    return paziente, box, alt_col, alt_spu, giorni_out


# ─── scrittura del .py ────────────────────────────────────────────
def _alt_src(alt):
    return "[\n" + "".join(f"    {tuple(a)!r},\n" for a in alt) + "]"


def zona_dati_src(paziente, box, alt_col, alt_spu, giorni):
    out = ["\n# ═════════════════════════════════════════════════════════════════\n",
           "#  ▶▶▶  ZONA DATI — generata da genera_zona_piano.py, non a mano   ◀◀◀\n",
           "#  Kcal da calcolatore.calcola_riga; testi dai metadati approvati.\n",
           "# ════════════════════════════════════════════════════════════════════\n\n",
           f"PAZIENTE = {paziente!r}\n\n", f"BOX_INFO = {box!r}\n\n",
           f"COLAZIONI = {_alt_src(alt_col) if alt_col else '[]'}\n\n",
           f"SPUNTINI = {_alt_src(alt_spu) if alt_spu else '[]'}\n\n", "GIORNI = [\n"]
    for g in giorni:
        out.append(f"    {{\n        'num': {g['num']!r}, 'nome': {g['nome']!r},\n")
        if g.get("libero"):
            out.append("        'libero': True,\n")
        out.append("        'pasti': [\n")
        for p in g["pasti"]:
            pasto, label, nome, det, kcal, nota = p[:6]
            ek = CHIAVE_EMOJI.get(pasto, pasto)
            if isinstance(nome, list):
                ref = ("COLAZIONI" if nome is alt_col or nome == alt_col else
                       "SPUNTINI" if nome is alt_spu or nome == alt_spu else _alt_src(nome))
                out.append(f"            ({ek!r}, {label!r}, {ref}, None, None, {nota!r}),\n")
            else:
                out.append(f"            ({ek!r}, {label!r}, {nome!r}, {det!r}, {kcal!r}, {nota!r}),\n")
        out.append(f"        ],\n        'totale': {g['totale']!r},\n    }},\n")
    out.append("]\n\n")
    return "".join(out)


def componi_py(template_src, zona):
    if template_src.count(MARCA_INIZIO) != 1 or template_src.count(MARCA_FINE) != 1:
        raise Fermo("template non riconosciuto: marcatori della zona dati non trovati")
    i = template_src.index(MARCA_INIZIO) + len(MARCA_INIZIO)
    j = template_src.index(MARCA_FINE)
    return template_src[:i] + zona + template_src[j:]


# ─── anteprima per il PASSO 6 e impronta dell'approvazione ────────
# Primo piano reale (23/10/2026): la tabella del PASSO 6 non aveva tutte le
# grammature, e testi del giorno libero e una regola operativa sono finiti nei
# metadati senza passare dall'approvazione. L'anteprima e' scritta dallo stesso
# codice che compila il PDF: si presenta INTERA al PASSO 6, e la sua impronta,
# scritta nei metadati dopo l'approvazione, ferma la chat B se piano, testi o
# valori sono cambiati da allora. Un controllo, non una garanzia: chi scrive i
# metadati puo' sempre rigenerare l'impronta; impedisce la svista, non il dolo.
CAMPI_FUORI_IMPRONTA = ("drive", "impronta_approvata")
CAMPI_GIA_IN_ANTEPRIMA = ("versione_piano", "giorni", "tdee_confermato_kcal", "intestazione",
                          "avvertenze_box", "indicazioni_giorno_libero", "titoli_piatti",
                          "obiettivo_intestazione", "criterio_rivalutazione",
                          "assunzioni", "alimenti_desiderati", "profili")


ETICHETTE_CAMPI = {
    "regole_operative": "Regole operative (documento di spiegazione)",
    "scelte_principali": "Scelte principali (documento di spiegazione)",
    "limiti_noti": "Limiti noti (documento di spiegazione)",
    "da_escludere": "Da escludere dal documento di spiegazione",
    "terapia": "Terapia (sezione 2 del documento di spiegazione)",
    "abbinamento_spuntino": "Abbinamento colazione → spuntino (opzioni di piano.csv)",
    "livello_colazione": "Livello colazione",
    "differenze_da_versione_precedente": "Differenze dalla versione precedente",
}


def _md_valore(v):
    if isinstance(v, str):
        return v
    # sort_keys: l'impronta non deve cambiare se uno strumento riordina le chiavi
    return json.dumps(v, ensure_ascii=False, sort_keys=True)


def _md_alternative(alt, rientro="  "):
    righe = []
    for i, (titolo, det, kcal, nota) in enumerate(alt):
        righe.append(f"{rientro}- **{'ABCDEFGH'[i]}** {titolo}: {det} ({kcal})"
                     + (f" — {nota}" if nota else ""))
    return righe


def _md_campo(L, nome, v, vuoto="(nessuna voce)"):
    if isinstance(v, list) and v:
        L.append(f"- **{nome}:**")
        L.extend(f"  - {_md_valore(x)}" for x in v)
    elif isinstance(v, dict) and v:
        L.append(f"- **{nome}:**")
        L.extend(f"  - {kk}: {_md_valore(v[kk])}" for kk in sorted(v))
    elif v in (None, "", [], {}):
        L.append(f"- **{nome}:** {vuoto}")
    else:
        L.append(f"- **{nome}:** {_md_valore(v)}")


# campi del documento di spiegazione: si mostrano sempre, anche vuoti, perche'
# il nutrizionista veda anche un'assenza (revisione del 23/10/2026)
CAMPI_SPIEGAZIONE = ("regole_operative", "scelte_principali", "limiti_noti", "da_escludere",
                     "terapia")


def _alternative_comuni(giorni):
    """Pasti a scelta con le stesse alternative in tutti i giorni strutturati
    che li hanno: si scrivono una volta in testa invece che in ogni giorno."""
    strutturati = [g for g in giorni if not g.get("libero")]
    per_pasto = {}
    for g in strutturati:
        for p in g["pasti"]:
            if isinstance(p[2], list):
                per_pasto.setdefault(p[0], []).append(p[2])
    comuni = {}
    for pasto, liste in per_pasto.items():
        # in TUTTI i giorni strutturati, sempre a scelta e con le stesse alternative
        # (secondo giro di revisione, 23/10/2026: un pranzo a scelta un solo giorno
        # finiva in testa come «uguale in tutti i giorni»)
        if len(liste) == len(strutturati) and all(x == liste[0] for x in liste):
            comuni[pasto] = liste[0]
    return comuni


def testo_anteprima(dati, meta, verdetto=None):
    """Tutto cio' che il nutrizionista approva al PASSO 6: i testi del PDF parola
    per parola, i campi da cui la chat B scrive il documento di spiegazione, gli
    altri campi dei metadati e il piano per esteso con le grammature. Restano
    fuori il mese e i riferimenti di Drive: non sono contenuto approvato."""
    paz, box, alt_col, alt_spu, giorni = dati
    L = ["## Testi del PDF (parola per parola)", "",
         f"- **Intestazione:** {paz['nome']} · {paz['eta']} · {paz['condizione']}",
         f"- **Obiettivo:** {paz['obiettivo']}",
         f"- **Criterio di rivalutazione:** {paz['rivalutare']}",
         f"- **Note del piano:** {paz['note_piano']}",
         f"- **Box target:** {box['target']}",
         f"- **Avvertenze:** {box['allergie']}"]
    ind = meta.get("indicazioni_giorno_libero")
    if isinstance(ind, dict):
        for k in sorted(ind, key=lambda k: (k != "pranzo", k != "cena", k)):
            L.append(f"- **Giorno libero, {k}:** {_md_valore(ind[k])}")
    L += ["", "## Contenuti del documento di spiegazione",
          "(la chat B scrive la prosa da questi campi e dai dati di piano e fascicolo, "
          "senza deduzioni cliniche; il testo si approva prima della consegna, M3)", ""]
    for k in CAMPI_SPIEGAZIONE:
        _md_campo(L, ETICHETTE_CAMPI[k].replace(" (documento di spiegazione)", ""), meta.get(k))
    # assunzioni e alimenti desiderati (30/10/2026): si approvano qui, per esteso
    L += ["", "## Assunzioni di composizione e alimenti desiderati", ""]
    ass, _ = mod_meta.leggi_assunzioni(meta)
    if ass:
        for t, st in ass:
            L.append(f"- **Assunzione:** {t} ({st.replace('_', ' ')})")
    else:
        L.append("- **Assunzioni:** nessuna")
    des, _ = mod_meta.leggi_desiderati(meta)
    L.append("- **Alimenti desiderati:** " + (", ".join(des) if des else "nessuno"))
    prof = meta.get("profili")
    L.append("- **Profili clinici (riferimenti):** generale"
             + (" + " + ", ".join(p for p in prof if p != "generale") if prof else ""))
    L += ["", "## Altri campi dei metadati (non stampati per il paziente)", "",
          f"- **TDEE confermato:** {_md_valore(meta.get('tdee_confermato_kcal'))} kcal"]
    inte = meta.get("intestazione")
    if isinstance(inte, dict):
        extra = {k: v for k, v in inte.items() if k not in ("nome", "eta", "condizione")}
        if extra:
            _md_campo(L, "Intestazione, altri campi", extra)
    _md_campo(L, "Giorni", meta.get("giorni"))
    usati = set(CAMPI_FUORI_IMPRONTA) | set(CAMPI_GIA_IN_ANTEPRIMA) | set(CAMPI_SPIEGAZIONE)
    for k in sorted(set(meta) - usati):
        _md_campo(L, ETICHETTE_CAMPI.get(k, k), meta[k], vuoto="(vuoto)")
    L += ["", "## Piano per esteso"]
    comuni = _alternative_comuni(giorni)
    for pasto in sorted(comuni, key=lambda p: list(ETICHETTE).index(p) if p in ETICHETTE else 9):
        L += ["", f"**{ETICHETTE.get(pasto, pasto).capitalize()}** — alternative uguali "
                  f"in tutti i giorni"]
        L += _md_alternative(comuni[pasto], "")
    for g in giorni:
        L += ["", f"### Giorno {g['num']} — {g['nome']}"]
        for p in g["pasti"]:
            pasto, label, nome, det, kcal = p[:5]
            if isinstance(nome, list):
                if comuni.get(pasto) == nome:
                    L.append(f"- **{label}:** alternative come sopra")
                else:
                    L.append(f"- **{label}:**")
                    L += _md_alternative(nome)
            elif g.get("libero") and not kcal:
                L.append(f"- **{label}:** {nome} — {det}")
            else:
                L.append(f"- **{label}** {nome}: {det} ({kcal})")
        L.append(f"- {g['totale']}")
        L += _md_macro_giorno(g)
    L += _md_macro_settimana(giorni)
    if verdetto is not None:
        # verdetto della pipeline (30/10/2026): le attenzioni si approvano insieme al
        # piano e fanno parte dell'impronta; con un bloccante l'anteprima non esiste
        att = [a for a in verdetto.get("attenzioni", []) if a[1] != "COLLAUDO_SALTATO"]
        L += ["", "## Verdetto della pipeline (approvato insieme al piano)", "",
              f"- **Collaudo:** {verdetto.get('collaudo')}; **bloccanti:** nessuno; "
              f"**da dichiarare:** {len(att)}; **registro dei riferimenti:** "
              f"{(verdetto.get('dati') or {}).get('riferimenti')}"]
        for passo, codice, msg in att:
            L.append(f"- [PASSO {passo} · {codice}] {msg}")
    return "\n".join(L) + "\n"


def _punti(v):
    return f"{v:+.2f}".replace(".", ",").replace("-", "−")


def _md_macro_giorno(g):
    """Giorno a scelta: per ogni macro la giornata reale piu' bassa e quella
    piu' alta rispetto al target, con le scelte (tappa 1, 29/10/2026)."""
    combos, target = g.get("_combos"), g.get("_target") or {}
    if not combos or len(combos) < 2:
        return []
    _, _, macro = mod_comb.estremi_giorno(combos)
    L = [f"- Giornate componibili: {len(combos)}. Macro sul target, giornata reale "
         f"più bassa e più alta:"]
    for nome, campo, _, chiave in mod_comb.MACRO:
        if chiave not in target or campo not in macro:
            continue
        (lo, c_lo), (hi, c_hi) = macro[campo]
        L.append(f"  - {nome}: {_punti(lo - target[chiave])} punti "
                 f"({mod_comb.descrivi_scelte(c_lo)}) / {_punti(hi - target[chiave])} punti "
                 f"({mod_comb.descrivi_scelte(c_hi)})")
    return L


def _md_macro_settimana(giorni):
    """Media settimanale dei macro sulle settimane reali (Dinkelbach), solo se
    il piano ha giorni a scelta: per i piani senza scelte l'anteprima, e quindi
    l'impronta, resta quella di prima."""
    strutt = [g for g in giorni if g.get("_combos")]
    if not any(len(g["_combos"]) > 1 for g in strutt):
        return []
    target = strutt[0]["_target"]
    sett = mod_comb.estremi_settimana([g["_combos"] for g in strutt])
    L = ["", "## Media settimanale dei macro sulle settimane reali",
         "(una scelta per ogni giorno a scelta; tolleranza ±5 punti sulla media)", ""]
    for nome, campo, _, chiave in mod_comb.MACRO:
        if chiave not in target or campo not in sett["macro"]:
            continue
        (lo, sc_lo), (hi, sc_hi) = sett["macro"][campo]
        L.append(f"- **{nome}:** {_punti(lo - target[chiave])} / "
                 f"{_punti(hi - target[chiave])} punti sul target "
                 f"{target[chiave]:g}%".replace('.', ','))
        for etich, v, sc in (("più bassa", lo, sc_lo), ("più alta", hi, sc_hi)):
            fuori = not entro_tolleranza(v - target[chiave])
            parti = [(g["num"], mod_comb.descrivi_scelte(g["_combos"][j]))
                     for g, j in zip(strutt, sc) if len(g["_combos"]) > 1]
            if len({s for _, s in parti}) == 1:
                desc = f"ogni giorno a scelta {parti[0][1]}"
            else:
                desc = "; ".join(f"giorno {n} {s}" for n, s in parti)
            L.append(f"  - settimana {etich}{' (FUORI TOLLERANZA)' if fuori else ''}: {desc}")
    return L


def impronta(testo):
    import hashlib
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:12]


def verifica_impronta(dati, meta, verdetto=None):
    calcolata = impronta(testo_anteprima(dati, meta, verdetto))
    attesa = meta.get("impronta_approvata")
    if attesa in (None, ""):
        raise Fermo("metadati: manca 'impronta_approvata'. Si ottiene al PASSO 6 con "
                    "--anteprima, si presenta l'anteprima intera e, dopo l'approvazione "
                    "esplicita, si scrive nei metadati (M2)")
    if attesa != calcolata:
        raise Fermo(f"metadati: 'impronta_approvata' vale {attesa}, ma piano, testi o "
                    f"valori di oggi danno {calcolata}: qualcosa e' cambiato dopo "
                    f"l'approvazione. Rigenerare l'anteprima e farla riapprovare (M2)")


def _prepara(piano_p, target_p, meta_p, alimenti_p=None, nomi_p=None, eccezione_p=None,
             nomi_eccezione_p=None, verdetto_p=None, _collaudo_saltato_ok=False):
    db = carica_alimenti(alimenti_p or os.path.join(QUI, "alimenti.csv"))
    nomi = carica_nomi(nomi_p or os.path.join(QUI, "nomi_paziente.csv"))
    # voci da etichetta: solo su richiesta del nutrizionista, mai nel database
    # (21/10/2026); stesse regole della pipeline, nome paziente da file a parte
    eccezioni = {}
    if eccezione_p:
        try:
            eccezioni = carica_eccezioni_etichetta(eccezione_p, db)
        except (OSError, ValueError) as e:
            raise Fermo(str(e))
        db.update(eccezioni)
    if nomi_eccezione_p:
        if not eccezione_p:
            raise Fermo("--nomi-eccezione senza --eccezione-etichetta")
        try:
            aggiunti = carica_nomi(nomi_eccezione_p)
        except (OSError, KeyError) as e:
            raise Fermo(f"{nomi_eccezione_p} non leggibile: {e}")
        estranei = sorted(set(aggiunti) - set(eccezioni))
        if estranei:
            raise Fermo(f"{nomi_eccezione_p}: food_id che non sono voci da etichetta "
                        f"dichiarate: {', '.join(estranei)}")
        nomi.update(aggiunti)
    piano = carica_piano_esteso(piano_p)
    target = carica_target(target_p)
    try:
        with open(meta_p, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, ValueError) as e:
        raise Fermo(f"metadati non leggibili ({meta_p}): {e}")
    if not isinstance(meta, dict):
        raise Fermo("metadati: il file deve contenere un oggetto JSON")
    controlla_metadati_disciplina(meta)
    try:
        verdetto = mod_meta.controlla_verdetto(verdetto_p, piano_p, target_p, meta,
                                               accetta_collaudo_saltato=_collaudo_saltato_ok)
    except mod_meta.VerdettoNonValido as e:
        raise Fermo(f"verdetto: {e}")
    return db, nomi, piano, target, meta, verdetto


def controlla_metadati_disciplina(meta):
    """Campi richiesti dall'anteprima dal 30/10/2026 (metadati_piano.py): drive con
    soli riferimenti a file; assunzioni dichiarate (anche nessuna) e tutte
    confermate; alimenti desiderati dichiarati (anche nessuno)."""
    err = mod_meta.errore_drive(meta)
    if err:
        raise Fermo(f"metadati: {err}")
    ass, err = mod_meta.leggi_assunzioni(meta)
    if err:
        raise Fermo(f"metadati: {err}")
    if ass is None:
        raise Fermo("metadati: manca il campo 'assunzioni' (lista delle assunzioni di "
                    "composizione con il loro stato; [] se non ce ne sono). Va scritto in "
                    "chat A (M2)")
    aperte = [t for t, st in ass if st != "confermata"]
    if aperte:
        raise Fermo("metadati: assunzioni non confermate dal nutrizionista: "
                    + "; ".join(f"«{t}»" for t in aperte) + ". Si chiedono prima "
                    "dell'approvazione (M2)")
    if "profili" not in meta:
        raise Fermo("metadati: manca il campo 'profili' (i profili clinici scelti dal "
                    "nutrizionista per i riferimenti, es. [\"ipercolesterolemia\"]; [] = solo "
                    "il generale). Va scritto in chat A (M2)")
    import riferimenti as mod_rif
    _, err = mod_rif.valida_profili(meta["profili"])
    if err:
        raise Fermo(f"metadati: {err}")
    des, err = mod_meta.leggi_desiderati(meta)
    if err:
        raise Fermo(f"metadati: {err}")
    if des is None:
        raise Fermo("metadati: manca il campo 'alimenti_desiderati' (gli alimenti richiesti "
                    "da paziente o nutrizionista, confrontati col database all'apertura; [] "
                    "se nessuno). Va scritto in chat A (M2)")


def anteprima(piano_p, target_p, meta_p, orari_p=None, **kw):
    """Testo dell'anteprima e sua impronta, senza template e senza PDF."""
    db, nomi, piano, target, meta, ver = _prepara(piano_p, target_p, meta_p, **kw)
    dati = costruisci_dati(piano, db, nomi, target, meta, carica_orari(orari_p), "")
    testo = testo_anteprima(dati, meta, ver)
    return testo, impronta(testo)


def verifica(piano_p, target_p, meta_p, orari_p=None, **kw):
    """Solo il controllo dell'impronta, senza PDF: si lancia prima del documento
    di spiegazione (M3), che la chat B scrive dai metadati senza passare dallo script."""
    db, nomi, piano, target, meta, ver = _prepara(piano_p, target_p, meta_p, **kw)
    dati = costruisci_dati(piano, db, nomi, target, meta, carica_orari(orari_p), "")
    verifica_impronta(dati, meta, ver)
    return meta["impronta_approvata"]


def genera(piano_p, target_p, meta_p, template_p, out_py, out_pdf, orari_p=None,
           mese=None, alimenti_p=None, nomi_p=None, eccezione_p=None,
           nomi_eccezione_p=None, verdetto_p=None, _collaudo_saltato_ok=False):
    """Con template_p None fa tutti i controlli (metadati, verdetto, impronta) senza
    scrivere il .py ne' il PDF: lo usa l'autotest nel collaudo, dove il template non
    c'e' (il comando d'avvio scarica solo la cartella del motore)."""
    db, nomi, piano, target, meta, ver = _prepara(piano_p, target_p, meta_p, alimenti_p,
                                                  nomi_p, eccezione_p, nomi_eccezione_p,
                                                  verdetto_p, _collaudo_saltato_ok)
    if mese is None:
        oggi = datetime.date.today()
        mese = f"{MESI[oggi.month - 1]} {oggi.year}"
    dati = costruisci_dati(piano, db, nomi, target, meta, carica_orari(orari_p), mese)
    verifica_impronta(dati, meta, ver)
    if template_p is None:
        return dati
    with open(template_p, encoding="utf-8") as f:
        src = f.read()
    with open(out_py, "w", encoding="utf-8") as f:
        f.write(componi_py(src, zona_dati_src(*dati)))
    esito = subprocess.run([sys.executable, out_py, out_pdf], capture_output=True, text=True)
    print(esito.stdout, end="")          # passa da sys.stdout: l'autotest lo puo' silenziare
    if esito.returncode != 0:
        print(esito.stderr, end="", file=sys.stderr)
        raise subprocess.CalledProcessError(esito.returncode, esito.args, esito.stdout,
                                            esito.stderr)
    return dati


# ─── autotest su caso golden 03 ───────────────────────────────────
def _piano_di_collaudo(tmp):
    """Il caso golden 03 con due grammature cambiate (pane della colazione A 100 g,
    mela dello spuntino B 250 g) e target sulle sue giornate: senza bloccanti della
    pipeline, perche' dal 30/10/2026 un piano bloccato non arriva all'anteprima.
    Il caso 03 resta com'e' per la suite di regressione."""
    caso = os.path.join(QUI, "golden", "caso_03_scelta_colazione_spuntino")
    with open(os.path.join(caso, "piano.csv"), newline="", encoding="utf-8") as f:
        righe = list(csv.reader(f))
    for r in righe:
        if r[1:3] == ["colazione", "000550"]:
            r[3] = "100"
        if r[1:3] == ["spuntino", "8807"]:
            r[3] = "250"
    with open(os.path.join(caso, "target.csv"), newline="", encoding="utf-8") as f:
        target = list(csv.reader(f))
    nuovi = {"kcal_target": "1336", "proteine_pct_target": "29",
             "carboidrati_pct_target": "40", "grassi_pct_target": "31"}
    for r in target:
        r[1] = nuovi.get(r[0], r[1])
    piano_c, target_c = os.path.join(tmp, "piano.csv"), os.path.join(tmp, "target.csv")
    for path, rr in ((piano_c, righe), (target_c, target)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rr)
    return caso, piano_c, target_c


def autotest(template_p=None):
    """Con il template: tutti i controlli, PDF compreso. Senza (collaudo di inizio
    sessione, dove il template non c'e'): i controlli su metadati, verdetto,
    anteprima e impronta; quelli sul .py e sul PDF si dichiarano saltati."""
    import io
    from contextlib import redirect_stdout
    import pipeline as mod_pipeline
    tmp = tempfile.mkdtemp()
    caso, piano_c, target_c = _piano_di_collaudo(tmp)
    meta = {
        "versione_piano": "v1",
        "giorni": {"lavorativi": ["lun"], "libero": "dom", "range_kcal_libero": [1600, 1900]},
        "livello_colazione": "standard",
        "tdee_confermato_kcal": 2040,
        "intestazione": {"nome": "Paziente Fittizio", "eta": "40 anni",
                         "condizione": "Caso di collaudo"},
        "avvertenze_box": "Nessuna allergia dichiarata (collaudo).",
        "abbinamento_spuntino": {"A": "B", "B": "A"},
        "indicazioni_giorno_libero": {"pranzo": "a piacere, porzione moderata",
                                      "cena": "a piacere, evitare fritti e alcol"},
        "titoli_piatti": {"*|colazione|A": "Colazione A", "*|colazione|B": "Colazione B",
                          "*|spuntino|A": "Spuntino A", "*|spuntino|B": "Spuntino B",
                          "1|pranzo|": "Pranzo di collaudo", "1|cena|": "Cena di collaudo"},
        "obiettivo_intestazione": "collaudo", "criterio_rivalutazione": "collaudo",
        "terapia": "nessuna terapia, confermato dal nutrizionista il 23/10/2026 (fonte: colloquio)",
        "assunzioni": [], "alimenti_desiderati": [], "profili": [],
    }
    mp = os.path.join(tmp, "metadati.json")
    vp = os.path.join(tmp, "verdetto.json")
    # il collaudo non puo' rieseguire se stesso: verdetti prodotti senza collaudo,
    # ammessi solo qui (la riga di comando non lo consente: verificato sotto)
    KW = dict(verdetto_p=vp, _collaudo_saltato_ok=True)

    def fai_verdetto(piano_p=piano_c, target_p=target_c, path=vp):
        """La pipeline vera sui metadati scritti in mp, come in chat A."""
        with redirect_stdout(io.StringIO()):
            ril, m_letti = mod_pipeline.esegui(piano_p, target_p, metadati_p=mp,
                                               salta_collaudo=True, nessuna_terapia=True)
        return mod_meta.scrivi_verdetto(path, ril, piano_p, target_p, m_letti)

    def scrivi_meta(m, piano_p=piano_c):
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(m, f)
        fai_verdetto(piano_p)

    def approva(m):
        """Scrive m, ne ricava l'anteprima e vi aggiunge l'impronta, come al PASSO 6."""
        m = {k: v for k, v in m.items() if k != "impronta_approvata"}
        scrivi_meta(m)
        m["impronta_approvata"] = anteprima(piano_c, target_c, mp, **KW)[1]
        scrivi_meta(m)
        return m

    meta = approva(meta)
    py, pdf = os.path.join(tmp, "piano.py"), os.path.join(tmp, "piano.pdf")
    esiti = []
    con_pdf = template_p is not None
    paz, box, col, spu, giorni = genera(piano_c, target_c, mp, template_p,
                                        py, pdf, mese="Mese di collaudo",
                                        alimenti_p=os.path.join(QUI, "alimenti.csv"), **KW)
    ns = None
    if con_pdf:
        # 1) kcal nel .py == calcolatore, pasto per pasto
        db = carica_alimenti(os.path.join(QUI, "alimenti.csv"))
        piano = carica_piano_esteso(piano_c)
        attese = {}
        for r in piano:
            k = (r["pasto"], r["opzione"])
            attese[k] = attese.get(k, 0) + calcola_riga(db[r["food_id"]], r["grammi"])["kcal_100g"]
        ns = {}
        exec(compile(open(py, encoding="utf-8").read().split("# ═══════════════════════════"
                                                               "════════════════════════════════════════\n#  ═══ MOTORE")[0],
                     py, "exec"), ns)
        trovate = {("colazione", "A"): ns["COLAZIONI"][0][2], ("colazione", "B"): ns["COLAZIONI"][1][2],
                   ("spuntino", "A"): ns["SPUNTINI"][0][2], ("spuntino", "B"): ns["SPUNTINI"][1][2],
                   ("pranzo", ""): ns["GIORNI"][0]["pasti"][1][4], ("cena", ""): ns["GIORNI"][0]["pasti"][3][4]}
        ok_k = all(trovate[k] == _kcal(v) for k, v in attese.items())
        esiti.append(("kcal nel .py = calcolatore.calcola_riga (6 pasti/alternative)", ok_k))
        # 2) motore grafico identico al template
        t = open(template_p, encoding="utf-8").read()
        g = open(py, encoding="utf-8").read()
        esiti.append(("motore grafico identico al template",
                      t[t.index(MARCA_FINE):] == g[g.index(MARCA_FINE):]))
        # 3) PDF: 2 pagine (giorno 1 + libero), niente segnaposto X
        txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
        pagine = txt.count("\f")
        esiti.append((f"PDF generato, {pagine} pagine (attese 2)", pagine == 2))
        esiti.append(("nessun segnaposto 'X' nel PDF", "XXX" not in txt and " Xg" not in txt))
        # 4) abbinamento risolto in lettere
        esiti.append(("abbinamento scritto sulle colazioni",
                      ns["COLAZIONI"][0][3] == "da abbinare allo spuntino B"))
    else:
        esiti.append(("controlli tutti superati fino al PDF, senza scriverlo (template "
                      "assente: .py e PDF verificati con --template)", True))
    # 5) metadato mancante -> fermo
    del meta["avvertenze_box"]
    scrivi_meta(meta)
    try:
        genera(piano_c, target_c, mp, template_p, py, pdf, mese="x", **KW)
        esiti.append(("metadato mancante ferma lo script", False))
    except Fermo as e:
        esiti.append((f"metadato mancante ferma lo script ({e})", True))
    # 6) segnaposto, spazi o non-testo in un campo che va nel PDF -> fermo, e
    #    per il motivo giusto (il messaggio nomina il campo e chiede il testo)
    base_meta = dict(meta, avvertenze_box="Nessuna allergia dichiarata (collaudo).")

    def prova_meta(m, approvato=False):
        if approvato:
            approva(m)
        else:
            scrivi_meta(m)
        genera(piano_c, target_c, mp, template_p, py, pdf, mese="x",
               alimenti_p=os.path.join(QUI, "alimenti.csv"), **KW)

    def deve_fermarsi(etichetta, m, campo):
        try:
            prova_meta(m)
            esiti.append((etichetta + " ferma lo script", False))
        except Fermo as e:
            esiti.append((etichetta + " ferma lo script", f"'{campo}'" in str(e)
                          and "manca il campo" not in str(e)))
        except Exception as e:  # un crash non e' un fermo: va contato come KO
            esiti.append((f"{etichetta}: crash {type(e).__name__} invece del fermo", False))

    def con(chiave, sotto, valore):
        return dict(base_meta, **{chiave: dict(base_meta[chiave], **{sotto: valore})})

    for campo in CAMPI_PAZIENTE:
        for scritto in ("non concordato", " Non concordata. ", "da concordare!", "N/D",
                        "\u2014", "   ", ["non concordato"], "non e' stato concordato",
                        "non\u00adconcordato", "\uff2e\uff2f\uff2e \uff23\uff2f\uff2e\uff23\uff2f\uff32\uff24\uff21\uff34\uff2f",
                        "n.d.", "\u2022"):
            deve_fermarsi(f"'{campo}' = {scritto!r}", dict(base_meta, **{campo: scritto}), campo)
    # testi di esempio del template v5
    deve_fermarsi("obiettivo = 'XX kg' (template)",
                  dict(base_meta, obiettivo_intestazione="XX kg"), "obiettivo_intestazione")
    deve_fermarsi("criterio = 'Da rivalutare dopo N settimane' (template)",
                  dict(base_meta, criterio_rivalutazione="Da rivalutare dopo N settimane"),
                  "criterio_rivalutazione")
    deve_fermarsi("avvertenze = testo di esempio del template",
                  dict(base_meta, avvertenze_box="Indicare qui allergie accertate e qualsiasi "
                                                 "esclusione obbligatoria."), "avvertenze_box")
    deve_fermarsi("intestazione.nome = 'Nome Cognome' (template)",
                  con("intestazione", "nome", "Nome Cognome"), "intestazione.nome")
    deve_fermarsi("intestazione.eta = 'XX anni' (template)",
                  con("intestazione", "eta", "XX anni"), "intestazione.eta")
    deve_fermarsi("intestazione.condizione = 'Descrizione condizione clinica' (template)",
                  con("intestazione", "condizione", "Descrizione condizione clinica"),
                  "intestazione.condizione")
    deve_fermarsi("intestazione.eta = 'n.d.'", con("intestazione", "eta", "n.d."),
                  "intestazione.eta")
    deve_fermarsi("indicazioni_giorno_libero.pranzo = 'da definire'",
                  con("indicazioni_giorno_libero", "pranzo", "da definire"),
                  "indicazioni_giorno_libero.pranzo")
    deve_fermarsi("indicazioni_giorno_libero.cena = '?'",
                  con("indicazioni_giorno_libero", "cena", "?"),
                  "indicazioni_giorno_libero.cena")
    deve_fermarsi("titolo del pranzo = 'non concordato'",
                  con("titoli_piatti", "1|pranzo|", "non concordato"),
                  "titoli_piatti[1|pranzo|]")
    deve_fermarsi("titolo con * della colazione A = '\u2014'",
                  con("titoli_piatti", "*|colazione|A", "\u2014"),
                  "titoli_piatti[*|colazione|A]")
    deve_fermarsi("titolo = 'titolo approvato' (schema di M2)",
                  con("titoli_piatti", "1|cena|", "titolo approvato"), "titoli_piatti[1|cena|]")
    for scritto in ("vers. 2", "v N/D", "v?", "vN1", "versione", "v2 bozza", "2bb",
                    "v\uff12", True):
        deve_fermarsi(f"versione_piano = {scritto!r}",
                      dict(base_meta, versione_piano=scritto), "versione_piano")
    attese = {"v3": "3", "V3": "3", "versione 2": "2", "Versione 2": "2", "v1.0": "1.0",
              "2b": "2b", 2: "2"}
    ottenute = {}
    for k in attese:
        try:
            ottenute[k] = _versione({"versione_piano": k})
        except Exception as e:  # una forma ammessa respinta e' un KO, non un crash
            ottenute[k] = f"{type(e).__name__}: {e}"
    esiti.append((f"versione stampata nel PDF ({len(attese)} forme ammesse)"
                  + ("" if ottenute == attese else f": {ottenute}"), ottenute == attese))
    deve_fermarsi("versione_piano = 'non concordato'",
                  dict(base_meta, versione_piano="non concordato"), "versione_piano")
    for campo, scritto in (("obiettivo_intestazione", "xx kg"), ("avvertenze_box", "+"),
                           ("criterio_rivalutazione", "non e\u2019 stato concordato"),
                           ("avvertenze_box", "(n.d.)"),
                           ("criterio_rivalutazione", "Da rivalutare dopo X settimane"),
                           ("versione_piano", "v."), ("versione_piano", "vN"),
                           ("obiettivo_intestazione", "XXX"),
                           ("criterio_rivalutazione", "Da rivalutare dopo N sett."),
                           ("avvertenze_box", "Indicare qui allergie")):
        deve_fermarsi(f"'{campo}' = {scritto!r}", dict(base_meta, **{campo: scritto}), campo)
    deve_fermarsi("intestazione.condizione = 'Descrizione della condizione clinica'",
                  con("intestazione", "condizione", "Descrizione della condizione clinica"),
                  "intestazione.condizione")
    deve_fermarsi("giorni scritti come testo", dict(base_meta, giorni="lun"), "giorni")
    deve_fermarsi("intestazione scritta come testo",
                  dict(base_meta, intestazione="Paziente Fittizio, 40 anni"), "intestazione")
    deve_fermarsi("indicazioni_giorno_libero scritte come testo",
                  dict(base_meta, indicazioni_giorno_libero="a piacere"),
                  "indicazioni_giorno_libero")
    deve_fermarsi("titoli_piatti scritti come testo",
                  dict(base_meta, titoli_piatti="*|colazione|A"), "titoli_piatti")
    # nomi, sigle e frasi legittime: passano
    legittimi = ["Nan", "Na", "N.D.", "ND", "NAFLD", "Nadia Xu", "9 anni",
                 "Obiettivo non concordato con il cardiologo", "Da definire con il cardiologo",
                 "Nessuna allergia dichiarata.", "Nefropatia diabetica (ND)",
                 "Gravidanza alla XX settimana", "Cariotipo 46,XX", "Non note",
                 "Allergie non pervenute", "Via XX Settembre",
                 "Indicare qui allergie: nichel", "Ignoto", "Sconosciute"]
    respinti = []
    for v in legittimi:
        try:
            _testo_paziente(v, "prova")
        except Fermo:
            respinti.append(v)
    esiti.append((f"nomi, sigle e frasi legittime passano ({len(legittimi)} valori)"
                  + (f": respinti {respinti}" if respinti else ""), not respinti))
    # 7) una frase vera che contiene le stesse parole NON si ferma
    try:
        prova_meta(dict(base_meta, obiettivo_intestazione="Obiettivo non concordato con il cardiologo",
                        abbinamento_spuntino="non concordato"), approvato=True)
        esiti.append(("frase vera con 'non concordato' e abbinamento non concordato: PDF generato", True))
    except Fermo as e:
        esiti.append((f"frase vera con 'non concordato': fermo inatteso ({e})", False))
    # 8) anteprima del PASSO 6 e impronta dell'approvazione (23/10/2026)
    regola = "Le verdure si possono scambiare a parita' di peso (collaudo)."
    approvato = approva(dict(base_meta, regole_operative=[regola]))
    testo, imp = anteprima(piano_c, target_c, mp, **KW)
    esiti.append(("anteprima ripetibile (stessa impronta in due esecuzioni)",
                  imp == anteprima(piano_c, target_c, mp, **KW)[1]
                  == approvato["impronta_approvata"]))
    if ns is not None:
        attesi = ([a[0] for a in ns["COLAZIONI"] + ns["SPUNTINI"]]
                  + [a[1] for a in ns["COLAZIONI"] + ns["SPUNTINI"]]
                  + [p[2] for p in ns["GIORNI"][0]["pasti"] if isinstance(p[2], str)]
                  + [p[3] for p in ns["GIORNI"][0]["pasti"] if isinstance(p[3], str)]
                  + list(approvato["indicazioni_giorno_libero"].values())
                  + [regola, approvato["obiettivo_intestazione"], approvato["avvertenze_box"]])
        mancanti = [t for t in attesi if t not in testo]
        esiti.append((f"anteprima con titoli, grammature e testi del PDF ({len(attesi)} voci)"
                      + (f": mancano {mancanti}" if mancanti else ""), not mancanti))
    # verdetto della pipeline nell'anteprima (30/10/2026)
    esiti.append(("anteprima con il verdetto della pipeline (attenzioni da approvare)",
                  "## Verdetto della pipeline" in testo
                  and "[PASSO 5 · TERAPIA_DICHIARATA_ASSENTE]" in testo
                  and "COLLAUDO_SALTATO" not in testo))
    try:
        prova_meta(approvato)
        esiti.append(("PDF generato con l'impronta approvata", True))
    except Fermo as e:
        esiti.append((f"impronta approvata: fermo inatteso ({e})", False))

    def ferma_impronta(etichetta, m, piano_p=piano_c, attesa="cambiato"):
        scrivi_meta(m, piano_p)
        try:
            genera(piano_p, target_c, mp, template_p, py, pdf, mese="x", **KW)
            esiti.append((etichetta + " ferma lo script", False))
        except Fermo as e:
            esiti.append((etichetta + " ferma lo script", "impronta_approvata" in str(e)
                          and attesa in str(e)))

    senza = {k: v for k, v in approvato.items() if k != "impronta_approvata"}
    ferma_impronta("metadati senza impronta", senza, attesa="manca")
    ferma_impronta("titolo cambiato dopo l'approvazione",
                   dict(approvato, titoli_piatti=dict(approvato["titoli_piatti"],
                                                      **{"1|cena|": "Cena cambiata"})))
    ferma_impronta("regola operativa aggiunta dopo l'approvazione",
                   dict(approvato, regole_operative=[regola, "Regola non approvata."]))
    ferma_impronta("indicazione del giorno libero cambiata dopo l'approvazione",
                   dict(approvato, indicazioni_giorno_libero=dict(
                       approvato["indicazioni_giorno_libero"], cena="a piacere")))
    righe_p = open(piano_c, encoding="utf-8").read().splitlines()
    i = next(n for n, r in enumerate(righe_p) if n and ",pranzo," in r)
    campi = righe_p[i].split(",")
    campi[3] = f"{float(campi[3]) + 10:g}"
    righe_p[i] = ",".join(campi)
    piano_mod = os.path.join(tmp, "piano_modificato.csv")
    with open(piano_mod, "w", encoding="utf-8") as f:
        f.write("\n".join(righe_p) + "\n")
    ferma_impronta("grammatura cambiata dopo l'approvazione", approvato, piano_p=piano_mod)
    try:
        prova_meta(dict(approvato, drive={"cartella_id": "1AltraCartellaDrive",
                                          "piano_csv": "piano_v2.csv"}))
        esiti.append(("riferimenti di Drive cambiati: impronta invariata, PDF generato", True))
    except Fermo as e:
        esiti.append((f"riferimenti di Drive cambiati: fermo inatteso ({e})", False))
    # sola verifica (prima del documento di spiegazione) e ordine delle chiavi
    scrivi_meta(approvato)
    try:
        esiti.append(("--verifica-impronta passa sui metadati approvati",
                      verifica(piano_c, target_c, mp, **KW) == approvato["impronta_approvata"]))
    except Fermo as e:
        esiti.append((f"--verifica-impronta: fermo inatteso ({e})", False))
    scrivi_meta(dict(approvato, limiti_noti=["Limite aggiunto dopo."]))
    try:
        verifica(piano_c, target_c, mp, **KW)
        esiti.append(("--verifica-impronta ferma un limite noto aggiunto dopo", False))
    except Fermo as e:
        esiti.append(("--verifica-impronta ferma un limite noto aggiunto dopo",
                      "impronta_approvata" in str(e)))
    diff_a = approva(dict(approvato, differenze_da_versione_precedente=[
        {"pasto": "cena", "da": "x", "a": "y"}]))
    with open(mp, "w", encoding="utf-8") as f:
        f.write(json.dumps(diff_a, sort_keys=True))   # stesso contenuto, chiavi riordinate
    fai_verdetto()
    try:
        verifica(piano_c, target_c, mp, **KW)
        esiti.append(("chiavi riordinate nel JSON: impronta invariata", True))
    except Fermo as e:
        esiti.append((f"chiavi riordinate nel JSON: fermo inatteso ({e})", False))
    testo_vuoto = anteprima(piano_c, target_c, mp, **KW)[0]
    esiti.append(("campi del documento di spiegazione assenti mostrati come (nessuna voce)",
                  "- **Limiti noti:** (nessuna voce)" in testo_vuoto
                  and "- **Terapia (sezione 2 del documento di spiegazione):** nessuna "
                      "terapia, confermato dal nutrizionista il 23/10/2026" in testo_vuoto
                  and "- **TDEE confermato:** 2040 kcal" in testo_vuoto))
    # 9) disciplina nel codice (30/10/2026): ogni blocco con la sua prova al contrario
    scrivi_meta(approvato)

    def ferma(etichetta, attesa, funz):
        try:
            funz()
            esiti.append((etichetta + " ferma lo script", False))
        except Fermo as e:
            esiti.append((etichetta + " ferma lo script" + ("" if attesa in str(e)
                          else f": motivo inatteso ({e})"), attesa in str(e)))
        except Exception as e:
            esiti.append((f"{etichetta}: crash {type(e).__name__} invece del fermo", False))

    ferma("anteprima senza --verdetto", "manca --verdetto",
          lambda: anteprima(piano_c, target_c, mp))
    ferma("PDF senza --verdetto", "manca --verdetto",
          lambda: genera(piano_c, target_c, mp, template_p, py, pdf, mese="x"))
    ferma("verdetto prodotto con --salta-collaudo, senza la deroga dell'autotest",
          "salta-collaudo", lambda: anteprima(piano_c, target_c, mp, verdetto_p=vp))
    # il piano originale del caso 03 ha bloccanti: verdetto vero, anteprima negata
    vp_bl = os.path.join(tmp, "verdetto_bloccato.json")
    fai_verdetto(os.path.join(caso, "piano.csv"), os.path.join(caso, "target.csv"), vp_bl)
    ferma("verdetto con rilievi bloccanti", "bloccanti",
          lambda: anteprima(os.path.join(caso, "piano.csv"), os.path.join(caso, "target.csv"),
                            mp, verdetto_p=vp_bl, _collaudo_saltato_ok=True))
    ferma("verdetto di un altro piano", "cambiati",
          lambda: anteprima(os.path.join(caso, "piano.csv"), target_c, mp, **KW))
    with open(mp, "w", encoding="utf-8") as f:     # metadati cambiati, verdetto vecchio
        json.dump(dict(approvato, regole_operative=[regola, "Aggiunta dopo la pipeline."]), f)
    ferma("metadati cambiati dopo la pipeline", "cambiati",
          lambda: anteprima(piano_c, target_c, mp, **KW))

    def ferma_meta(etichetta, attesa, m):
        scrivi_meta(m)
        ferma(etichetta, attesa, lambda: anteprima(piano_c, target_c, mp, **KW))

    da_conf = [{"testo": "pranzo a casa", "stato": "confermata"},
               {"testo": "pesce a pranzo", "stato": "da_confermare"}]
    ferma_meta("assunzione da confermare", "pesce a pranzo", dict(approvato, assunzioni=da_conf))
    ferma_meta("campo 'assunzioni' assente", "'assunzioni'",
               {k: v for k, v in approvato.items() if k != "assunzioni"})
    ferma_meta("assunzione senza stato", "assunzione 1",
               dict(approvato, assunzioni=[{"testo": "pranzo a casa"}]))
    ferma_meta("campo 'alimenti_desiderati' assente", "'alimenti_desiderati'",
               {k: v for k, v in approvato.items() if k != "alimenti_desiderati"})
    ferma_meta("nota clinica nel campo drive", "drive",
               dict(approvato, drive={"piano_csv": "piano_v1.csv", "nota": "assume warfarin"}))
    ferma_meta("frase nel campo drive.fascicolo", "drive.fascicolo",
               dict(approvato, drive={"fascicolo": "il paziente assume warfarin"}))
    # profili clinici del registro dei riferimenti (30/10/2026)
    ferma_meta("campo 'profili' assente", "'profili'",
               {k: v for k, v in approvato.items() if k != "profili"})
    ferma_meta("profilo sconosciuto", "sconosciuti", dict(approvato, profili=["celiachia"]))
    ferma_meta("profili scritti come testo", "lista", dict(approvato, profili="ipercolesterolemia"))
    scrivi_meta(approvato)
    vero_reg = mod_meta.impronta_registro
    mod_meta.impronta_registro = lambda: "registro-cambiato"
    try:
        ferma("registro dei riferimenti cambiato dopo la pipeline", "registro dei riferimenti",
              lambda: anteprima(piano_c, target_c, mp, **KW))
    finally:
        mod_meta.impronta_registro = vero_reg
    scrivi_meta(dict(approvato, profili=["ipercolesterolemia"]))
    try:
        t_pr = anteprima(piano_c, target_c, mp, **KW)[0]
        esiti.append(("profilo nei metadati: anteprima con profili, registro e avvisi dei "
                      "riferimenti", "generale + ipercolesterolemia" in t_pr
                      and "RIFERIMENTI_NON_VERIFICABILI" in t_pr
                      and "registro dei riferimenti:** " + str(vero_reg()) in t_pr))
    except Fermo as e:
        esiti.append((f"profilo nei metadati: fermo inatteso ({e})", False))
    # prove al contrario: gli stessi campi scritti bene passano
    ok_m = dict(approvato, assunzioni=[{"testo": "pranzo a casa", "stato": "confermata"}],
                alimenti_desiderati=["petto di pollo", "hamburger"],
                drive={"cartella_id": "1AltraCartellaDrive", "fascicolo": "Fascicolo P00.docx",
                       "altri_file": ["orari_pasti.csv", "verdetto_v1.json"]})
    scrivi_meta(ok_m)
    try:
        t_ok = anteprima(piano_c, target_c, mp, **KW)[0]
        esiti.append(("assunzioni confermate, desiderati e drive con nomi di file: anteprima "
                      "con assunzioni, desiderati e avviso dei mancanti",
                      "- **Assunzione:** pranzo a casa (confermata)" in t_ok
                      and "hamburger" in t_ok and "ALIMENTI_DESIDERATI_MANCANTI" in t_ok))
    except Fermo as e:
        esiti.append((f"metadati scritti bene: fermo inatteso ({e})", False))
    # le attenzioni sono nell'impronta: un verdetto diverso cambia l'impronta
    scrivi_meta(approvato)
    with open(vp, encoding="utf-8") as f:
        v_mod = json.load(f)
    v_mod["attenzioni"] = v_mod["attenzioni"][:-1]
    with open(vp, "w", encoding="utf-8") as f:
        json.dump(v_mod, f)
    ferma("attenzione tolta dal verdetto dopo l'approvazione", "impronta_approvata",
          lambda: verifica(piano_c, target_c, mp, **KW))
    fai_verdetto()
    # alternative in testa solo se il pasto e' a scelta in TUTTI i giorni strutturati
    alt1, alt2 = [["T", "d", "k", None]], [["U", "e", "k", None]]
    finti = [{"pasti": [("colazione", "", alt1), ("pranzo", "", alt2)]},
             {"pasti": [("colazione", "", alt1), ("pranzo", "", "fisso", "d", "k")]},
             {"libero": True, "pasti": [("colazione", "", alt1)]}]
    esiti.append(("alternative in testa solo per i pasti a scelta in tutti i giorni",
                  _alternative_comuni(finti) == {"colazione": alt1}))
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("AUTOTEST genera_zona_piano.py")
    for m, ok in esiti:
        print(f"  [{'OK ' if ok else 'KO '}] {m}")
    tutti = all(ok for _, ok in esiti)
    print("ESITO:", "SUPERATO" if tutti else "FALLITO")
    return 0 if tutti else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--template")
    ap.add_argument("--autotest", action="store_true")
    ap.add_argument("--anteprima", action="store_true",
                    help="PASSO 6: anteprima completa (testi, grammature, verdetto) e "
                         "impronta, sempre su file; senza template e senza PDF")
    ap.add_argument("--out-anteprima", dest="out_anteprima",
                    help="file dell'anteprima (predefinito: anteprima_<versione>_<impronta>.md)")
    ap.add_argument("--verifica-impronta", dest="verifica", action="store_true",
                    help="prima del documento di spiegazione: controlla solo l'impronta")
    ap.add_argument("--piano"); ap.add_argument("--target"); ap.add_argument("--metadati")
    ap.add_argument("--verdetto", help="verdetto di pipeline.py --out-verdetto sugli stessi "
                                       "piano, target e metadati (obbligatorio)")
    ap.add_argument("--orari"); ap.add_argument("--mese")
    ap.add_argument("--eccezione-etichetta", dest="eccezione")
    ap.add_argument("--nomi-eccezione", dest="nomi_eccezione")
    ap.add_argument("--out-py"); ap.add_argument("--out-pdf")
    a = ap.parse_args()
    modi = [n for n, v in (("--anteprima", a.anteprima), ("--verifica-impronta", a.verifica),
                           ("--autotest", a.autotest)) if v]
    if len(modi) > 1:
        ap.error(f"{' e '.join(modi)} non si combinano: uno per comando")
    if (a.anteprima or a.verifica) and (a.template or a.out_py or a.out_pdf):
        ap.error("--anteprima e --verifica-impronta non generano il PDF: togliere "
                 "--template, --out-py e --out-pdf")
    kw = dict(eccezione_p=a.eccezione, nomi_eccezione_p=a.nomi_eccezione, verdetto_p=a.verdetto)
    try:
        if a.autotest:
            return autotest(a.template)
        for n in ("piano", "target", "metadati"):
            if not getattr(a, n):
                ap.error(f"--{n} obbligatorio")
        if a.verifica:
            imp = verifica(a.piano, a.target, a.metadati, a.orari, **kw)
            print(f"IMPRONTA VERIFICATA: {imp} - piano e testi sono quelli approvati")
            return 0
        if a.anteprima:
            testo, imp = anteprima(a.piano, a.target, a.metadati, a.orari, **kw)
            testo += f"\n**Impronta per l'approvazione:** `{imp}`\n"
            # sempre su file (30/10/2026): il 28/10 l'approvazione era avvenuta su un
            # estratto riportato in chat; il file si consegna intero e si approva quello
            with open(a.metadati, encoding="utf-8") as f:
                versione = str(json.load(f).get("versione_piano") or "piano")
            versione = re.sub(r"[^\w.-]+", "", versione) or "piano"
            out = a.out_anteprima or f"anteprima_{versione}_{imp}.md"
            with open(out, "w", encoding="utf-8") as f:
                f.write(testo)
            print(f"ANTEPRIMA SCRITTA: {out} ({testo.count(chr(10))} righe)")
            print(f"IMPRONTA: {imp}")
            print("Si consegna il FILE intero (non un estratto in chat); approvato, "
                  "l'impronta va in 'impronta_approvata' dei metadati (M2, PASSO 6).")
            return 0
        if not a.template:
            ap.error("--template obbligatorio")
        for n in ("out_py", "out_pdf"):
            if not getattr(a, n):
                ap.error(f"--{n.replace('_', '-')} obbligatorio")
        genera(a.piano, a.target, a.metadati, a.template, a.out_py, a.out_pdf, a.orari, a.mese,
               **kw)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
