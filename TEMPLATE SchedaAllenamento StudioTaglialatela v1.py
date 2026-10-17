#!/usr/bin/env python3
"""
TEMPLATE UFFICIALE — Scheda di allenamento (formato telefono)
Studio Nutrizionale Taglialatela

Uso:  python3 template_scheda_allenamento.py dati_paziente.json [output.pdf]
Richiede: wkhtmltopdf

MOTORE GRAFICO CONGELATO: non modificare CSS, colori, dimensioni pagina,
struttura dei riquadri. Si modifica solo il file JSON dei dati.
"""
import json, sys, html, subprocess, os, tempfile

PAGE_W_MM, PAGE_H_MM = 100, 222
E = html.escape

CSS = '''
@page{margin:0}
body{font-family:"DejaVu Sans",Arial,sans-serif;margin:0;padding:5mm 4.5mm;color:#1c1c1c;font-size:10pt;line-height:1.35}
h1{font-size:17pt;margin:0 0 1mm;line-height:1.15}
.meta{color:#777;font-size:8.5pt;margin-bottom:3mm;border-bottom:2.5px solid #e8820c;padding-bottom:2mm}
h2{font-size:12.5pt;color:#e8820c;margin:4mm 0 2mm}
p{margin:0 0 2mm}
.box{background:#f6f6f6;border-radius:6px;padding:2.5mm 3mm;margin-bottom:2.5mm}
.box b{color:#111}
.tb{width:100%;border-collapse:collapse;font-size:9.5pt;margin-bottom:2mm}
.tb th{background:#222;color:#fff;padding:1.5mm;font-size:8.5pt}
.tb td{border-bottom:1px solid #ddd;padding:1.5mm;text-align:center}
.tb td:first-child{text-align:left;font-weight:bold}
ul{padding-left:4.5mm;margin:0 0 2mm} li{margin-bottom:1.5mm}
.sess{page-break-before:always}
.sh{background:#222;color:#fff;border-radius:6px;padding:2mm 3mm;margin-bottom:2.5mm}
.sn{font-size:16pt;font-weight:bold}.sd{font-size:9pt;color:#f0b060}
.ex{border:1px solid #ddd;border-left:4px solid #e8820c;border-radius:5px;padding:2mm 2.5mm;margin-bottom:2mm;page-break-inside:avoid}
.en{font-weight:bold;font-size:11pt}
.num{display:inline-block;background:#e8820c;color:#fff;border-radius:50%;width:5.5mm;height:5.5mm;line-height:5.5mm;text-align:center;font-size:8.5pt;margin-right:2mm}
.sub{color:#666;font-size:8.5pt;margin:0.5mm 0 1mm 7.5mm}
.bl{width:100%;border-collapse:collapse;margin:1.5mm 0;table-layout:fixed}
.bl th{font-size:7.5pt;color:#888;font-weight:normal;padding:0}
.bl td{font-size:10pt;font-weight:bold;text-align:center;background:#fff4e5;padding:1.2mm 0.5mm;border:1px solid #fff}
.rec{font-size:9pt;margin-top:1mm}.foc{font-size:9pt;color:#444;margin-top:0.5mm}
.pb{page-break-before:always}
'''

def rich(t):
    """Testo con **grassetto** e a capo; tutto il resto viene escapato."""
    out = []
    for i, part in enumerate(E(t).split('**')):
        out.append(('<b>' if i % 2 else '') + part + ('</b>' if i % 2 else ''))
    righe = ''.join(out).split('\n')
    righe = ['&nbsp;' * (len(r) - len(r.lstrip(' '))) + r.lstrip(' ') for r in righe]
    return '<br>'.join(righe)

def box(b):
    h = '<div class="box">'
    if b.get('titolo'):
        h += f'<b>{E(b["titolo"])}</b>'
        if b.get('sottotitolo'): h += f' · {E(b["sottotitolo"])}'
        h += '<br>'
    if b.get('testo'): h += rich(b['testo'])
    if b.get('punti'): h += '<br>'.join('• ' + rich(p) for p in b['punti'])
    return h + '</div>'

def esercizio(i, ex, nblocchi):
    h = f'<div class="ex"><div class="en"><span class="num">{i}</span>{E(ex["nome"])}</div>'
    if ex.get('dettaglio'): h += f'<div class="sub">{E(ex["dettaglio"])}</div>'
    h += '<table class="bl"><tr>' + ''.join(f'<th>B{k}</th>' for k in range(1, nblocchi + 1)) + '</tr><tr>'
    h += ''.join(f'<td>{E(x).replace(" + ", "<br>+ ")}</td>' for x in ex['blocchi']) + '</tr></table>'
    h += f'<div class="rec">Recupero: <b>{E(ex["recupero"])}</b></div>'
    if ex.get('focus'): h += f'<div class="foc">{E(ex["focus"])}</div>'
    return h + '</div>'

def build(d):
    nb = len(d['progressione']['righe'])
    h = f'<h1>{E(d["titolo"])}<br>{E(d["paziente"])}</h1>'
    h += f'<div class="meta">{E(d["autore"])} · {E(d["data"])}</div>'
    h += box({'testo': d['intro']})
    p = d['progressione']
    h += '<h2>Come si progredisce</h2>' + f'<p>{rich(p["testo"])}</p>'
    h += '<table class="tb"><tr>' + ''.join(f'<th>{E(c)}</th>' for c in p['colonne']) + '</tr>'
    h += ''.join('<tr>' + ''.join(f'<td>{E(c)}</td>' for c in r) + '</tr>' for r in p['righe']) + '</table>'
    if p.get('nota'): h += box({'testo': p['nota']})
    h += '<h2>Regole</h2><ul>' + ''.join(f'<li>{rich(r)}</li>' for r in d['regole']) + '</ul>'
    h += '<div class="pb"></div><h2>Ogni seduta: prima</h2>' + ''.join(box(b) for b in d['prima'])
    h += '<h2>Ogni seduta: dopo</h2>' + ''.join(box(b) for b in d['dopo'])
    for s in d['sedute']:
        h += f'<section class="sess"><div class="sh"><div class="sn">{E(s["nome"])}</div><div class="sd">{E(s["sedute"])}</div></div>'
        h += ''.join(esercizio(i, ex, nb) for i, ex in enumerate(s['esercizi'], 1)) + '</section>'
    return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{h}</body></html>'

def main():
    src = sys.argv[1]
    d = json.load(open(src, encoding='utf-8'))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.pdf'
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(build(d)); tmp = f.name
    subprocess.run(['wkhtmltopdf', '--enable-local-file-access', '-q', '--page-width', f'{PAGE_W_MM}mm',
                    '--page-height', f'{PAGE_H_MM}mm', '-T', '0', '-B', '0', '-L', '0', '-R', '0',
                    '--disable-smart-shrinking', tmp, out], check=False, stderr=subprocess.DEVNULL)
    os.unlink(tmp)
    print('PDF creato:', out)

if __name__ == '__main__':
    main()
