#!/usr/bin/env python3
"""
Scheda di una pagina per chi cucina, con le tabelle di conversione (04/11/2026).

Modello grafico: la scheda scritta a mano per un piano reale, approvata dal
nutrizionista il 04/11/2026 come formato delle tabelle. Qui i dati vengono tutti da
piano, metadati e alimenti.csv: nessuna grammatura scritta a mano.

Si genera dopo i controlli del piano: stesso verdetto e stessa impronta approvata
del PDF (genera_zona_piano.verifica). Testi facoltativi nei metadati, approvati con
l'anteprima: scheda_cucina = {"note_carboidrati": "...", "note_piede": "..."}.

USO
  python3 genera_scheda_cucina.py --piano piano_vN.csv --target target_vN.csv
      --metadati metadati_piano_vN.json --verdetto verdetto_vN.json
      [--orari orari_pasti.csv] --out-html scheda.html [--out-pdf scheda.pdf]
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
CSS = """@page{size:A4;margin:9mm 10mm}*{box-sizing:border-box}body{margin:0;font-family:'Liberation Sans',Arial,sans-serif;font-size:8.9pt;line-height:1.25;color:#1b1b1b;background:#fff}
.top{display:flex;justify-content:space-between;border-bottom:1px solid #2e7d8c;padding-bottom:2px;color:#2e6b7a;font-weight:bold}.top i{font-weight:normal;color:#555}
h1{font-size:17pt;color:#1d3a4a;text-align:center;margin:4px 0 0}.sub{text-align:center;font-style:italic;color:#555;margin-bottom:3px}
h2{font-size:10.5pt;color:#c0562b;margin:5px 0 2px}.tit{font-weight:bold;color:#1d3a4a}.cols{display:grid;grid-template-columns:1.9fr 1fr;gap:8px}.gr{display:grid;grid-template-columns:1fr 1fr;gap:2px 8px}.op{padding:1px 0}
table{width:100%;border-collapse:collapse}th,td{border:1px solid #c9d6da;padding:2px 4px;vertical-align:top}thead th{background:#2e7d8c;color:#fff;text-align:center}tbody th{text-align:left;color:#1d3a4a;width:58px;background:#f0f5f6}tbody tr:nth-child(even) td{background:#f7fafa}
.c td,.c th{text-align:center;white-space:nowrap;padding:2px 3px}.c tbody th{width:auto;text-align:left}.nota{font-style:italic;color:#555;margin-top:2px}.d{display:grid;grid-template-columns:1fr 1fr;gap:8px}.foot{margin-top:4px;border-top:1px solid #ccc;padding-top:2px;color:#666;display:flex;justify-content:space-between;font-size:8pt}"""


def _g(v):
    return f"{float(v):g} g"


def voce(r, nomi, uovo_g):
    fid, g = r["food_id"], float(r["grammi"])
    if fid == FOOD_UOVO:
        n = round(g / uovo_g)
        return f"{n} uov{'o' if n == 1 else 'a'}"
    nome = nomi.get(fid, (fid,))
    nome = nome[0] if isinstance(nome, tuple) else nome
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
        raise Fermo(f"scheda: {pasto} diverso tra i giorni, la pagina unica non lo regge")


def _orario(orari, primo, pasto):
    o = orari.get((primo, pasto)) or orari.get(("*", pasto))
    return f" ore {o}" if o else ""


def _tabella_html(t, intestazione_riga="Nel piano"):
    testa = "".join(f"<th>{E(c)}</th>" for c in t["colonne"])
    corpo = ""
    for r in t["righe"]:
        celle = "".join("<td>—</td>" if c is None else f"<td>{c['grammi']} g</td>"
                        for c in r["celle"])
        corpo += f"<tr><th>{E(r['nome'])} {_g(r['grammi'])}</th>{celle}</tr>"
    return (f"<table class=c><thead><tr><th>{intestazione_riga}</th>{testa}</tr></thead>"
            f"<tbody>{corpo}</tbody></table>")


def scarto_massimo(t):
    valori = [c["scarto_kcal"] for r in t["righe"] for c in r["celle"] if c]
    return (min(valori), max(valori)) if valori else None


def _nota_scarto(t):
    s = scarto_massimo(t)
    return f"<div class=nota>Scarto di energia degli scambi: da {s[0]:+d} a {s[1]:+d} kcal.</div>" if s else ""


def componi(piano, db, nomi, meta, orari):
    titoli = meta["titoli_piatti"]
    giorni = sorted({r["giorno"] for r in piano}, key=int)
    primo = giorni[0]
    uovo_g = formati.carica_formati().get(FOOD_UOVO, {"unita": [52.0]})["unita"][0]
    for p in ("colazione", "spuntino", "spuntino2"):
        _fisso(piano, p)
    ab = gzp._abbinamenti(meta) or {}

    def blocco(giorno, pasto, opzione, freccia=""):
        rr = _sel(piano, giorno, pasto, opzione)
        t = gzp._titolo(titoli, giorno, pasto, opzione)
        lista = " · ".join(voce(r, nomi, uovo_g) for r in rr)
        return f"<span class=tit>{E(t)}</span><br>{E(lista)}{freccia}"

    def opz(pasto):
        out = ""
        for o in _opzioni(piano, primo, pasto):
            fr = ""
            if pasto == "colazione" and o in ab:
                fr = f" <i>→ spuntino {E(' o '.join(ab[o]))}</i>"
            let = f"<b>{E(o)}</b> " if o else ""
            out += f"<div class=op>{let}{blocco(primo, pasto, o, fr)}</div>"
        return out

    righe = ""
    lav = meta["giorni"]["lavorativi"]
    for i, g in enumerate(giorni):
        nome = GIORNI.get(str(lav[i]).lower()[:3], str(lav[i]))
        cc = []
        for pasto in ("pranzo", "cena"):
            ops = _opzioni(piano, g, pasto)
            if len(ops) > 1 or (ops and ops[0]):
                cc.append("".join(f"<div><b>{E(o)}</b> {blocco(g, pasto, o)}</div>" for o in ops))
            else:
                cc.append(blocco(g, pasto, "") if ops else "")
        righe += f"<tr><th>{E(nome)}</th><td>{cc[0]}</td><td>{cc[1]}</td></tr>"
    lib = meta.get("indicazioni_giorno_libero")
    if isinstance(lib, dict):
        nome = GIORNI.get(str(meta["giorni"].get("libero", "")).lower()[:3], "Giorno libero")
        righe += (f"<tr><th>{E(nome)}</th><td><span class=tit>Pasto libero</span><br>{E(lib['pranzo'])}</td>"
                  f"<td><span class=tit>Pasto libero</span><br>{E(lib['cena'])}</td></tr>")

    carbo, pesce, verd = (tc.tabella_carboidrati(piano, db), tc.tabella_pesce(piano, db),
                          tc.tabella_verdure(piano, db))
    note = meta.get("scheda_cucina") or {}
    seg = "".join(f" {E(s)}." for s in verd["segnalate"])
    sez_v = (f"<h2>VERDURE: stesso peso, stesso gruppo</h2><table><tbody>"
             f"<tr><th>Crude</th><td>{E(', '.join(verd['gruppi']['crude']))}</td></tr>"
             f"<tr><th>Cotte</th><td>{E(', '.join(verd['gruppi']['cotte']))}</td></tr></tbody></table>"
             f"<div class=nota>Patate e legumi non si scambiano con le verdure.{seg}</div>")
    sez_p = (f"<h2>PESCE: a parità di proteine</h2>{_tabella_html(pesce)}{_nota_scarto(pesce)}"
             if pesce["righe"] else "")
    sez_c = (f"<h2>CARBOIDRATI: a parità di carboidrati</h2>{_tabella_html(carbo)}{_nota_scarto(carbo)}"
             if carbo["righe"] else "")
    if note.get("note_carboidrati"):
        sez_c += f"<div class=nota>{E(note['note_carboidrati'])}</div>"
    sp2 = ""
    if any(r["pasto"] == "spuntino2" for r in piano):
        sp2 = f"<h2>SECONDO SPUNTINO{_orario(orari, primo, 'spuntino2')}</h2>{opz('spuntino2')}"
    nome_paz = meta["intestazione"]["nome"]
    pagina = f"""<!doctype html><html lang=it><head><meta charset=utf-8><title>Scheda per chi cucina</title><style>{CSS}</style></head><body>
<div class=top><span>Dott. Giuseppe Taglialatela <i>— Consulente in Nutrizione</i></span><span>Scheda per chi cucina</span></div>
<h1>LA SETTIMANA IN UNA PAGINA</h1><div class=sub>{E(nome_paz)} · pesi sempre a crudo, tranne legumi lessati e scatolame</div>
<div class=cols><div><h2>COLAZIONE (una a scelta)</h2><div class=gr>{opz('colazione')}</div></div><div><h2>SPUNTINO{_orario(orari, primo, 'spuntino')}</h2>{opz('spuntino')}{sp2}</div></div>
<h2>PRANZO E CENA</h2><table><thead><tr><th>Giorno</th><th>Pranzo{_orario(orari, primo, 'pranzo').replace(' ore', ', ore')}</th><th>Cena{_orario(orari, primo, 'cena').replace(' ore', ', ore')}</th></tr></thead><tbody>{righe}</tbody></table>
<div class=d><div>{sez_v}{sez_p}</div><div>{sez_c}</div></div>
<div class=foot><span>{E(note.get('note_piede', ''))}</span><span>Studio Nutrizionale Taglialatela</span></div></body></html>"""
    return pagina, {"carboidrati": carbo, "pesce": pesce, "verdure": verd}


def _prepara(piano_p, target_p, meta_p, orari_p=None, **kw):
    gzp.verifica(piano_p, target_p, meta_p, orari_p, **kw)     # verdetto e impronta
    db, nomi, piano, _t, meta, _v = gzp._prepara(piano_p, target_p, meta_p, **kw)
    return componi(piano, db, nomi, meta, gzp.carica_orari(orari_p))


def in_pdf(html_p, pdf_p):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pag = b.new_page()
        pag.goto("file://" + os.path.abspath(html_p))
        pag.pdf(path=pdf_p, prefer_css_page_size=True, print_background=True)
        b.close()


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
    for atteso in ("LA SETTIMANA IN UNA PAGINA", "Paziente Fittizio", "Pranzo di collaudo",
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
    return problemi


def main():
    a = argparse.ArgumentParser(description="Scheda per chi cucina")
    a.add_argument("--piano"); a.add_argument("--target"); a.add_argument("--metadati")
    a.add_argument("--verdetto"); a.add_argument("--orari"); a.add_argument("--out-html")
    a.add_argument("--out-pdf"); a.add_argument("--autotest", action="store_true")
    o = a.parse_args()
    if o.autotest:
        p = autotest()
        print("\n".join(p) or "Autotest della scheda superato.")
        return 1 if p else 0
    try:
        pagina, tabelle = _prepara(o.piano, o.target, o.metadati, o.orari, verdetto_p=o.verdetto)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    with open(o.out_html, "w", encoding="utf-8") as f:
        f.write(pagina)
    print("\n".join(riepilogo(tabelle)))
    if o.out_pdf:
        in_pdf(o.out_html, o.out_pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
