#!/usr/bin/env python3
"""
genera_spiegazione.py - Studio Nutrizionale Taglialatela

Genera il PDF del documento di spiegazione (M3) SOLO se i testi sono puliti e i
dati sono quelli approvati. Controllo automatico dei segnaposto, tappa 2,
30/10/2026: fino ad allora il template si generava anche con «testo placeholder»
dentro (verificato), e il controllo era a vista.

Controlli, nell'ordine (al primo che fallisce si ferma e dice dove):
  1. impronta: piano, target, metadati e verdetto sono quelli approvati al PASSO 6
     (stesso controllo di genera_zona_piano.py --verifica-impronta);
  2. motore grafico del .py identico al template (principio 4) e intestazione e
     chiusura dello studio invariate;
  3. struttura: 6 sezioni, numerate da 1 a 6, ognuna con almeno un paragrafo;
  4. testi: nessun segnaposto o testo d'esempio del template («testo
     placeholder», «XX», «N settimane»...), nessuna parentesi quadra (le etichette
     [dedotto], [piano], [fascicolo] della presentazione o le alternative del
     modello «[i farmaci in terapia / il contesto di vita]»), nessun campo vuoto;
  5. registro: il nome del paziente non compare nel corpo del testo.
Poi esegue il .py e scrive il PDF. Il testo si approva comunque per intero prima
della consegna (M3): questo controllo toglie gli errori meccanici, non giudica i
contenuti.

USO
  python3 genera_spiegazione.py --py CognomeNome_spiegazione_vN.py
      --template TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py
      --piano piano_vN.csv --target target.csv --metadati metadati_piano_vN.json
      --verdetto verdetto_vN.json [--orari orari_pasti.csv]
      [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
      --out-pdf CognomeNome_spiegazione_vN.pdf

  python3 genera_spiegazione.py --autotest --template TEMPLATE_SpiegazioneDieta_..._v1.py
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_zona_piano as gzp
from genera_zona_piano import Fermo

MARCA_MOTORE = "#  ═══ MOTORE GRAFICO"
CAMPI_STUDIO = ("INTESTAZIONE", "CHIUSURA_NOME", "CHIUSURA_QUALIFICA", "CHIUSURA_NOTA")
CAMPI_TESTO = ("TITOLO", "SOTTOTITOLO", "INTRO")
N_SEZIONI = 6
# frammenti che non devono comparire in nessun punto del testo
_FRAMMENTI = re.compile(
    r"placeholder|lorem ipsum|\btodo\b|\bxx+\b|\bn settimane\b|\bnome cognome\b|"
    r"\bda completare\b|\bda inserire\b|\btesto (?:di|d')esempio\b|<[^>]*>|\{[^}]*\}",
    re.IGNORECASE)
_PAROLE_NON_NOME = {"dott", "dottssa", "sig", "sigra", "paziente", "fittizio", "collaudo"}


def _zona(src, dove):
    if MARCA_MOTORE not in src:
        raise Fermo(f"{dove}: manca la marca del motore grafico («{MARCA_MOTORE}»)")
    zona, motore = src.split(MARCA_MOTORE, 1)
    valori = {}
    try:
        albero = ast.parse(zona)
    except SyntaxError as e:
        raise Fermo(f"{dove}: zona dati non leggibile ({e})")
    for nodo in albero.body:
        if isinstance(nodo, ast.Assign) and len(nodo.targets) == 1 \
                and isinstance(nodo.targets[0], ast.Name):
            try:
                valori[nodo.targets[0].id] = ast.literal_eval(nodo.value)
            except ValueError:
                raise Fermo(f"{dove}: «{nodo.targets[0].id}» non e' un valore scritto per "
                            f"esteso (niente espressioni nella zona dati)")
    return valori, motore


def _testi(valori):
    """(dove, testo) per ogni testo del corpo, nell'ordine del PDF."""
    out = [(c, valori.get(c)) for c in CAMPI_TESTO]
    sezioni = valori.get("SEZIONI")
    if not isinstance(sezioni, list):
        raise Fermo("SEZIONI deve essere una lista di sezioni (titolo, [paragrafi], "
                    "[in pratica] o None)")
    if len(sezioni) != N_SEZIONI:
        raise Fermo(f"il documento ha {len(sezioni)} sezioni: la struttura e' di "
                    f"{N_SEZIONI} (M3, «Si adattano i contenuti, non la struttura»)")
    for i, sez in enumerate(sezioni, 1):
        if not (isinstance(sez, tuple) and len(sez) == 3):
            raise Fermo(f"sezione {i}: serve (titolo, [paragrafi], [in pratica] o None)")
        titolo, paragrafi, pratica = sez
        if not isinstance(titolo, str) or not re.match(rf"\s*{i}\.\s+\S", titolo):
            raise Fermo(f"sezione {i}: il titolo deve cominciare con «{i}.» ({titolo!r})")
        out.append((f"sezione {i}, titolo", titolo))
        if not isinstance(paragrafi, list) or not paragrafi:
            raise Fermo(f"sezione {i}: nessun paragrafo")
        out += [(f"sezione {i}, paragrafo {j}", p) for j, p in enumerate(paragrafi, 1)]
        if pratica is not None:
            if not isinstance(pratica, list) or not pratica:
                raise Fermo(f"sezione {i}: «in pratica» deve essere una lista non vuota o None")
            out += [(f"sezione {i}, punto {j}", p) for j, p in enumerate(pratica, 1)]
    return out


def _nome_paziente(meta):
    inte = meta.get("intestazione")
    nome = inte.get("nome") if isinstance(inte, dict) else None
    if not isinstance(nome, str):
        return []
    parole = re.findall(r"[^\W\d_]{3,}", unicodedata.normalize("NFKC", nome))
    return [p for p in parole if p.lower().strip(".") not in _PAROLE_NON_NOME]


def controlla(py_p, template_p, meta):
    """Tutti i controlli sul .py (2-5). Restituisce il numero di testi controllati."""
    try:
        src = open(py_p, encoding="utf-8").read()
        tpl = open(template_p, encoding="utf-8").read()
    except OSError as e:
        raise Fermo(f"file non leggibile: {e}")
    valori, motore = _zona(src, py_p)
    valori_t, motore_t = _zona(tpl, template_p)
    if motore != motore_t:
        raise Fermo("il motore grafico del .py e' diverso da quello del template: si "
                    "modifica solo la zona dati (principio 4)")
    for c in CAMPI_STUDIO:
        if valori.get(c) != valori_t.get(c):
            raise Fermo(f"«{c}» e' diverso dal template: intestazione e chiusura dello "
                        f"studio non si cambiano")
    testi = _testi(valori)
    nome = _nome_paziente(meta)
    for dove, t in testi:
        try:
            gzp._testo_paziente(t, dove)
        except Fermo:
            raise Fermo(f"{dove}: «{t}» e' vuoto o un segnaposto: serve il testo vero")
        trovato = _FRAMMENTI.search(t)
        if trovato:
            raise Fermo(f"{dove}: contiene «{trovato.group(0)}», un segnaposto o un testo "
                        f"d'esempio del template")
        if "[" in t or "]" in t:
            raise Fermo(f"{dove}: contiene una parentesi quadra («{t[:60]}»): etichette "
                        f"[dedotto]/[piano]/[fascicolo] o alternative del modello non vanno "
                        f"nel PDF")
        for p in nome:
            if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", t):
                raise Fermo(f"{dove}: contiene «{p}», dal nome del paziente: il registro e' "
                            f"impersonale, il nome sta solo nel nome del file (M3)")
    return len(testi)


def genera(py_p, template_p, piano_p, target_p, meta_p, out_pdf, orari_p=None, **kw):
    gzp.verifica(piano_p, target_p, meta_p, orari_p, **kw)
    with open(meta_p, encoding="utf-8") as f:
        meta = json.load(f)
    n = controlla(py_p, template_p, meta)
    esito = subprocess.run([sys.executable, py_p, out_pdf], capture_output=True, text=True)
    print(esito.stdout, end="")
    if esito.returncode != 0:
        raise Fermo(f"il .py non ha generato il PDF: {esito.stderr.strip()[-300:]}")
    return n


# ─── autotest ──────────────────────────────────────────────────────
def _scrivi_zona(template_src, valori, out):
    zona, motore = template_src.split(MARCA_MOTORE, 1)
    righe = ["#!/usr/bin/env python3", "import sys", ""]
    for k, v in valori.items():
        righe.append(f"{k} = {v!r}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n\n" + MARCA_MOTORE + motore)


def autotest(template_p):
    """Prove sul .py (controlli 2-5): un documento pulito passa, ogni difetto noto si
    ferma. Il controllo 1 (impronta) e' quello di genera_zona_piano.py, collaudato
    nel suo autotest."""
    tpl = open(template_p, encoding="utf-8").read()
    base_t, _ = _zona(tpl, template_p)
    sezioni = [(f"{i}. Titolo della sezione {i}",
                [f"Paragrafo della sezione {i}, scritto per il piano."],
                ["Un punto pratico."] if i % 2 else None) for i in range(1, 7)]
    buono = dict(base_t, SEZIONI=sezioni)
    meta = {"intestazione": {"nome": "Paziente Fittizio Rossetti"}}
    tmp = tempfile.mkdtemp()
    py = os.path.join(tmp, "spiegazione.py")
    esiti = []

    def prova(etichetta, valori, attesa=None, motore=None):
        _scrivi_zona(tpl if motore is None else motore, valori, py)
        try:
            controlla(py, template_p, meta)
            esiti.append((etichetta, attesa is None))
        except Fermo as e:
            esiti.append((etichetta + ("" if attesa and attesa in str(e)
                                       else f": motivo inatteso ({e})"),
                          bool(attesa) and attesa in str(e)))

    def sez(i, campo, valore):
        s = [list(x) for x in sezioni]
        s[i - 1][campo] = valore
        return dict(buono, SEZIONI=[tuple(x) for x in s])

    prova("documento pulito passa", buono)
    prova("template intatto (una sezione, «testo placeholder») si ferma", base_t, "1 sezioni")
    prova("sei sezioni con «testo placeholder» si fermano",
          sez(3, 1, ["testo placeholder"]), "placeholder")
    prova("cinque sezioni si fermano", dict(buono, SEZIONI=sezioni[:5]), "5 sezioni")
    prova("sezioni fuori ordine si fermano",
          dict(buono, SEZIONI=[sezioni[1], sezioni[0]] + sezioni[2:]), "«1.»")
    prova("etichetta [dedotto] rimasta si ferma",
          sez(2, 1, ["Il pranzo e' portatile [dedotto]."]), "parentesi quadra")
    prova("alternativa del modello rimasta si ferma",
          sez(2, 0, "2. La dieta e [i farmaci in terapia / il contesto di vita]: come si integrano"),
          "parentesi quadra")
    prova("«XX» nel testo si ferma", sez(6, 1, ["Obiettivo: XX kg in tre mesi."]), "XX")
    prova("paragrafo vuoto si ferma", sez(4, 1, ["   "]), "segnaposto")
    prova("sezione senza paragrafi si ferma", sez(5, 1, []), "nessun paragrafo")
    prova("«non concordato» da solo si ferma", sez(1, 1, ["non concordato"]), "segnaposto")
    prova("nome del paziente nel testo si ferma",
          sez(1, 1, ["Il piano di Rossetti parte da qui."]), "nome del paziente")
    prova("parola comune che contiene il nome passa",
          sez(1, 1, ["Il piano parte da un quadro chiaro."]))
    prova("intestazione dello studio cambiata si ferma",
          dict(buono, INTESTAZIONE=dict(base_t["INTESTAZIONE"], qualifica="Nutrizionista")),
          "INTESTAZIONE")
    prova("motore grafico cambiato si ferma", buono, "motore grafico",
          motore=tpl.replace("fontSize=17", "fontSize=18"))
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("AUTOTEST genera_spiegazione.py")
    for m, ok in esiti:
        print(f"  [{'OK ' if ok else 'KO '}] {m}")
    tutti = all(ok for _, ok in esiti)
    print("ESITO:", "SUPERATO" if tutti else "FALLITO")
    return 0 if tutti else 1


def main():
    ap = argparse.ArgumentParser(description="Documento di spiegazione: controlli e PDF")
    ap.add_argument("--py"); ap.add_argument("--template", required=True)
    ap.add_argument("--piano"); ap.add_argument("--target"); ap.add_argument("--metadati")
    ap.add_argument("--verdetto"); ap.add_argument("--orari")
    ap.add_argument("--eccezione-etichetta", dest="eccezione")
    ap.add_argument("--nomi-eccezione", dest="nomi_eccezione")
    ap.add_argument("--out-pdf", dest="out_pdf")
    ap.add_argument("--autotest", action="store_true")
    a = ap.parse_args()
    if a.autotest:
        return autotest(a.template)
    for n in ("py", "piano", "target", "metadati", "verdetto", "out_pdf"):
        if not getattr(a, n):
            ap.error(f"--{n.replace('_', '-')} obbligatorio")
    try:
        n = genera(a.py, a.template, a.piano, a.target, a.metadati, a.out_pdf, a.orari,
                   eccezione_p=a.eccezione, nomi_eccezione_p=a.nomi_eccezione,
                   verdetto_p=a.verdetto)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    print(f"CONTROLLI SUPERATI: {n} testi, impronta approvata. Ora il testo intero si "
          f"presenta per l'approvazione (pdftotext -layout {a.out_pdf} -), M3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
