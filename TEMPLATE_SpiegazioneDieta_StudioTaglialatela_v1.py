#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║   TEMPLATE SPIEGAZIONE DIETA — Studio Nutrizionale Taglialatela          ║
║   Dott. Giuseppe Taglialatela — Consulente in Nutrizione                 ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Versione: 1.0 | Creato: 27/07/2026                                      ║
║  Accompagna il PDF del piano alimentare (documento informativo).        ║
║                                                                          ║
║  ISTRUZIONI D'USO                                                        ║
║  1. Modificare SOLO la sezione "ZONA DATI" qui sotto.                    ║
║  2. NON toccare nulla sotto "MOTORE GRAFICO".                            ║
║  3. Lanciare: python3 TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py \
║               output/nomefile.pdf                                       ║
║                                                                          ║
║  REGISTRO OBBLIGATORIO: tecnico e impersonale. Non rivolgersi al        ║
║  paziente in seconda persona ("tu"/"lei") e non usarne il nome nel      ║
║  corpo del testo — si parla del profilo/piano, non alla persona.        ║
║  Ogni SEZIONE è una tupla (titolo, [paragrafi...], [bullet "in pratica"] ║
║  o None).                                                                ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
import sys

# ═════════════════════════════════════════════════════════════════
#  ▶▶▶  ZONA DATI — MODIFICARE QUI PER OGNI PAZIENTE                ◀◀◀
# ════════════════════════════════════════════════════════════════════

INTESTAZIONE = {
    "studio": "STUDIO NUTRIZIONALE",
    "nutrizionista": "Dott. Giuseppe Taglialatela",
    "qualifica": "Consulente in Nutrizione",
}

TITOLO = "IL PERCORSO ALIMENTARE: PERCHÉ È FATTO COSÌ"
SOTTOTITOLO = "Documento informativo che accompagna il piano alimentare personalizzato"

INTRO = (
    "Questo documento spiega, in modo semplice, perché il piano alimentare è costruito "
    "in un certo modo. Non è uno schema standard: è costruito sul profilo, sul contesto "
    "di vita e sull'obiettivo concordato. Capire il perché delle scelte è il primo passo "
    "per seguirle con serenità e ottenere risultati duraturi."
)

# Ogni sezione: (titolo, [paragrafi...], [bullet "in pratica"] oppure None)
SEZIONI = [
    ("1. Il punto di partenza", ["testo placeholder"], None),
]

CHIUSURA_NOME = "Dott. Giuseppe Taglialatela"
CHIUSURA_QUALIFICA = "Consulente in Nutrizione"
CHIUSURA_NOTA = (
    "Nota: questo documento ha finalità informative e accompagna il piano alimentare "
    "personalizzato."
)

# ═══════════════════════════════════════════════════════════════════
#  ═══ MOTORE GRAFICO — NON MODIFICARE ═══
# ════════════════════════════════════════════════════════════════════

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 HRFlowable, ListFlowable, ListItem)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

COLORE_TITOLO = colors.HexColor("#1F4E5F")
COLORE_ACCENTO = colors.HexColor("#C9752B")
COLORE_TESTO = colors.HexColor("#2B2B2B")
COLORE_GRIGIO = colors.HexColor("#6B6B6B")

STY_STUDIO = ParagraphStyle("studio", fontName="Helvetica-Bold", fontSize=10,
                             textColor=COLORE_TITOLO, spaceAfter=0)
STY_QUALIFICA = ParagraphStyle("qualifica", fontName="Helvetica-Oblique", fontSize=9,
                                textColor=COLORE_GRIGIO, spaceAfter=0)
STY_TITOLO = ParagraphStyle("titolo", fontName="Helvetica-Bold", fontSize=17,
                             textColor=COLORE_TITOLO, spaceBefore=14, spaceAfter=6,
                             alignment=TA_LEFT, leading=21)
STY_SOTTOTITOLO = ParagraphStyle("sottotitolo", fontName="Helvetica-Oblique", fontSize=10,
                                  textColor=COLORE_GRIGIO, spaceAfter=14)
STY_INTRO = ParagraphStyle("intro", fontName="Helvetica", fontSize=10,
                            textColor=COLORE_TESTO, spaceAfter=14, leading=14)
STY_SEZIONE_TITOLO = ParagraphStyle("sezione_titolo", fontName="Helvetica-Bold", fontSize=12.5,
                                     textColor=COLORE_ACCENTO, spaceBefore=14, spaceAfter=6)
STY_PARAGRAFO = ParagraphStyle("paragrafo", fontName="Helvetica", fontSize=10,
                                textColor=COLORE_TESTO, spaceAfter=8, leading=14)
STY_BULLET = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10,
                             textColor=COLORE_TESTO, leading=13.5, leftIndent=0)
STY_FIRMA = ParagraphStyle("firma", fontName="Helvetica-Bold", fontSize=10,
                            textColor=COLORE_TITOLO, spaceBefore=18)
STY_FIRMA_Q = ParagraphStyle("firma_q", fontName="Helvetica-Oblique", fontSize=9,
                              textColor=COLORE_GRIGIO)
STY_NOTA = ParagraphStyle("nota", fontName="Helvetica-Oblique", fontSize=8.5,
                           textColor=COLORE_GRIGIO, spaceBefore=16, leading=11)


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8D8D8"))
    canvas.setLineWidth(0.6)
    canvas.line(20 * mm, 285 * mm, 190 * mm, 285 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLORE_GRIGIO)
    canvas.drawString(20 * mm, 12 * mm, INTESTAZIONE["nutrizionista"])
    canvas.drawRightString(190 * mm, 12 * mm, f"Pag. {doc.page}")
    canvas.restoreState()


def genera_documento(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             leftMargin=20 * mm, rightMargin=20 * mm,
                             topMargin=18 * mm, bottomMargin=18 * mm)
    story = []

    story.append(Paragraph(INTESTAZIONE["studio"], STY_STUDIO))
    story.append(Paragraph(f"{INTESTAZIONE['nutrizionista']} — {INTESTAZIONE['qualifica']}",
                            STY_QUALIFICA))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#D8D8D8"),
                             spaceBefore=6, spaceAfter=4))

    story.append(Paragraph(TITOLO, STY_TITOLO))
    story.append(Paragraph(SOTTOTITOLO, STY_SOTTOTITOLO))
    story.append(Paragraph(INTRO, STY_INTRO))

    for titolo, paragrafi, bullets in SEZIONI:
        story.append(Paragraph(titolo, STY_SEZIONE_TITOLO))
        for p in paragrafi:
            story.append(Paragraph(p, STY_PARAGRAFO))
        if bullets:
            items = [ListItem(Paragraph(b, STY_BULLET), leftIndent=14) for b in bullets]
            story.append(ListFlowable(items, bulletType="bullet", start="●",
                                       leftIndent=10, spaceBefore=2, spaceAfter=10))

    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#D8D8D8"),
                             spaceBefore=10, spaceAfter=10))
    story.append(Paragraph(CHIUSURA_NOME, STY_FIRMA))
    story.append(Paragraph(CHIUSURA_QUALIFICA, STY_FIRMA_Q))
    story.append(Paragraph(CHIUSURA_NOTA, STY_NOTA))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"✅ PDF generato: {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/spiegazione_dieta.pdf"
    genera_documento(out)
