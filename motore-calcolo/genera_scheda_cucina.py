#!/usr/bin/env python3
"""
Scheda per chi cucina (04/11/2026): pagina 1 la settimana, a riquadri per giorno;
pagina 2 le tabelle di conversione.

Grafica scelta dal nutrizionista il 04/11/2026 (versione B). Qui i dati vengono tutti da
piano, metadati e alimenti.csv: nessuna grammatura scritta a mano.

Si genera dopo i controlli del piano: stesso verdetto e stessa impronta approvata
del PDF (genera_zona_piano.verifica). Testi facoltativi nei metadati, approvati con
l'anteprima: scheda_cucina = {"note_carboidrati": "...", "note_piede": "..."}.

USO
  python3 genera_scheda_cucina.py --piano piano_vN.csv --target target_vN.csv
      --metadati metadati_piano_vN.json --verdetto verdetto_vN.json
      [--orari orari_pasti.csv] [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
      --out-html scheda.html [--out-pdf scheda.pdf]
  python3 genera_scheda_cucina.py --autotest
"""
import argparse
import html
import json
import os
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import formati
import genera_zona_piano as gzp
from genera_zona_piano import Fermo
import tabelle_conversione as tc

E = html.escape
FOOD_UOVO = "1800"
NOMI_BREVI = {"702901": "Olio EVO", "391": "Pomodori", "392": "Pomodori pelati",
              "1515": "Tonno al naturale", "8520": "Vitellone magro", "123200": "Spigola",
              "150030": "Yogurt greco 0%", "1631": "Yogurt parz. scremato",
              "135020": "Latte p.s.", "9090": "Piadina", "999057": "Cereali integrali",
              "8711": "Prosciutto crudo sgrassato", "8807": "Mela", "4005": "Ceci lessati",
              "4505": "Lenticchie lessate", "000550": "Pane integrale"}
GIORNI = {"lun": "Lunedì", "mar": "Martedì", "mer": "Mercoledì", "gio": "Giovedì",
          "ven": "Venerdì", "sab": "Sabato", "dom": "Domenica"}
CSS = """@page{size:A4;margin:12mm 13mm}*{box-sizing:border-box}
:root{--blu:#1d3a4a;--ver:#2e7d8c;--ara:#c0562b;--gr:#5b6770;--lin:#d5e0e3;--ten:#f1f6f7}
body{margin:0;font-family:'Liberation Sans',Arial,sans-serif;font-size:10pt;line-height:1.35;color:#1f2529;background:#fff}
.pag{page-break-after:always;height:272mm;display:flex;flex-direction:column}.pag:last-child{page-break-after:auto}
.top{display:flex;justify-content:space-between;font-size:8.5pt;color:var(--gr);border-bottom:1.5px solid var(--ver);padding-bottom:3px}.top b{color:var(--ver)}
h1{font-size:19pt;color:var(--blu);margin:7px 0 1px}.sub{color:var(--gr);font-size:9.5pt;margin-bottom:5px}
h2{font-size:11pt;color:var(--ara);margin:8px 0 4px}h2 span{color:var(--gr);font-weight:normal;font-size:9pt}
.t{font-weight:bold;color:var(--blu)}.griglia{display:grid;gap:5px 10px;grid-template-columns:1fr 1fr}
.voci{display:flex;flex-wrap:wrap;gap:0 9px;font-size:9.5pt}.voci span{white-space:nowrap}
.card{background:var(--ten);border-radius:4px;padding:4px 8px;break-inside:avoid}.l{color:var(--ver);font-weight:bold;margin-right:3px}.sc{color:var(--gr);font-size:9pt}
.gg{break-inside:avoid;border:1px solid var(--lin);border-radius:5px;overflow:hidden}.gg .d{background:var(--ver);color:#fff;font-weight:bold;padding:2px 8px}.gg .m{padding:3px 8px;border-top:1px solid var(--lin)}.gg .d+.m{border-top:0}.gg .e{font-size:8pt;color:var(--ver);font-weight:bold;letter-spacing:.4px}
.libero{grid-column:1/3}.libero .m{display:grid;grid-template-columns:1fr 1fr;gap:10px;border-top:0}
.conv{width:100%;border-collapse:collapse;font-size:9.5pt}.conv th,.conv td{padding:3.5px 6px;text-align:center;border-bottom:1px solid var(--lin)}.conv thead th{color:var(--blu);font-weight:normal;font-size:8.5pt;border-bottom:1.5px solid var(--ver);vertical-align:bottom}.conv th.cap{text-align:left;color:var(--gr);font-style:italic}.conv tbody th{text-align:left;color:var(--blu);font-weight:bold}.conv td.sel{color:#b6c1c5}.conv tbody tr:nth-child(even){background:var(--ten)}
.n{color:var(--gr);font-size:9pt;margin-top:4px}.chip{display:inline-block;background:var(--ten);border-radius:10px;padding:1px 8px;margin:0 3px 3px 0;font-size:9.5pt}.v{display:grid;grid-template-columns:60px 1fr;gap:3px 6px;align-items:baseline}.v>b{color:var(--ver)}
.densa{font-size:9pt;line-height:1.22}.densa h1{font-size:15pt;margin:4px 0 0}.densa .sub{margin-bottom:2px}.densa h2{font-size:10pt;margin:4px 0 2px}.densa .griglia{gap:3px 8px}.densa .voci{font-size:8.5pt}.densa .card{padding:2px 6px}.densa .gg .m{padding:1px 6px}.densa .gg .e{font-size:7pt}
.foot{margin-top:auto;border-top:1px solid var(--lin);padding-top:3px;color:var(--gr);font-size:8pt;display:flex;justify-content:space-between;gap:12px}"""


def _g(v):
    return f"{float(v):g} g"


def voce(r, nomi, uovo_g, etichetta=frozenset()):
    """Le voci da etichetta portano anche la nota di peso del file --nomi-eccezione."""
    fid, g = r["food_id"], float(r["grammi"])
    if fid == FOOD_UOVO:
        n = round(g / uovo_g)
        return f"{n} uov{'o' if n == 1 else 'a'}"
    nome = nomi.get(fid, (fid,))
    nota = nome[1] if isinstance(nome, tuple) and len(nome) > 1 else ""
    nome = nome[0] if isinstance(nome, tuple) else nome
    if fid in etichetta and nota:
        nome = f"{nome} ({nota})"
    return f"{NOMI_BREVI.get(fid) or nome} {_g(g)}"


def _sel(piano, giorno, pasto, opzione=None):
    return [r for r in piano if r["giorno"] == giorno and r["pasto"] == pasto
            and (opzione is None or r["opzione"] == opzione)]


def _opzioni(piano, giorno, pasto):
    return sorted({r["opzione"] for r in _sel(piano, giorno, pasto)})


def _fisso(piano, pasto):
    """Colazione e spuntini stanno una volta sola: devono essere uguali ogni giorno."""
    per_giorno = {}
    for r in piano:
        if r["pasto"] == pasto:
            per_giorno.setdefault(r["giorno"], set()).add((r["opzione"], r["food_id"], r["grammi"]))
    if len(set(map(frozenset, per_giorno.values()))) > 1:
        raise Fermo(f"scheda: {pasto} diverso tra i giorni, la scheda lo mostra una volta sola")


def _orario(orari, primo, pasto):
    o = orari.get((primo, pasto)) or orari.get(("*", pasto))
    return f" ore {o}" if o else ""


def _tabella_html(t):
    """Una riga per alternativa, una colonna per ogni voce del piano."""
    testa = "".join(f"<th>{E(r['nome'])}<br><b>{r['grammi']:g} g</b></th>" for r in t["righe"])
    corpo = ""
    for i, col in enumerate(t["colonne"]):
        celle = "".join("<td class=sel>—</td>" if r["celle"][i] is None
                        else f"<td>{r['celle'][i]['grammi']}\u00a0g</td>" for r in t["righe"])
        corpo += f"<tr><th>{E(col)}</th>{celle}</tr>"
    return (f"<table class=conv><thead><tr><th class=cap>Al posto di →</th>{testa}</tr></thead>"
            f"<tbody>{corpo}</tbody></table>")


def scarto_massimo(t):
    valori = [c["scarto_kcal"] for r in t["righe"] for c in r["celle"] if c]
    return (min(valori), max(valori)) if valori else None


def _nota_scarto(t):
    s = scarto_massimo(t)
    return f"<div class=n>Scarto di energia degli scambi: da {s[0]:+d} a {s[1]:+d} kcal.</div>" if s else ""


def _voci(rr, nomi, uovo_g, etichetta=frozenset()):
    out = ""
    for r in rr:
        v = voce(r, nomi, uovo_g, etichetta)
        if r["food_id"] == FOOD_UOVO:
            out += f"<span><b>{E(v)}</b></span>"
        else:
            nome, peso = v.rsplit(" ", 1)
            out += f"<span>{E(nome)} <b>{E(peso)}</b></span>"
    return f"<div class=voci>{out}</div>"


def componi(piano, db, nomi, meta, orari, etichetta=frozenset()):
    """etichetta: i food_id delle voci da etichetta dichiarate. Stanno nella settimana;
    le tabelle leggono solo i loro elenchi, quindi non le propongono mai come scambio."""
    titoli = meta["titoli_piatti"]
    giorni = sorted({r["giorno"] for r in piano}, key=int)
    primo = giorni[0]
    uovo_g = formati.carica_formati().get(FOOD_UOVO, {"unita": [52.0]})["unita"][0]
    for p in ("colazione", "spuntino", "spuntino2"):
        _fisso(piano, p)
    ab = gzp._abbinamenti(meta) or {}

    def piatto(giorno, pasto, opzione):
        return (f"<div class=t>{E(gzp._titolo(titoli, giorno, pasto, opzione))}</div>"
                + _voci(_sel(piano, giorno, pasto, opzione), nomi, uovo_g, etichetta))

    def carte(pasto):
        out = ""
        for o in _opzioni(piano, primo, pasto):
            fr = ""
            if pasto == "colazione" and o in ab:
                fr = f" <span class=sc>→ spuntino {E(' o '.join(ab[o]))}</span>"
            let = f"<span class=l>{E(o)}</span>" if o else ""
            t = E(gzp._titolo(titoli, primo, pasto, o))
            out += (f"<div class=card>{let}<span class=t>{t}</span>{fr}"
                    + _voci(_sel(piano, primo, pasto, o), nomi, uovo_g, etichetta) + "</div>")
        return out

    def ora(pasto):
        return _orario(orari, primo, pasto).replace(" ore ", "ore ")

    def cont(pasto):
        return sorted((r["opzione"], r["food_id"], r["grammi"]) for r in _sel(piano, primo, pasto))

    def tit(pasto):
        return [gzp._titolo(titoli, primo, pasto, o) for o in _opzioni(piano, primo, pasto)]

    def sez(nome, pasto):
        n = len(_opzioni(piano, primo, pasto))
        nota = ", ".join(x for x in ("una a scelta" if n > 1 else "", ora(pasto)) if x)
        return f"<h2>{nome} <span>{E(nota)}</span></h2>"

    if any(r["pasto"] == "spuntino2" for r in piano):
        if cont("spuntino") == cont("spuntino2") and tit("spuntino") == tit("spuntino2"):
            orari_sp = " e ".join(x for x in (ora("spuntino"), ora("spuntino2")) if x)
            nota = ", ".join(x for x in ("uno a scelta", orari_sp) if x)
            spuntini = f"<h2>Spuntini <span>{E(nota)}</span></h2><div class=griglia>{carte('spuntino')}</div>"
        else:
            spuntini = (f"<div class=griglia><div>{sez('Spuntino', 'spuntino')}{carte('spuntino')}</div>"
                        f"<div>{sez('Secondo spuntino', 'spuntino2')}{carte('spuntino2')}</div></div>")
    else:
        spuntini = sez("Spuntino", "spuntino") + f"<div class=griglia>{carte('spuntino')}</div>"

    lav = meta["giorni"]["lavorativi"]
    gg = ""
    for i, g in enumerate(giorni):
        nome = GIORNI.get(str(lav[i]).lower()[:3], str(lav[i]))
        blocchi = ""
        for pasto, et in (("pranzo", "PRANZO"), ("cena", "CENA")):
            orario = ora(pasto)
            testa = f"{et}{' · ' + E(orario) if orario else ''}"
            for o in _opzioni(piano, g, pasto):
                let = f" {E(o)}" if o else ""
                blocchi += f"<div class=m><div class=e>{testa}{let}</div>{piatto(g, pasto, o)}</div>"
        gg += f"<div class=gg><div class=d>{E(nome)}</div>{blocchi}</div>"
    lib = meta.get("indicazioni_giorno_libero")
    if isinstance(lib, dict):
        nome = GIORNI.get(str(meta["giorni"].get("libero", "")).lower()[:3], "Giorno libero")
        gg += (f"<div class='gg libero'><div class=d>{E(nome)} · pasto libero</div><div class=m>"
               f"<div><span class=e>PRANZO</span> {E(lib['pranzo'])}</div>"
               f"<div><span class=e>CENA</span> {E(lib['cena'])}</div></div></div>")

    carbo, pesce, verd = (tc.tabella_carboidrati(piano, db), tc.tabella_pesce(piano, db),
                          tc.tabella_verdure(piano, db))
    note = meta.get("scheda_cucina") or {}
    seg = "".join(f" {E(s)}." for s in verd["segnalate"])
    chip = lambda k: "".join(f"<span class=chip>{E(x)}</span>" for x in verd["gruppi"][k])
    sez_c = (f"<h2>Carboidrati <span>stessa quantità di carboidrati</span></h2>{_tabella_html(carbo)}"
             f"{_nota_scarto(carbo)}" if carbo["righe"] else "")
    if note.get("note_carboidrati"):
        sez_c += f"<div class=n>{E(note['note_carboidrati'])}</div>"
    sez_p = (f"<h2>Pesce <span>stessa quantità di proteine</span></h2>{_tabella_html(pesce)}"
             f"{_nota_scarto(pesce)}" if pesce["righe"] else "")
    sez_v = (f"<h2>Verdure <span>stesso peso, stesso gruppo</span></h2><div class=v><b>Crude</b>"
             f"<div>{chip('crude')}</div><b>Cotte</b><div>{chip('cotte')}</div></div>"
             f"<div class=n>Patate e legumi non si scambiano con le verdure.{seg}</div>")
    top = ("<div class=top><span><b>Dott. Giuseppe Taglialatela</b> — Consulente in Nutrizione</span>"
           "<span>Scheda per chi cucina</span></div>")
    nome_paz = E(meta["intestazione"]["nome"])
    piede = " · ".join(x for x in ("Pesi sempre a crudo, tranne legumi lessati e scatolame",
                                   E(note.get("note_piede", ""))) if x)
    foot = lambda n: (f"<div class=foot><span>{piede}</span><span>Studio Nutrizionale "
                      f"Taglialatela · {n}/2</span></div>")
    pagina = f"""<!doctype html><html lang=it><head><meta charset=utf-8><title>Scheda per chi cucina</title><style>{CSS}</style></head><body>
<div class=pag>{top}<h1>La settimana</h1><div class=sub>{nome_paz}</div>
{sez('Colazione', 'colazione')}<div class=griglia>{carte('colazione')}</div>{spuntini}
<h2>Pranzo e cena</h2><div class=griglia>{gg}</div>{foot(1)}</div>
<div class=pag>{top}<h1>Come scambiare gli alimenti</h1><div class=sub>{nome_paz} · Lo scambio vale nello stesso pasto</div>
{sez_c}{sez_p}{sez_v}{foot(2)}</div></body></html>"""
    return pagina, {"carboidrati": carbo, "pesce": pesce, "verdure": verd}


def _prepara(piano_p, target_p, meta_p, orari_p=None, **kw):
    gzp.verifica(piano_p, target_p, meta_p, orari_p, **kw)     # verdetto e impronta
    db, nomi, piano, _t, meta, _v = gzp._prepara(piano_p, target_p, meta_p, **kw)
    etichetta = frozenset(db) - frozenset(tc.carica_db())
    return componi(piano, db, nomi, meta, gzp.carica_orari(orari_p), etichetta)


def in_pdf(html_p, pdf_p):
    """PDF con Chromium. La pagina si misura alla larghezza di stampa: se il contenuto
    non sta, si passa alla versione compatta; se non basta, ci si ferma."""
    from playwright.sync_api import sync_playwright
    sborda = ("[...document.querySelectorAll('.pag')].some("
              "p => p.scrollHeight > p.clientHeight + 1)")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pag = b.new_page(viewport={"width": 695, "height": 1028})
        pag.goto("file://" + os.path.abspath(html_p))
        pag.emulate_media(media="print")
        troppo = pag.evaluate(sborda)
        if troppo:
            pag.evaluate("document.body.classList.add('densa')")
            troppo = pag.evaluate(sborda)
        if not troppo:
            pag.pdf(path=pdf_p, prefer_css_page_size=True, print_background=True)
        b.close()
    if troppo:
        raise Fermo("scheda: il contenuto non sta nelle due pagine, PDF non generato")


def riepilogo(tabelle):
    """Righe per il nutrizionista, in chat: gli scarti e cio' che resta fuori."""
    L = []
    for nome in ("carboidrati", "pesce"):
        s = scarto_massimo(tabelle[nome])
        L.append(f"{nome}: {len(tabelle[nome]['righe'])} righe" +
                 (f", scarto da {s[0]:+d} a {s[1]:+d} kcal" if s else ""))
    if tabelle["verdure"]["fuori_elenco"]:
        L.append("verdure del piano fuori elenco: " + ", ".join(tabelle["verdure"]["fuori_elenco"]))
    return L


def autotest():
    import io
    import json as _j
    from contextlib import redirect_stdout
    import metadati_piano as mod_meta
    import pipeline as mod_pipeline
    tmp = tempfile.mkdtemp()
    _caso, piano_c, target_c = gzp._piano_di_collaudo(tmp)
    meta = {"versione_piano": "v1",
            "giorni": {"lavorativi": ["lun"], "libero": "dom", "range_kcal_libero": [1600, 1900]},
            "livello_colazione": "standard", "tdee_confermato_kcal": 2040,
            "intestazione": {"nome": "Paziente Fittizio", "eta": "40 anni", "condizione": "Collaudo"},
            "avvertenze_box": "Nessuna allergia dichiarata (collaudo).",
            "abbinamento_spuntino": {"A": "B", "B": "A"},
            "indicazioni_giorno_libero": {"pranzo": "a piacere", "cena": "a piacere, senza fritti"},
            "titoli_piatti": {"*|colazione|A": "Colazione A", "*|colazione|B": "Colazione B",
                              "*|spuntino|A": "Spuntino A", "*|spuntino|B": "Spuntino B",
                              "1|pranzo|": "Pranzo di collaudo", "1|cena|": "Cena di collaudo"},
            "obiettivo_intestazione": "collaudo", "criterio_rivalutazione": "collaudo",
            "terapia": "nessuna terapia, confermato dal nutrizionista il 23/10/2026 (fonte: colloquio)",
            "assunzioni": [], "alimenti_desiderati": [], "profili": [],
            "scheda_cucina": {"note_carboidrati": "Nota di collaudo.", "note_piede": "Piede di collaudo"}}
    mp, vp = os.path.join(tmp, "m.json"), os.path.join(tmp, "v.json")
    kw = dict(verdetto_p=vp, _collaudo_saltato_ok=True)

    def scrivi(m):
        with open(mp, "w", encoding="utf-8") as f:
            _j.dump(m, f)
        with redirect_stdout(io.StringIO()):
            ril, letti = mod_pipeline.esegui(piano_c, target_c, metadati_p=mp,
                                             salta_collaudo=True, nessuna_terapia=True)
        mod_meta.scrivi_verdetto(vp, ril, piano_c, target_c, letti)
    problemi = []
    scrivi(meta)
    testo, imp = gzp.anteprima(piano_c, target_c, mp, **kw)
    if "Nota di collaudo." not in testo:
        problemi.append("i testi della scheda non sono nell'anteprima")
    try:                                                     # senza approvazione: fermo
        _prepara(piano_c, target_c, mp, **kw)
        problemi.append("scheda generata senza impronta approvata")
    except Fermo:
        pass
    meta["impronta_approvata"] = imp
    scrivi(meta)
    try:
        pagina, tab = _prepara(piano_c, target_c, mp, **kw)
    except Fermo as e:
        return [f"scheda non generata sul piano approvato: {e}"]
    for atteso in ("La settimana", "Come scambiare gli alimenti", "Paziente Fittizio",
                   "Pranzo di collaudo", "Domenica",
                   "Nota di collaudo.", "Piede di collaudo", "Patate e legumi", "Carote"):
        if atteso not in pagina:
            problemi.append(f"scheda senza «{atteso}»")
    if "(&#x27;" in pagina or "(\'" in pagina:
        problemi.append("nomi degli alimenti scritti come coppie grezze")
    # le celle vengono dal calcolo, a parita' di carboidrati e di proteine
    db = tc.carica_db()
    prova = [{"pasto": "pranzo", "food_id": "000550", "grammi": "100"},
             {"pasto": "cena", "food_id": "1313", "grammi": "180"},
             {"pasto": "cena", "food_id": "381", "grammi": "250"}]
    t = tc.tabella_carboidrati(prova, db)
    i = t["colonne"].index("Couscous")
    pane = [r for r in t["righe"] if r["food_id"] == "000550"][0]
    if pane["celle"][i]["grammi"] != 60:
        problemi.append("pane integrale 100 g in couscous non vale 60 g")
    if [r["food_id"] for r in t["righe"]] != ["000550", "381"]:
        problemi.append("righe dei carboidrati non legate al piano")
    if tc.tabella_pesce(prova, db)["righe"][0]["celle"][1]["grammi"] != 185:
        problemi.append("merluzzo 180 g in spigola non vale 185 g")
    if tc.tabella_verdure(prova, db)["segnalate"] == []:
        problemi.append("nessuna verdura segnalata")
    problemi += _autotest_etichetta(tmp, meta)
    return problemi


def _autotest_etichetta(tmp, meta):
    """Voce da etichetta FITTIZIA in un piano approvato: con i due file la scheda si
    genera, con il nome e la nota di peso e senza proporla come scambio; senza un
    file si ferma. Con la voce arrivata al calcolo, le tabelle non si fermano."""
    import io
    import json as _j
    import shutil
    from contextlib import redirect_stdout
    import metadati_piano as mod_meta
    import pipeline as mod_pipeline
    d = os.path.join(tmp, "etichetta")
    os.mkdir(d)
    _c, piano_c, target_c = gzp._piano_di_collaudo(d)
    with open(piano_c, "a", encoding="utf-8") as f:
        f.write("1,pranzo,ETI_TEST,30,,\n")
    voci = os.path.join(d, "voci.csv")
    shutil.copy(os.path.join(QUI, "golden", "caso_18_eccezione_etichetta_dichiarata",
                             "voci_etichetta.csv"), voci)
    nomi_p = os.path.join(d, "nomi.csv")
    with open(nomi_p, "w", encoding="utf-8") as f:
        f.write("food_id,nome_paziente,nota_peso\nETI_TEST,Vellutata di prova,peso da confezione\n")
    m = {k: v for k, v in meta.items() if k != "impronta_approvata"}
    mp, vp = os.path.join(d, "m.json"), os.path.join(d, "v.json")

    def scrivi(x):
        with open(mp, "w", encoding="utf-8") as f:
            _j.dump(x, f)
        with redirect_stdout(io.StringIO()):
            ril, letti = mod_pipeline.esegui(piano_c, target_c, metadati_p=mp, salta_collaudo=True,
                                             nessuna_terapia=True, eccezione_etichetta=voci)
        mod_meta.scrivi_verdetto(vp, ril, piano_c, target_c, letti)
    base = dict(verdetto_p=vp, _collaudo_saltato_ok=True)
    con = dict(base, eccezione_p=voci, nomi_eccezione_p=nomi_p)
    scrivi(m)
    m["impronta_approvata"] = gzp.anteprima(piano_c, target_c, mp, **con)[1]
    scrivi(m)
    problemi = []
    try:
        pagina, tab = _prepara(piano_c, target_c, mp, **con)
    except Fermo as e:
        return [f"scheda con voce da etichetta fermata: {e}"]
    if "Vellutata di prova (peso da confezione)" not in pagina:
        problemi.append("voce da etichetta senza nome o nota di peso")
    if any("ETI" in c or "Vellutata" in c for t in (tab["carboidrati"], tab["pesce"])
           for c in t["colonne"]) or "Vellutata" in str(tab["verdure"]["gruppi"]):
        problemi.append("voce da etichetta proposta come scambio")
    for nome, kw in (("senza i file", base), ("senza i nomi", dict(base, eccezione_p=voci)),
                     ("nomi senza voci", dict(base, nomi_eccezione_p=nomi_p))):
        try:
            _prepara(piano_c, target_c, mp, **kw)
            problemi.append(f"voce da etichetta accettata {nome}")
        except Fermo:
            pass
    with open(os.path.join(QUI, "alimenti.csv"), encoding="utf-8") as f:
        if "ETI_TEST" in f.read():
            problemi.append("voce da etichetta in alimenti.csv")
    return problemi


def main():
    a = argparse.ArgumentParser(description="Scheda per chi cucina")
    a.add_argument("--piano"); a.add_argument("--target"); a.add_argument("--metadati")
    a.add_argument("--verdetto"); a.add_argument("--orari"); a.add_argument("--out-html")
    a.add_argument("--out-pdf"); a.add_argument("--autotest", action="store_true")
    a.add_argument("--eccezione-etichetta", dest="eccezione")
    a.add_argument("--nomi-eccezione", dest="nomi_eccezione")
    o = a.parse_args()
    if o.autotest:
        p = autotest()
        print("\n".join(p) or "Autotest della scheda superato.")
        return 1 if p else 0
    try:
        pagina, tabelle = _prepara(o.piano, o.target, o.metadati, o.orari, verdetto_p=o.verdetto,
                                   eccezione_p=o.eccezione, nomi_eccezione_p=o.nomi_eccezione)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    with open(o.out_html, "w", encoding="utf-8") as f:
        f.write(pagina)
    print("\n".join(riepilogo(tabelle)))
    if o.out_pdf:
        try:
            in_pdf(o.out_html, o.out_pdf)
        except Fermo as e:
            print(f"FERMO: {e}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
