# M3 — TEMPLATE PDF: PIANO ALIMENTARE E DOCUMENTO DI SPIEGAZIONE

Modulo operativo. Si carica **dopo l'approvazione dei calcoli**, per generare i due
deliverable che il paziente riceve. Presuppone **M2 già eseguito** (in chat A):
copre i suoi PASSO 7 e PASSO 8 e non si esegue prima. **In chat B M2 e M1 non si
ricaricano**: tutto ciò che serve sta nei metadati del piano e nel motore.

### Avvio della chat B

1. I file del paziente (`piano_vN.csv`, `metadati_piano_vN.json`, fascicolo) si
   chiedono **allegati alla chat**: la cartella uploads non costa token. Drive si
   usa solo se un allegato manca.
2. Motore: scarica ed estrai `motore calcolo.zip`, scarica `alimenti.csv` sciolto
   accanto (URL e procedura in M1, sezione 1 "Avvio di sessione": si legge solo quella sezione, non si carica M1 intero),
   esegui `python3 collaudo.py`. Il collaudo completo dura meno di un secondo: si
   esegue intero, come in ogni sessione (principio 7).
3. Verifica del CSV: leggibile e coerente con le `differenze_da_versione_precedente`
   dichiarate nei metadati. Non si scaricano versioni precedenti per confronto.
4. Kcal per pasto e per alternativa: dal motore (`calcolatore.calcola_riga`), mai
   scritte a mano e mai prese da riassunti.
   **Strumento:** `genera_zona_piano.py`, nello zip del motore, compila la zona
   dati del template v5 e genera il PDF in un comando; la zona dati non si compila
   a mano. Il template si scarica dal link della sezione 2.
   ```
   python3 genera_zona_piano.py --piano piano_vN.csv --target target.csv
       --metadati metadati_piano_vN.json --template TEMPLATE_..._v5.py
       --orari orari_pasti.csv --out-py piano_Cognome_vN.py
       --out-pdf piano_Cognome_vN.pdf
   ```
   Se si ferma, stampa quale campo o titolo manca: si chiede al nutrizionista, non
   si completa a intuito. Il `.py` prodotto è quello da archiviare (sezione 5).
5. Se nei metadati manca un campo necessario (titolo, obiettivo, criterio), ci si
   ferma e lo si chiede: non si decide in chat B.

Il template dell'andamento dieta non sta qui: è in **M5**.

**Precondizione non negoziabile.** Nessun PDF viene generato prima che i calcoli
siano stati presentati in tabella e APPROVATI ESPLICITAMENTE dal nutrizionista
(nucleo M0, principio 1). Se ricevi la richiesta di generare direttamente il PDF
saltando il gate, ricorda il gate e chiedi conferma esplicita dei calcoli — anche
quando la fretta è dichiarata, anche se il piano sembra identico a uno precedente.

---

## 1. IL MOTORE GRAFICO È CONGELATO

Vale per entrambi i template di questo modulo.

Non si tocca mai, per nessuna ragione: font, colori, emoji, layout, header, footer,
barra legenda, linee separatrici, numero di pagina.
Si modifica **esclusivamente la zona dati**.

**Niente improvvisazione di layout.** Se un template non si trova — né su GitHub né
su Drive — fermati e segnalalo. Non ricostruire un layout alternativo: un PDF che
somiglia al template non è il template, e la differenza si vede in mano al
paziente.

---

## 2. TEMPLATE PIANO ALIMENTARE

**File obbligatorio:** `TEMPLATE_PianoAlimentare_StudioTaglialatela_v5.py`

Recupero (raw GitHub):
`https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/TEMPLATE_PianoAlimentare_StudioTaglialatela_v5.py`

Copia di riserva: Drive > Template.

Questo file **sostituisce e annulla** la v4 e le precedenti v1.0 e v3.0. Se ne
trovi altre copie in giro, non usarle e segnalalo.

Novità della v5 (19/09/2026): icone dei pasti non più tagliate; emoji ⭐ e 🚫
dei box info rese come immagine; blocco alternative nativo per colazione e
spuntino; segnaposto sul modello standard (4 colazioni, spuntino delle 17,
6 giorni strutturati + 1 libero). Motore grafico per il resto invariato; un
piano scritto nel formato v4 produce con la v5 lo stesso testo.

### Due zone

| Zona | Cosa contiene | Si modifica? |
|---|---|---|
| ZONA DATI | `PAZIENTE`, `BOX_INFO`, `COLAZIONI`, `SPUNTINI`, `GIORNI` | Sì — è l'unica |
| MOTORE GRAFICO | tutto il resto | Mai |

### Regole

- Copia il template, modifica solo la zona dati, genera il PDF.
- Chiavi emoji ammesse: `"colazione"` · `"pranzo"` · `"spuntino"` · `"cena"`.
  Lo spuntino usa `"spuntino"`, mai `"pranzo"`.
- Output: A4, **un giorno per pagina**, giorno 1 nella pagina dell'intestazione.
- Le emoji ⭐ e 🚫 nei testi di `BOX_INFO` si scrivono come carattere normale: il
  template le converte in immagine.
- La zona dati accetta un numero libero di giorni. Il piano standard è a 7 giorni
  (6 strutturati + 1 libero, di norma la domenica). Il giorno libero va comunque
  compilato con indicazioni di massima e range calorico: è un margine di
  flessibilità da spiegare al paziente, non un giorno saltato.
- Dipendenze già presenti nell'ambiente: `reportlab`, `pillow`, LiberationSans,
  NotoColorEmoji.
- **Formato output SEMPRE e SOLO PDF con questo template.** Mai Word, mai una
  tabella come deliverable finale del piano.

### Colazione e spuntino nel PDF

Il piano espone al paziente le **4 colazioni e i 2 spuntini** del livello scelto
(M2, sezione 2), non una singola combinazione. Il livello — standard o
rinforzata_calcio — è uno solo per l'intero piano settimanale, e le stesse 4+2
valgono per tutti i giorni strutturati: nel PDF non compaiono colazioni diverse
giorno per giorno.

**Come si scrivono (v5).** Le alternative si dichiarano una volta sola nelle liste
`COLAZIONI` e `SPUNTINI` della zona dati; ogni voce è
`("Nome", "dettaglio", "~kcal", nota_o_None)`. Nel giorno, il pasto con alternative
porta la lista al posto del nome e `None` in dettaglio e kcal:
`("colazione", "COLAZIONE — ore 08:00", COLAZIONI, None, None, nota_o_None)`.
Il template scrive "A scelta tra:" e assegna le lettere A, B, C, D da solo.

**Dove compaiono (decisione del 19/09/2026).** Il blocco alternative è **ripetuto
in ogni pagina-giorno strutturato**: il paziente apre il giorno e ha tutto. Misurato:
con testi lunghi e note, il giorno 1 entra nella pagina dell'intestazione con
circa 40 mm di margine sopra il footer.

L'abbinamento colazione→spuntino non ha ancora un campo nel motore: nel PDF si
scrive come nota della singola alternativa.

Le kcal di ogni alternativa vengono dal motore (`calcolatore.calcola_riga`), mai
scritte a mano. Il totale del giorno con alternative è un intervallo
(min–max secondo la scelta).

---

## 3. DOCUMENTO DI SPIEGAZIONE DIETA

**File template:** `TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py`

Recupero (raw GitHub, in radice):
`https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py`

Copia di riserva: Drive > Template (stessa cartella del template piano alimentare).

### Cosa è

Documento informativo che accompagna il PDF del piano, generato **di default per
ogni piano consegnato**. Spiega al paziente il perché delle scelte del piano: non
introduce contenuti clinici nuovi, riusa solo le scelte già approvate al PASSO 6.
**Fonte dei contenuti:** i campi `regole_operative`, `scelte_principali`,
`limiti_noti`, `obiettivo_intestazione`, `criterio_rivalutazione` e `da_escludere`
di `metadati_piano_vN.json`. Non si recuperano testi dalle chat precedenti.

### Registro obbligatorio

Tecnico e impersonale. Non rivolgersi al paziente in seconda persona ("tu"/"lei") e
non usarne il nome nel corpo del testo: si parla del profilo, del piano, del
contesto di vita — non alla persona. Il nome del paziente compare **solo nel nome
del file**.

### Struttura a 6 sezioni

Si adattano i contenuti, non la struttura.

1. **Il punto di partenza** — quadro clinico e antropometrico ed elementi di
   contesto di vita rilevanti per il piano (lavoro, tempo per cucinare, storia di
   diete precedenti), qualunque sia la loro natura per quel paziente.
2. **La dieta e [i farmaci in terapia / il contesto di vita]: come si integrano** —
   se ci sono farmaci, spiega le interazioni farmaco-alimento con il registro del
   PASSO 4 di M2; se non ce ne sono, spiega come il piano si adatta ai vincoli
   operativi principali (turni, mensa o salumeria, tempo di cucina).
3. **Una scelta apparentemente controintuitiva, spiegata nel dettaglio** — nel caso
   Mattei: perché pasta, pane e patate restano nonostante il diabete (indice vs
   carico glicemico). Va adattata al vincolo più rilevante e meno intuitivo per
   quel paziente specifico: perché la colazione resta fissa nonostante una storia
   di ripetitività, perché le porzioni sembrano contenute, perché il piano non è a
   basso contenuto di un dato nutriente.
4. **Altre domande frequenti** — 3-4 domande realistiche specifiche per quel piano,
   con risposta tecnica breve.
5. **Le tre scelte più importanti (e il perché)** — le decisioni strutturali con
   maggiore impatto sul piano, motivate singolarmente.
6. **L'obiettivo: salute e benessere, non un numero** — chiusura che ribadisce
   l'obiettivo clinico concordato (non estetico) e il fatto che il percorso viene
   rivisto nel tempo.

### Quando generarlo

Subito dopo il PDF del piano, **nella stessa consegna**. Non richiede un nuovo giro
di approvazione dei calcoli — usa solo scelte già approvate — ma il nutrizionista lo
rivede comunque prima dell'invio al paziente, in particolare su tono e accuratezza
del contenuto esplicativo.

Se qualcosa nel testo esplicativo risulta impreciso rispetto al piano approvato,
segnalalo e correggi prima di consegnare: è il documento in cui un'imprecisione
arriva al paziente in prosa, senza una tabella accanto che la smentisca.

### Formato — eccezione alla regola generale

Questo documento è **SEMPRE in PDF**, non Word, a differenza della regola generale
sugli altri documenti importanti: è pensato per essere consegnato insieme al PDF del
piano, con la stessa veste professionale.

---

## 4. ANTEPRIMA OBBLIGATORIA

Vale per entrambi i PDF di questo modulo. Nessun PDF viene consegnato senza
anteprima approvata.

- Genera l'anteprima con `pdftoppm`.
- Piano alimentare: controllo visivo di **almeno la pagina di intestazione e una
  pagina interna**.
- Documento di spiegazione: controllo visivo di **almeno la prima pagina**.

L'anteprima serve a vedere quello che il codice non dichiara: testo che sborda,
emoji mancante, pagina vuota, riga tagliata dal footer. Un PDF generato senza errori
non è un PDF corretto.

---

## 5. SALVATAGGIO SU MEMORIA ESTERNA

Da fare per ogni piano consegnato:

| Cosa | Formato |
|---|---|
| Piano alimentare | PDF **+ il `.py` della zona dati compilata** |
| Documento di spiegazione | PDF |

Entrambi sono un'eccezione alla regola generale "gli altri documenti importanti in
Word".

Destinazione su Drive: `Andamento Dieta Pazienti > [Cognome Nome]`. Se la cartella
del paziente non esiste, va creata: un piano generato e non archiviato è un piano
che esiste solo nella conversazione in cui è nato.

**Limite del connettore Drive.** Non esiste sovrascrittura: caricare un file con un
nome già presente crea un duplicato. Quando aggiorni un file già su Drive, avvisa
esplicitamente il nutrizionista che deve cancellare a mano la versione vecchia,
indicando come distinguerle (data di modifica o dimensione). Non fingere di aver
sovrascritto. Sopra ~500 KB il caricamento è inaffidabile: fornisci il file e il link
della cartella di destinazione.

**Verifica di integrità.** Un PDF su Drive di dimensione anomala va sempre
verificato prima di essere usato o inviato: è già successo due volte che un file si
corrompesse in silenzio, e uno dei due era il PDF di un piano ridotto a 238 byte,
senza xref né `%%EOF`, non apribile.

Ricorda al nutrizionista, a fine conversazione, il salvataggio di ogni documento
clinico rilevante prodotto. Non serve per collaudi e simulazioni dichiarati come
tali.
