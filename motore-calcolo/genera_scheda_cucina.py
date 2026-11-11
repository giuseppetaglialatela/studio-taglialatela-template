#!/usr/bin/env python3
"""
Scheda per chi cucina (04/11/2026): la settimana, a riquadri per giorno, e le tabelle
di conversione. Si adatta da sola al contenuto: due pagine finche' si puo', con spazi
e scrittura ridotti fino al minimo di 9 punti per gli ingredienti, poi tre pagine.

Grafica approvata dal nutrizionista il 04/11/2026: griglie regolari, stile del piano. Qui i dati vengono tutti da
piano, metadati e alimenti.csv: nessuna grammatura scritta a mano.

Si genera dopo i controlli del piano: stesso verdetto e stessa impronta approvata
del PDF (genera_zona_piano.verifica). Testi facoltativi nei metadati, approvati con
l'anteprima: scheda_cucina = {"note_carboidrati": "...", "note_piede": "..."}.

USO
  python3 genera_scheda_cucina.py --piano piano_vN.csv --target target_vN.csv
      --metadati metadati_piano_vN.json --verdetto verdetto_vN.json
      [--orari orari_pasti.csv] [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
      [--esclusioni esclusioni.json]
      --out-html scheda.html [--out-pdf scheda.pdf]
  python3 genera_scheda_cucina.py --autotest
"""
import argparse
import html
import json
import os
import re
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import formati
import genera_zona_piano as gzp
from genera_zona_piano import Fermo
import tabelle_conversione as tc

E = html.escape
NOMI_BREVI = {"702901": "Olio EVO", "391": "Pomodori", "392": "Pomodori pelati",
              "1515": "Tonno al naturale", "8520": "Vitellone magro", "123200": "Spigola",
              "150030": "Yogurt greco 0%", "1631": "Yogurt parz. scremato",
              "135020": "Latte p.s.", "9090": "Piadina", "999057": "Cereali integrali",
              "8711": "Prosciutto crudo sgrassato", "8807": "Mela", "4005": "Ceci lessati",
              "4505": "Lenticchie lessate", "000550": "Pane integrale"}
GIORNI = {"lun": "Lunedì", "mar": "Martedì", "mer": "Mercoledì", "gio": "Giovedì",
          "ven": "Venerdì", "sab": "Sabato", "dom": "Domenica"}
CSS = """@page{size:A4;margin:11mm 15mm 10mm}*{box-sizing:border-box}
:root{--navy:#1C3A4A;--teal:#2E7D8C;--ara:#C0622B;--gr:#666;--lin:#CCC;--ten:#F4F8F9;--testo:#333}
body{margin:0;width:180mm;font-family:'Liberation Sans',Arial,sans-serif;color:#1A1A1A;background:#fff}
.pag{page-break-after:always;height:275mm;display:flex;flex-direction:column;font-size:var(--fs,10pt);line-height:var(--lh,1.32)}.pag:last-child{page-break-after:auto}
.top{font-size:9pt;color:var(--gr);border-bottom:.7pt solid var(--teal);padding-bottom:3px}.top b{color:var(--teal)}.top i{font-style:italic}
h1{font-size:var(--h1,19pt);color:var(--navy);text-align:center;margin:var(--mh1,10px 0 1px)}.sub{color:var(--gr);font-style:italic;font-size:9pt;text-align:center;margin-bottom:var(--msub,6px)}
h2{font-size:10.5pt;color:var(--ara);margin:var(--mh,10px 0 4px);text-transform:uppercase;letter-spacing:.4px}h2 span{color:var(--gr);font-weight:normal;font-size:9pt;text-transform:none;letter-spacing:0;font-style:italic}
.griglia{display:grid;gap:var(--gap,6px 10px)}
.t{font-weight:bold;color:var(--navy);font-size:calc(var(--fs,10pt) + .5pt)}.l{color:var(--ara);font-weight:bold;margin-right:4px}.sc{color:var(--gr);font-size:8.5pt;font-style:italic}
.voci{display:flex;flex-wrap:wrap;gap:0 10px;font-size:var(--fv,9.5pt);color:var(--testo);margin-top:1px}.voci>span{max-width:100%;min-width:0;overflow-wrap:anywhere}.voci b{color:#1A1A1A;white-space:nowrap}
.card{background:var(--ten);border:.5pt solid #DCE6E9;border-radius:3px;padding:var(--pc,4px 8px);min-width:0}
.giorni{grid-template-columns:1fr 1fr}
.gg{display:grid;grid-row:span 3;grid-template-rows:subgrid;row-gap:0;border:.7pt solid var(--teal);border-radius:3px;overflow:hidden;min-width:0;break-inside:avoid}.gg .d{background:var(--teal);color:#fff;font-weight:bold;padding:2px 8px}.gg .m{padding:var(--pm,4px 8px);border-top:.5pt solid var(--lin)}.pr .m:first-child{border-top:0}.ce{border-top:.5pt solid var(--lin)}.ce .m{border-top:0}
.e{font-size:8pt;color:var(--teal);font-weight:bold;letter-spacing:.5px}.cena .e{color:var(--navy)}
.libero .m{grid-row:span 2;border-top:0}.fascia{grid-column:1/3;grid-row:span 2}.fascia .m{grid-row:auto}.fascia .m{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.conv{width:100%;border-collapse:collapse;font-size:var(--fv,9.5pt)}.conv th,.conv td{padding:var(--pt,3.5px 6px);text-align:center;border-bottom:.5pt solid var(--lin)}.conv thead th{background:var(--teal);color:#fff;font-weight:normal;font-size:8.5pt;vertical-align:bottom;border:0}.conv th.cap{text-align:left;font-style:italic}.conv tbody th{text-align:left;color:var(--navy);font-weight:bold}.conv td.sel{color:#B6C1C5}.conv tbody tr:nth-child(even){background:var(--ten)}
.n{color:var(--gr);font-size:9pt;margin-top:3px;font-style:italic}.chip{display:inline-block;background:var(--ten);border-radius:10px;padding:1px 8px;margin:0 3px 3px 0;font-size:9.5pt}.v{display:grid;grid-template-columns:60px 1fr;gap:3px 6px;align-items:baseline}.v>b{color:var(--teal)}
.foot{margin-top:auto;border-top:.5pt solid var(--lin);padding-top:3px;color:var(--gr);font-size:7.5pt;display:flex;justify-content:space-between;gap:12px}"""


def _giorno(testo):
    """Il testo dei metadati, con le abbreviazioni scritte per intero («sab o dom»)."""
    t = re.sub(r"\b(lun|mar|mer|gio|ven|sab|dom)\b",
               lambda m: GIORNI[m.group(1)].lower(), str(testo), flags=re.I)
    return t[:1].upper() + t[1:]


def colonne_griglia(n):
    """Colonne per n riquadri, mai uno solo sull'ultima riga."""
    c = {1: 1, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 3}.get(n, 4)
    if n > c and n % c == 1:
        c -= 1
    return c


def _g(v):
    return f"{float(v):g} g"


def voce(r, nomi, formati_pz, etichetta=frozenset()):
    """Le voci da etichetta portano anche la nota di peso del file --nomi-eccezione."""
    fid, g = r["food_id"], float(r["grammi"])
    a_pezzi = formati.testo_pezzi(fid, g, formati_pz, lambda x: f"{x:g}", "\u00a0")
    if a_pezzi:                          # «Uova 2 (104 g)», come nel PDF (11/11/2026)
        return a_pezzi
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


MIN_SCAMBI_COLONNA = 3


def salumi():
    """Nomi di scambi_carni.csv con ruolo salume: nella scheda portano la nota sul sale."""
    ruoli = {r["food_id"]: r["ruolo"] for r in tc._righe("ruoli_alimenti.csv")}
    return {s["nome_riferimento"] for s in tc.carica_scambi("scambi_carni.csv")
            if ruoli.get(s["food_id"]) == "salume"}


def _tabella_html(t):
    """Una riga per alternativa, una colonna per ogni voce del piano. Le voci con meno di
    tre scambi non occupano una colonna quasi vuota: vanno in una riga sotto la tabella."""
    piene = [j for j, r in enumerate(t["righe"])
             if sum(c is not None for c in r["celle"]) >= MIN_SCAMBI_COLONNA]
    testa = "".join(f"<th>{E(t['righe'][j]['nome'])}<br><b>{t['righe'][j]['grammi']:g} g</b></th>" for j in piene)
    corpo = ""
    for i, col in enumerate(t["colonne"]):
        if not any(t["righe"][j]["celle"][i] for j in piene):
            continue
        celle = "".join("<td class=sel>—</td>" if t["righe"][j]["celle"][i] is None
                        else f"<td>{t['righe'][j]['celle'][i]['grammi']}\u00a0g</td>" for j in piene)
        corpo += f"<tr><th>{E(col)}</th>{celle}</tr>"
    out = (f"<table class=conv><thead><tr><th class=cap>Al posto di →</th>{testa}</tr></thead>"
           f"<tbody>{corpo}</tbody></table>") if piene else ""
    for j, r in enumerate(t["righe"]):
        if j in piene:
            continue
        sc = ", ".join(f"{col} {c['grammi']}\u00a0g" for col, c in zip(t["colonne"], r["celle"]) if c)
        out += f"<div class=n><b>{E(r['nome'])} {r['grammi']:g} g:</b> {E(sc) if sc else 'nessuno scambio previsto'}.</div>"
    return out


def scarto_massimo(t):
    valori = [c["scarto_kcal"] for r in t["righe"] for c in r["celle"] if c]
    return (min(valori), max(valori)) if valori else None


def _nota_scarto(t):
    s = scarto_massimo(t)
    return f"<div class=n>Scarto di energia degli scambi: da {s[0]:+d} a {s[1]:+d} kcal.</div>" if s else ""


def _voci(rr, nomi, formati_pz, etichetta=frozenset()):
    out = ""
    for r in rr:
        v = voce(r, nomi, formati_pz, etichetta)
        nome, peso = v.rsplit(" ", 1)    # la quantita' usa spazi non divisibili
        out += f"<span class=x>{E(nome)} <b class=q>{E(peso)}</b></span>"
    return f"<div class=voci>{out}</div>"


def componi(piano, db, nomi, meta, orari, target_kcal, etichetta=frozenset(), pagine=2, giorni_p1=0,
            esclusioni=None):
    """etichetta: i food_id delle voci da etichetta dichiarate. Stanno nella settimana;
    le tabelle leggono solo i loro elenchi, quindi non le propongono mai come scambio."""
    titoli = meta["titoli_piatti"]
    giorni = sorted({r["giorno"] for r in piano}, key=int)
    primo = giorni[0]
    formati_pz = formati.carica_formati()      # pezzi: peso e tolleranza da formati_confezione.csv
    for p in ("colazione", "spuntino", "spuntino2"):
        _fisso(piano, p)
    ab = gzp._abbinamenti(meta) or {}

    def piatto(giorno, pasto, opzione):
        return (f"<div class=t>{E(gzp._titolo(titoli, giorno, pasto, opzione))}</div>"
                + _voci(_sel(piano, giorno, pasto, opzione), nomi, formati_pz, etichetta))

    def carte(pasto):
        out = ""
        for o in _opzioni(piano, primo, pasto):
            fr = ""
            if pasto == "colazione" and o in ab:
                fr = f" <span class=sc>→ spuntino {E(' o '.join(ab[o]))}</span>"
            let = f"<span class=l>{E(o)}</span>" if o else ""
            t = E(gzp._titolo(titoli, primo, pasto, o))
            out += (f"<div class=card>{let}<span class=t>{t}</span>{fr}"
                    + _voci(_sel(piano, primo, pasto, o), nomi, formati_pz, etichetta) + "</div>")
        return out

    def griglia_carte(pasto):
        n = len(_opzioni(piano, primo, pasto))
        return (f"<div class=griglia style='grid-template-columns:repeat({colonne_griglia(n)},1fr)'>"
                f"{carte(pasto)}</div>")

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
            spuntini = f"<h2>Spuntini <span>{E(nota)}</span></h2>{griglia_carte('spuntino')}"
        else:
            spuntini = (f"<div class=griglia><div>{sez('Spuntino', 'spuntino')}{carte('spuntino')}</div>"
                        f"<div>{sez('Secondo spuntino', 'spuntino2')}{carte('spuntino2')}</div></div>")
    else:
        spuntini = sez("Spuntino", "spuntino") + f"{griglia_carte('spuntino')}"

    lav = meta["giorni"]["lavorativi"]
    carte_g = []
    for i, g in enumerate(giorni):
        nome = _giorno(lav[i])
        blocchi = {"pranzo": "", "cena": ""}
        for pasto, et in (("pranzo", "PRANZO"), ("cena", "CENA")):
            orario = ora(pasto)
            testa = f"{et}{' · ' + E(orario) if orario else ''}"
            for o in _opzioni(piano, g, pasto):
                let = f" {E(o)}" if o else ""
                blocchi[pasto] += f"<div class=m><div class=e>{testa}{let}</div>{piatto(g, pasto, o)}</div>"
        carte_g.append(f"<div class=gg><div class=d>{E(nome)}</div><div class=pr>{blocchi['pranzo']}</div>"
                       f"<div class=ce>{blocchi['cena']}</div></div>")
    lib = meta.get("indicazioni_giorno_libero")
    if isinstance(lib, dict):
        nome = _giorno(meta["giorni"].get("libero") or "Giorno libero")
        # numero dispari di giorni: il giorno libero chiude la griglia, altrimenti fascia
        classe = "libero" if len(carte_g) % 2 else "libero fascia"
        carte_g.append(f"<div class='gg {classe}'><div class=d>{E(nome)} · pasto libero</div><div class=m>"
                       f"<div><span class=e>PRANZO</span> {E(lib['pranzo'])}</div>"
                       f"<div><span class=e>CENA</span> {E(lib['cena'])}</div></div></div>")
    primi, resto = (carte_g[:giorni_p1], carte_g[giorni_p1:]) if pagine == 3 else ([], carte_g)

    filtro = tc.Filtro(piano, db, target_kcal)
    if esclusioni:
        contro = tc.controlla_esclusioni(piano, esclusioni)
        if contro:
            raise Fermo(f"scheda: {', '.join(contro)} vietato dal file delle esclusioni ma "
                        f"presente nel piano: contraddizione da risolvere")
    carbo, pesce, verd = (tc.tabella_carboidrati(piano, db, filtro=filtro, esc=esclusioni),
                          tc.tabella_pesce(piano, db, filtro=filtro, esc=esclusioni),
                          tc.tabella_verdure(piano, db, filtro=filtro, esc=esclusioni))
    carni = tc.tabella_carni(piano, db, filtro=filtro, esc=esclusioni)
    note = meta.get("scheda_cucina") or {}
    seg = "".join(f" {E(s)}." for s in verd["segnalate"])
    gruppi_v = "".join(f"<b>{n}</b><div>{''.join(f'<span class=chip>{E(x)}</span>' for x in f)}</div>"
                       for n, k in (("Crude", "crude"), ("Cotte", "cotte"))
                       for f in verd["gruppi"][k])
    if any(len(f) > 1 for f in verd["gruppi"].values()):
        seg = " Si scambiano solo le verdure della stessa riga." + seg
    if verd["senza_scambio"]:
        seg += f" Senza scambio: {E(', '.join(verd['senza_scambio']))}."
    trattino = "<div class=n>— = scambio non previsto per questo piano.</div>"
    vuoto = "<div class=n>Nessuno scambio previsto per questo piano.</div>"
    corpo = lambda t: f"{_tabella_html(t)}{trattino}{_nota_scarto(t)}" if t["colonne"] else vuoto
    sez_c = (f"<h2>Carboidrati <span>stessa quantità di carboidrati</span></h2>{corpo(carbo)}"
             if carbo["righe"] else "")
    if note.get("note_carboidrati"):
        sez_c += f"<div class=n>{E(note['note_carboidrati'])}</div>"
    sez_p = (f"<h2>Pesce <span>stessa quantità di proteine</span></h2>{corpo(pesce)}"
             if pesce["righe"] else "")
    # carni e affettati (11/11/2026): gli affettati portano «*» e la nota sul sale, perche'
    # il motore non calcola il sodio; il dato resta a parita' di proteine
    sal = salumi()
    carni_v = dict(carni, colonne=[c + "*" if c in sal else c for c in carni["colonne"]],
                   righe=[dict(r, nome=r["nome"] + "*" if r["nome"] in sal else r["nome"])
                          for r in carni["righe"]])
    nota_sale = ("<div class=n>* Affettato: contiene più sale della carne fresca.</div>"
                 if carni["colonne"] and any(n.endswith("*") for n in
                                             carni_v["colonne"] + [r["nome"] for r in carni_v["righe"]])
                 else "")
    sez_k = (f"<h2>Carni e affettati <span>stessa quantità di proteine</span></h2>"
             f"{corpo(carni_v)}{nota_sale}" if carni["righe"] else "")
    sez_v = (f"<h2>Verdure <span>stesso peso, stesso gruppo</span></h2><div class=v>{gruppi_v}</div>"
             f"<div class=n>Patate e legumi non si scambiano con le verdure.{seg}</div>")
    top = "<div class=top><b>Dott. Giuseppe Taglialatela</b> <i>— Consulente in Nutrizione</i></div>"
    nome_paz = E(meta["intestazione"]["nome"])
    piede = " · ".join(x for x in ("Pesi sempre a crudo, tranne legumi lessati e scatolame",
                                   E(note.get("note_piede", ""))) if x)
    foot = lambda n: (f"<div class=foot><span>{piede}</span><span>Studio Nutrizionale "
                      f"Taglialatela · {n}/{pagine}</span></div>")
    griglia = lambda c: f'<div class="griglia giorni">{"".join(c)}</div>'
    salto = ""
    if pagine == 3:
        salto = ((f"<h2>Pranzo e cena</h2>{griglia(primi)}" if primi else "")
                 + f"{foot(1)}</div><div class=pag>{top}<h1>Pranzo e cena</h1><div class=sub>{nome_paz}</div>")
    pagina = f"""<!doctype html><html lang=it><head><meta charset=utf-8><title>Scheda per chi cucina</title><style>{CSS}</style></head><body>
<div class=pag>{top}<h1>La settimana</h1><div class=sub>{nome_paz} · scheda per chi cucina</div>
{sez('Colazione', 'colazione')}{griglia_carte('colazione')}{spuntini}
{salto}{"" if pagine == 3 else "<h2>Pranzo e cena</h2>"}{griglia(resto)}{foot(pagine - 1)}</div>
<div class=pag>{top}<h1>Come scambiare gli alimenti</h1><div class=sub>{nome_paz} · Lo scambio vale nello stesso pasto</div>
{sez_c}{sez_p}{sez_k}{sez_v}{foot(pagine)}</div></body></html>"""
    return pagina, {"carboidrati": carbo, "pesce": pesce, "carni": carni, "verdure": verd}


def _prepara(piano_p, target_p, meta_p, orari_p=None, **kw):
    return componi(*_dati(piano_p, target_p, meta_p, orari_p, **kw))


def _dati(piano_p, target_p, meta_p, orari_p=None, **kw):
    gzp.verifica(piano_p, target_p, meta_p, orari_p, **kw)     # verdetto e impronta
    db, nomi, piano, target, meta, _v = gzp._prepara(piano_p, target_p, meta_p, **kw)
    etichetta = frozenset(db) - frozenset(tc.carica_db())
    return piano, db, nomi, meta, gzp.carica_orari(orari_p), target["kcal_target"], etichetta


# Adattamento al contenuto (decisione del nutrizionista, 04/11/2026). Ogni pagina prova i
# livelli in ordine e si ferma al primo che entra; il contenuto non cambia mai. Ogni
# livello tiene la stessa griglia. Minimo: ingredienti a 9 punti, poi la terza pagina.
SPAZI = ("--gap:4px 8px;--mh:6px 0 3px;--h1:16pt;--mh1:5px 0 0;--msub:3px;--pc:3px 6px;"
         "--pm:2px 7px;--pt:2.5px 5px;")
LIVELLI = (("normale", 10.0, 9.5, ""),
           ("spazi ridotti", 10.0, 9.5, SPAZI),
           ("scrittura minima 9", 9.5, 9.0, SPAZI))
_TAGLI = """() => { const fuori = [];
  for (const q of document.querySelectorAll('.q, .t, .chip, .conv td, .conv th, .x')) {
    const c = q.closest('.card, .gg, .pag').getBoundingClientRect(), r = q.getBoundingClientRect();
    if (r.right > c.right + 0.5 || r.left < c.left - 0.5) fuori.push(q.textContent.trim().slice(0, 60)); }
  return fuori; }"""


_VUOTI = """() => [...document.querySelectorAll('.pag')].map(p => {
  const c = [...p.children], f = c[c.length - 1], u = c[c.length - 2];
  return Math.round(f.getBoundingClientRect().top - u.getBoundingClientRect().bottom); })"""


def piedi_a_posto(pdf_p):
    """La misura in px puo' non coincidere con la stampa: fa fede il PDF. Ogni pagina deve
    contenere il proprio «n/N» e le pagine devono essere N."""
    try:
        from pypdf import PdfReader
        testi = [p.extract_text() or "" for p in PdfReader(pdf_p).pages]
    except ImportError:
        import subprocess
        testi = subprocess.run(["pdftotext", pdf_p, "-"], capture_output=True, text=True,
                               check=True).stdout.rstrip("\f").split("\f")
    n = len(testi)
    return all(f"· {i}/{n}" in t for i, t in enumerate(testi, 1))


def controlla_tagli(pag):
    """Ogni quantita' e ogni testo devono stare dentro il loro riquadro."""
    fuori = pag.evaluate(_TAGLI)
    if fuori:
        raise Fermo("scheda: testo tagliato dal bordo, quantita' non leggibile: "
                    + "; ".join(f"«{t}»" for t in fuori[:3]) + ". PDF non generato")


def _adatta_pagine(pag):
    """Prova i livelli su ogni pagina. Restituisce [(pagina, livello, punti)] oppure, se
    una pagina non entra al minimo, (None, pagina, altezza, disponibile)."""
    esito = []
    for n, el in enumerate(pag.query_selector_all(".pag"), 1):
        for nome, fs, fv, spazi in LIVELLI:
            el.evaluate("(p, a) => { p.style.cssText = a; }",
                        f"--fs:{fs}pt;--fv:{fv}pt;--lh:{1.32 if fs >= 10 else 1.25};{spazi}")
            alto, disp = el.evaluate("p => [p.scrollHeight, p.clientHeight]")
            if alto <= disp + 1:
                esito.append((n, nome, fv))
                break
        else:
            return (None, n, alto, disp)
    return esito


def adatta(costruisci, html_p, pdf_p, n_giorni):
    """costruisci(pagine, giorni_p1) -> html. Due pagine se entrano al minimo; altrimenti
    tre, dividendo la settimana dove la scrittura resta piu' grande. Prima del PDF ogni
    pagina e' misurata; se non entra nulla si ferma."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        # la stessa larghezza della stampa: A4 meno i margini di @page, 180 mm. Con una
        # finestra piu' larga il testo andava a capo meno che sulla carta, e il piede
        # della pagina finiva sulla pagina dopo (rilievo del 04/11/2026)
        pag = b.new_page(viewport={"width": 680, "height": 1040})
        pag.emulate_media(media="print")

        def prova(pagine, k):
            with open(html_p, "w", encoding="utf-8") as f:
                f.write(costruisci(pagine, k))
            pag.goto("file://" + os.path.abspath(html_p))
            return _adatta_pagine(pag)
        def tre_pagine():
            ultimo, migliore = None, None
            for k in range(0, n_giorni + 1, 2):         # righe intere di riquadri
                e = prova(3, k)
                if isinstance(e, tuple):
                    ultimo = e
                    continue
                v = pag.evaluate(_VUOTI)                # pagine piene in modo simile
                voto = (-abs(v[0] - v[1]), min(x[2] for x in e))
                if migliore is None or voto > migliore[0]:
                    migliore = (voto, e, k)
            if migliore is None:
                b.close()
                _, n, alto, disp = ultimo
                raise Fermo(f"scheda: il contenuto non sta in tre pagine con ingredienti a 9 punti, "
                            f"la scrittura minima (pagina {n}: {alto} px su {disp}, "
                            f"{100 * (alto - disp) // disp + 1}% di troppo). PDF non generato: "
                            f"serve una decisione del nutrizionista")
            prova(3, migliore[2])
            return migliore[1]

        def stampa():
            """Scrive il PDF e controlla sul PDF che ogni pagina porti il proprio piede."""
            try:
                controlla_tagli(pag)
            except Fermo:
                b.close()
                raise
            pag.pdf(path=pdf_p, prefer_css_page_size=True, print_background=True)
            return piedi_a_posto(pdf_p)
        esito = prova(2, 0)
        a_posto = not isinstance(esito, tuple) and stampa()
        if not a_posto:
            esito = tre_pagine()
            if not stampa():
                b.close()
                os.remove(pdf_p)
                raise Fermo("scheda: un piede di pagina non sta sulla sua pagina del PDF, "
                            "PDF non generato")
        with open(html_p, "w", encoding="utf-8") as f:
            f.write(pag.content())
        b.close()
    return esito


def riepilogo(tabelle):
    """Righe per il nutrizionista, in chat: gli scarti e cio' che resta fuori."""
    L = []
    voci = sum(tabelle[k]["da_file"]["voci"] for k in tabelle)
    celle = sum(tabelle[k]["da_file"]["celle"] for k in tabelle)
    if voci or celle:
        L.append(f"esclusioni del piano: tolte {voci} voci e {celle} caselle")
    for nome in ("carboidrati", "pesce", "carni"):
        s = scarto_massimo(tabelle[nome])
        L.append(f"{nome}: {len(tabelle[nome]['righe'])} righe, {tabelle[nome]['esclusi']} scambi "
                 f"esclusi dal filtro" + (f", scarto da {s[0]:+d} a {s[1]:+d} kcal" if s else ""))
    v = tabelle["verdure"]
    L.append(f"verdure: {sum(len(f) for g in v['gruppi'].values() for f in g)} in tabella, "
             f"{v['esclusi']} escluse dal filtro" +
             (f", senza scambio: {', '.join(v['senza_scambio'])}" if v["senza_scambio"] else ""))
    if tabelle["verdure"]["fuori_elenco"]:
        L.append("verdure del piano fuori elenco: " + ", ".join(tabelle["verdure"]["fuori_elenco"]))
    return L


def _autotest_carni(db):
    """Caso golden della tabella carni e affettati (11/11/2026): grammature a parita' di
    proteine ricalcolate a mano una volta e fissate qui; filtro, esclusioni, pasti e sale."""
    problemi = []
    riga = lambda p, f, q: {"giorno": "1", "pasto": p, "food_id": f, "grammi": q, "opzione": ""}
    piano = [riga("pranzo", "106500", "100"), riga("cena", "101170", "120"),
             riga("colazione", "100061", "40")]
    t = tc.tabella_carni(piano, db)
    if [r["food_id"] for r in t["righe"]] != ["106500", "101170"]:
        problemi.append(f"carni: righe {[r['food_id'] for r in t['righe']]}, attese pollo e manzo "
                        f"(solo pranzo e cena, la bresaola a colazione no)")
    attese = {"Petto di tacchino": 95, "Coscia di pollo senza pelle": 125, "Lombo di maiale": 115,
              "Fesa di tacchino affettata": 80, "Bresaola": 75, "Prosciutto cotto sgrassato": 105}
    pollo = t["righe"][0]
    for nome, g in attese.items():
        c = pollo["celle"][t["colonne"].index(nome)] if nome in t["colonne"] else None
        if not c or c["grammi"] != g:
            problemi.append(f"carni: petto di pollo 100 g in {nome} non vale {g} g ({c})")
    if "Filetto di manzo" in t["colonne"]:
        problemi.append("carni: voce da_confermare proposta come alternativa")
    manzo = t["righe"][1]
    if manzo["celle"][t["colonne"].index("Petto di pollo")]["grammi"] != 105:
        problemi.append("carni: filetto di manzo 120 g in petto di pollo non vale 105 g")
    tf = tc.tabella_carni(piano, db, filtro=tc.Filtro(piano, db, 320))  # giorno ~312 kcal
    if "Lombo di maiale" in tf["colonne"] and tf["righe"][0]["celle"][tf["colonne"].index("Lombo di maiale")]:
        problemi.append("carni: scambio oltre il 2,5% del target (maiale +68 kcal su 320) rimasto")
    if "Petto di tacchino" not in tf["colonne"]:
        problemi.append("carni: scambio entro il 2,5% (tacchino) tolto")
    te = tc.tabella_carni(piano, db, esc={"vieti": {"100061": "prova"}, "massimi": {}})
    if "Bresaola" in te["colonne"] or te["da_file"]["voci"] != 1:
        problemi.append("carni: bresaola vietata dal file delle esclusioni rimasta")
    if "Bresaola" not in salumi() or "Petto di pollo" in salumi():
        problemi.append("carni: affettati non riconosciuti per la nota sul sale")
    return problemi


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
    # Uova a pezzi (11/11/2026), uguali in scheda e PDF; un non multiplo resta in grammi
    problemi_pz = []
    fmt, nomi_t = formati.carica_formati(), gzp.carica_nomi(os.path.join(QUI, "nomi_paziente.csv"))
    for g, atteso in ((52, "Uovo 1 (52 g)"), (104, "Uova 2 (104 g)"), (106, "Uova 2 (106 g)"),
                      (80, "Uovo intero 80 g")):
        r = {"food_id": "1800", "grammi": float(g)}
        sch = voce(r, nomi_t, fmt).replace("\u00a0", " ")
        pdf = gzp._dettaglio([r], nomi_t)
        if sch != atteso or pdf != atteso:
            problemi_pz.append(f"uova {g} g: scheda «{sch}», PDF «{pdf}», atteso «{atteso}»")
    problemi = list(problemi_pz)
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
                   "Nota di collaudo.", "Piede di collaudo", "Patate e legumi"):
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
    tp = tc.tabella_pesce(prova, db)
    if tp["righe"][0]["celle"][tp["colonne"].index("Spigola")]["grammi"] != 185:
        problemi.append("merluzzo 180 g in spigola non vale 185 g")
    problemi += _autotest_carni(db)
    tv = tc.tabella_pesce([{"pasto": "cena", "food_id": "1313", "grammi": "150", "giorno": "1", "opzione": ""}], db,
                          filtro=tc.Filtro([], db, 1))
    if tv["colonne"] or "nessuno scambio previsto" not in _tabella_html(tv):
        problemi.append("tabella senza scambi: colonne rimaste")
    if tc.tabella_verdure(prova, db)["segnalate"] == []:
        problemi.append("nessuna verdura segnalata")
    problemi += _autotest_filtro(db)
    problemi += _autotest_esclusioni(tmp, db)
    problemi += _autotest_etichetta(tmp, meta)
    return problemi


def _autotest_filtro(db):
    """Il filtro toglie lo scambio oltre il 2,5% del target e quello che, nel giorno
    reale, porterebbe oltre il 10%. Prova al contrario: lo stesso scambio resta con un
    target largo o con un giorno lontano dal limite."""
    problemi = []
    riga = lambda g, p, f, q, o="": {"giorno": g, "pasto": p, "food_id": f, "grammi": q, "opzione": o}
    # riso 80 g -> pane integrale: scarto ricalcolato, target tarato attorno al limite
    piano = [riga("1", "pranzo", "000100", "80"), riga("1", "cena", "1313", "150")]
    scarto = tc.kcal("000550", tc.equivalente(80, "000100", "000550", "carboidrati_g", db), db) \
        - tc.kcal("000100", 80, db)
    target_stretto = abs(scarto) / tc.QUOTA_SCAMBIO - 1
    giorno = sum(tc.kcal(r["food_id"], float(r["grammi"]), db) for r in piano)
    f = tc.Filtro([], db, target_stretto)      # senza giorni: agisce solo il 2,5%
    if f.ammesso("000100", 80, scarto):
        problemi.append("scambio oltre il 2,5% del target rimasto")
    largo = abs(scarto) / tc.QUOTA_SCAMBIO + 1
    if tc.Filtro([], db, largo).ammesso("000100", 80, scarto) is not True:
        problemi.append("scambio entro il 2,5% tolto")
    # stesso scarto: il giorno a +9% lo esclude, il giorno in pari no
    vicino = tc.Filtro(piano, db, giorno / 1.09)
    pari = tc.Filtro(piano, db, giorno)
    scambio = 0.02 * giorno
    if vicino.ammesso("000100", 80, scambio):
        problemi.append("scambio che porta il giorno oltre il 10% rimasto")
    if not pari.ammesso("000100", 80, scambio):
        problemi.append("scambio su giorno in pari tolto")
    # un giorno a scelta conta con l'opzione piu' alta
    scelta = tc.Filtro([riga("1", "cena", "000100", "80", "A"), riga("1", "cena", "000100", "40", "B")], db, 100)
    if not (scelta.giorni["1"][0] < scelta.giorni["1"][1]):
        problemi.append("opzioni a scelta non considerate nel giorno")
    # il pesce grasso che non e' in elenco non diventa scambio; la cella esclusa non si mostra
    t = tc.tabella_pesce([riga("1", "cena", "1313", "150")], db, filtro=tc.Filtro([riga("1", "cena", "1313", "150")], db, 1000))
    if any(c and abs(c["scarto_kcal"]) > 25 for r in t["righe"] for c in r["celle"]):
        problemi.append("cella oltre il filtro mostrata")
    return problemi


def _autotest_esclusioni(tmp, db):
    """Ogni regola del file --esclusioni, con i fermi e la prova al contrario."""
    import json as _j
    problemi = []
    riga = lambda f, q: {"giorno": "1", "pasto": "cena", "food_id": f, "grammi": q, "opzione": ""}
    piano = [riga("1313", "150"), riga("000800", "80"), riga("349", "200"), riga("391", "100")]
    fl = tc.Filtro(piano, db, sum(tc.kcal(r["food_id"], float(r["grammi"]), db) for r in piano))

    def esc(contenuto):
        p = os.path.join(tmp, "esc.json")
        with open(p, "w", encoding="utf-8") as f:
            _j.dump(contenuto, f)
        return tc.carica_esclusioni(p, db)
    for nome, cont in (("campo non previsto", {"altro": 1}), ("food_id sconosciuto", {"escludi_food_id": {"XXX": "x"}}),
                       ("massimo non valido", {"massimo_g_a_pasto": {"000100": 0}})):
        try:
            esc(cont)
            problemi.append(f"esclusioni: {nome} accettato")
        except ValueError:
            pass
    vuoto = esc({})
    uguali = [tc.tabella_carboidrati(piano, db, filtro=fl) == tc.tabella_carboidrati(piano, db, filtro=fl, esc=vuoto),
              tc.tabella_verdure(piano, db, filtro=fl) == tc.tabella_verdure(piano, db, filtro=fl, esc=vuoto)]
    if not all(uguali):
        problemi.append("esclusioni: file vuoto cambia le tabelle")
    e = esc({"escludi_food_id": {"000100": "riso", "005120": "carciofi", "101": "fagiolini"},
             "massimo_g_a_pasto": {"000550": 70}, "verdure_crude_ammesse": ["391"]})
    t = tc.tabella_carboidrati(piano, db, filtro=fl, esc=e)
    if "Riso" in t["colonne"] or t["da_file"]["voci"] != 1:
        problemi.append("esclusioni: voce vietata rimasta tra gli scambi")
    if "Pane integrale" in t["colonne"] or t["da_file"]["celle"] != 1:
        problemi.append("esclusioni: casella oltre il massimo rimasta")
    if not t["righe"] or t["righe"][0]["food_id"] != "000800":
        problemi.append("esclusioni: voce del piano in colonna persa")
    v = tc.tabella_verdure(piano, db, filtro=fl, esc=e)
    nomi_v = {n for g in v["gruppi"].values() for f in g for n in f}
    if {"Fagiolini", "Carciofi"} & nomi_v or "Carciofi" in " ".join(v["segnalate"]):
        problemi.append("esclusioni: verdura vietata mostrata o citata")
    crude = {n for f in v["gruppi"]["crude"] for n in f}
    if crude - {"Pomodori"}:
        problemi.append("esclusioni: gruppo Crude con voci non ammesse")
    if tc.controlla_esclusioni(piano, esc({"escludi_food_id": {"1313": "merluzzo"}})) != ["1313"]:
        problemi.append("esclusioni: voce vietata nel piano non rilevata")
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
    if any("ETI" in c or "Vellutata" in c for t in (tab["carboidrati"], tab["pesce"], tab["carni"])
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
    a.add_argument("--esclusioni")
    o = a.parse_args()
    if o.autotest:
        p = autotest()
        print("\n".join(p) or "Autotest della scheda superato.")
        return 1 if p else 0
    if not o.out_html and not o.out_pdf:
        print("FERMO: indicare --out-pdf (la scheda da consegnare) e, se serve, --out-html")
        return 1
    try:
        dati = _dati(o.piano, o.target, o.metadati, o.orari, verdetto_p=o.verdetto,
                     eccezione_p=o.eccezione, nomi_eccezione_p=o.nomi_eccezione)
        esc = None
        if o.esclusioni:
            try:
                esc = tc.carica_esclusioni(o.esclusioni, dati[1])
            except (OSError, ValueError) as e:
                raise Fermo(f"esclusioni: {e}")
        pagina, tabelle = componi(*dati, esclusioni=esc)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    if o.out_html:
        with open(o.out_html, "w", encoding="utf-8") as f:
            f.write(pagina)
    print("\n".join(riepilogo(tabelle)))
    if not o.out_pdf:
        print("HTML non misurato: l'adattamento alle pagine avviene solo con --out-pdf")
        return 0
    # --out-html e' facoltativo (11/11/2026): senza, la pagina misurata sta in una
    # cartella temporanea, cancellata alla fine (prima: TypeError su open(None))
    tmp_html = None if o.out_html else tempfile.mkdtemp()
    html_p = o.out_html or os.path.join(tmp_html, "scheda.html")
    try:
        n_giorni = len({r["giorno"] for r in dati[0]}) + 1
        esito = adatta(lambda p, k: componi(*dati, pagine=p, giorni_p1=k, esclusioni=esc)[0], html_p, o.out_pdf, n_giorni)
    except Fermo as e:
        print(f"FERMO: {e}")
        return 1
    finally:
        if tmp_html:
            import shutil
            shutil.rmtree(tmp_html, ignore_errors=True)
    print(f"pagine: {len(esito)}")
    for n, nome, fv in esito:
        print(f"pagina {n}: livello «{nome}», ingredienti a {fv:g} punti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
