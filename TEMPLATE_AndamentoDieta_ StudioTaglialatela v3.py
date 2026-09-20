#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          TEMPLATE ANDAMENTO DIETA — Studio Nutrizionale Taglialatela         ║
║          Dott. Giuseppe Taglialatela — Consulente in Nutrizione              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Versione: 3.0 (RISCRITTURA)  |  20/09/2026                                  ║
║                                                                              ║
║  Questo file e' una RISCRITTURA, non un ripristino. Il motore grafico        ║
║  originale (v1-v3, luglio 2026) e' andato perso: su Drive restavano solo     ║
║  stub. Ricostruito da: docstring v1, changelog v2, docstring v3, modulo M5.  ║
║  Identita' visiva (font, palette, header, footer) copiata dal template       ║
║  TEMPLATE_PianoAlimentare_StudioTaglialatela_v5.py.                          ║
║                                                                              ║
║  USO                                                                         ║
║    python3 TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py Paziente.json    ║
║            [output.pdf]                                                      ║
║  Lo script NON contiene dati di pazienti: legge tutto dal JSON.              ║
║                                                                              ║
║  STRUTTURA (3 pagine)                                                        ║
║   1. Titolo, introduzione, barra KPI, box circonferenza vita (se presente),  ║
║      cronologia delle pesate, "cosa significano questi numeri"               ║
║   2. Grafico, tabella di proiezione, box di avvertenza                       ║
║   3. Consigli pratici, box motivazionale                                     ║
║                                                                              ║
║  PROIEZIONE — decisioni cliniche del nutrizionista (20/09/2026)              ║
║   CON FARMACO (GIP/GLP-1): tre fasi contate dall'inizio della dieta,         ║
║     settimane 0-8 / 8-16 / 16+ a 0,55 / 0,60 / 0,40 kg/settimana.            ║
║     I tassi NON si cambiano senza indicazione esplicita del nutrizionista.   ║
║   SENZA FARMACO: nessun tasso a priori. La linea si ricava dalle pesate      ║
║     reali (regressione lineare), ESCLUDENDO dal calcolo quelle dei primi     ║
║     14 giorni (acqua e glicogeno): restano nel grafico. Servono almeno 2     ║
║     pesate dopo il giorno 14; altrimenti nessuna proiezione.                 ║
║   Entrambi: orizzonte 27 settimane dall'ultima pesata, banda +/-1,5 kg.      ║
║     La curva si ferma a obiettivo_peso_kg se impostato, altrimenti a         ║
║     weight_floor_kg. weight_floor_kg e' OBBLIGATORIO: se manca lo script     ║
║     si ferma (nessun default).                                               ║
║                                                                              ║
║  SOGLIE CIRCONFERENZA VITA: automatiche da "sesso" (M 94/102, F 80/88 cm).   ║
║  NOTE nota_glicemia / nota_urea / nota_extra: compaiono solo se non vuote.   ║
║                                                                              ║
║  I testi fissi (sezione TESTI) sono BOZZA da approvare: il testo originale   ║
║  e' perso.                                                                   ║
║                                                                              ║
║  DIPENDENZE: pip install reportlab matplotlib                                ║
║  FONT: /usr/share/fonts/truetype/liberation/LiberationSans-*.ttf             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import io
import json
import os
import sys
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, KeepTogether,
                                Image as RLImage)

# ════════════════════════════════════════════════════════════════════
#  PARAMETRI CLINICI — modificare solo su indicazione del nutrizionista
# ════════════════════════════════════════════════════════════════════
TASSI_FARMACO_DEFAULT = (0.55, 0.60, 0.40)   # kg/settimana, fasi 0-8, 8-16, 16+
CONFINI_FASI_SETT = (8, 16)
BANDA_DEFAULT_KG = 1.5
SETTIMANE_PROIEZIONE_DEFAULT = 27
GIORNI_ESCLUSI_REGRESSIONE = 14               # solo pazienti senza farmaco
PESATE_MINIME_REGRESSIONE = 2                 # dopo il giorno 14
SOGLIE_VITA = {"M": (94, 102), "F": (80, 88)}

# ════════════════════════════════════════════════════════════════════
#  TESTI — BOZZA DA APPROVARE (il testo originale e' perso)
# ════════════════════════════════════════════════════════════════════
TESTI = {
    "intro": (
        "Questo documento riassume il tuo percorso dall'inizio del piano "
        "alimentare a oggi. Trovi le pesate registrate, il confronto con il "
        "punto di partenza e una stima prudente dei prossimi mesi."
    ),
    "significato": [
        ("Il peso", "Conta la tendenza, non la singola pesata. Da un giorno "
         "all'altro il peso oscilla di 0,5-1,5 kg per acqua, sale e contenuto "
         "intestinale: una pesata ferma o in lieve salita non cancella il "
         "lavoro fatto."),
        ("L'IMC", "L'Indice di Massa Corporea mette in rapporto peso e altezza. "
         "È un indicatore generale: non distingue tra grasso e muscolo, per "
         "questo lo leggiamo insieme alla circonferenza vita."),
        ("La circonferenza vita", "Misura il grasso addominale, quello più "
         "legato al rischio cardiometabolico. Ogni centimetro in meno ha un "
         "valore per la salute anche quando la bilancia rallenta."),
    ],
    "avvertenza_farmaco": (
        "La proiezione è una stima prudente, non una promessa. Nelle prime "
        "settimane il calo è spesso più rapido perchè si perde anche acqua; "
        "col tempo è normale che rallenti. Le variazioni della terapia vanno "
        "sempre concordate con il medico prescrittore."
    ),
    "avvertenza_dieta": (
        "La proiezione prolunga il ritmo delle tue ultime pesate: è una stima, "
        "non una promessa. Col passare dei mesi il calo tende naturalmente a "
        "rallentare, per cui i tempi reali possono essere più lunghi di quelli "
        "indicati. Le pesate delle prime due settimane non entrano nel calcolo, "
        "perchè comprendono soprattutto acqua."
    ),
    "proiezione_assente_poche": (
        "La proiezione comparirà quando avremo almeno due pesate successive "
        "alle prime due settimane di percorso. Prima di allora il calo "
        "comprende soprattutto acqua e una stima non sarebbe affidabile."
    ),
    "proiezione_assente_stabile": (
        "Nelle ultime pesate il peso è stabile: in questa fase non tracciamo "
        "una proiezione. Ne parleremo insieme al prossimo controllo."
    ),
    "consigli": [
        ("Pesati sempre nelle stesse condizioni",
         "Al mattino, a digiuno, dopo il bagno, con la stessa "
         "bilancia. Una volta a settimana basta."),
        ("Guarda la tendenza",
         "Confronta le settimane, non i giorni. Una pesata isolata dice poco."),
        ("Bevi con regolarità",
         "Acqua distribuita durante la giornata, anche quando non hai sete."),
        ("Rispetta i pasti del piano",
         "Saltare un pasto non accelera il risultato: aumenta la fame dopo."),
        ("Muoviti ogni giorno",
         "Anche una camminata quotidiana sostiene il percorso e la massa "
         "muscolare."),
        ("Annota gli imprevisti",
         "Una cena fuori o una settimana difficile vanno raccontate, non "
         "nascoste: servono a regolare il piano."),
    ],
    "motivazionale": (
        "Ogni chilo perso e ogni centimetro di vita in meno sono un risultato "
        "concreto per la tua salute. Il percorso non è una linea retta: "
        "quello che conta è la direzione, e la stai mantenendo."
    ),
}

# ════════════════════════════════════════════════════════════════════
#  ═══ MOTORE GRAFICO ═══  (identita' visiva dal template piano v5)
# ════════════════════════════════════════════════════════════════════
_FONT_DIR = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Sans",       f"{_FONT_DIR}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",   f"{_FONT_DIR}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SansItalic", f"{_FONT_DIR}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("SansBI",     f"{_FONT_DIR}/LiberationSans-BoldItalic.ttf"))
for _f in ("Regular", "Bold", "Italic"):
    font_manager.fontManager.addfont(f"{_FONT_DIR}/LiberationSans-{_f}.ttf")
matplotlib.rcParams["font.family"] = "Liberation Sans"

_TEAL    = colors.HexColor("#2E7D8C")
_ORANGE  = colors.HexColor("#C0622B")
_NAVY    = colors.HexColor("#1C3A4A")
_DARK    = colors.HexColor("#1A1A1A")
_GREY    = colors.HexColor("#666666")
_RED_AL  = colors.HexColor("#C0392B")
_GOLD    = colors.HexColor("#8B6914")
_BORDER  = colors.HexColor("#CCCCCC")
_WHITE   = colors.white
_BG_GOLD = colors.HexColor("#FEF9E7")
_BG_RED  = colors.HexColor("#FDECEA")
_BG_TEAL = colors.HexColor("#EAF4F6")

_W, _H   = A4
_MARGIN  = 20*mm
_INNER   = _W - 2*_MARGIN


def _S(name, **kw):
    d = dict(fontName="Sans", fontSize=9, leading=13, textColor=_DARK,
             spaceAfter=0, spaceBefore=0)
    d.update(kw)
    return ParagraphStyle(name, **d)

_sTitolo  = _S("tit", fontSize=21, textColor=_NAVY, fontName="SansBold",
               leading=25, alignment=TA_CENTER, spaceAfter=2)
_sSub     = _S("sub", fontSize=10, fontName="SansBold", leading=14,
               alignment=TA_CENTER, spaceAfter=1)
_sTagline = _S("tgl", fontSize=8.5, textColor=_GREY, fontName="SansItalic",
               leading=12, alignment=TA_CENTER)
_sSez     = _S("sez", fontSize=10.5, textColor=_ORANGE, fontName="SansBold",
               leading=14, spaceBefore=6, spaceAfter=3)
_sTxt     = _S("txt", fontSize=9, leading=13)
_sTxtB    = _S("txb", fontSize=9, leading=13, fontName="SansBold", textColor=_NAVY)
_sSmall   = _S("sml", fontSize=7.5, leading=10, textColor=_GREY, fontName="SansItalic")
_sKpiV    = _S("kpv", fontSize=13, leading=16, fontName="SansBold",
               textColor=_WHITE, alignment=TA_CENTER)
_sKpiL    = _S("kpl", fontSize=7, leading=9, textColor=_WHITE, alignment=TA_CENTER)
_sTh      = _S("th", fontSize=8, leading=10, fontName="SansBold",
               textColor=_WHITE, alignment=TA_CENTER)
_sTd      = _S("td", fontSize=8, leading=10, alignment=TA_CENTER)
_sTdL     = _S("tdl", fontSize=8, leading=10, alignment=TA_LEFT)
_sBoxG    = _S("bxg", fontSize=8.5, leading=12, textColor=_GOLD)
_sBoxR    = _S("bxr", fontSize=8.5, leading=12, textColor=_RED_AL)
_sBoxT    = _S("bxt", fontSize=10, leading=15, textColor=_NAVY,
               fontName="SansItalic", alignment=TA_CENTER)


def _on_page(canvas, doc, piede):
    canvas.saveState()
    canvas.setFont("SansBold", 9)
    canvas.setFillColor(_TEAL)
    canvas.drawString(_MARGIN, _H - 11*mm, "Dott. Giuseppe Taglialatela")
    canvas.setFont("SansItalic", 9)
    canvas.setFillColor(_GREY)
    canvas.drawString(_MARGIN + 133, _H - 11*mm, "— Consulente in Nutrizione")
    canvas.setStrokeColor(_TEAL)
    canvas.setLineWidth(0.7)
    canvas.line(_MARGIN, _H - 12.5*mm, _W - _MARGIN, _H - 12.5*mm)
    canvas.setFont("Sans", 7)
    canvas.setFillColor(_GREY)
    canvas.drawString(_MARGIN, 9*mm, piede)
    canvas.drawRightString(_W - _MARGIN, 9*mm, f"Pag.  {doc.page}")
    canvas.restoreState()


def _box(testo, stile, sfondo):
    t = Table([[Paragraph(testo, stile)]], colWidths=[_INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sfondo),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def _tabella(righe, larghezze):
    t = Table(righe, colWidths=larghezze, repeatRows=1)
    stile = [
        ("BACKGROUND", (0, 0), (-1, 0), _TEAL),
        ("GRID", (0, 0), (-1, -1), 0.4, _BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for i in range(2, len(righe), 2):
        stile.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F6F6")))
    t.setStyle(TableStyle(stile))
    return t

# ════════════════════════════════════════════════════════════════════
#  LETTURA E CONTROLLO DEL JSON
# ════════════════════════════════════════════════════════════════════

class ErroreDati(Exception):
    pass


def _d(s, campo):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        raise ErroreDati(f"data non valida in '{campo}': {s!r} (atteso AAAA-MM-GG)")


def carica(path):
    with open(path, encoding="utf-8") as f:
        p = json.load(f)
    errori = []
    for c in ("nome", "altezza_cm", "sesso", "data_inizio_dieta", "kcal_piano",
              "misurazioni", "weight_floor_kg"):
        if p.get(c) in (None, "", []):
            errori.append(f"campo obbligatorio mancante o vuoto: '{c}'")
    for c in ("farmaco", "circ_vita", "obiettivo_peso_kg"):
        if c not in p:
            errori.append(f"campo '{c}' assente (se non rilevante va scritto null)")
    if p.get("sesso") not in ("M", "F"):
        errori.append(f"'sesso' deve essere \"M\" o \"F\", trovato {p.get('sesso')!r}")
    if errori:
        raise ErroreDati("\n  - " + "\n  - ".join(errori))

    p["_inizio"] = _d(p["data_inizio_dieta"], "data_inizio_dieta")
    mis = []
    for i, m in enumerate(p["misurazioni"]):
        if not isinstance(m.get("peso"), (int, float)):
            raise ErroreDati(f"misurazioni[{i}]: 'peso' deve essere un numero con "
                             f"il punto decimale, trovato {m.get('peso')!r}")
        mis.append((_d(m["data"], f"misurazioni[{i}].data"), float(m["peso"]),
                    m.get("etichetta", "")))
    if [x[0] for x in mis] != sorted(x[0] for x in mis):
        raise ErroreDati("le misurazioni non sono in ordine cronologico")
    p["_mis"] = mis
    if p["circ_vita"]:
        p["_vita_data"] = _d(p["circ_vita"]["data_attuale"], "circ_vita.data_attuale")
    return p

# ════════════════════════════════════════════════════════════════════
#  PROIEZIONE
# ════════════════════════════════════════════════════════════════════

def proiezione(p):
    """Restituisce dict: modo, punti [(date, kg)], motivo_assenza, tasso."""
    mis = p["_mis"]
    ultima_data, ultimo_peso, _ = mis[-1]
    sett = int(p.get("settimane_proiezione") or SETTIMANE_PROIEZIONE_DEFAULT)
    tetto = p["obiettivo_peso_kg"] if p["obiettivo_peso_kg"] is not None \
        else p["weight_floor_kg"]
    out = {"tetto": tetto, "settimane": sett,
           "banda": float(p.get("banda_incertezza") or BANDA_DEFAULT_KG)}

    if p["farmaco"]:
        t = (p.get("tasso_fase1") or TASSI_FARMACO_DEFAULT[0],
             p.get("tasso_fase2") or TASSI_FARMACO_DEFAULT[1],
             p.get("tasso_fase3") or TASSI_FARMACO_DEFAULT[2])
        def tasso(giorno):
            s = (giorno - p["_inizio"]).days / 7
            return t[0] if s < CONFINI_FASI_SETT[0] else \
                t[1] if s < CONFINI_FASI_SETT[1] else t[2]
        out["modo"] = "farmaco"
        out["tassi"] = t
    else:
        validi = [(d, w) for d, w, _ in mis
                  if (d - p["_inizio"]).days >= GIORNI_ESCLUSI_REGRESSIONE]
        if len(validi) < PESATE_MINIME_REGRESSIONE:
            out.update(modo="nessuna", motivo="poche", n_validi=len(validi))
            return out
        xs = [(d - validi[0][0]).days / 7 for d, _ in validi]
        ys = [w for _, w in validi]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        den = sum((x - mx) ** 2 for x in xs)
        pend = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
        if pend >= 0:
            out.update(modo="nessuna", motivo="stabile", pendenza=pend)
            return out
        out["modo"] = "andamento"
        out["pendenza"] = pend
        out["n_validi"] = len(validi)
        def tasso(giorno):
            return -pend

    punti = [(ultima_data, ultimo_peso)]
    w = ultimo_peso
    for k in range(1, sett + 1):
        g = ultima_data + timedelta(weeks=k)
        w = max(tetto, w - tasso(g - timedelta(days=7)))
        punti.append((g, w))
        if w <= tetto:          # raggiunto obiettivo/soglia: la curva si ferma
            out["data_tetto"] = g
            break
    out["punti"] = punti
    return out

# ════════════════════════════════════════════════════════════════════
#  COMPOSIZIONE
# ════════════════════════════════════════════════════════════════════

def _kg(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def _diff(nuovo, vecchio):
    x = round(nuovo - vecchio, 1)
    return "0,0" if x == 0 else (f"−{_kg(-x)}" if x < 0 else f"+{_kg(x)}")


def _dt(d):
    return d.strftime("%d/%m/%Y")


def _imc(peso, h_cm):
    return peso / (h_cm / 100) ** 2


def _grafico(p, pr):
    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=200)
    teal, orange, navy, grey = "#2E7D8C", "#C0622B", "#1C3A4A", "#666666"
    dd = [m[0] for m in p["_mis"]]
    ww = [m[1] for m in p["_mis"]]
    if pr["modo"] == "andamento":
        esc = [(d, w) for d, w in zip(dd, ww)
               if (d - p["_inizio"]).days < GIORNI_ESCLUSI_REGRESSIONE]
    else:
        esc = []
    ax.plot(dd, ww, color=teal, lw=2, marker="o", ms=4.5, zorder=3,
            label="Pesate")
    if esc:
        ax.scatter([e[0] for e in esc], [e[1] for e in esc], s=40,
                   facecolors="white", edgecolors=teal, lw=1.5, zorder=4,
                   label="Pesate escluse dal calcolo")
    if "punti" in pr:
        pd = [x[0] for x in pr["punti"]]
        pw = [x[1] for x in pr["punti"]]
        b = pr["banda"]
        ax.fill_between(pd, [max(pr["tetto"], w - b) for w in pw],
                        [w + b for w in pw], color=orange, alpha=0.13, lw=0)
        ax.plot(pd, pw, color=orange, lw=1.8, ls="--", label="Proiezione prudente")
    etich = "Obiettivo" if p["obiettivo_peso_kg"] is not None else "Soglia prudenziale"
    if "punti" in pr:
        ax.axhline(pr["tetto"], color=grey, lw=0.9, ls=":")
        ax.text(ax.get_xlim()[0], pr["tetto"], f"  {etich} {_kg(pr['tetto'])} kg",
                color=grey, fontsize=7, va="bottom")
    f = p["farmaco"]
    if f:
        for chiave, testo in (("data_titolazione", "titolazione"),
                              ("data_detitolazione", "riduzione dose")):
            if f.get(chiave):
                x = date.fromisoformat(f[chiave])
                ax.axvline(x, color=navy, lw=0.7, ls="-.", alpha=0.5)
                ax.text(x, ax.get_ylim()[1], f" {testo}", rotation=90, fontsize=6.5,
                        color=navy, va="top", ha="right", alpha=0.8)
    lo, hi = ax.get_ylim()                 # scala minima 6 kg: evita di
    if hi - lo < 6:                        # ingigantire cali piccoli
        c = (hi + lo) / 2
        ax.set_ylim(c - 3, c + 3)
    ax.set_ylabel("Peso (kg)", fontsize=8, color=navy)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.tick_params(labelsize=7, colors=grey)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#CCCCCC")
    ax.grid(axis="y", color="#EEEEEE", lw=0.6)
    ax.legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return RLImage(buf, width=_INNER, height=_INNER * 3.6 / 7.0)


def _pagina1(p):
    mis = p["_mis"]
    d0, w0, _ = mis[0]
    d1, w1, _ = mis[-1]
    calo = w0 - w1
    sett = (d1 - p["_inizio"]).days / 7
    s = [Spacer(1, 2*mm), Paragraph("ANDAMENTO DEL PERCORSO", _sTitolo),
         Spacer(1, 1*mm),
         Paragraph(f"{p['nome']}  |  Altezza {p['altezza_cm']} cm  |  "
                   f"Piano da {p['kcal_piano']}", _sSub)]
    f = p["farmaco"]
    if f:
        riga = f"Terapia: {f['nome']} dal {_dt(_d(f['data_inizio'], 'farmaco'))} ({f['dose_iniziale']})"
        if f.get("data_titolazione"):
            riga += f" · {f['dose_titolazione']} dal {_dt(_d(f['data_titolazione'], 'farmaco'))}"
        if f.get("data_detitolazione"):
            riga += f" · {f['dose_detitolazione']} dal {_dt(_d(f['data_detitolazione'], 'farmaco'))}"
        s.append(Paragraph(riga, _sTagline))
    s += [Spacer(1, 2.5*mm),
          HRFlowable(width=_INNER, thickness=1.5, color=_ORANGE, spaceAfter=3),
          Paragraph(TESTI["intro"], _sTxt), Spacer(1, 3*mm)]

    kpi = [(f"{_kg(w0)} kg", f"Peso iniziale<br/>{_dt(d0)}", _NAVY),
           (f"{_kg(w1)} kg", f"Peso attuale<br/>{_dt(d1)}", _TEAL),
           (f"−{_kg(calo)} kg" if calo >= 0 else f"+{_kg(-calo)} kg",
            f"Variazione<br/>{_kg(calo / w0 * 100)}% del peso iniziale", _ORANGE),
           (_kg(_imc(w1, p["altezza_cm"])),
            f"IMC attuale<br/>(iniziale {_kg(_imc(w0, p['altezza_cm']))})", _GOLD),
           (_kg(sett, 0), "Settimane<br/>di percorso", _NAVY)]
    kt = Table([[[Paragraph(v, _sKpiV), Paragraph(l, _sKpiL)] for v, l, _ in kpi]],
               colWidths=[_INNER / 5] * 5)
    kt.setStyle(TableStyle(
        [("BACKGROUND", (i, 0), (i, 0), c) for i, (_, _, c) in enumerate(kpi)] +
        [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
         ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
         ("LINEAFTER", (0, 0), (-2, -1), 1.5, _WHITE)]))
    s += [kt, Spacer(1, 3*mm)]

    cv = p["circ_vita"]
    if cv:
        a, b = SOGLIE_VITA[p["sesso"]]
        att = cv["attuale_cm"]
        fascia = ("sotto la soglia di rischio" if att < a else
                  "nella fascia di rischio aumentato" if att < b else
                  "nella fascia di rischio elevato")
        diff = cv["iniziale_cm"] - att
        s.append(_box(
            f"<b>Circonferenza vita:</b> {_kg(cv['iniziale_cm'], 0)} cm all'inizio, "
            f"{_kg(att, 0)} cm al {_dt(p['_vita_data'])} "
            f"(<b>−{_kg(diff, 0)} cm</b>). Valore attuale {fascia}. "
            f"Riferimenti: rischio aumentato da {a} cm, elevato da {b} cm.",
            _sBoxG, _BG_GOLD))
        s.append(Spacer(1, 3*mm))

    s.append(Paragraph("Cronologia delle pesate", _sSez))
    righe = [[Paragraph(h, _sTh) for h in
              ("Data", "Peso", "Rispetto alla<br/>precedente", "Dall'inizio", "Nota")]]
    prec = None
    for d, w, e in mis:
        dp = "—" if prec is None else _diff(w, prec)
        righe.append([Paragraph(_dt(d), _sTd), Paragraph(f"{_kg(w, 2)} kg", _sTd),
                      Paragraph(dp, _sTd), Paragraph(_diff(w, w0), _sTd),
                      Paragraph(e, _sTdL)])
        prec = w
    s.append(_tabella(righe, [_INNER * x for x in (0.16, 0.15, 0.16, 0.14, 0.39)]))
    if p.get("strumento_riferimento"):
        s.append(Paragraph(f"Pesate eseguite con: {p['strumento_riferimento']}", _sSmall))

    blocco = [Paragraph("Cosa significano questi numeri", _sSez)]
    for tit, txt in TESTI["significato"]:
        blocco.append(Paragraph(f"<b>{tit}.</b> {txt}", _sTxt))
        blocco.append(Spacer(1, 1.5*mm))
    for c in ("nota_glicemia", "nota_urea", "nota_extra"):
        if (p.get(c) or "").strip():
            blocco.append(Paragraph(f"<b>Nota.</b> {p[c]}", _sTxt))
            blocco.append(Spacer(1, 1.5*mm))
    s.append(KeepTogether(blocco))
    return s


def _pagina2(p, pr):
    s = [Paragraph("Il tuo andamento", _sSez), _grafico(p, pr), Spacer(1, 3*mm)]
    if "punti" in pr:
        s.append(Paragraph("Proiezione dei prossimi mesi", _sSez))
        righe = [[Paragraph(h, _sTh) for h in ("Mese", "Data indicativa", "Peso stimato")]]
        ultima = pr["punti"][0][0]
        fine = pr["punti"][-1][0]
        for m in range(1, 7):
            target = ultima + timedelta(days=round(30.44 * m))
            if target > fine + timedelta(days=15):
                break
            pt = min(pr["punti"], key=lambda x: abs((x[0] - target).days))
            lo = max(pr["tetto"], pt[1] - pr["banda"])
            hi = pt[1] + pr["banda"]
            righe.append([Paragraph(f"+{m}", _sTd), Paragraph(_dt(target), _sTd),
                          Paragraph(f"{_kg(lo)} – {_kg(hi)} kg", _sTd)])
        s.append(_tabella(righe, [_INNER * 0.2, _INNER * 0.35, _INNER * 0.45]))
        if pr.get("data_tetto"):
            nome = ("l'obiettivo concordato" if p["obiettivo_peso_kg"] is not None
                    else "la soglia prudenziale")
            s.append(Paragraph(f"Secondo questa stima {nome} di {_kg(pr['tetto'])} kg "
                               f"verrebbe raggiunto intorno al {_dt(pr['data_tetto'])}.",
                               _sSmall))
        s.append(Spacer(1, 3*mm))
        s.append(_box(TESTI["avvertenza_farmaco"] if pr["modo"] == "farmaco"
                      else TESTI["avvertenza_dieta"], _sBoxR, _BG_RED))
    else:
        s.append(_box(TESTI["proiezione_assente_poche"] if pr["motivo"] == "poche"
                      else TESTI["proiezione_assente_stabile"], _sBoxR, _BG_RED))
    return s


def _pagina3():
    s = [Paragraph("Consigli pratici", _sSez)]
    for tit, txt in TESTI["consigli"]:
        s.append(Paragraph(f"<b>{tit}.</b> {txt}", _sTxt))
        s.append(Spacer(1, 2*mm))
    s += [Spacer(1, 5*mm), _box(TESTI["motivazionale"], _sBoxT, _BG_TEAL)]
    return s


def genera(json_path, output_path=None):
    p = carica(json_path)
    pr = proiezione(p)
    if output_path is None:
        base = os.path.splitext(os.path.basename(json_path))[0]
        output_path = f"Andamento_{base}.pdf"
    piede = f"Andamento aggiornato al {_dt(p['_mis'][-1][0])}"
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=_MARGIN, rightMargin=_MARGIN,
                            topMargin=17*mm, bottomMargin=14*mm,
                            title=f"Andamento — {p['nome']}")
    story = _pagina1(p) + [PageBreak()] + _pagina2(p, pr) + [PageBreak()] + _pagina3()
    cb = lambda c, d: _on_page(c, d, piede)
    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    return output_path, pr


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py "
                 "Paziente.json [output.pdf]")
    try:
        out, pr = genera(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    except ErroreDati as e:
        sys.exit(f"STOP — dati del JSON non validi:{e}")
    desc = {"farmaco": "fasi da terapia", "andamento": "da pesate reali",
            "nessuna": "nessuna proiezione"}[pr["modo"]]
    print(f"PDF generato: {out}  (proiezione: {desc})")
