#!/usr/bin/env python3
"""
controllo_privacy.py - Studio Nutrizionale Taglialatela

Il repository e' PUBBLICO: nessun paziente vi compare, nemmeno per nome (GDPR).
Nel repository i pazienti si citano solo con il codice P01, P02... (P00 =
fittizio); la corrispondenza sta solo su Drive. Lo script cerca nomi di persona
nel CONTENUTO dei file, nei NOMI dei file e nei MESSAGGI di commit. Nato il
24/10/2026: nomi di pazienti erano entrati dal 30/07/2026 perche' il controllo
prima del commit guardava quali file cambiavano, non cosa contenevano.

DUE LIVELLI
  1. DIZIONARIO (sta nel repository, nessun dato dei pazienti): nomi propri
     italiani come «Nome Cognome», «Cognome Nome», «Nome C.», «paziente /
     piano / caso + Cognome», «CognomeNome» attaccati e nomi non ambigui da soli.
     Le parole TUTTE MAIUSCOLE si confrontano come se fossero «Parola».
  2. ELENCO DEI PAZIENTI (--nomi FILE, da Drive, MAI nel repository): ogni nome
     e cognome dell'elenco, riconosciuto anche attaccato, con trattini bassi,
     apostrofi tipografici, accenti o in maiuscolo; nome e cognome insieme in ogni
     forma e ordine. Un nome di battesimo da solo non conta. Un cognome che e' una
     parola comune si segna «~» nell'elenco: da solo conta con la maiuscola o in un
     nome di file o in un dato. E' il livello che conta: prima di ogni commit si usa
     SEMPRE (M1).
Prima di cercare: NFKC, caratteri invisibili tolti, sosia cirillici, greci, armeni e
latini («ø», «ı») in latino semplice.
Si leggono anche zip/xlsx/docx, .gz, .bz2, .xz, UTF-16 senza BOM e le sequenze leggibili dei
binari (questi ultimi e i file interni agli archivi solo contro l'elenco).
LIMITI DICHIARATI del solo dizionario: «N. Cognome», «Cognome N.», un cognome da
solo fuori contesto, nomi stranieri, nome e cognome tutti minuscoli. Li copre
solo l'elenco. Dell'elenco: un nome di battesimo da solo; un cognome «~» in
minuscolo nella prosa; il testo di PDF compressi, immagini e .7z.

ECCEZIONI: strumenti/privacy_consentiti.txt, un nome INTERO per riga (almeno due
parole vere, particelle escluse), tolto solo come frase intera a confini di parola.
Prima del commit valgono quelle in stage; su GitHub quelle dell'ultimo commit.
Valgono SOLO per il dizionario, mai contro l'elenco.
Gli esempi dell'autotest e i nomi propri del dizionario sono in ROT13.

USO
  python3 strumenti/controllo_privacy.py                    # file tracciati
  python3 strumenti/controllo_privacy.py --staged           # pre-commit
  python3 strumenti/controllo_privacy.py --messaggio FILE   # commit-msg
  python3 strumenti/controllo_privacy.py --intervallo A..B  # ogni commit, merge compresi;
                                    # A assente o inesistente: l'intera cronologia (GitHub)
  ... --nomi elenco.txt    ... --senza-testo (log pubblici: né nome né percorso stampati)
Elenco: un paziente per riga («P03 = Cognome Nome (nota)» o solo il nome); «!Nome
Cognome» cerca solo il nome completo (cognome uguale a quello dello studio).
  python3 strumenti/controllo_privacy.py --autotest
Esce 1 se trova un nome, 2 per un errore d'uso (elenco vuoto o illeggibile).
"""
import argparse, bz2, gzip, io, lzma, os, re, subprocess, sys, unicodedata, zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
# editoria cita autori di linee guida, e gli archivi di dati (zip, xlsx: cache CREA e
# BDA-IEO) citano gli autori delle schede: il dizionario li scambierebbe per pazienti.
# Lì vale solo l'elenco.
SOLO_ELENCO = re.compile(r"editoria[/:\\]")    # anche «editoria:/», nome caricato a mano in passato

def _r13(t):
    import codecs
    return codecs.decode(t, "rot13")


# Nomi propri italiani frequenti, in ROT13: in chiaro coinciderebbero con i nomi di
# battesimo dei pazienti dell'elenco e questo file non passerebbe il proprio controllo.
NOMI = _r13("""
nqevnan nqevnab ntarfr ntbfgvab nyoregb nyon nyoregn nyrffnaqen nyrffnaqeb nyrffvn nyrffvb
nysbafb nyserqb nyvpr nyzn nznyvn nzoen nzrqrb naqern natryn natryb navgn naan naanyvfn
naanznevn nagbaryyn nagbavrggn nagbavb nevnaan neznaqb negheb nffhagn nheben oneonen
orngevpr orarqrggn oreaneqb oehan oehab pnzvyyn pneyn pneyb pnezryn pnezra pnezvar
pnebyvan pngrevan prpvyvn prfner puvnen pveb pynhqvn pynhqvb pynen pbaprggn pbeenqb pevfgvna
pevfgvnan pevfgvan pevfgvnab qnavryn qnavryr qnevb qnivqr qroben qravf qvnan qvrtb qvab
qbzravpb qbangryyn rqbneqb ryran ryrbaben ryvb ryvfn ryvfnorggn rznahryn rznahryr rzvyvn
rzvyvnab rzvyvb rzzn raevpn raevpb ramb revpn rearfgb rggber rhtravb snovnan snovb snoevmvb
srqrevpn srqrevpb svyvccb svybzran svberyyn synivn synivb senaprfpn senaprfpb senapb tnoevryr
tnoevryyn tnrgnab traaneb tvnpbzb tvnayhpn tvnaan tvnaav tvyoregb tvab tvbnppuvab tvbetvn
tvbetvb tvbinaan tvbinaav tvhyvn tvhyvnan tvhyvnab tvhyvb tvhfrccr tvhfrccvan tybevn tenmvn
tenmvryyn thvqb vqn vynevn vzznpbyngn verar vfnoryyn vina vinan wnpbcb ynhen ynivavn yrn
yrbaneqb yrgvmvn yvn yvyvnan yvan yvab yvfn yvivn yberan yberamb yberqnan yhnan yhpn yhpvn
yhpvnan yhpvnab yhvtv yhvfn znqqnyran znahryn znahry znepryyn znepryyb znepb zneturevgn znevn
znevnatryn znevnab znevncvn znevnaan znevyran znevan znevb znevfn znegn znegvan znffvzb zngvyqr
znggrb znggvn znhevmvb znheb zvpuryn zvpuryr zvyran zveryyn zbavpn anqvn angnyvn avpbyn
avpbyrggn abrzv ahamvn ahamvb bytn benmvb bearyyn cnbyn cnbyb cnfdhnyr cngevmvn cngevmvb
cvrgeb enssnryr enssnryyn erangn erangb evppneqb evgn eboregn eboregb ebppb ebzvan ebfnyon
ebfnaan ebfnevn ebfnevb ebffnan fnoevan fnyingber fnzhryr fnaqen fnaqeb fnen fretvb fvyinan
fvyivn fvyivb fvzban fvzbar fbsvn fbavn fgrsnavn fgrsnab fhfnaan gnavn grerfn gvmvnan gvmvnab
gbzznfb htb hzoregb inyragvan inyragvab inyrevn inyrevb inarffn ivapramn ivapramb ivetvavn
ivgb ivggbevn ivggbevb jnygre navryyb nagvzb naahamvngn fbffvb yhpvb vinab vyravn wrffvpn
yhvtvn pnezryvan gvgvan gvan evab avab crccr crccvab gbgb tvtv cvan cvab vzzn zran ebfn
""").split()
# nomi che sono anche parole comuni, toponimi o marchi: solo accanto a un cognome
AMBIGUI = set(_r13("""
nyon nyzn nzoen naqern natryn natryb nheben oehan pnezra puvnen pynen qvnan qvab ramb senapb
tybevn tenmvn vqn yrn yvn yvan yvab yvfn yhpn znevan znevb evgn ebppb fnaqen fnen fbsvn htb
ivgn ivgb ivggbevn rzzn zngvyqr zneturevgn tvab cvab cvan gbgb gvan avab evab ebfn znegvan
zryvffn inyrevnan fnyivn fvzbar srqrevpb fgryyn fcrenamn znffvzb znffvzn sbeghangb sbeghangn
""").split())
# parole che seguono o precedono un nome senza esserne il cognome
PAROLE_COMUNI = set("""
il lo la i gli le un una uno e ed o di da del della dei degli delle al alla ai agli alle
con per su tra fra che non se come nel nella nei negli sul sulla sui dal dalla dai
piano dieta paziente pazienti dott dottor dottore dott.ssa caso golden modulo sezione passo
giorno pasto pranzo cena colazione spuntino totale san santa sant santo torre corso via viale
piazza vico largo rione universita università ospedale istituto policlinico regione provincia
pizza pizzeria clinica casa villa fondazione patri magno mattina sera lunedi lunedì
martedi martedì mercoledi mercoledì giovedi giovedì venerdi venerdì sabato domenica
senza dopo prima solo tutti tutte nessun nessuna nessuno ogni questo questa quello quella anche
gia già sempre mai quando dove perche perché cosi così ancora oggi ieri domani json csv pdf xlsx
docx html md py api url id nota note vedi oppure ovvero cioe cioè circa sotto sopra entro oltre
fase step tabella figura allegato capitolo punto livello gruppo opzione versione
""".split()) | set(_r13("senapn rznahryr").split())   # nome di una via e aggettivo (ROT13)
# parole maiuscole legittime dopo «piano», «caso»... (oltre agli aggettivi, vedi sotto)
CONTESTO_OK = {"alimentare", "nutrizionale", "golden", "settimanale", "studio", "esempio",
               "fittizio", "reale", "drive", "andamento", "template", "archivio", "clinico",
               "limite", "dash", "standard", "rinforzata", "libero", "nutrizionista"}
TOPONIMI = {"san", "santa", "sant", "santo", "corso", "via", "viale", "piazza", "largo", "vico",
            "torre", "universita", "ospedale", "istituto", "policlinico", "certosa", "castel",
            "rione", "contrada", "chiesa", "basilica", "parrocchia", "pizzeria", "trattoria",
            "ristorante", "bar", "caseificio", "salumeria"}
ATTACCATO_OK = {_r13("ebffvznevb"), "cognomenome", "nomecognome"}   # esempio dei moduli, ROT13
PARTICELLE = {"de", "di", "del", "della", "dello", "dei", "degli", "la", "lo", "d", "da", "van", "von", "el"}

NOME_RE = "|".join(sorted(NOMI, key=len, reverse=True))
CAP = r"[A-ZÀ-Ý][a-zà-ÿ']+"
COGN = rf"(?:(?:[Dd][ei]|[Dd]el|[Dd]ella|[Ll][ao]|[Dd]')\s?)?{CAP}"
PAT = [
    ("Nome Cognome", re.compile(rf"\b(?i:{NOME_RE})\s+({COGN})")),
    ("Cognome Nome", re.compile(rf"\b({CAP})\s+(?i:{NOME_RE})\b")),
    ("Nome C.", re.compile(rf"\b(?i:{NOME_RE})\s+[A-Z]\.(?:\s?[A-Z]\.)?")),
]
CONTESTO = re.compile(r"\b(?i:paziente|piano|caso|dieta|signor[ae]?|sig\.(?:ra)?|cartella|"
                      r"dott\.ssa|dottoressa)\s+(" + CAP + r")|\b(?i:famiglia|cartella)\s+(?:(?i:di|del|della)\s+)?(" + CAP + r")")
AGGETTIVO = re.compile(r"(?i).*(ica|ico|iche|ici|anea|aneo|ale|ali|ivo|iva|ata|ato|ente|ante|ario|aria)$")
ATTACCATO = re.compile(r"\b([A-ZÀ-Ý][a-zà-ÿ]{2,})(" +
                       "|".join(sorted((n.capitalize() for n in NOMI), key=len, reverse=True)) +
                       r")(?![a-zà-ÿ])")
SOLO = re.compile(r"\b(" + "|".join(sorted((n.capitalize() for n in NOMI if n not in AMBIGUI),
                                         key=len, reverse=True)) + r")\b")


class ErroreUso(Exception):
    pass


# ─── normalizzazione per l'elenco ────────────────────────────────────
def _piano(t):
    """minuscolo, senza accenti, apostrofi tipografici unificati"""
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    return t.lower()


# lettere cirilliche, greche e armene identiche a quelle latine, e lettere latine che la
# conversione in ASCII cancellerebbe invece di semplificare: un cognome scritto con una di
# queste sfuggirebbe a entrambi i livelli
_SOSIA = str.maketrans(
    "аеорсухіјѕԁӏһԛԝАВЕКМНОРСТХІЈЅУԌοαειкνρτυχΑΒΕΖΗΙΚΜΝΟΡΤΥΧ",
    "aeopcyxijsdlhqwABEKMHOPCTXIJSYGoaeikvptuxABEZHIKMNOPTYX")
_SOSIA.update(str.maketrans({"ø": "o", "Ø": "O", "ı": "i", "ł": "l", "Ł": "L", "đ": "d",
                             "Đ": "D", "ħ": "h", "ŧ": "t", "ß": "ss", "æ": "ae", "Æ": "AE",
                             "œ": "oe", "Œ": "OE", "օ": "o", "ս": "u", "ց": "g", "ɑ": "a",
                             "ɡ": "g", "ȷ": "j", "ꞵ": "b"}))
_INVISIBILI = re.compile("[­​-‏⁠-⁤﻿]")


def _norma(t):
    """forma canonica prima di ogni ricerca: NFKC (lettere a larghezza piena, legature),
    niente caratteri invisibili, sosia cirillici e greci in latino"""
    t = unicodedata.normalize("NFKC", t)
    return _INVISIBILI.sub("", t).translate(_SOSIA)


def _ascii(t):
    """senza accenti, maiuscole conservate, minuscola→Maiuscola separate"""
    t = re.sub(r"([a-zà-ÿ])([A-ZÀ-Ý])", r"\1 \2", t)
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")


def _parola_singola(f0, testo_ascii):
    """Per un cognome dell'elenco segnato «~» (parola comune, «~Rossi»): conta solo con
    l'iniziale maiuscola (o tutto maiuscolo) oppure in un nome di file o in un dato
    (accanto a _ . / - cifre , ; : = virgolette). In minuscolo nella prosa no."""
    for m in re.finditer(rf"(?<![A-Za-z]){f0}(?![A-Za-z])", testo_ascii, re.I):
        if m.group(0)[0].isupper():
            return True
        intorno = testo_ascii[max(0, m.start() - 1):m.start()] + testo_ascii[m.end():m.end() + 1]
        if re.search(r"[_./\\\-0-9,;:=\"'`]", intorno):
            return True
    return False


def _token(t):
    """parole: separa su ogni non-lettera e sui passaggi minuscola→Maiuscola"""
    t = re.sub(r"([a-zà-ÿ])([A-ZÀ-Ý])", r"\1 \2", t)
    return [w for w in re.split(r"[^a-z]+", _piano(t)) if w]


def carica_elenco_testo(testo):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write(testo)
    try:
        return carica_elenco(fh.name)
    finally:
        os.unlink(fh.name)


def carica_elenco(path):
    """Restituisce (forme, propri, comuni): forme = sequenze di token da cercare (ogni
    parola, e la riga intera nei due ordini); propri = parole singole; comuni = parole
    segnate «~» (cognomi che sono parole comuni). I nomi di battesimo del dizionario NON
    sono forme da sole (solo con il cognome): da soli non identificano e coincidono con il
    nome del titolare."""
    try:
        righe = open(path, encoding="utf-8").read().splitlines()
    except OSError as e:
        raise ErroreUso(f"elenco dei pazienti non leggibile ({path}): {e}")
    forme, propri, comuni = set(), set(), set()
    for r in righe:
        r = r.strip()
        if not r or r.startswith("#"):
            continue
        intero = False
        if r.startswith("!"):
            # «!Nome Cognome»: solo il nome completo, mai le parole da sole (un cognome che
            # e' anche il nome dello studio o di un luogo)
            intero, r = True, r[1:].strip()
        r = re.sub(r"\(.*?\)", " ", r.split("=", 1)[-1])       # «P03 = Nome (nota)»
        if intero:
            t = _token(re.sub(r"\bP\d+\b", " ", r))
            if t:
                forme.add(tuple(t))
                forme.add(tuple(reversed(t)))
            continue
        r = re.sub(r"\bP\d+\b", " ", r)
        for w in re.findall(r"~(\S+)", r):
            comuni.update(_token(w))
        r = r.replace("~", " ")
        tutta = _token(r)
        if len(tutta) >= 2:                                   # nome e cognome insieme
            forme.add(tuple(tutta))
            forme.add(tuple(reversed(tutta)))
            if len(tutta) >= 3:                                # «De X Nome» -> «Nome De X»
                for k in range(1, len(tutta)):
                    forme.add(tuple(tutta[k:] + tutta[:k]))
        parti = [p for p in re.split(r"[\s,;]+", r) if p]
        i = 0
        while i < len(parti):
            w = parti[i]
            toks = _token(w)
            if toks and toks[0] in PARTICELLE and len(toks) == 1 and i + 1 < len(parti):
                toks = toks + _token(parti[i + 1])               # cognome con particella («De X»)
                i += 1
            if toks:
                for pezzo in re.split(r"-", w):                  # doppio cognome col trattino
                    pt = _token(pezzo)
                    if pt and len("".join(pt)) >= 2 and not (len(pt) == 1 and pt[0] in PARTICELLE) \
                            and not (len(pt) == 1 and pt[0] in NOMI):
                        forme.add(tuple(pt))
                if not (len(toks) == 1 and toks[0] in NOMI):
                    forme.add(tuple(toks))
                if len(toks) == 1:
                    propri.add(toks[0])
            i += 1
    forme = {f for f in forme if len("".join(f)) >= 2}
    if not forme:
        raise ErroreUso(f"elenco dei pazienti vuoto ({path}): nessun nome da cercare")
    return forme, propri, comuni


def _in_elenco(testo, forme, propri, comuni=frozenset()):
    tok = _token(testo)
    if not tok:
        return set()
    insieme = set(tok)
    trovati = set()
    nomi_noti = set(NOMI) | propri
    testo_ascii = _ascii(testo)
    for f in forme:
        unito = "".join(f)
        if len(f) == 1:
            if f[0] in insieme and (f[0] not in comuni or _parola_singola(f[0], testo_ascii)):
                trovati.add(unito)
        elif f[0] in insieme:
            n = len(f)
            for i, t in enumerate(tok):
                if t == f[0] and tuple(tok[i:i + n]) == f:
                    trovati.add(unito)
                    break
        if len(unito) >= 4 and len(f) > 1 and unito in insieme:     # particella attaccata («dexxx»)
            trovati.add(unito)
        if len(unito) >= 5:
            for t in insieme:
                if len(t) > len(unito) and (t.startswith(unito) or t.endswith(unito)):
                    resto = t[len(unito):] if t.startswith(unito) else t[:-len(unito)]
                    if resto in nomi_noti:                            # cognome e nome attaccati, minuscoli
                        trovati.add(unito)
    return trovati


# ─── dizionario ──────────────────────────────────────────────────────
def _titolo(riga):
    """parole TUTTE MAIUSCOLE (almeno 3 lettere) come «Parola»: «COGNOME NOME»"""
    return re.sub(r"\b([A-ZÀ-Ý])([A-ZÀ-Ý']{2,})\b", lambda m: m.group(1) + m.group(2).lower(), riga)


def _togli_consentiti(riga, consentiti):
    """toglie le eccezioni solo come frase intera, a confini di parola"""
    for c in consentiti:
        rx = r"\s+".join(re.escape(w) for w in c.split())
        riga = re.sub(rf"(?<![^\W\d_]){rx}(?![^\W\d_])", " ", riga, flags=re.I)
    return riga


def _dizionario(riga, consentiti):
    pulita = _togli_consentiti(_titolo(riga), consentiti)
    visti = set()
    for tipo, rx in PAT:
        for m in rx.finditer(pulita):
            parole = m.group(0).split()
            altro = parole[-1] if tipo == "Nome Cognome" else parole[0]
            if tipo != "Nome C." and _piano(altro).strip("'") in PAROLE_COMUNI:
                continue
            prima = [_piano(w) for w in re.findall(r"[A-Za-zÀ-ÿ']+", pulita[:m.start()])[-1:]]
            if any(w.strip("'") in TOPONIMI for w in prima):      # un toponimo («Santa» + nome + luogo)
                continue
            visti.add((tipo, m.group(0)))
    for m in CONTESTO.finditer(pulita):
        w = m.group(1) or m.group(2)
        if _piano(w) in PAROLE_COMUNI or _piano(w) in CONTESTO_OK or AGGETTIVO.match(w):
            continue
        visti.add(("dopo paziente/piano/caso", m.group(0)))
    for m in ATTACCATO.finditer(pulita):
        if _piano(m.group(0)) not in ATTACCATO_OK:
            visti.add(("NomeCognome attaccati", m.group(0)))
    for m in SOLO.finditer(pulita):
        prima = [_piano(w) for w in re.findall(r"[A-Za-zÀ-ÿ']+", pulita[:m.start()])[-2:]]
        # «San», «Corso», «Via» + nome: toponimi, non persone
        if any(w.strip("'") in TOPONIMI for w in prima):
            continue
        if not any(m.group(0) in v for _, v in visti):
            visti.add(("nome da solo", m.group(0)))
    return visti


def cerca(testo, consentiti, elenco=None, solo_elenco=False):
    """[(riga, tipo, testo trovato)]"""
    forme, propri, comuni = elenco if elenco else (set(), set(), set())
    out = []
    for n, riga in enumerate(_norma(testo).splitlines() or [testo], 1):
        visti = set()
        if not solo_elenco:
            visti |= _dizionario(riga, consentiti)
        # le eccezioni NON valgono contro l'elenco: un'eccezione uguale al nome di un
        # paziente non deve poterlo nascondere (né nascondersi nel file delle eccezioni)
        for x in (_in_elenco(riga, forme, propri, comuni) if forme else ()):
            visti.add(("elenco pazienti", x))
        out += [(n, t, v) for t, v in sorted(visti)]
    return out


# ─── dove si cerca ───────────────────────────────────────────────────
def _git(*a):
    return subprocess.run(["git", *a], cwd=RADICE, capture_output=True)


def _testi_del_blob(dati, percorso, livello=0):
    """[(etichetta, testo, dentro_archivio)]: testo del file; per zip/xlsx/docx e .gz il
    testo dei file interni; UTF-16 anche senza BOM; dei binari le sequenze leggibili"""
    if dati[:2] == b"PK" and livello < 4:
        try:
            z = zipfile.ZipFile(io.BytesIO(dati))
            out = []
            for i in z.infolist():
                if not i.is_dir() and i.file_size < 50_000_000:
                    out.append((f"{percorso}!{i.filename}", i.filename, True))
                    for et, t, _ in _testi_del_blob(z.read(i), f"{percorso}!{i.filename}", livello + 1):
                        out.append((et, t, True))
            return out
        except (zipfile.BadZipFile, RuntimeError, NotImplementedError):
            pass
    if dati[:2] == b"\x1f\x8b" and livello < 4:
        try:
            interno = gzip.GzipFile(fileobj=io.BytesIO(dati)).read(50_000_000)
            return [(et, t, True) for et, t, _ in _testi_del_blob(interno, f"{percorso}!gz", livello + 1)]
        except (OSError, EOFError):
            pass
    for firma, apri in ((b"BZh", bz2.decompress), (b"\xfd7zXZ\x00", lzma.decompress)):
        if dati.startswith(firma) and livello < 4:
            try:
                interno = apri(dati)[:50_000_000]
                return [(et, t, True) for et, t, _ in _testi_del_blob(interno, f"{percorso}!", livello + 1)]
            except (OSError, ValueError, EOFError, lzma.LZMAError):
                pass
    if dati[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return [(percorso, dati.decode("utf-16", "ignore"), False)]
    campione = dati[:8000]
    if b"\x00" not in campione:
        return [(percorso, dati.decode("utf-8", "ignore"), False)]
    pari, dispari = campione[0::2].count(0), campione[1::2].count(0)
    meta = max(1, len(campione) // 2)
    if dispari > 0.3 * meta and pari < 0.05 * meta:
        return [(percorso, dati.decode("utf-16-le", "ignore"), False)]
    if pari > 0.3 * meta and dispari < 0.05 * meta:
        return [(percorso, dati.decode("utf-16-be", "ignore"), False)]
    # binario: le sequenze leggibili (anche in UTF-16), contro il solo elenco
    pezzi = [m.decode("latin-1") for m in re.findall(rb"[\x20-\x7e\xc0-\xff]{4,}", dati)]
    pezzi += [m.decode("utf-16-le", "ignore") for m in re.findall(rb"(?:[\x20-\x7e]\x00){4,}", dati)]
    return [(percorso, "\n".join(pezzi), True)]


def _voci(modo, percorso, dati):
    """(etichetta, etichetta pubblica, testo, solo_elenco) di un file"""
    yield (f"[nome file] {percorso}", "nome di un file", percorso, False)
    for et, t, interno in _testi_del_blob(dati, percorso):
        yield (et, "contenuto di un file", t, interno or bool(SOLO_ELENCO.match(percorso)))


def _commit_da_controllare(a, b):
    """Commit nuovi tra a e b. Se a manca (ramo nuovo, primo caricamento) o non esiste
    piu' (storia riscritta, push forzato): TUTTI i commit raggiungibili da b."""
    if a.strip("0") and _git("cat-file", "-e", f"{a}^{{commit}}").returncode == 0:
        r = _git("rev-list", "--reverse", f"{a}..{b}")
    else:
        r = _git("rev-list", "--reverse", b)
    if r.returncode != 0:
        raise ErroreUso(f"intervallo non leggibile: {r.stderr.decode(errors='ignore').strip()}")
    return r.stdout.decode().split()


def _oggetti(modo, intervallo=None):
    """(etichetta, etichetta pubblica, testo, solo_elenco) da controllare"""
    if modo == "albero":
        for p in _git("ls-files", "-z").stdout.decode("utf-8", "ignore").split("\0"):
            if not p:
                continue
            try:
                dati = open(os.path.join(RADICE, p), "rb").read()
            except OSError:
                dati = b""
            yield from _voci(modo, p, dati)
    elif modo == "staged":
        out = _git("diff", "--cached", "--name-status", "-z", "--diff-filter=ACMRT", "-M").stdout
        campi = out.decode("utf-8", "ignore").split("\0")
        i = 0
        while i < len(campi) - 1:
            stato = campi[i]
            if stato.startswith(("R", "C")):
                percorso = campi[i + 2]; i += 3
            else:
                percorso = campi[i + 1]; i += 2
            yield from _voci(modo, percorso, _git("show", f":{percorso}").stdout)
        # il messaggio di commit lo controlla il blocco commit-msg
    elif modo == "intervallo":
        a, b = intervallo.split("..", 1)
        blob_visti, nomi_visti = set(), set()
        for c in _commit_da_controllare(a, b):
            c7 = c[:7]
            msg = _git("log", "-1", "--format=%B", c).stdout.decode("utf-8", "ignore")
            yield (f"[messaggio {c7}]", f"messaggio del commit {c7}", msg, False)
            # -m: anche i merge, confrontati con ciascun genitore (un merge puo' introdurre
            # contenuto proprio); --raw da' l'impronta del blob, controllato una volta sola
            out = _git("diff-tree", "--no-commit-id", "-r", "-m", "-z", "--raw", "-M",
                       "--diff-filter=ACMRT", "--root", c).stdout.decode("utf-8", "ignore").split("\0")
            i = 0
            while i < len(out) - 1:
                meta = out[i]
                if not meta.startswith(":"):
                    i += 1
                    continue
                campi = meta[1:].split()
                modo_nuovo, sha, stato = campi[1], campi[3], campi[4]
                if stato.startswith(("R", "C")):
                    percorso = out[i + 2]; i += 3
                else:
                    percorso = out[i + 1]; i += 2
                if modo_nuovo == "160000":                     # sottomodulo: nessun blob
                    continue
                if percorso not in nomi_visti:
                    nomi_visti.add(percorso)
                    yield (f"[nome file {c7}] {percorso}", f"nome di un file, commit {c7}", percorso, False)
                if sha in blob_visti:
                    continue
                blob_visti.add(sha)
                dati = _git("cat-file", "blob", sha).stdout
                for et, t, interno in _testi_del_blob(dati, percorso):
                    yield (f"{c7}:{et}", f"contenuto di un file, commit {c7}", t,
                           interno or bool(SOLO_ELENCO.match(percorso)))


def carica_consentiti(modo="albero", intervallo=None):
    """Eccezioni: nel blocco prima del commit quelle IN STAGE (non la copia di lavoro),
    su GitHub quelle dell'ultimo commit caricato."""
    rel = "strumenti/privacy_consentiti.txt"
    if modo in ("staged", "messaggio"):
        r = _git("show", f":{rel}")
        righe = r.stdout.decode("utf-8", "ignore").splitlines() if r.returncode == 0 else []
    elif modo == "intervallo":
        r = _git("show", f"{intervallo.split('..', 1)[1]}:{rel}")
        righe = r.stdout.decode("utf-8", "ignore").splitlines() if r.returncode == 0 else []
    else:
        p = os.path.join(RADICE, rel)
        righe = open(p, encoding="utf-8").read().splitlines() if os.path.exists(p) else []
    return _valida_consentiti(righe)


def _valida_consentiti(righe):
    out = []
    for n, r in enumerate(righe, 1):
        r = _norma(r).strip()
        if not r or r.startswith("#"):
            continue
        parole = r.split()
        vere = [w for w in parole if len(re.sub(r"[^\w]|[\d_]", "", w)) >= 2
                and not re.search(r"[\d_]", w)
                and _piano(w) not in PARTICELLE and _piano(w) not in PAROLE_COMUNI]
        if not all(re.fullmatch(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*\.?", w) for w in parole) or len(vere) < 2:
            raise ErroreUso(f"privacy_consentiti.txt riga {n}: un'eccezione va scritta come nome "
                            "INTERO: almeno due parole vere di due o piu' lettere (non particelle "
                            "come «di», «de»), solo lettere")
        out.append(r)
    return out


# ─── autotest ────────────────────────────────────────────────────────
# I nomi degli esempi sono INVENTATI e scritti in ROT13, decifrati solo qui: in
# chiaro coinciderebbero con cognomi comuni e, contro l'elenco reale dei pazienti,
# bloccherebbero ogni commit a causa di questo stesso file. Nessuna eccezione serve.
def _r(t):
    import codecs
    return codecs.decode(t, "rot13")


def _autotest_storia(el):
    """ramo nuovo, push forzato e merge che introduce contenuto proprio, in un deposito
    temporaneo"""
    import tempfile, shutil
    global RADICE
    ko, vecchia, d = [], RADICE, tempfile.mkdtemp()
    try:
        RADICE = d
        g = lambda *a: _git("-c", "user.name=t", "-c", "user.email=t@t", "-c",
                            "core.hooksPath=/dev/null", *a)
        g("init", "-q", "-b", "main")
        def commit(f, testo, msg):
            open(os.path.join(d, f), "w", encoding="utf-8").write(testo)
            g("add", f); g("commit", "-q", "-m", msg)
        commit("a.md", "pulito", "uno")
        commit("b.md", _r("ivfgb Ehffb"), "due")          # nome nel commit centrale
        commit("c.md", "pulito", "tre")
        trovati = lambda a: [p for _, p, t, s in _oggetti("intervallo", f"{a}..HEAD")
                             if cerca(t, [], el, s)]
        if not trovati("0" * 40):
            ko.append("ramo nuovo: controllato solo l'ultimo commit")
        if not trovati("1" * 40):
            ko.append("push forzato: controllato solo l'ultimo commit")
        g("checkout", "-q", "-b", "lato"); commit("d.md", "pulito", "lato")
        g("checkout", "-q", "main"); base = g("rev-parse", "HEAD").stdout.decode().strip()
        g("merge", "-q", "--no-ff", "--no-commit", "lato")
        open(os.path.join(d, "e.md"), "w", encoding="utf-8").write(_r("Ehffb Traaneb"))
        g("add", "e.md"); g("commit", "-q", "-m", "unione")
        if not trovati(base):
            ko.append("merge non controllato")
    finally:
        RADICE = vecchia
        shutil.rmtree(d, ignore_errors=True)
    return ko


def autotest():
    cons = [_r("Tvhfrccr Gntyvnyngryn"), _r("Anqvn Kh")]
    devono = [_r(t) for t in ['Traaneb Ehffb un crefb 2 xt', "ivfvgn qv Naan Q'Nzvpb", 'Rfcbfvgb Znevn Ebfnevn', 'Pneyn Q.Y. (i2)', 'Rfpyhfb Oehab Z.: vy svyr', 'Fbeeragvab Cnfdhnyr (crfpr)', 'qny cvnab Fbeeragvab.', 'rf. `EhffbTraaneb_i2.wfba`', 'EHFFB TRAANEB', 'yn fvtaben Rfcbfvgb un puvrfgb', 'Pnegryyn Qr Yhpn Naan']]
    passano = [_r(t) for t in ['Qbgg. Tvhfrccr Gntyvnyngryn — Pbafhyragr', 'Fghqvb Ahgevmvbanyr Gntyvnyngryn', 'Cnmvragr C01, yharqì', 'vy cvnab qv C03', 'Ebfn qrv iragv', 'Cnfgn r yrthzv', 'rf. `EbffvZnevb_i2.wfba`', 'Vy Cvnab Nyvzragner i5', 'Qvrgn Zrqvgreenarn', 'Pnfb Pyvavpb', 'Fna Tvbetvb n Perznab', 'Pbefb Ivggbevb Rznahryr', 'Cvmmn Zneturevgn', 'Havirefvgà Srqrevpb VV', 'Cvnab Yharqì', 'Ivgnzvan Q', 'Fnagn Znevn Pnchn Irgrer', 'Znffvzb 5 cnfgv', 'pnegryyn qry WFBA']]
    ko = []
    for t in devono:
        if not cerca(t, cons):
            ko.append(f"NON trovato: {t!r}")
    for t in passano:
        if cerca(t, cons):
            ko.append(f"falso allarme: {t!r} -> {cerca(t, cons)}")
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write(_r("C01 = Ehffb Traaneb\nC02 = Naan Q'Nzvpb\nC03 = Qr Yhpn Pneyn (abgn)\nC04 = Ebffv-Ovnapuv Grerfn\nC05 = Yv Jrv\n"))
    el = carica_elenco(fh.name)
    os.unlink(fh.name)
    con_elenco = [_r(t) for t in ['ivfgb Ehffb vrev', 'ehffb_traaneb.wfba', 'Ehffb_Traaneb_i2', 'TraanebEhffb', 'qnzvpb', 'QNzvpb_Naan.wfba', 'Q’Nzvpb', 'vy fvtabe Qr Yhpn', 'Ovnapuv', 'Yv Jrv', 'qryhpn']]
    for t in con_elenco:
        if not cerca(t, cons, el, solo_elenco=True):
            ko.append(f"elenco: NON trovato {t!r}")
    for t in ["Studio a Napoli", "rosso e verde", "la lucana", "grossi pezzi"]:
        if cerca(t, cons, el, solo_elenco=True):
            ko.append(f"elenco: falso allarme {t!r}")
    if not cerca(_r("Ehffb ary PFI"), [_r('Ehffb Traaneb')], el):
        ko.append("un'eccezione ha spento l'elenco")
    try:
        carica_elenco(os.devnull)
        ko.append("elenco vuoto accettato")
    except ErroreUso:
        pass
    # lettere sosia e caratteri invisibili
    for t in [_r("Ehffb").replace("o", "\u043e"), _r("Ehf\u200bfb Traaneb"), "".join(chr(ord(x) + 0xFEE0) for x in _r("EHFFB"))]:
        if not cerca(t, cons, el, solo_elenco=True):
            ko.append(f"sosia o invisibili: NON trovato {t!r}")
    # cognome che e' una parola comune: in minuscolo nella prosa no, maiuscolo o nei file si'
    el2 = (el[0] | {(_r("ebffv"),)}, el[1], el[2] | {_r("ebffv")})   # «~Ebffv» nell'elenco
    el3 = carica_elenco_testo(_r("C09 = ~Ebffv Tvbinaan\nC10 = Mnasebggv Rezratvyqb\n"))
    for t in [_r("pbagebyyb qv tvbinaan ebffv"), _r("rezratvyqb mnasebggv"), _r("ebffv,tvbinaan,1980"),
              _r('{"pbtabzr": "ebffv"}'), _r("mnasebggv"), _r("Rezratvyqb Mnasebggv").replace("o", "\u00f8"),
              _r("Mnasebggv").replace("o", "\u00f8"), _r("Mnasebggv").replace("i", "\u0131")]:
        if not cerca(t, [], el3, solo_elenco=True):
            ko.append(f"elenco (minuscolo/dati/sosia latini): NON trovato {t!r}")
    if cerca(_r("cbzbqbev ebffv"), [], el3, solo_elenco=True):
        ko.append("cognome «~» in minuscolo nella prosa segnalato")
    if cerca(_r("Tvbinaan"), [], el3, solo_elenco=True):
        ko.append("nome di battesimo da solo segnalato")
    if not cerca(_r("cvnab qv Rezratvyqb Mnasebggv"), [_r("Rezratvyqb Mnasebggv")], el3):
        ko.append("un'eccezione uguale al nome di un paziente lo nasconde")
    if cerca(_r("cbzbqbev ebffv"), cons, el2, solo_elenco=True):
        ko.append("cognome-parola comune in minuscolo segnalato")
    for t in [_r("Ebffv"), _r("ebffv.wfba"), _r("cvnab_ebffv_i2")]:
        if not cerca(t, cons, el2, solo_elenco=True):
            ko.append(f"cognome-parola comune NON trovato {t!r}")
    # eccezioni: a confini di parola, mai una parola sola o con particelle
    if not cerca(_r("Znevnaan Ebffv"), [_r("Naan Ebffv")], el2, solo_elenco=True):
        ko.append("eccezione applicata dentro una parola")
    for cattiva in [_r("qv Ehffb"), "o G", _r("Ehffb"), _r("Ehffb 2"), _r("qr yn Ehffb")]:
        try:
            _valida_consentiti([cattiva])
            ko.append(f"eccezione debole accettata {cattiva!r}")
        except ErroreUso:
            pass
    try:
        _valida_consentiti([_r("Traaneb Ehffb"), _r("Naan Q'Nzvpb"), _r("Anqvn Kh")])
    except ErroreUso as e:
        ko.append(f"eccezione valida rifiutata: {e}")
    # file: UTF-16 senza BOM, NUL iniziale, gz, zip; «!» nel percorso non spegne il dizionario
    import gzip as _gz
    nome = _r("Traaneb Ehffb")
    for dati in [nome.encode("utf-16-le"), nome.encode("utf-16-be"), b"\x00\x00" + nome.encode(),
                 _gz.compress(nome.encode())]:
        if not any(cerca(t, cons, el, solo) for _, t, solo in _testi_del_blob(dati, "x")):
            ko.append(f"contenuto non letto {dati[:12]!r}")
    if any(solo for *_, solo in _voci("albero", "a!b.md", nome.encode())):
        ko.append("«!» nel percorso spegne il dizionario")
    ko += _autotest_storia(el)
    print("AUTOTEST controllo_privacy.py")
    for k in ko:
        print("  [KO ]", k)
    print("ESITO:", "FALLITO" if ko else
          f"SUPERATO ({len(devono)} nomi col dizionario, {len(passano)} testi legittimi passano, "
          f"{len(con_elenco)} forme con l'elenco)")
    return 1 if ko else 0


def main():
    ap = argparse.ArgumentParser(description="Nomi di persona nel repository (privacy)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--staged", action="store_true", help="file in stage (pre-commit)")
    g.add_argument("--messaggio", help="file con il messaggio di commit (commit-msg)")
    g.add_argument("--intervallo", help="A..B: ogni commit dell'intervallo (GitHub)")
    g.add_argument("--autotest", action="store_true")
    ap.add_argument("--nomi", help="elenco dei pazienti, fuori dal repository")
    ap.add_argument("--senza-testo", action="store_true",
                    help="non stampa il testo trovato (log pubblici)")
    a = ap.parse_args()
    try:
        if a.autotest:
            return autotest()
        modo = ("messaggio" if a.messaggio else "staged" if a.staged else
                "intervallo" if a.intervallo else "albero")
        consentiti = carica_consentiti(modo, a.intervallo)
        elenco = carica_elenco(a.nomi) if a.nomi else None
        if a.messaggio:
            # anche le righe con «#»: con --cleanup=verbatim restano nel messaggio
            testo = open(a.messaggio, encoding="utf-8", errors="ignore").read()
            oggetti = [("[messaggio di commit]", "messaggio di commit", testo, False)]
        else:
            oggetti = _oggetti(modo, a.intervallo)
        tot = 0
        for et, pub, testo, solo_el in oggetti:
            for n, tipo, v in cerca(testo, consentiti, elenco, solo_el):
                tot += 1
                # log pubblici: né il nome trovato né il percorso (anche il percorso puo'
                # contenere il nome); solo il tipo di oggetto e il commit
                print(f"  [{tot}] {pub}, riga {n}: {tipo}" if a.senza_testo
                      else f"  {et}:{n}: {tipo}: «{v}»")
    except ErroreUso as e:
        print(f"CONTROLLO PRIVACY NON ESEGUITO: {e}")
        return 2
    if tot:
        print(f"\nCONTROLLO PRIVACY FALLITO: {tot} possibili nomi di persona. Nel repository i "
              "pazienti si citano solo con il codice P01, P02... (M1). Un falso allarme si "
              "aggiunge, come nome intero, a strumenti/privacy_consentiti.txt.")
        return 1
    print("CONTROLLO PRIVACY SUPERATO" + (" (anche contro l'elenco dei pazienti)" if elenco
                                         else " (solo dizionario: prima del commit serve l'elenco)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
