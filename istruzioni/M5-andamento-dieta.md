# M5 — ANDAMENTO DIETA

Modulo operativo. Si carica per creare o aggiornare il report grafico di andamento
peso di un paziente. **Non dipende da M1 né da M2**: non calcola nulla di
nutrizionale, legge un JSON e produce un PDF. È il modulo più autonomo del sistema
e può essere caricato da solo.

Ultima modifica: 27/09/2026 (template v3.2 con misura di riferimento; pagina 3 ad
personam; report dalla seconda pesata; rilievi aperti).

**TRIGGER** — qualsiasi frase del tipo:
"aggiorna il peso di [paziente]" · "nuova pesata [nome]" · "[nome] pesa [X] kg" ·
"aggiornamento andamento [nome]" · "crea andamento per [nome]".

---

## 1. IL TEMPLATE

**File obbligatorio:** `TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py`
Percorso: GitHub, radice del repository, accanto agli altri due template.
Raw: `https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py`
Si scarica con `bash` + `curl`, come i moduli. Gli stub su Drive
(`_Template/`, v1-v2-v3) sono resti non funzionanti: non vanno usati.

**Riferimento di misura: 30.863 byte, versione 3.2 del 27/09/2026** (l'intestazione
del file dichiara la versione). Un file di poche centinaia di byte è uno stub e va
trattato come template mancante.

> **RISCRITTURA del 20/09/2026.** Il motore grafico originale era andato perso: su
> Drive restavano tre file con la sola docstring. La v3 è stata riscritta da
> docstring v1, changelog v2 e questo modulo, con identità visiva copiata dal
> template del piano v5. Non è un ripristino: i testi fissi della pagina 1 sono
> nuovi e approvati dal nutrizionista il 20/09/2026.
> **v3.2 del 27/09/2026:** pagina 3 ad personam, KPI corretto alla prima pesata,
> asse del grafico corretto con una sola pesata, due refusi.

**Motore grafico congelato**, come per il template del piano (M3): font, colori,
layout, header, footer, numero di pagina non si toccano mai. Si modificano solo i
dati in ingresso, che qui stanno tutti nel JSON del paziente. Una modifica al
template si fa solo su richiesta del nutrizionista, con collaudo su più casistiche
e numero di versione alzato (M0, principio 4).

**Niente improvvisazione:** se il template non si trova, fermati e segnalalo. Non
ricostruire un grafico alternativo.

---

## 2. STRUTTURA DEL JSON PAZIENTE

Campi obbligatori per ogni nuovo paziente:

| Campo | Contenuto |
|---|---|
| `nome` | nome del paziente |
| `altezza_cm` | altezza in centimetri |
| `sesso` | `"M"` o `"F"` |
| `farmaco` | `{nome, data_inizio, dose_iniziale}` — oppure `null` |
| `farmaco.data_titolazione` · `farmaco.dose_titolazione` | se la titolazione è avvenuta |
| `data_inizio_dieta` | data di partenza del percorso |
| `kcal_piano` | kcal del piano in corso |
| `misurazioni` | `[{data, peso, etichetta}]` — una riga per pesata, ordine cronologico |
| `circ_vita` | `{iniziale_cm, attuale_cm, data_attuale}` — oppure `null` |
| `obiettivo_peso_kg` | oppure `null` |
| `weight_floor_kg` | plateau minimo cautelativo — **obbligatorio, nessun default**: se manca, lo script si ferma. Il 96 che circolava era il valore di un singolo paziente |
| `nota_glicemia` · `nota_urea` · `nota_extra` | stringa vuota `""` se non rilevanti |

**Pagina 3 ad personam** (decisione del 20/09/2026): i consigli pratici e la frase
di chiusura si scrivono nel JSON del singolo paziente, non nel motore.

| Campo | Contenuto |
|---|---|
| `consigli` | `[["Titolo", "testo"], ...]` — quanti servono, riferiti a quel paziente |
| `motivazionale` | frase di chiusura, riferita a quel paziente |

Se i due campi mancano, il template usa i testi generici che porta dentro. Sono un
**ripiego**, non il comportamento voluto: vanno scritti sui vincoli e sugli ostacoli
reali di quella persona, e riletti a ogni consegna.

**Opzionali:** `strumento_riferimento` (riga sotto la cronologia),
`tasso_fase1/2/3`, `banda_incertezza`, `settimane_proiezione`.

**Formato date: `AAAA-MM-GG`. Formato numeri: punto decimale.** `120.65`, non
`120,65`. È un JSON, non un foglio di calcolo italiano.

---

## 3. REGOLE INVARIABILI

- **Altezza:** usa sempre `altezza_cm` dal JSON. Ignora le altezze che compaiono
  sugli scontrini della bilancia.
- **Proiezioni, paziente CON farmaco GIP/GLP-1:** tre fasi contate dall'inizio della
  dieta (settimane 0-8, 8-16, 16+). NON modificare mai `tasso_fase1/2/3` senza
  indicazione esplicita del nutrizionista. I valori (0,55 / 0,60 / 0,40 kg a
  settimana) sono cautelativi per scelta clinica, non una stima da raffinare: una
  proiezione più ottimistica non è una proiezione migliore, è una promessa che il
  paziente legge come impegno.
- **Proiezioni, paziente SENZA farmaco** (decisione clinica del 20/09/2026): nessun
  tasso a priori, perché il calo dipende dalla restrizione calorica effettiva. La
  linea si ricava per regressione dalle pesate reali, escludendo dal calcolo quelle
  dei primi 14 giorni — restano nel grafico come punti vuoti. Servono almeno **2
  pesate dopo il giorno 14**: sotto quella soglia, o con peso stabile o in salita,
  la proiezione non compare e al suo posto il PDF spiega perché.
- **Limite noto da dichiarare al nutrizionista:** la regressione prolunga per 27
  settimane il ritmo di poche pesate recenti, mentre nella realtà il calo rallenta.
  I tempi indicati sono quindi ottimistici. La curva si ferma comunque a
  `obiettivo_peso_kg`, se impostato, altrimenti a `weight_floor_kg`.
- **Soglie circonferenza vita:** automatiche dal campo `sesso`
  (M: 94 / 102 cm — F: 80 / 88 cm). Non si impostano a mano.
- **Anteprima obbligatoria:** il PDF non viene mai consegnato senza anteprima
  `pdftoppm` approvata, tutte e tre le pagine.
- **Mai un report con una sola pesata** (decisione del 20/09/2026): con un punto
  solo il documento non dice nulla al paziente. La baseline si registra nel JSON e
  basta; il report parte dalla seconda pesata.

---

## 4. WORKFLOW, IN QUEST'ORDINE

**1. Recupera il JSON del paziente da Drive**
Cartella: `Andamento Dieta Pazienti > [Cognome Nome]`
File: `[CognomeNome]_vN.json` (es. `CirulloAniello_v2.json`). La versione corrente
si riconosce dal suffisso nel nome, non dalla data di modifica.
Se il paziente non ha ancora una cartella, creala e crea il JSON da zero con i campi
della sezione 2. In questo caso ci si ferma qui: niente PDF alla prima pesata.

**2. Recupera il template** (sezione 1).

**3. Aggiorna il JSON del paziente**

| Evento | Modifica |
|---|---|
| Nuova pesata | aggiungi una riga in `misurazioni` |
| Nuova circonferenza vita | aggiorna `attuale_cm` e `data_attuale` in `circ_vita` |
| Nuova titolazione | aggiungi `data_titolazione` e `dose_titolazione` in `farmaco` |
| Nuovo obiettivo | imposta `obiettivo_peso_kg` col valore concordato |

**4. Esegui**
`python3 TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py [CognomeNome]_vN.json [output.pdf]`

**5. Valida con `pdftoppm`** — anteprima visiva obbligatoria prima di consegnare.

**6. Salva su Drive il JSON aggiornato con il numero di versione successivo**, nella
cartella del paziente, insieme al PDF. Il connettore non sovrascrive: un nome già
esistente crea un duplicato. Segnala quale versione è la corrente e come distinguere
la vecchia (nome e dimensione); la cancellazione è manuale e differibile.

---

## 5. LETTURA DEI DATI — COSA SEGNALARE

Il modulo produce un grafico, non un giudizio clinico. Ma due situazioni vanno
segnalate al nutrizionista quando emergono dai dati, perché il grafico da solo non
le dichiara:

- **Plateau con aderenza alta.** In un paziente in terapia tiroidea — o comunque con
  patologia endocrina in trattamento — l'assenza di calo non è automaticamente una
  questione di porzioni. Prima di attribuirla al piano, segnala la verifica del
  quadro ormonale e dell'adeguatezza della titolazione. La stessa logica vale ogni
  volta che una terapia in corso può giustificare l'assenza di risposta.
- **Calo che si avvicina a `weight_floor_kg`.** È un plateau minimo cautelativo, non
  un obiettivo: quando ci si avvicina, la decisione se proseguire è clinica e va
  esposta, non applicata in automatico.

Le soglie operative del follow-up (aderenza, silenzio, plateau a 4 settimane) sono
in **M7**.

---

## 6. RILIEVI APERTI SUL TEMPLATE — verificati il 27/09/2026

- **`monitoraggio_bia` non viene letto.** Il blocco presente in alcuni JSON
  (impedenziometria, offset dello strumento, pressione) non compare in nessuna
  pagina del PDF. Se serve nel report, è una modifica al template da decidere.
- **Testi della pagina 1 approvati** il 20/09/2026 (intro e "cosa significano questi
  numeri"). Il paragrafo sull'IMC resta generico anche per i pazienti molto alti,
  dove l'indice sovrastima: la lettura si affida alla circonferenza vita.
