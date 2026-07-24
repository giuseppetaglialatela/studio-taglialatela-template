#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          TEMPLATE PIANO ALIMENTARE — Studio Nutrizionale Taglialatela        ║
║          Dott. Giuseppe Taglialatela — Consulente in Nutrizione              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Versione: 4.0  |  Unificato: 22/07/2026                                     ║
║  Sostituisce e annulla le precedenti v1.0 e v3.0 (file duplicati/incompleti) ║
║                                                                              ║
║  Motore grafico: identico byte-per-byte alla v1.0 approvata il 24/06/2026.   ║
║  Zona dati: placeholder puliti, chiavi emoji corrette.                       ║
║                                                                              ║
║  ISTRUZIONI D'USO                                                            ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║  1. Modificare SOLO le sezioni "DATI PAZIENTE", "BOX_INFO" e "GIORNI"        ║
║  2. NON toccare nulla sotto "═══ MOTORE GRAFICO ═══"                         ║
║  3. Lanciare: python3 TEMPLATE_PianoAlimentare_StudioTaglialatela_v4.py      ║
║     oppure:   python3 TEMPLATE..._v4.py output/nomefile.pdf                  ║
║                                                                              ║
║  STRUTTURA PASTO — 6 campi:                                                  ║
║  ("chiave_emoji", "LABEL", "Nome piatto", "dettaglio ingredienti",           ║
║   "~kcal", nota_o_None)                                                      ║
║                                                                              ║
║  chiave_emoji: "colazione" | "pranzo" | "spuntino" | "cena"                  ║
║  ATTENZIONE: lo SPUNTINO usa la chiave "spuntino", non "pranzo".             ║
║                                                                              ║
║  NOTA: le appendici (alternative spuntino, guide verdure/legumi/frutta)      ║
║  NON sono implementate nel motore. Se servono, vanno aggiunte come giorni    ║
║  extra nella zona dati oppure richieste come sviluppo separato.              ║
║                                                                              ║
║  OUTPUT: A4, un giorno per pagina, giorno 1 nella pagina dell'intestazione.  ║
║                                                                              ║
║  DIPENDENZE: pip install reportlab pillow                                    ║
║  FONT richiesti (Ubuntu/Debian):                                             ║
║    /usr/share/fonts/truetype/liberation/LiberationSans-*.ttf                 ║
║    /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os, sys, base64, tempfile

# ═════════════════════════════════════════════════════════════════
#  ▶▶▶  DATI PAZIENTE — MODIFICARE QUI                             ◀◀◀
# ════════════════════════════════════════════════════════════════════

PAZIENTE = {
    "nome":       "Nome Cognome",
    "eta":        "XX anni",
    "condizione": "Descrizione condizione clinica",
    "obiettivo":  "XX kg",
    "note_piano": "Struttura su N giorni · N pasti · versione 1",
    "mese":       "Mese Anno",
    "rivalutare": "Da rivalutare dopo N settimane",
}

BOX_INFO = {
    # Testo box giallo sinistra — target calorico e obiettivi
    "target":   "⭐  Target: ~X.XXX kcal/die  ·  deficit ~XXX kcal  ·  perdita attesa X,X kg/sett",
    # Testo box rosso destra — allergie e avvertenze assolute
    "allergie": "🚫  Indicare qui allergie accertate e qualsiasi esclusione obbligatoria.",
}

# ───────────────────────────────────────────────────────────────────
#  GIORNI DEL PIANO
#  Struttura ogni pasto: 6 campi
#  (chiave_emoji, "LABEL", "Nome piatto", "dettaglio ingredienti", "~kcal", nota)
#
#  chiave_emoji: "colazione" | "pranzo" | "spuntino" | "cena"
#  nota: stringa opzionale oppure None
#  "libero": True  →  colori oro anziché arancione/blu (giorno libero)
# ────────────────────────────────────────────────────────────────────

GIORNI = [
    {
        "num": "1", "nome": "Lunedì",
        "pasti": [
            ("colazione", "COLAZIONE",
             "Nome colazione",
             "ingrediente 1 Xg · ingrediente 2 Xg · ingrediente 3 Xg",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Nome piatto pranzo",
             "ingrediente 1 Xg · ingrediente 2 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Nome piatto cena",
             "ingrediente 1 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
        ],
        "totale": "Totale giornata: ~X.XXX kcal  ·  Spuntino pomeridiano facoltativo: 1 frutto di stagione",
    },
    {
        "num": "2", "nome": "Martedì",
        "pasti": [
            ("colazione", "COLAZIONE",
             "Nome colazione",
             "ingrediente 1 Xg · ingrediente 2 Xg · ingrediente 3 Xg",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Nome piatto pranzo",
             "ingrediente 1 Xg · ingrediente 2 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Nome piatto cena",
             "ingrediente 1 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
        ],
        "totale": "Totale giornata: ~X.XXX kcal  ·  Spuntino pomeridiano facoltativo: 1 frutto di stagione",
    },
    {
        "num": "3", "nome": "Mercoledì",
        "pasti": [
            ("colazione", "COLAZIONE",
             "Nome colazione",
             "ingrediente 1 Xg · ingrediente 2 Xg · ingrediente 3 Xg",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Nome piatto pranzo",
             "ingrediente 1 Xg · ingrediente 2 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Nome piatto cena",
             "ingrediente 1 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
        ],
        "totale": "Totale giornata: ~X.XXX kcal  ·  Spuntino pomeridiano facoltativo: 1 frutto di stagione",
    },
    {
        "num": "4", "nome": "Giovedì",
        "pasti": [
            ("colazione", "COLAZIONE",
             "Nome colazione",
             "ingrediente 1 Xg · ingrediente 2 Xg · ingrediente 3 Xg",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Nome piatto pranzo",
             "ingrediente 1 Xg · ingrediente 2 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Nome piatto cena",
             "ingrediente 1 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
        ],
        "totale": "Totale giornata: ~X.XXX kcal  ·  Spuntino pomeridiano facoltativo: 1 frutto di stagione",
    },
    {
        "num": "5", "nome": "Venerdì",
        "pasti": [
            ("colazione", "COLAZIONE",
             "Nome colazione",
             "ingrediente 1 Xg · ingrediente 2 Xg · ingrediente 3 Xg",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Nome piatto pranzo",
             "ingrediente 1 Xg · ingrediente 2 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Nome piatto cena",
             "ingrediente 1 Xg · verdura Xg · olio EVO Xg",
             "~XXX kcal", None),
        ],
        "totale": "Totale giornata: ~X.XXX kcal  ·  Spuntino pomeridiano facoltativo: 1 frutto di stagione",
    },
    {
        "num": "6", "nome": "Sabato o Domenica — Giorno libero",
        "libero": True,
        "pasti": [
            ("colazione", "COLAZIONE",
             "A piacere",
             "indicazioni generali per colazione libera",
             "~XXX kcal", None),
            ("spuntino", "SPUNTINO MATTINA",
             "Nome spuntino",
             "ingrediente 1 Xg · ingrediente 2 Xg",
             "~XXX kcal", None),
            ("pranzo", "PRANZO",
             "Pasto libero o indicazioni",
             "indicazioni generali pranzo giorno libero",
             "~XXX kcal", None),
            ("cena", "CENA",
             "Pasto libero",
             "linee guida minime: evitare eccesso di carni rosse, fritti, alcol",
             None, None),
        ],
        "totale": "Totale giornata: ~X.XXX–X.XXX kcal con cena libera moderata",
    },
]

# ═══════════════════════════════════════════════════════════════════
#  ═══ MOTORE GRAFICO — NON MODIFICARE ═══
#  Tutto ciò che segue definisce l'identità visiva approvata.
#  Qualsiasi modifica altera il formato ufficiale dello studio.
# ════════════════════════════════════════════════════════════════════

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 HRFlowable, PageBreak, Table, TableStyle,
                                 Flowable, Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage, ImageDraw, ImageFont

# ── Font ──
_FONT_DIR = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Sans",       f"{_FONT_DIR}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",   f"{_FONT_DIR}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SansItalic", f"{_FONT_DIR}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("SansBI",     f"{_FONT_DIR}/LiberationSans-BoldItalic.ttf"))

# ── Colori istituzionali ──
_TEAL    = colors.HexColor("#2E7D8C")
_ORANGE  = colors.HexColor("#C0622B")
_NAVY    = colors.HexColor("#1C3A4A")
_DARK    = colors.HexColor("#1A1A1A")
_GREY    = colors.HexColor("#666666")
_RED_AL  = colors.HexColor("#C0392B")
_GOLD    = colors.HexColor("#8B6914")
_BORDER  = colors.HexColor("#CCCCCC")
_WHITE   = colors.white
_ICON_COL  = colors.HexColor("#E8A020")
_ICON_PRAN = colors.HexColor("#2E7D8C")
_ICON_SPUN = colors.HexColor("#8B6914")
_ICON_CENA = colors.HexColor("#1C3A4A")

_W, _H   = A4
_MARGIN  = 20*mm
_INNER   = _W - 2*_MARGIN
_EMOJI_SZ = 3.8*mm

# ── Genera emoji PNG da NotoColorEmoji ──
def _make_emoji_imgs():
    font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(
            f"NotoColorEmoji.ttf non trovato in {font_path}.\n"
            "Installare con: sudo apt install fonts-noto-color-emoji")
    font = ImageFont.truetype(font_path, 109)
    mapping = {
        "colazione": "☀️",
        "pranzo":    "🍽️",
        "spuntino":  "🥨",
        "cena":      "🌙",
    }
    tmpdir = tempfile.mkdtemp()
    paths = {}
    for key, emoji in mapping.items():
        img = PILImage.new("RGBA", (109, 109), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), emoji, font=font, embedded_color=True)
        path = os.path.join(tmpdir, f"{key}.png")
        img.save(path, "PNG")
        paths[key] = path
    return paths

# ── Stili tipografici ──
def _S(name, **kw):
    d = dict(fontName="Sans", fontSize=9, leading=13, textColor=_DARK,
             spaceAfter=0, spaceBefore=0)
    d.update(kw)
    return ParagraphStyle(name, **d)

_sTitolo  = _S("tit", fontSize=21, textColor=_NAVY,  fontName="SansBold",
                leading=25, alignment=TA_CENTER, spaceAfter=2)
_sSub     = _S("sub", fontSize=10, textColor=_DARK,  fontName="SansBold",
                leading=14, alignment=TA_CENTER, spaceAfter=1)
_sTagline = _S("tgl", fontSize=8.5,textColor=_GREY,  fontName="SansItalic",
                leading=12, alignment=TA_CENTER)
_sLeg     = _S("leg", fontSize=8.5,textColor=_WHITE, fontName="SansBold",
                leading=12, alignment=TA_CENTER)
_sTgt     = _S("tgt", fontSize=8,  textColor=_GOLD,  fontName="Sans", leading=12)
_sAlg     = _S("alg", fontSize=8,  textColor=_RED_AL,fontName="Sans", leading=12)
_sMealTxt = _S("mt",  fontSize=9,  textColor=_DARK,  fontName="Sans", leading=13)
_sMealKcal= _S("mk",  fontSize=8.5,textColor=_ORANGE,fontName="SansItalic", leading=11)
_sMealNote= _S("mn",  fontSize=8,  textColor=_TEAL,  fontName="SansItalic", leading=11)
_sTotale  = _S("tot", fontSize=8.5,textColor=_GREY,  fontName="Sans", leading=12)

# ── MealLabel Flowable ──
class _MealLabel(Flowable):
    """Emoji PNG + testo label pasto. Non modificare."""
    def __init__(self, emoji_path, label, space_before=8):
        Flowable.__init__(self)
        self._path  = emoji_path
        self._label = label
        self._fs    = 8.5
        self._esz   = _EMOJI_SZ
        self._sb    = space_before
        self._w     = _INNER
        self._h     = max(self._esz, self._fs * 1.3) + space_before

    def wrap(self, aw, ah): return (self._w, self._h)
    def split(self, aw, ah): return []

    def draw(self):
        c = self.canv
        y = self._sb
        try:
            c.drawImage(self._path, 0, y - 0.5,
                        width=self._esz, height=self._esz,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
        c.setFont("SansBold", self._fs)
        c.setFillColor(_ORANGE)
        c.drawString(self._esz + 2.5, y - 0.5, self._label)

# ── Header/Footer ──
def _on_page(canvas, doc, paziente, mese, rivalutare):
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
    canvas.drawString(_MARGIN, 9*mm, f"{mese}   ·   {rivalutare}")
    canvas.drawRightString(_W - _MARGIN, 9*mm, f"Pag.  {doc.page}")
    canvas.restoreState()

# ── Blocco pasto ──
def _meal_block(emoji_path, label, nome, det, kcal, nota):
    items = [_MealLabel(emoji_path, label)]
    txt = f'<b>{nome}</b>'
    if det:
        txt += f' <font color="#444444">— {det}</font>'
    items.append(Paragraph(txt, _sMealTxt))
    if kcal:
        items.append(Paragraph(f'<i>({kcal})</i>', _sMealKcal))
    if nota:
        items.append(Paragraph(
            f'<font color="#2E7D8C">■</font>  <i>{nota}</i>', _sMealNote))
    return items

# ── Blocco giorno ──
def _day_block(g, emoji_paths):
    is_libero = g.get("libero", False)
    d_col = _GOLD if is_libero else _ORANGE
    elems = []
    num_p = Paragraph(
        f'<font color="{"#8B6914" if is_libero else "#C0622B"}"><b>{g["num"]}</b></font>',
        _S("dn", fontSize=20, fontName="SansBold", leading=24))
    nome_p = Paragraph(
        f'<b>{g["nome"]}</b>',
        _S("nn", fontSize=20, fontName="SansBold", leading=24, textColor=_NAVY))
    hdr = Table([[num_p, nome_p]], colWidths=[10*mm, _INNER-10*mm])
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (0,0), 0),
        ("LEFTPADDING",   (1,0), (1,0), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))
    elems.append(hdr)
    elems.append(HRFlowable(width=_INNER, thickness=1.2, color=d_col, spaceAfter=5))
    for (ek, label, nome, det, kcal, nota) in g["pasti"]:
        elems += _meal_block(emoji_paths[ek], label, nome, det, kcal, nota)
        elems.append(Spacer(1, 5*mm))
    elems.append(HRFlowable(width=_INNER, thickness=0.4, color=_BORDER, spaceAfter=2))
    elems.append(Paragraph(g["totale"], _sTotale))
    return elems

# ── Intestazione pagina 1 ──
def _cover(p, box_info, emoji_paths):
    story = []
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("PIANO ALIMENTARE SETTIMANALE", _sTitolo))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        f"{p['eta']}  |  {p['condizione']}  |  Obiettivo: {p['obiettivo']}", _sSub))
    story.append(Paragraph(p["note_piano"], _sTagline))
    story.append(Spacer(1, 2.5*mm))
    story.append(HRFlowable(width=_INNER, thickness=1.5, color=_ORANGE, spaceAfter=2.5))
    # Barra legenda
    e_sz = 3.5*mm
    leg_data = [[
        Table([[RLImage(emoji_paths["colazione"], width=e_sz, height=e_sz),
                Paragraph("Colazione", _sLeg)]], colWidths=[e_sz+1*mm, 24*mm]),
        Table([[RLImage(emoji_paths["pranzo"],    width=e_sz, height=e_sz),
                Paragraph("Pranzo",    _sLeg)]], colWidths=[e_sz+1*mm, 20*mm]),
        Table([[RLImage(emoji_paths["spuntino"],  width=e_sz, height=e_sz),
                Paragraph("Spuntino",  _sLeg)]], colWidths=[e_sz+1*mm, 22*mm]),
        Table([[RLImage(emoji_paths["cena"],      width=e_sz, height=e_sz),
                Paragraph("Cena",      _sLeg)]], colWidths=[e_sz+1*mm, 18*mm]),
    ]]
    leg_tbl = Table(leg_data, colWidths=[_INNER/4]*4, rowHeights=[8*mm])
    leg_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), _ICON_COL),
        ("BACKGROUND",    (1,0), (1,0), _ICON_PRAN),
        ("BACKGROUND",    (2,0), (2,0), _ICON_SPUN),
        ("BACKGROUND",    (3,0), (3,0), _ICON_CENA),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 2),
        ("RIGHTPADDING",  (0,0), (-1,-1), 2),
    ]))
    story.append(leg_tbl)
    story.append(Spacer(1, 3*mm))
    # Box info
    tgt_data = [[
        Paragraph(box_info["target"],   _sTgt),
        Paragraph(box_info["allergie"], _sAlg),
    ]]
    tgt_tbl = Table(tgt_data, colWidths=[_INNER*0.52, _INNER*0.48])
    tgt_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), colors.HexColor("#FEF9E7")),
        ("BACKGROUND",    (1,0), (1,0), colors.HexColor("#FDECEA")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LINEAFTER",     (0,0), (0,-1), 0.5, _BORDER),
    ]))
    story.append(tgt_tbl)
    story.append(Spacer(1, 5*mm))
    return story

# ════════════════════════════════════════════════════════════════════
#  FUNZIONE PRINCIPALE
# ════════════════════════════════════════════════════════════════════

def genera_piano(output_path, paziente=PAZIENTE, giorni=GIORNI,
                 box_info=BOX_INFO):
    """
    Genera il PDF del piano alimentare.
    output_path: percorso del file PDF da creare.
    """
    emoji_paths = _make_emoji_imgs()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=_MARGIN, rightMargin=_MARGIN,
        topMargin=17*mm, bottomMargin=14*mm,
    )

    def _page_cb(canvas, doc):
        _on_page(canvas, doc,
                 paziente, paziente["mese"], paziente["rivalutare"])

    story = _cover(paziente, box_info, emoji_paths)

    # Giorno 1 — stessa pagina dell'intestazione
    for el in _day_block(giorni[0], emoji_paths):
        story.append(el)

    # Giorni 2–N — ognuno su pagina propria
    for g in giorni[1:]:
        story.append(PageBreak())
        for el in _day_block(g, emoji_paths):
            story.append(el)

    doc.build(story, onFirstPage=_page_cb, onLaterPages=_page_cb)
    print(f"✅ PDF generato: {output_path}")


# ── Esecuzione diretta ──
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else \
        "/mnt/user-data/outputs/piano_alimentare.pdf"
    genera_piano(out)
