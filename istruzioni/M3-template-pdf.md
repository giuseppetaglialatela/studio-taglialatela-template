# M3 — TEMPLATE PDF: PIANO ALIMENTARE E DOCUMENTO DI SPIEGAZIONE

Modulo operativo. Si carica **dopo l'approvazione dei calcoli**, per generare i due
deliverable che il paziente riceve.
Ultimo aggiornamento: 30/10/2026 (verdetto della pipeline allegato e richiesto da PDF e verifica;
documento di spiegazione generato con `genera_spiegazione.py`, che si ferma su segnaposto,
parentesi quadre, struttura e nome del paziente). 23/10/2026: testo del documento di spiegazione approvato prima della consegna; template di spiegazione: elenchi puntati «•» al posto di «●», che il font non ha e stampava «NO GLYPH», unica modifica al motore grafico autorizzata dal nutrizionista; impronta dell'approvazione: il PDF si ferma se piano o testi sono cambiati, `--verifica-impronta` prima del documento di spiegazione, orari tra gli allegati; 22/10: fermo sui segnaposto nei testi del paziente; prima: 30/09/2026, secondo spuntino, fino a 5 pasti nel PDF). Presuppone **M2 già eseguito** (in chat A):
copre i suoi PASSO 7 e PASSO 8 e non si esegue prima. **In chat B M2 e M1 non si
ricaricano**: tutto ciò che serve sta nei metadati del piano e nel motore.

### Avvio della chat B

1. I file del paziente (`piano_vN.csv`, `metadati_piano_vN.json`, `verdetto_vN.json`,
   fascicolo) si chiedono **allegati alla chat**: la cartella uploads non costa token. Drive si
   usa solo se un allegato manca. Un piano con eccezione etichetta richiede anche il
   file delle voci da etichetta e quello dei loro nomi paziente (M1, sezione 4); un
   piano con orari anche `orari_pasti.csv`. Si chiedono tutti i file elencati in
   `drive.altri_file` dei metadati.
2. Motore: un solo comando scarica la cartella del motore ed esegue collaudo e
   regressione:
   ```
   rm -rf /tmp/motore /tmp/repo-motore && mkdir /tmp/motore && cd /tmp/motore && { curl -sfL https://codeload.github.com/giuseppetaglialatela/studio-taglialatela-template/tar.gz/refs/heads/main | tar xz --strip-components=2 studio-taglialatela-template-main/motore-calcolo || { echo "codeload non disponibile: ripiego con git clone"; cd /tmp && rm -rf /tmp/motore && git clone --depth 1 -q https://github.com/giuseppetaglialatela/studio-taglialatela-template /tmp/repo-motore && cp -r /tmp/repo-motore/motore-calcolo /tmp/motore && rm -rf /tmp/repo-motore && cd /tmp/motore; }; } && python3 collaudo.py && python3 regressione.py
   ```
   (è lo stesso comando di M1, sezione 1: non serve caricare M1). Il collaudo completo dura meno di un secondo: si
   esegue intero, come in ogni sessione (principio 7).
3. Verifica del CSV: leggibile e coerente con le `differenze_da_versione_precedente`
   dichiarate nei metadati. Non si scaricano versioni precedenti per confronto.
   Il controllo formati NON si ripete in chat B: i rilievi si dichiarano e si approvano
   al PASSO 6 (pipeline), e l'impronta garantisce che il piano è quello approvato. Un
   piano senza impronta si ferma al punto 4 e torna al PASSO 6.
4. Kcal per pasto e per alternativa: dal motore (`calcolatore.calcola_riga`), mai
   scritte a mano e mai prese da riassunti.
   **Strumento:** `genera_zona_piano.py`, nella cartella del motore, compila la zona
   dati del template v5 e genera il PDF in un comando; la zona dati non si compila
   a mano. Il template si scarica dal link della sezione 2.
   ```
   python3 genera_zona_piano.py --piano piano_vN.csv --target target.csv
       --metadati metadati_piano_vN.json --verdetto verdetto_vN.json
       --template TEMPLATE_..._v5.py
       --orari orari_pasti.csv --out-py CognomeNome_piano_vN.py
       --out-pdf CognomeNome_piano_vN.pdf
       [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
   ```
   Se si ferma, stampa quale campo o titolo manca o contiene un segnaposto («non
   concordato», «N/D», «XX kg», testi d'esempio del template; elenco in M1): si chiede
   al nutrizionista, non si completa a intuito. Si ferma anche se `impronta_approvata`
   manca o non coincide (M2, PASSO 6): piano o testi diversi da quelli approvati, e se il
   verdetto manca, ha un bloccante o riguarda altri dati. Il verdetto NON si rifà in chat
   B: è quello approvato al PASSO 6, con le sue attenzioni dentro l'impronta. In chat
   B l'impronta NON si rigenera: si torna al nutrizionista con l'anteprima
   (`--anteprima`) e la si fa approvare. Il `.py` prodotto è quello da
   archiviare (sezione 5).
5. Se nei metadati manca un campo necessario (titolo, obiettivo, criterio) o contiene
   un segnaposto, ci si ferma e lo si chiede: non si decide in chat B. Il documento di
   spiegazione si genera con `genera_spiegazione.py` (sezione 3, «Come si genera»), che
   prima verifica l'impronta con gli stessi file del PDF: un campo cambiato dopo il PDF lo
   ferma. Il documento si scrive dai campi approvati
   (`regole_operative`, `scelte_principali`, `limiti_noti`, `da_escludere`, `terapia`)
   e dai dati di piano e fascicolo, senza deduzioni cliniche (sezione 3): la prosa è
   della chat B, i contenuti no, e il testo intero passa dall'approvazione del
   nutrizionista prima della consegna (sezione 3, «Quando generarlo»). Obiettivo e
   criterio sono già
   protetti, perché il PDF del piano, generato prima dagli stessi metadati, si ferma
   su un loro segnaposto.

**Due spuntini nello stesso giorno (dal 30/09/2026).** Il secondo spuntino ha il suo
valore di pasto, `spuntino2`: non si forza più dentro un unico gruppo `spuntino`.
Nel PDF compare come SECONDO SPUNTINO, con l'icona dello spuntino; le sue kcal entrano
nel totale del giorno. Verificato con un piano di prova a 5 pasti nel caso peggiore
per lo spazio (4 colazioni, 2 spuntini e 2 secondi spuntini a scelta): un giorno per
pagina, giorno 1 nella pagina dell'intestazione con margine sopra il footer.

**Verifiche note prima di generare** (emerse in un piano con surplus e due spuntini,
29/09/2026; da confermare con l'esecuzione reale):
- il generatore accetta un solo `gruppo_scelta` per pasto;
- il riquadro del target calcola deficit e perdita attesa: con un surplus il segno
  può risultare invertito. Se compare una «perdita», ci si ferma e si chiede.
- **Frutta a scelta:** la zona dati del PDF non si modifica. La tabella di scambio
  (`scambi_frutta.csv`, via `formati.carica_scambi_frutta()`) va nel documento di
  spiegazione. Se il generatore non gestisce una voce di frutta di riferimento, ci si
  ferma e si segnala, senza ricostruire il layout.

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
Si modifica **esclusivamente la zona dati**. Unica via per cambiare il motore grafico: un
difetto dimostrato, la decisione esplicita del nutrizionista, il collaudo e il numero di
versione alzato nell'intestazione del template (stesso nome di file). Unico caso finora:
template di spiegazione 1.1 (23/10/2026), elenchi puntati «•» al posto di «●», che
Helvetica non contiene e stampava «NO GLYPH» in verticale.

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
  Lo spuntino usa `"spuntino"`, mai `"pranzo"`. Il **secondo spuntino** usa anch'esso
  `"spuntino"`, con etichetta `SECONDO SPUNTINO`: il template ha 4 chiavi e non si
  modifica. La barra legenda resta a 4 voci.
- Pasti per giorno: fino a 5, contati dai dati; un pasto assente non compare (niente
  "0", niente riga vuota). Nei piani a 5 pasti l'ordine è colazione, SPUNTINO
  (metà mattina), pranzo, SECONDO SPUNTINO, cena; se tutti i pasti del giorno hanno
  un orario, vale l'orario.
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

Il piano espone al paziente le **4 colazioni e i 2 spuntini** (più il secondo
spuntino, se il piano lo ha) del livello scelto
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
(min–max secondo la scelta). Se anche il secondo spuntino è a scelta, la frase del
totale diventa "secondo le alternative scelte".

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
di `metadati_piano_vN.json`, più `terapia` per la sezione 2. Non si recuperano testi
dalle chat precedenti. Tutte le sezioni possono usare dati di `piano_vN.csv` e del
fascicolo (quadro di partenza, contesto di vita, turni, mensa). **Mai deduzioni
cliniche:** un dato clinico che non sta in questi file non entra (es. «nessun farmaco in
terapia» solo se lo dice il campo `terapia` dei metadati o il fascicolo; `terapia`
vuota o «non concordato» = nessuna informazione; se `terapia` e fascicolo non coincidono
ci si ferma e si chiede). Spiegazioni
pratiche ed esempi non clinici (`[dedotto]`) sono ammessi, ma passano dall'approvazione
del testo («Quando generarlo»).

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
   P01: perché pasta, pane e patate restano nonostante il diabete (indice vs
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
di approvazione dei calcoli, ma **il testo si approva prima della consegna** (decisione
del 23/10/2026: nel primo piano reale la chat B aveva aggiunto sette contenuti non
approvati, tra cui «nessun farmaco in terapia» dedotto, e tre frasi inventate):
1. si genera il PDF con `genera_spiegazione.py` (sotto) e se ne estrae il testo intero:
   `pdftotext -layout CognomeNome_spiegazione_vN.pdf -`;
2. lo si presenta COSÌ COM'È, non riassunto, con accanto a ogni frase che non viene dai
   campi dei metadati la sua fonte: `[piano]`, `[fascicolo]` o `[dedotto]`. Una
   deduzione clinica si toglie PRIMA di presentare il testo; le altre `[dedotto]`
   (es. un esempio pratico) restano solo se il nutrizionista le approva;
3. il PDF si consegna solo dopo l'approvazione esplicita del testo; ogni correzione
   produce un nuovo PDF, una nuova anteprima visiva (sezione 4) e un nuovo testo da
   approvare: si approva sempre l'ultimo PDF.

### Come si genera (dal 30/10/2026)

Si copia il template, si scrive SOLO la zona dati (`SEZIONI` e, se serve, `INTRO`) nel
file `CognomeNome_spiegazione_vN.py`, e il PDF si genera con il comando del motore, mai
lanciando il `.py` direttamente:
```
python3 genera_spiegazione.py --py CognomeNome_spiegazione_vN.py
    --template TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py
    --piano piano_vN.csv --target target.csv --metadati metadati_piano_vN.json
    --verdetto verdetto_vN.json [--orari orari_pasti.csv]
    --out-pdf CognomeNome_spiegazione_vN.pdf
```
Si ferma, dicendo dove, se: l'impronta non coincide; motore grafico, intestazione o
chiusura dello studio sono diversi dal template; le sezioni non sono 6, numerate 1-6, con
almeno un paragrafo; un testo è vuoto, un segnaposto o un testo d'esempio («testo
placeholder», «XX», «N settimane», «Nome Cognome»…); un testo contiene parentesi quadre
(le etichette `[piano]`, `[fascicolo]`, `[dedotto]` si usano SOLO nella presentazione in
chat, mai nel `.py`; e le alternative del modello come «[i farmaci in terapia / il
contesto di vita]» vanno sciolte); compare una parola del nome del paziente. Non giudica i
contenuti: deduzioni cliniche, seconda persona e frasi inventate restano all'approvazione
del testo intero.
Il PDF del documento approvato è il riferimento: un contenuto nuovo aggiunto in questa
fase (es. una regola operativa dettata dal nutrizionista) non torna nei metadati né
nell'impronta del piano, che restano quelli del PASSO 6.

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

Destinazione su Drive: `Andamento Dieta Pazienti > [Cognome Nome]`. Nomi dei file con
la stessa convenzione di Drive (M5): `CognomeNome_piano_vN.pdf`, `CognomeNome_piano_vN.py`,
`CognomeNome_spiegazione_vN.pdf` (es. `RossiMario_piano_v2.pdf`), con lo stesso numero di
versione di `piano_vN.csv` e dei metadati; stessa radice `CognomeNome_` dei file di M5. Il
template di spiegazione prende il nome d'uscita come primo argomento:
`python3 TEMPLATE_SpiegazioneDieta_StudioTaglialatela_v1.py CognomeNome_spiegazione_vN.pdf`
(senza argomento scrive `spiegazione_dieta.pdf`), ma dal 30/10/2026 non si lancia
direttamente: lo lancia `genera_spiegazione.py` dopo i controlli (sezione 3). Andamento (M5) e scheda di allenamento
(M8) hanno ancora convenzioni proprie, già in uso su Drive: non si cambiano qui. Se la cartella
del paziente non esiste, va creata: un piano generato e non archiviato è un piano
che esiste solo nella conversazione in cui è nato. **I PDF e il `.py` non li carica
Claude** (nucleo, sezione 7: il connettore consuma molti token e non sovrascrive): si
consegnano in chat e li carica il nutrizionista, con il nome esatto e il link della
cartella. Claude scrive su Drive solo i file piccoli che non esistono altrove (JSON),
e solo a fine conversazione.

**Limite del connettore Drive.** Non esiste sovrascrittura: caricare un file con un
nome già presente crea un duplicato. Quando aggiorni un file già su Drive, indica al
nutrizionista quale versione è la corrente e come distinguerle (nome, data o dimensione).
La vecchia si sposta nel cestino con `trash_file` solo se lo chiede lui, oppure la toglie
a mano (nucleo, sezione 7). Non fingere di aver sovrascritto. Sopra ~500 KB il caricamento è inaffidabile: fornisci il file e il link
della cartella di destinazione.

**Verifica di integrità.** Un PDF su Drive di dimensione anomala va sempre
verificato prima di essere usato o inviato: è già successo due volte che un file si
corrompesse in silenzio, e uno dei due era il PDF di un piano ridotto a 238 byte,
senza xref né `%%EOF`, non apribile.

Ricorda al nutrizionista, a fine conversazione, il salvataggio di ogni documento
clinico rilevante prodotto. Non serve per collaudi e simulazioni dichiarati come
tali.
