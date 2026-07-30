# M5 — ANDAMENTO DIETA

Modulo operativo. Si carica per creare o aggiornare il report grafico di andamento
peso di un paziente. **Non dipende da M1 né da M2**: non calcola nulla di
nutrizionale, legge un JSON e produce un PDF. È il modulo più autonomo del sistema
e può essere caricato da solo.

**TRIGGER** — qualsiasi frase del tipo:
"aggiorna il peso di [paziente]" · "nuova pesata [nome]" · "[nome] pesa [X] kg" ·
"aggiornamento andamento [nome]" · "crea andamento per [nome]".

---

## 1. IL TEMPLATE

**File obbligatorio:** `TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py`
Percorso: `Drive > Andamento Dieta Pazienti > _Template`

> **Stato aperto — verificato il 30/07/2026.** Questo template NON è su GitHub: il
> canale raw risponde 404 sia con underscore sia con spazi. È l'unico dei tre
> template ancora vincolato a Drive. Non contiene dati di paziente — è codice —
> quindi per la regola di separazione dovrebbe stare su GitHub come gli altri due.
> Finché non ci sta, il recupero dipende dal canale più lento e fragile.

**Motore grafico congelato**, come per il template del piano (M3): font, colori,
layout, header, footer, numero di pagina non si toccano mai. Si modificano solo i
dati in ingresso, che qui stanno tutti nel JSON del paziente.

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
| `weight_floor_kg` | plateau minimo cautelativo (default 96) |
| `nota_glicemia` · `nota_urea` · `nota_extra` | stringa vuota `""` se non rilevanti |

**Formato numeri: punto decimale.** `120.65`, non `120,65`. È un JSON, non un foglio
di calcolo italiano.

---

## 3. REGOLE INVARIABILI

- **Altezza:** usa sempre `altezza_cm` dal JSON. Ignora le altezze che compaiono
  sugli scontrini della bilancia.
- **Proiezioni:** NON modificare mai `tasso_fase1/2/3` senza indicazione esplicita
  del nutrizionista. I valori (0,55 / 0,60 / 0,40 kg a settimana) sono cautelativi
  per scelta clinica, non una stima da raffinare: una proiezione più ottimistica non
  è una proiezione migliore, è una promessa che il paziente legge come impegno.
- **Soglie circonferenza vita:** automatiche dal campo `sesso`
  (M: 94 / 102 cm — F: 80 / 88 cm). Non si impostano a mano.
- **Anteprima obbligatoria:** il PDF non viene mai consegnato senza anteprima
  `pdftoppm` approvata.

---

## 4. WORKFLOW, IN QUEST'ORDINE

**1. Recupera il JSON del paziente da Drive**
Cartella: `Andamento Dieta Pazienti > [Cognome Nome]`
File: `[CognomeNome].json` (es. `VitaleIvan.json`)
Se il paziente non ha ancora una cartella, creala e crea il JSON da zero usando come
riferimento la struttura di `VitaleIvan.json` in `_Template/`.

**2. Recupera il template** (sezione 1).

**3. Aggiorna il JSON del paziente**

| Evento | Modifica |
|---|---|
| Nuova pesata | aggiungi una riga in `misurazioni` |
| Nuova circonferenza vita | aggiorna `attuale_cm` e `data_attuale` in `circ_vita` |
| Nuova titolazione | aggiungi `data_titolazione` e `dose_titolazione` in `farmaco` |
| Nuovo obiettivo | imposta `obiettivo_peso_kg` col valore concordato |

**4. Esegui**
`python3 TEMPLATE_AndamentoDieta_StudioTaglialatela_v3.py [CognomeNome].json`

**5. Valida con `pdftoppm`** — anteprima visiva obbligatoria prima di consegnare.

**6. Salva il JSON aggiornato su Drive.**
Attenzione al limite del connettore: non esiste sovrascrittura, il caricamento crea
un **duplicato**. Segnala esplicitamente che la versione vecchia va cancellata a
mano, indicando come distinguerla (data di modifica o dimensione). Non fingere di
aver sovrascritto.

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
