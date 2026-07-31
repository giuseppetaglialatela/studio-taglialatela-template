"""
TEMPLATE_AndamentoDieta_StudioTaglialatela.py
================================================
Template per generare il PDF "Andamento Dieta" da inviare al paziente.

COME USARLO (per Claude, ad ogni nuova richiesta):
1. Copiare questo file in /home/claude/
2. Modificare SOLO la sezione "DATI PAZIENTE" qui sotto (PAZIENTE, MISURAZIONI,
   FARMACO, OBIETTIVO, CONSIGLI)
3. Non toccare la sezione "MOTORE GRAFICO" (palette, stili, layout, grafico,
   struttura del PDF): è identica per ogni paziente e garantisce coerenza
   visiva con tutti i documenti dello studio.
4. Eseguire lo script: python3 NomeFile.py
5. Validare con pdftoppm prima di consegnare il file definitivo
6. Salvare PDF + .py compilato su memoria esterna (Drive)

STRUTTURA DEL DOCUMENTO (fissa, non modificare):
- Pagina 1: titolo, intro, KPI bar, box circonferenza vita (se presente),
  cronologia misurazioni, spiegazione "cosa significano questi numeri"
- Pagina 2: grafico andamento + tabella proiezione prossimi mesi + box
  avvertenza cautelativa
- Pagina 3: consigli pratici + box motivazionale + footer

Logica di proiezione (cautelativa, NON modificare i tassi senza indicazione
esplicita del nutrizionista):
  - Settimane 0-8 dall'inizio dieta: rallentamento progressivo da titolazione
    iniziale farmaco (default 0.55 kg/settimana)
  - Settimane 8-16: fase titolazione intermedia (default 0.60 kg/settimana)
  - Settimane 16+: avvicinamento a plateau (default 0.40 kg/settimana)
  - Floor di sicurezza: il peso proiettato non scende mai sotto WEIGHT_FLOOR_KG
  - Banda di incertezza: ±1.5 kg attorno alla proiezione
Questi tassi rispecchiano un'aspettativa REALISTICA E PRUDENTE per pazienti
in trattamento con farmaci agonisti GIP/GLP-1 — non vanno resi più aggressivi
per "abbellire" il documento.
"""

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  NOTA DI PROVENIENZA — leggere prima di usare questo file                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# QUESTO FILE NON È ESEGUIBILE. È una SPECIFICA, non un template funzionante.
#
# Il template originale è andato perduto: il corpo del motore grafico stava in
# una cartella di sessione non più esistente, e nessuna delle tre copie su
# Drive lo contiene (verificato il 30/07/2026 — 5.109 B, 605 B, 635 B: tutte
# header + zona dati, nessuna con il motore).
#
# Ciò che segue è quanto è sopravvissuto, ricomposto dalla copia più completa:
#   · il docstring integrale, che è di fatto la specifica del documento
#   · gli import, che dicono su cosa è costruito (matplotlib Agg + reportlab)
#   · la struttura della zona dati
#
# La ZONA DATI è stata NEUTRALIZZATA: i valori del paziente reale sono stati
# sostituiti da segnaposto. Per la regola di separazione dello studio, i dati
# dei pazienti non escono da Drive. In questa forma il file è condivisibile e
# può stare su GitHub insieme agli altri due template.
#
# COSA MANCA: tutto ciò che sta sotto il marcatore MOTORE GRAFICO in fondo.
# Riferimenti per la ricostruzione: i PDF di andamento già consegnati (Drive >
# Andamento Dieta Pazienti) come riferimento visivo, e il modulo M5 su GitHub
# per le regole invariabili.

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
from datetime import date, timedelta
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


# ════════════════════════════════════════════════════════════════════════════
# ██ DATI PAZIENTE — UNICA SEZIONE DA MODIFICARE PER OGNI NUOVO REPORT ██
# ════════════════════════════════════════════════════════════════════════════
# I valori qui sotto sono SEGNAPOSTO. Nessun dato reale.

PAZIENTE = {
    "nome": "<Nome Cognome>",
    "altezza_cm": 000,           # altezza FISSA da usare in tutti i calcoli IMC
                                 # (anche se gli scontrini riportano valori diversi)
}

# Farmaco / terapia in corso (per box dedicato e linguaggio del testo).
# Se il paziente non assume farmaci dimagranti, impostare FARMACO = None
FARMACO = {
    "nome": "<principio attivo>",
    "data_inizio": date(2000, 1, 1),
    "dose_iniziale": "<dose>/settimana",
}

# Data di inizio del piano alimentare (prima misurazione = baseline)
DATA_INIZIO_DIETA = date(2000, 1, 1)
KCAL_PIANO = "<n> kcal"

# ── MISURAZIONI (aggiungere una riga per ogni nuova pesata) ─────────────────
# Formato: (data, peso_kg, etichetta_evento)
# La prima riga è sempre la baseline. L'ultima è la misurazione più recente.
MISURAZIONI = [
    (date(2000, 1, 1), 000.00, "Inizio piano alimentare"),
    (date(2000, 1, 8), 000.00, "Seconda misurazione"),
    # ... una riga per ogni pesata successiva
]

# ─ CIRCONFERENZA VITA (opzionale) ───────────────────────────────────────────
# Impostare CIRC_VITA = None se non disponibile/non rilevata in questo report
CIRC_VITA = {
    "iniziale_cm": 000,
    "attuale_cm": 000,
    "data_attuale": date(2000, 1, 1),   # data dell'ultima rilevazione vita nota
}

# ─ PARAMETRI PROIEZIONE (modificare solo su indicazione clinica esplicita) ──
# Questi NON sono segnaposto: sono i valori reali di design clinico.
WEIGHT_FLOOR_KG = 96
TASSO_FASE2_KG_SETT = 0.60
TASSO_FASE3_KG_SETT = 0.40
TASSO_FASE1_KG_SETT = 0.55
BANDA_INCERTEZZA_KG = 1.5
SETTIMANE_PROIEZIONE = 27

# ─ NOTE CLINICHE PERSONALIZZATE (opzionale, lasciare "" se non necessarie) ──
NOTA_GLICEMIA = ""
NOTA_UREA = ""


# ════════════════════════════════════════════════════════════════════════════
# ██ CAMPI AGGIUNTI NELLE VERSIONI SUCCESSIVE — da prevedere nella ricostruzione
# ════════════════════════════════════════════════════════════════════════════
# Questo file riflette la PRIMA versione. Il target da ricostruire è la v3, che
# secondo il modulo M5 legge tutti i dati da un JSON paziente esterno anziché
# dalla zona dati qui sopra, ed è invocata così:
#
#     python3 TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py CognomeNome.json
#
# Rispetto alla v1, la v3 aggiunge:
#   · "sesso": "M" | "F"   → soglie circonferenza vita adattive (OMS)
#                            M: 94 / 102 cm — F: 80 / 88 cm, MAI impostate a mano
#   · "obiettivo_peso_kg"  → se valorizzato, sovrascrive WEIGHT_FLOOR_KG nel grafico
#   · farmaco.data_titolazione / farmaco.dose_titolazione, se la titolazione è avvenuta
#   · NOTA_EXTRA, oltre a NOTA_GLICEMIA e NOTA_UREA
#   · classifica_vita() sex-aware, che sostituisce classifica_vita_uomo()
#
# Formato numeri nel JSON: punto decimale (100.50, non 100,50).


# ════════════════════════════════════════════════════════════════════════════
# ██ MOTORE GRAFICO — DA RICOSTRUIRE ██
# ════════════════════════════════════════════════════════════════════════════
# Da qui in poi il codice originale è perduto. Deve produrre le tre pagine
# descritte nel docstring in testa al file, in A4, con anteprima pdftoppm
# obbligatoria prima di ogni consegna.
#
# Vincoli invariabili (modulo M5):
#   · Altezza: sempre da altezza_cm, mai dagli scontrini della bilancia
#   · Tassi di proiezione: mai modificati senza indicazione clinica esplicita
#   · Soglie vita: automatiche dal campo sesso
#   · Nessun PDF consegnato senza anteprima visiva approvata

raise NotImplementedError(
    "Motore grafico non presente: questo file è una specifica, non un template "
    "eseguibile. Vedi la nota di provenienza in testa al file."
)
