# M1 — MOTORE DI CALCOLO

Modulo operativo (principio 6). Dipendenze: nessuna. Ne dipendono M2 e M6.
Ultima modifica: 23/10/2026 (anteprima del PASSO 6 e impronta dell'approvazione in `genera_zona_piano.py`; catalogo e libreria ai formati, condimenti a porzione libera;
Atwater solo sul piano e controllo 9 del collaudo; `--nessuna-terapia`; ripiego d'avvio;
casi golden 45-50). 22/10: distribuzione del calcio, avviso del livello rinforzato, fermi
sui segnaposto. Motivazioni, episodi e date in
`istruzioni/archivio/M1-motivazioni.md`, che non si carica.

Copre: avvio della sessione, moduli software, casi golden, database e fonti, schema CSV e
file affiancati, gap, recupero USDA, falsi positivi, stato di validazione.
NON copre: composizione del piano (M2), ampliamento del database (M6).

---

## 1. AVVIO E SALVATAGGIO

**Avvio, obbligatorio prima di qualsiasi calcolo.** UN comando scarica in una cartella
pulita l'intera cartella `motore-calcolo` (codice, dati, casi golden, cache) ed esegue
collaudo e regressione:
```
rm -rf /tmp/motore /tmp/repo-motore && mkdir /tmp/motore && cd /tmp/motore && { curl -sfL https://codeload.github.com/giuseppetaglialatela/studio-taglialatela-template/tar.gz/refs/heads/main | tar xz --strip-components=2 studio-taglialatela-template-main/motore-calcolo || { echo "codeload non disponibile: ripiego con git clone"; cd /tmp && rm -rf /tmp/motore && git clone --depth 1 -q https://github.com/giuseppetaglialatela/studio-taglialatela-template /tmp/repo-motore && cp -r /tmp/repo-motore/motore-calcolo /tmp/motore && rm -rf /tmp/repo-motore && cd /tmp/motore; }; } && python3 collaudo.py && python3 regressione.py
```
Il ripiego con `git clone` è DENTRO il comando: se `codeload.github.com` è bloccato dalla
sessione (errore 403, che `curl -sf` nasconde: compare come «gzip: stdin: unexpected end
of file»), scatta da solo e stampa «codeload non disponibile: ripiego con git clone». Stesso
risultato; provato in entrambi i rami il 23/10/2026.
Poi si lavora in `/tmp/motore`. Nessun calcolo su paziente prima dell'esito positivo
(principio 7). Il download è pubblico: non serve il repository collegato. Il motore si
esegue con `python3` normale dalla sua cartella, **mai con `python3 -I`** (modalità
isolata): i moduli non si importano e il collaudo fallisce senza motivo.
`cache.zip`, `BDA_alimenti.xlsx` e `crea_cache.zip` servono solo per ampliare il database
(M6), ma arrivano con lo stesso comando e il collaudo li verifica.

**Una sola copia di tutto.** Ogni file esiste una volta sola, in `motore-calcolo`. Non
reintrodurre zip né copie parallele.

**Salvare una modifica.** La salva Claude con un commit, dalle sessioni del progetto di
consolidamento con il repository collegato: `git clone`, poi SUBITO
`git config core.hooksPath .githooks` (controllo privacy, sotto), modifica, collaudo e
regressione, commit e push, poi comando d'avvio e nuovo collaudo. Il nutrizionista non carica niente a
mano. `git log` è il registro delle versioni; ogni modifica è annullabile.
Ripiego solo senza collegamento: caricamento manuale dalla pagina di upload della
cartella, poi verifica delle impronte.

**Nessun paziente nel repository, nemmeno per nome (obbligo di legge, GDPR).** Il
repository è PUBBLICO: un nome accanto a un piano o a una diagnosi è un dato sanitario
esposto. I pazienti si citano solo con il codice `P01`, `P02`… (`P00` = paziente fittizio);
la corrispondenza codice → nome sta SOLO su Drive
(`Studio Nutrizionale Taglialatela > codici_pazienti_repository.txt`); un paziente nuovo
prende lì il codice successivo, mai il nome nel repository. Il controllo è nel codice,
`strumenti/controllo_privacy.py`. Guarda il contenuto dei file (anche dentro zip, xlsx,
.gz, .bz2 e .xz, UTF-16 anche senza BOM, sequenze leggibili dei binari), i nomi dei file
(rinomine e cambi di tipo compresi) e i messaggi di commit (righe con `#` comprese). Prima
di cercare toglie i caratteri invisibili e riporta all'alfabeto latino le lettere
cirilliche, greche e armene identiche e quelle come «ø» e «ı». Due livelli:
- **elenco dei pazienti** (`--nomi FILE`), il livello che conta: ogni nome e cognome,
  riconosciuto anche attaccato, con trattini bassi, apostrofi tipografici, accenti o in
  maiuscolo; nome e cognome insieme in qualunque forma e ordine. Un nome di battesimo da
  solo non conta (non identifica e coincide con quello del titolare). Un cognome che è una
  parola comune si segna `~` nell'elenco (`P05 = ~Cognome Nome`): da solo conta allora con
  l'iniziale maiuscola o in un nome di file o in un dato, non in minuscolo nella prosa.
  L'elenco sta FUORI dal repository e si prepara a ogni sessione da Drive: le
  cartelle di `Andamento Dieta Pazienti` più la tabella dei codici, un paziente per riga
  (`P03 = Cognome Nome`); `!Nome Cognome` cerca solo il nome completo, per i cognomi
  uguali a quello dello studio;
- **dizionario** (nel repository, nomi italiani in ROT13): «Nome Cognome», «Cognome Nome»,
  «Nome C.», «paziente / piano / caso + Cognome», «CognomeNome» attaccati, nomi non ambigui
  da soli, parole tutte maiuscole. Non vale per `editoria/`, per i file dentro gli archivi
  e per i binari, che citano autori o contengono testo casuale: lì solo l'elenco.

Eccezioni in `strumenti/privacy_consentiti.txt`: solo nomi interi (titolare, autori delle
fonti), almeno due parole vere di due o più lettere, solo lettere, particelle come «di» e
«de» escluse; si tolgono solo come frase intera, a confini di parola, e valgono SOLO per il
dizionario, mai contro l'elenco: un'eccezione uguale al nome di un paziente non lo nasconde. Il blocco prima del
commit legge le eccezioni IN STAGE, GitHub quelle dell'ultimo commit caricato. `--autotest` verifica entrambi i livelli, con
esempi inventati scritti in ROT13.

**Dove gira.**
- **Prima di ogni commit**, nelle sessioni di Claude: dopo ogni `git clone`, una volta,
  `git config core.hooksPath .githooks`; poi `export PRIVACY_NOMI=/percorso/elenco.txt`
  (fuori dal repository). I blocchi `pre-commit` e `commit-msg` si fermano senza elenco e
  su ogni nome trovato. Un falso allarme si risolve riformulando o con un'eccezione
  motivata; `--no-verify` è vietato.
- **Su GitHub, a ogni caricamento**, anche fatto a mano dal sito: l'azione
  `controllo-privacy` controlla OGNI commit del caricamento, merge compresi; su un ramo
  nuovo o dopo un push forzato, l'intera cronologia. Il log è pubblico: stampa commit,
  tipo di oggetto e riga, mai il nome né il percorso del file. Se fallisce GitHub manda
  un'email al titolare: il nome va tolto subito, cronologia compresa. Senza il segreto
  `NOMI_PAZIENTI` (un nome per riga) su GitHub vale solo il dizionario: archivi, binari ed
  `editoria/` lì NON sono controllati, e l'azione lo segnala con un avviso.

**Limiti dichiarati.** Del solo dizionario: «N. Cognome», «Cognome N.», un cognome da solo
fuori contesto, nomi stranieri, nome e cognome tutti minuscoli. Per questo l'elenco è
obbligatorio nel blocco prima del commit. Dell'elenco: un nome di battesimo da solo; un
cognome segnato `~` in minuscolo nella prosa; un cognome che coincide con un nome di
battesimo del dizionario, da solo; il testo dentro PDF compressi, immagini e archivi `.7z`.

Il 24/10/2026 sono stati trovati nomi di 15 pazienti reali e del paziente fittizio, entrati
dal 30/07/2026 con le istruzioni caricate a mano e poi con commit di Claude (anche il 23/10):
la regola c'era, il controllo sul contenuto no. Tolti dai file e dall'intera cronologia,
riscritta due volte il 24/10 (la seconda per una forma attaccata sfuggita alla prima); i
codici dei commit precedenti non valgono più. Su GitHub restano consultabili per un tempo
non noto le pagine dei vecchi commit, solo per chi ne conosce il codice: il titolare ha
scelto di non chiederne la rimozione al supporto.

**Sessioni lunghe.** La copia estratta all'avvio invecchia in silenzio: oltre una giornata
di lavoro, riscarica e ricollauda prima di fidarti dei numeri.

---

## 2. MODULI SOFTWARE

### collaudo.py — certificato di inizio sessione
Nove controlli:
1. presenza e integrità di tutti i CSV, incluso il numero di colonne per riga
   (`csv.DictReader` da solo NON lo segnala)
2. righe di `alimenti.csv` contro `EXPECTED_ALIMENTI_COUNT`
3. nessun `food_id` duplicato
4. giornata golden contro il riferimento congelato
5. integrità byte per byte contro `SHA256SUMS` (standard: verificabile anche con
   `sha256sum -c SHA256SUMS`)
6. ogni `food_id` di `alimenti.csv` ha un nome paziente in `nomi_paziente.csv`, senza
   duplicati né righe orfane
7. `formati_confezione.csv` e `scambi_frutta.csv`: ogni `food_id` esiste in
   `alimenti.csv`, unità e tolleranze valide; ogni alternativa del catalogo
   `colazioni_spuntini.csv` e ogni blocco della libreria (`moduli_pasto.csv`,
   `moduli_colazione.csv`) rispettano i formati di confezione
8. ogni `food_id` ha un ruolo ammesso in `ruoli_alimenti.csv`; le regole di
   `accoppiamenti_vietati.csv` usano voci valide (ruoli o `food_id`); nessun blocco della
   libreria (`moduli_pasto.csv`, `moduli_colazione.csv`) contiene un accoppiamento vietato
   o un tag calcolato scritto a mano (vitD, calcio, leggero)
9. cross-check Atwater sull'intero database: ogni anomalia deve essere un falso positivo
   verificato (`coerenza.ATWATER_FALSI_POSITIVI_NOTI`: aglio, carciofi, semi di lino) e
   ogni voce dell'elenco deve essere ancora anomala; la pipeline lo esegue solo sugli
   alimenti del piano (sezione 8)

Esce 0 (superato) o 1 (fallito). File opzionali (`cache.zip`, `BDA_alimenti.xlsx`,
`crea_cache.zip`): se presenti si verificano come gli altri, se assenti il collaudo lo
dichiara e prosegue.

`python3 collaudo.py --genera-checksums` riscrive `SHA256SUMS`, dopo aver aggiornato
`alimenti.csv` o un modulo, e **solo dopo aver capito perché** il file era cambiato: mai per
far tornare verde un collaudo rosso. Firma **tutto** ciò che sta nella cartella, tranne
`__pycache__` e i file paziente con nome standard nella radice (`piano.csv`, `target.csv`,
`farmaci_paziente.csv`...): un file appoggiato lì con un altro nome (es. `piano_vN.csv`)
finisce nei checksum e fa fallire il collaudo alla sessione dopo. Prima del commit
`git status` mostra solo i file modificati di proposito; `__pycache__` resta fuori
(`.gitignore`). `EXPECTED_ALIMENTI_COUNT` si aggiorna a mano quando il database cresce.

### pipeline.py — orchestratore, il modo raccomandato di valutare un piano
Un comando, passi sempre nello stesso ordine, un report unico:
0. collaudo (si ferma se fallisce)
1. calcolo per pasto e per giorno
2. scenari min/max dei pasti a scelta multipla, PRIMA di ogni riepilogo; poi verifica
   settimanale di kcal e macro
3. micronutrienti per giorno e media settimanale, con flag LARN e gap
4. coerenza dei dati e gap dichiarati; controlli E (formati) e F (accoppiamenti)
5. interazioni farmaco-alimento
6. livello unico di colazione, spuntino e, se presente, secondo spuntino su tutto il piano

La pipeline usa SEMPRE il database ufficiale del motore, più le sole voci da etichetta
dichiarate con `--eccezione-etichetta` (sezione 4): non accetta un altro `alimenti.csv`.
Prima del PASSO 1 si ferma (bloccante) su un file di eccezione non valido, su un `food_id`
sconosciuto (compresa una voce da etichetta non dichiarata) o su un valore di pasto non
ammesso (`PASTO_NON_AMMESSO`, es. `spuntino 2` con lo spazio).
```
python3 pipeline.py --piano piano.csv --target target.csv
  [--farmaci f.csv --interazioni i.csv --orari o.csv]
  [--nessuna-terapia "fonte della verifica"]
  [--deroga-struttura "motivo"] [--eccezione-etichetta voci.csv] [--salta-collaudo]
```
Esce 0 senza rilievi bloccanti, 1 altrimenti; il report si stampa per intero in entrambi i
casi.

**Rilievi BLOCCANTI** (piano non presentabile): collaudo fallito o assente; `food_id`
sconosciuto; valore di pasto non ammesso; file di eccezione etichetta non valido; **media settimanale delle kcal** fuori tolleranza
(basta un estremo dell'intervallo); **media settimanale di un macro** fuori tolleranza su
tutto l'intervallo, dallo stesso lato; **giorno o scenario oltre ±10% di kcal**; target incoerenti; file dei formati o
degli accoppiamenti illeggibili o accoppiamenti non verificati; interazione di gravità ALTA;
gravità, tipo o nutriente non riconosciuti nella tabella interazioni;
orario di un pasto mancante; terapia dichiarata solo in parte; assenza di terapia dichiarata
(`--nessuna-terapia`) insieme a file di terapia, o senza fonte (`TERAPIA_CONTRADDITTORIA`: i
file si valutano comunque e i loro rilievi restano); struttura pasti non uniforme;
livelli colazione/spuntino misti o incoerenti tra pasti; catalogo disallineato.

**Rilievi DA DICHIARARE** (non bloccano): eccezione etichetta dichiarata
(`ALIMENTO_FUORI_DATABASE_SU_RICHIESTA`); giorno con kcal fuori ±5% (entro ±10%) o macro
fuori ±5 punti; scenario di scelta fuori tolleranza entro ±10%; estremi macro degli scenari
(limiti di garanzia, non giornate componibili); un solo estremo della media settimanale
di un macro fuori tolleranza; fibra sotto l'80% del target;
micronutrienti sotto l'80% LARN *in media settimanale* (con o senza gap); target privo di
LARN (micronutrienti non confrontati con niente); distribuzione concentrata; anomalia
Atwater di un alimento del piano che non è un falso positivo verificato (in pratica solo una
voce da etichetta); micronutrienti tutti a zero; quantità fuori formato; accoppiamenti vietati;
interazioni di gravità media o bassa (`INTERAZIONE_GRAVITA_MEDIA`, `_BASSA`); riga della
tabella interazioni su un `food_id` assente dal database;
principi attivi assenti dalla tabella; terapia non dichiarata (né file né
`--nessuna-terapia`); terapia dichiarata assente, con la fonte
(`TERAPIA_DICHIARATA_ASSENTE`: è la traccia della verifica nel verdetto); pasto assente su tutto il
piano; livello parziale o fuori catalogo; catalogo assente (livello verificato solo come
uniforme); collaudo saltato; avviso del livello rinforzato (`VALUTARE_LIVELLO_RINFORZATO`,
PASSO 6). I totali sottostimati per gap si stampano nel report.

Ogni rilievo porta un CODICE stabile: la suite congela `(passo, codice)`, non la prosa.

**Micronutrienti — giudizio settimanale (principio 8).** I valori di micronutrienti del
singolo giorno restano stampati senza allarme; il PASSO 2 riporta gli estremi dei
micronutrienti per giorno come informazione, non come verdetto.
`DISTRIBUZIONE_CONCENTRATA` (PASSO 3) riguarda SOLO il calcio (`NUTRIENTI_DISTRIBUZIONE`):
presente in meno di 3 giorni, su un piano di almeno 6. «Presente» = almeno il 30% del LARN
nel giorno (`SOGLIA_PRESENZA_PCT`), nei giorni a scelta nello scenario MINIMO; confronto
arrotondato a 6 decimali. `MEDIA_SOTTO_LARN` guarda invece lo scenario MASSIMO.

**PASSO 6, tre verifiche distinte:**
- (a) colazione e spuntino identici su tutti i giorni strutturati;
- (b) a quale livello appartengono, confrontandoli con `colazioni_spuntini.csv`: intercetta
  una colazione standard con uno spuntino rinforzato, che la (a) lascia passare.
- (c) avviso `VALUTARE_LIVELLO_RINFORZATO`, mai bloccante: media settimanale del calcio
  sotto l'80% del LARN (`SOGLIA_MEDIA_RINFORZATO_PCT`, scenario minimo nei giorni a scelta)
  OPPURE calcio presente in meno di 3 giorni su almeno 6. Tace se colazione e spuntino
  presenti nel piano sono tutti `rinforzata_calcio`, anche parziale o con alternative su
  misura accanto alle rinforzate (caso già bloccato da `LIVELLO_MISTO`); il secondo
  spuntino non conta; un pasto interamente fuori catalogo non conta come rinforzato.
  Catalogo assente o disallineato: l'avviso compare con una nota. Limite: senza
  `larn_calcio_mg` nel target né l'avviso né `DISTRIBUZIONE_CONCENTRATA` girano, senza
  rilievo (`LARN_ASSENTI` scatta solo se mancano tutti i LARN).
Alternative costruite su misura: non è un errore, si segnalano come fuori catalogo e il
livello non è verificabile.
Il secondo spuntino (`spuntino2`) segue le regole dello spuntino, solo se il piano lo
contiene: presente in un giorno e assente in un altro blocca come struttura non uniforme; il
livello si confronta con gli spuntini del catalogo; un piano a 4 pasti non riceve rilievi
sul secondo spuntino. Il catalogo ha 2 spuntini per livello: spuntino e secondo spuntino
fissi (una sola alternativa ciascuno) danno `LIVELLO_PARZIALE`, attenzione e non blocco.
`--deroga-struttura "motivo"` declassa ad attenzione, per le deroghe legittime (spuntino
saltato, giorno libero), i blocchi di struttura non uniforme e di livello incoerente tra
pasti; il rilievo resta nel report con il motivo. Livello misto e catalogo disallineato
restano bloccanti anche con la deroga.

### regressione.py
Suite sui 50 casi golden in `golden/`: un comando, pass/fail per caso. Si riesegue **dopo
ogni modifica** al motore o al database, e comunque prima di qualsiasi uso clinico.
- Dopo i casi, la suite esegue davvero `pipeline.py` con `--nessuna-terapia` sul caso 45
  e controlla che l'opzione arrivi al PASSO 5 e che la fonte compaia nel VERDETTO: i casi
  chiamano i passi direttamente e non
  vedrebbero un'opzione persa tra la riga di comando e `main()`. Vale solo per questa
  opzione.
- Nei casi `pipeline` la suite ripete la sequenza di `pipeline.main()`: un controllo nuovo
  va in una funzione chiamata da entrambi (come `controlla_pasti_ammessi`), altrimenti la
  suite non lo vede.
- `python3 regressione.py --genera` rigenera gli attesi SOLO quando una modifica cambia
  intenzionalmente i risultati e il nuovo output è già stato verificato a mano. Mai per far
  passare una suite rossa senza averne capito il motivo.
- Su un caso tarato su un confine (caso 04), se i dati cambiano si ricalibra il TARGET con
  gli stessi scarti, non solo l'atteso.
- Non è una validazione clinica: verifica che il motore dia gli stessi numeri su input
  fissi, non che quei numeri siano giusti per un paziente.

### calcolatore.py — il modulo principale
Totali per pasto e per giorno, confronto con i target, flag LARN. Legge `gap.csv` e marca
SOTTOSTIMATI i totali che pescano da voci con dati mancanti. È l'**unica fonte** di elenco
e ordine dei pasti (`PASTI_AMMESSI`, `ordine_pasti()`, `pasti_non_ammessi()`):
`pipeline.py` e `genera_zona_piano.py` li importano, non li riscrivono.

### interazioni.py
Incrocia la tabella interazioni, curata e validata dal nutrizionista, con gli orari di
pasti e farmaci. La tabella si legge senza distinzione tra maiuscole e minuscole:
- gravità ammesse `alta` (blocca), `media`, `bassa` (si dichiarano); ogni altro valore
  blocca, perché il motore non decide da solo quanto è grave un'interazione;
- `tipo_target` ammessi `nutriente` e `food_id`; un nutriente deve essere una colonna di
  `alimenti.csv` (es. `calcio_mg`); altri valori bloccano, perché farebbero sparire
  l'interazione in silenzio;
- un `food_id` assente dal database si dichiara: quell'interazione non può scattare.
Nessuna conoscenza farmacologica propria, nessuna interazione inventata:
segnala esplicitamente i principi attivi assenti dalla tabella, perché l'assenza di
allarme non sia scambiata per assenza di rischio.

### formati.py
Regola anti-spreco (nucleo, sezione 5). Legge `formati_confezione.csv` e
`scambi_frutta.csv`. Al PASSO 4, controllo E: per ogni alimento vincolato verifica che i
grammi siano una confezione intera o un multiplo (fino a 6) entro la tolleranza. Esito:
`FORMATO_CONFEZIONE_NON_RISPETTATO`, **non bloccante**. Funzioni: `carica_formati`,
`carica_scambi_frutta`, `controlla_piano(piano, formati)`, `quantita_valida`. Controllo
manuale fuori pipeline (la chat B non lo usa: l'impronta copre il piano approvato), stampa
`[]` se tutto è a formato:
`python3 -c "import csv,formati; print(formati.controlla_piano(list(csv.DictReader(open('piano_vN.csv'))), formati.carica_formati()))"`

### coerenza.py
Cross-check Atwater (doppio criterio, sezione 8), coerenza interna dei target, righe con
micronutrienti tutti a zero: intercetta errori nei DATI prima che entrino nei piani. Non ha
entry point standalone: si importa.

### scelte_multiple.py
Intervalli min/max per nutriente sui pasti a scelta: limiti garantiti, non una giornata
realmente componibile. Distingue ciò che è sotto soglia anche nel caso migliore da ciò che
dipende dalla scelta del paziente. Va eseguito per OGNI giorno subito dopo aver fissato
pranzo e cena di quel giorno, mai a posteriori dopo una tabella con una sola combinazione
«esemplare». `pipeline.py` lo fa da solo al PASSO 2.

### struttura_pasti.py
Legge `colazioni_spuntini.csv` e riconosce il livello di un piano. `python3
struttura_pasti.py` ristampa il catalogo con i valori RICALCOLATI da `alimenti.csv` e
segnala se le 4 colazioni di un livello hanno kcal troppo distanti tra loro.

### accoppiamenti.py — si segnala, non si blocca
Legge `ruoli_alimenti.csv` e `accoppiamenti_vietati.csv`. Al PASSO 4, controllo F:
attenzione `ACCOPPIAMENTO_VIETATO`, una per coppia, pasto e scenario, con i giorni. I pasti
con alternative si valutano scenario per scenario: due opzioni dello stesso
`gruppo_scelta` non si mangiano insieme e non formano un accoppiamento.
```
python3 accoppiamenti.py --piano piano_vN.csv   controlla un piano senza pipeline
python3 accoppiamenti.py --libreria             controlla la libreria dei blocchi
```
- Una coppia nuova è una riga nuova in `accoppiamenti_vietati.csv`, nessuna modifica al
  codice; le coppie crescono man mano che si presentano.
- Ogni lato nomina un RUOLO (pesce) o un `food_id` preciso (1313 merluzzo), per le coppie
  che non valgono per tutto il ruolo (pasta con merluzzo no, con alici sì).
- Stesso ruolo sui due lati (formaggio + formaggio) = due alimenti DIVERSI di quel ruolo.
- Una regola nuova che colpisce un blocco della libreria fa fallire il collaudo finché il
  blocco non viene tolto.
- *Falso allarme noto:* i piani scritti prima del 30/09/2026 con due spuntini li registrano
  entrambi come `spuntino`, e il controllo li legge come un pasto unico. Non è una
  violazione: il piano va riscritto con `spuntino2` prima di essere rivalutato.

### moduli_pasto.py
Legge la libreria (`moduli_pasto.csv` pranzo/cena, `moduli_colazione.csv`
colazioni/spuntini), ricalcolando i valori da `alimenti.csv`, marcando i nutrienti
sottostimati da `gap.csv` e aggiungendo i tag calcolati (vitD, calcio, leggero, sezione 5).
```
python3 moduli_pasto.py                     tutta la libreria
python3 moduli_pasto.py --categoria cena    solo le cene (anche colazione, spuntino, pranzo)
python3 moduli_pasto.py --tag pesce vitD    blocchi con TUTTI i tag
python3 moduli_pasto.py --scala M07 1.15    grammature riscalate del 15%
```
Il flag ⛔ sui gap evita di scartare un blocco per la ragione sbagliata (l'orata mostra
vitamina D 0.00 perché CREA non la pubblica, non perché non ne contenga).

### cerca_cache.py — cache BDA-IEO
```
python3 cerca_cache.py ricerca "sgombro" "farro" "kefir"
python3 cerca_cache.py ricerca --file nomi.txt
python3 cerca_cache.py estrai 1321_2
```
Si usa al PASSO 4 del protocollo di estrazione (M6). La ricerca interroga l'indice `_foods.json` in un solo passaggio e dice quali nomi mancano
davvero. L'estrazione riporta i nutrienti dello schema con la fonte di ciascuno: «tr»
diventa il valore di soglia (`vltraccia`), non zero; un campo assente è dichiarato DA
CERCARE SU USDA, non lasciato a zero. Energia e macronutrienti non vengono proposti (fonte
CREA). Non scrive in `alimenti.csv`: la trascrizione resta una scelta.

### cerca_crea.py — cache CREA
`crea_cache.zip`: copia locale delle 832 schede CREA 2019, con il codice di origine di ogni
valore. Si usa questa, non le pagine del sito.
```
python3 cerca_crea.py ricerca "yogurt greco" "ravanelli"
python3 cerca_crea.py estrai 150030
python3 cerca_crea.py verifica
python3 cerca_crea.py --autotest
```
`estrai` riporta i valori con l'origine (A analitico, C calcolato, ZL e S imputato, B
metodica non dichiarata) e segnala: campi ASSENTI (si scende a BDA-IEO, poi USDA); TRACCE
(la cache non porta la soglia: non scrivere zero); parte edibile diversa da 100% (es. fuso
di pollo 66%: il peso nel piano va convertito).
`verifica` confronta kcal, macro e fibra delle righe CREA di `alimenti.csv` con la cache:
esce 0 se coincidono, 1 se differiscono, non modifica nulla. Si esegue dopo ogni
ampliamento (M6, passo 8); non è nel collaudo perché richiede un file opzionale.

### tdee.py
Stima il TDEE (Mifflin-St Jeor + PAL) e propone un `target.csv` di partenza da peso,
altezza, età, sesso e livello di attività. La copia su Drive è archivio e non si usa.
Testato solo contro il paziente fittizio P00 (2040 kcal, coincidente):
`python3 tdee.py --autotest` rifà il confronto e fallisce con `assert` se la formula cambia.
Il valore è SEMPRE da confermare dal nutrizionista: il modulo propone, non decide.
```
python3 tdee.py --peso 80 --altezza 175 --eta 39 --sesso M --attivita leggero
python3 tdee.py ... --piano deficit_lieve --proteine 25 --carboidrati 45 --grassi 30
    --fibra 30 [--condizione menopausa] [--tdee-confermato 2300] [--out target_proposto.csv]
```
`--attivita` usa le chiavi di `PAL`, le stesse di `livello_attivita_dichiarato` del Form A.
Senza uno dei cinque dati si ferma e li elenca (mai default); senza argomenti non esegue
più la demo (fino al 23/10/2026 `--help` stampava il caso del paziente fittizio P00). Con `--piano` servono
le tre percentuali (somma 100) e la fibra; `--tdee-confermato` calcola il target sul TDEE
già confermato invece che sulla stima; `--condizione` (LARN) vale solo con `--piano` e si
controlla prima di stampare. Si ferma su peso fuori 30-300 kg, altezza fuori 120-220 cm,
età fuori 18-100 anni (Mifflin-St Jeor è validata sugli adulti) e TDEE confermato fuori
800-6.000 kcal; una stima fuori campo dà un avviso, e con `--piano` serve `--tdee-confermato`. `--out` scrive un `target.csv` leggibile da `carica_target` e non
sovrascrive un file esistente: è una proposta, si usa dopo la conferma.
`proponi_target_csv` legge i LARN da `larn.csv` tramite `larn.py` e **si ferma con errore
se sesso ed età non sono passati** (nucleo, sezione 6). Il parametro `larn={...}`
sovrascrive singoli valori solo con motivazione clinica.

### genera_zona_piano.py — dal piano approvato al PDF
Compila la zona dati del template piano v5 (M3) e genera il PDF. Legge `piano.csv`,
`alimenti.csv`, `nomi_paziente.csv`, `target.csv`, `metadati_piano_vN.json` e, se passato,
`orari_pasti.csv`.
```
python3 genera_zona_piano.py --piano piano_vN.csv --target target.csv
    --metadati metadati_piano_vN.json --template TEMPLATE_..._v5.py
    --out-py CognomeNome_piano_vN.py --out-pdf CognomeNome_piano_vN.pdf
    [--orari orari_pasti.csv] [--mese "Settembre 2026"]
    [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
python3 genera_zona_piano.py --anteprima --piano piano_vN.csv --target target.csv
    --metadati metadati_piano_vN.json [--orari ...] [--out-anteprima anteprima.md]
python3 genera_zona_piano.py --verifica-impronta --piano ... --target ... --metadati ...
python3 genera_zona_piano.py --autotest --template TEMPLATE_..._v5.py
```
- **`--anteprima` (PASSO 6, M2):** senza template e senza PDF, stampa i testi del PDF parola
  per parola, i campi del documento di spiegazione (anche vuoti), gli altri campi di primo
  livello dei metadati salvo `drive` e `impronta_approvata` (con il TDEE confermato in
  chiaro), e il piano per esteso: giorni, pasti, alternative con titolo, grammatura, nota
  di peso e kcal; le alternative di un pasto a scelta in tutti i giorni strutturati, sempre
  uguali, si scrivono una volta in testa. In fondo l'impronta (SHA-256 dell'anteprima, 12
  caratteri; JSON annidato con chiavi ordinate, quindi indipendente dal loro ordine).
  Sottochiavi non usate dentro `giorni` o `intestazione` si mostrano; quelle che il PDF
  non legge non lo cambiano. La generazione del PDF ricalcola l'impronta e si ferma se
  `impronta_approvata` manca o non coincide: piano, testi o valori cambiati dopo
  l'approvazione. L'impronta comprende le kcal (una voce del database corretta dopo
  l'approvazione ferma il PDF) e gli orari (`--orari` va passato come all'anteprima).
- **Impronte e versioni dello script:** l'impronta dipende dal testo dell'anteprima, quindi
  una modifica alla sua forma la cambia per tutti i metadati (23/10/2026 sera: aggiunta la
  riga `terapia`). Un'impronta approvata con una versione precedente ferma il PDF:
  si rigenera l'anteprima e la si fa riapprovare. Il commit che cambia l'anteprima lo
  dichiara.
- **`--verifica-impronta`:** solo il controllo, senza PDF (non si combina con `--anteprima`
  né con le opzioni del PDF: errore); si lancia in chat B prima del
  documento di spiegazione (M3), che non passa dallo script.
- Kcal da `calcola_riga`, arrotondate alle 10 con la tilde. Totale del giorno = intervallo
  min–max sulle combinazioni colazione×spuntino ammesse dall'abbinamento; ogni altro pasto a
  scelta (es. secondo spuntino) entra con la sua alternativa minima e massima, come scelta
  indipendente.
- **Pasti:** al massimo 5; un pasto senza righe non compare. Con `spuntino2` l'ordine è
  colazione, SPUNTINO (metà mattina), pranzo, SECONDO SPUNTINO, cena; a 4 pasti resta
  colazione, pranzo, spuntino, cena. Se tutti i pasti di un giorno hanno un orario in
  `orari_pasti.csv`, vale l'orario (uno spuntino alle 22:30 va dopo la cena). Il secondo
  spuntino usa la chiave emoji `"spuntino"`: il template non si tocca. «N pasti»
  nell'intestazione è contato dai dati. Un valore di pasto non ammesso ferma lo script.
- Dettaglio dei pasti con nome e nota di peso di `nomi_paziente.csv`; lettere A, B, C...
  nell'ordine della colonna `opzione`.
- Motore grafico copiato byte per byte dal template: si sostituisce solo la zona dati.
- Box target: `kcal_target` da `target.csv`; deficit = `tdee_confermato_kcal` dei metadati
  − target; perdita attesa = deficit × 7 / 7.700 kg/settimana.
- Giorno libero: colazione, spuntino e secondo spuntino come nei giorni strutturati, pranzo
  e cena liberi con le indicazioni dei metadati, totale da `range_kcal_libero`.
- **Si ferma, nominando il problema**, se manca un campo obbligatorio dei metadati (elenco
  in M2, PASSO 6; `versione_piano` e `abbinamento_spuntino` invece non lo fermano) o un
  titolo di piatto,
  se un `food_id` non ha nome paziente, se i giorni di `piano.csv` non coincidono con quelli
  dichiarati, o se un pasto mescola alimenti fissi e alternative.
- **Si ferma sui segnaposto nei testi del paziente** (`_testo_paziente`): obiettivo,
  criterio di rivalutazione, avvertenze, intestazione (nome, età, condizione), indicazioni
  del giorno libero, titoli dei piatti. Fermo se il valore non è testo, se è vuoto o fatto
  solo di spazi e simboli, se il campo INTERO è un segnaposto («non concordato» e varianti,
  «da concordare/definire», «N/D», «N/A», «n.d.» minuscolo, «TBD»…) o un testo d'esempio
  del template v5 o dello schema di M2 («Nome Cognome», «XX kg», «XX anni», «Da rivalutare
  dopo N settimane», «Indicare qui allergie…», «titolo approvato»). Passano frasi vere con
  le stesse parole, sigle e nomi brevi («NA», «Nan», «N.D.», «Gravidanza alla XX
  settimana», «46,XX», «Non note»). `abbinamento_spuntino` = «non concordato» resta ammesso
  (scritto esattamente così): non finisce nel PDF. «Non concordato» ferma invece anche
  `versione_piano`. Elenco dei testi d'esempio CHIUSO: i titoli d'esempio della zona dati
  del template v5 («Nome piatto pranzo», «Colazione dolce 1», «Spuntino 1», «Pasto libero o
  indicazioni»…) passano.
- Fermo, invece di un errore Python, se `giorni`, `intestazione`,
  `indicazioni_giorno_libero` o `titoli_piatti` non sono oggetti; `versione_piano`, se
  c'è, deve essere un numero con o senza «v»/«versione» davanti, anche con lettera finale
  («v3», «3», «versione 3», «2b»), altrimenti fermo («vN», «3 bis», «v1,0»). Se manca, la
  nota del PDF esce «versione » vuota.
- `--autotest` (96 controlli) genera il caso golden 03 con metadati fittizi e verifica:
  kcal uguali al calcolatore, motore grafico identico al template, PDF senza segnaposto,
  abbinamento risolto in lettere, fermo su metadato mancante, su ogni segnaposto e testo
  d'esempio, su tipi e versione non validi; passaggio di nomi, sigle e frasi legittime;
  anteprima ripetibile e completa; fermo senza impronta e su titolo, regola operativa,
  giorno libero o grammatura cambiati dopo l'approvazione; impronta invariata se cambia
  solo `drive` o l'ordine delle chiavi del JSON; `--verifica-impronta` che passa e che
  ferma; campi del documento di spiegazione vuoti mostrati.
  Richiede il template v5 (fuori da `motore-calcolo/`) e `pdftotext`; NON lo esegue né il
  collaudo né la regressione: va lanciato a mano dopo ogni modifica allo script. Scrive in
  una cartella temporanea e la cancella; restano in /tmp le cartelle che il template v5
  crea a ogni PDF (riga 218, motore grafico congelato: non si tocca).

### larn.py + larn.csv — riferimenti per sesso, età e condizione
`larn.csv`: `gruppo, sesso, eta_min, eta_max, condizione, larn_* (8 colonne), nota`.
Fonte: **LARN V revisione, SINU 2024** (tabelle riassuntive di sinu.it/larn/, trascritte il
19/09/2026); si usa la V revisione, non la IV. Copre 11-14, 15-17, 18-64, 65-74 e ≥75 anni
per entrambi i sessi, più `menopausa`, `gravidanza`, `allattamento`. Sotto gli 11 anni il
modulo si ferma: i LARN pediatrici non sono caricati.
`python3 larn.py` stampa cinque casi tipici; `riferimenti(sesso, eta, condizione)` dà i
valori e la nota della riga usata.
Valori da tenere presenti nell'adulto: B12 **4,0 µg** (non 2,4: un piano adeguato con 2,4
può non esserlo), folati **330 µg**, calcio **950 mg** (1100 dai 65 anni e in
post-menopausa). Donna in età fertile: ferro **18 mg**, zinco 9 mg, vitamina C 85 mg.

---

## 3. CASI GOLDEN

In `motore-calcolo/golden/`, una sottocartella per caso con `piano.csv`, `target.csv`,
`atteso.json` (valori attesi più `descrizione`, cosa copre, e `riferimento`, come è stato
validato).

- **01_base** — giornata reale validata (P01, lunedì), riprodotta al decimale su tutti i
  pasti: legumi lessati a peso cotto, pesce a peso crudo.
- **02_legumi_inscatolati** — legumi e pesce in scatola e olive a peso netto nella stessa
  giornata; esercita anche il percorso «macro fuori tolleranza».
- **03_scelta_colazione_spuntino** — colazione e spuntino a 2 alternative, pranzo e cena
  fissi: verifica minimo/massimo per nutriente di `scelte_multiple.py`.
- **04_limite_tolleranza** — target tarati sul confine ±5 punti (scarti +4.999/+5.001), non
  un piano realistico. Limite dichiarato: non distingue un confine incluso da uno escluso
  scritto male esattamente a scarto 5.000.
- **05_livelli_colazione_misti** — 2 giorni con colazioni diverse, entrambi dentro
  tolleranza su kcal e macro: fermato solo dalla regola strutturale del PASSO 6.
- **06_livelli_incoerenti_tra_pasti** — colazioni standard con spuntini rinforzati, giorni
  identici: solo il riconoscimento del livello vede l'incoerenza.
- **07_micro_basso_giorno_ok_settimana** — calcio al 65% LARN il giorno 1, all'85% in
  media: nessun rilievo sul calcio (né giornaliero né settimanale), exit 0. Protegge il
  giudizio settimanale dei micronutrienti.
- **08_giorno_fuori_settimana_ok** — giorno a -6,96% kcal, media dentro: attenzione
  `KCAL_FUORI_TOLLERANZA`, non bloccante, exit 0.
- **09_settimana_fuori_tolleranza** — media a -6,96%: bloccanti
  `SETTIMANA_KCAL_FUORI_TOLLERANZA` e `SETTIMANA_MACRO_FUORI_TOLLERANZA`, exit 1. Senza
  questo caso un motore che non blocca più nulla passerebbe la suite.
- **10_giorno_oltre_limite_sicurezza** — giorno a -11,98% con media dentro: bloccante
  `GIORNO_KCAL_OLTRE_LIMITE_SICUREZZA`, exit 1.
- **11_formati_confezione_violati** — fiocchi di latte 100 g (vaschette 200/400):
  attenzione `FORMATO_CONFEZIONE_NON_RISPETTATO`, non bloccante. Altri casi la contengono
  anch'essi, perché i loro input di test non seguono i formati commerciali. Dal 23/10/2026
  i casi 06, 13, 36, 39, 42, 43 usano il catalogo ai formati (grammi aggiornati nei loro
  piani; caso 42 con LARN calcio 1100 per tenere la media minima sotto l'80%); i casi 12 e
  14 hanno ancora i grammi vecchi, irrilevanti per ciò che proteggono (12 confronta solo i
  totali, 14 si ferma al PASSO 1). Limite: i casi «nessun avviso perché…» (36, 42, 44)
  proteggono la regola solo se la media minima del calcio resta sotto l'80%, e la suite
  non lo verifica.
- **12_cinque_pasti** — un giorno a 5 pasti; totali congelati pasto per pasto, secondo
  spuntino compreso (verificati a mano da `alimenti.csv`).
- **13_secondo_spuntino_non_uniforme** — secondo spuntino solo nel giorno 1: unico
  bloccante `STRUTTURA_NON_UNIFORME`.
- **14_pasto_non_ammesso** — `spuntino 2` con lo spazio: unico bloccante
  `PASTO_NON_AMMESSO`.
- **15_accoppiamenti_vietati** — latte + yogurt in colazione (solo scenario A), pollo +
  merluzzo a cena: due attenzioni. Controllo negativo: yogurt e latte alternative dello
  stesso spuntino non scattano.
- **16_accoppiamenti_alimento_preciso** — pasta + merluzzo (A04) e parmigiano + mozzarella
  (A03): due attenzioni. Negativo: pasta integrale + alici con un solo formaggio.
- **17_carne_pasta_frutta_secca** — pasta + vitellone (A05), noci + nocciole nello stesso
  spuntino (A06): due attenzioni. Negativi: pasta integrale + pollo; mandorle a colazione e
  noci allo spuntino.
- **18_eccezione_etichetta_dichiarata** — voce da etichetta fittizia passata con
  `--eccezione-etichetta`: attenzione `ALIMENTO_FUORI_DATABASE_SU_RICHIESTA`, exit 0.
- **19_alimento_fuori_database** — la stessa voce non dichiarata: unico bloccante
  `FOOD_ID_SCONOSCIUTO`.
- **20_gravita_interazioni** — «Alta» con la maiuscola blocca come gravità alta; «bassa» e
  «media» (con «Nutriente» e «Zinco_mg» maiuscoli) si dichiarano; «grave», il nutriente «calcio» e
  il tipo «alimento» bloccano; un `food_id` inesistente si dichiara.
- **21_eccezione_riusa_voce_ufficiale** — eccezione con il `food_id` dei pomodori: unico
  bloccante `ECCEZIONE_ETICHETTA_NON_VALIDA`.
- **22_eccezione_valore_non_valido**, **23_eccezione_riga_corta**,
  **24_eccezione_valore_negativo**, **25_eccezione_macro_non_plausibili** — eccezione con
  calcio «nan», con una riga corta, con kcal negative, con macro a 90 g ciascuno: unico
  bloccante `ECCEZIONE_ETICHETTA_NON_VALIDA`.
- **26_eccezione_somma_esattamente_100** — etichetta con somma esattamente 100 g: passa
  (confine della soglia di plausibilità).
- **27-32, distribuzione del calcio** (`DISTRIBUZIONE_CONCENTRATA`, piani da 5-6 giorni):
  27 calcio al 29,8% in 4 giorni su 6, rilievo (soglia del 30%); 28 presente in esattamente
  3 giorni (30,65%), nessun rilievo; 29 spuntino a scelta, presente solo nello scenario
  massimo, rilievo (conta il minimo); 30 media adeguata (87%) ma concentrata, rilievo senza
  `MEDIA_SOTTO_LARN`; 31 giorno esattamente al 30,0% del LARN 950, presente; 32 piano di 5
  giorni, nessun rilievo (minimo 6 giorni).
- **33-44, avviso del livello rinforzato** (`VALUTARE_LIVELLO_RINFORZATO`): 33 media al
  79,9%, avviso; 34 all'80,03%, nessun avviso; 35 media sotto l'80% solo nello scenario
  minimo, avviso (e nessun `MEDIA_SOTTO_LARN`, che guarda il massimo); 36 livello
  rinforzato già scelto, nessun avviso; 37 presente in esattamente 3 giorni con media
  adeguata, nessun avviso; 38 piano di 5 giorni, nessun avviso; 39 solo la colazione
  rinforzata, avviso (più il blocco `LIVELLO_INCOERENTE_TRA_PASTI`); 40 piano senza
  spuntino con colazione rinforzata, nessun avviso; 41 media esattamente all'80,0%, nessun
  avviso; 42 secondo spuntino standard, nessun avviso (non conta), resta il blocco; 43
  colazione fuori catalogo, avviso; 44 rinforzato parziale, nessun avviso.
  Limite dichiarato (31 e 41): l'arrotondamento a 6 decimali dei confronti non è protetto da
  nessun caso.
- **45_nessuna_terapia_dichiarata** — il piano del 36 con `nessuna_terapia` (la fonte):
  `TERAPIA_NON_DICHIARATA` diventa `TERAPIA_DICHIARATA_ASSENTE`, il resto uguale al 36.
- **46_nessuna_terapia_con_farmaci** — il piano del 20 con i suoi file di terapia e
  `nessuna_terapia`: i verdetti del 20 più il bloccante `TERAPIA_CONTRADDITTORIA`.
- **47_atwater_falso_positivo_noto_nel_piano** — il 36 con aglio 5 g a cena: nessun
  `ATWATER_SEGNALATO`.
- **48_atwater_etichetta_incoerente** — il 18 con la voce da etichetta a grassi 0,2 g (kcal
  invariate, scarto -25,5%): `ATWATER_SEGNALATO`, il resto uguale al 18.
- **49_nessuna_terapia_senza_fonte**, **50_nessuna_terapia_senza_fonte_con_farmaci** —
  `nessuna_terapia` vuota (o solo spazi): bloccante `TERAPIA_CONTRADDITTORIA`; nel 50 i file
  di terapia del caso 20 si valutano comunque e tutti i suoi verdetti restano.

**Tipi di caso.** `fisso` e `scelta_multipla` si deducono dal piano (presenza di
`gruppo_scelta`). `pipeline` è l'unico DICHIARATO, da un `pipeline.json` nella cartella del
caso, che porta anche le opzioni di esecuzione (`deroga_struttura`, `farmaci`,
`interazioni`, `orari`, `eccezione_etichetta`, `nessuna_terapia`). I casi `pipeline`
congelano i VERDETTI (passo, codice del rilievo, codice di uscita), non i numeri.

**Limite di copertura.** I casi toccano solo gli alimenti dei rispettivi piani: una
modifica ai valori di carni e pesci non presenti passa la suite. La intercetta il controllo
5 del collaudo, non la regressione.

Una regola nuova si verifica anche al contrario: togliendola, la suite deve diventare rossa
sul caso che la sorveglia. Un errore di un caso reale che il motore non ha intercettato
diventa un nuovo caso golden.

---

## 4. DATABASE ALIMENTI E GERARCHIA FONTI

**Stato:** 159 alimenti verificati e tracciati alla fonte; il numero vincolante è
`EXPECTED_ALIMENTI_COUNT` in `collaudo.py`. Conformità kcal/macro/fibra a CREA:
`python3 cerca_crea.py verifica`.

**Criterio «Key Foods»:** un alimento si aggiunge solo quando un piano reale lo richiede e
non è già presente. Oltre le 150 voci solo su richiesta esplicita del nutrizionista.

**Gerarchia fonti — congelata, non riaprire:**
1. **CREA eTCA 2019** (alimentinutrizione.it) — kcal, macronutrienti, fibra, minerali. Le
   kcal si LEGGONO da CREA, mai ricalcolate con 4/4/9 (CREA usa il metodo Southgate, scarto
   fisiologico noto del 4-8% rispetto ad Atwater).
2. **BDA-IEO** — vitamina D, folati, B12 e minerali non coperti da CREA.
3. **USDA FoodData Central** — residuale, quando le prime due tacciono. Mai per le kcal.

**Eccezione INSA** (tabella nazionale portoghese, Base de Dados da Composição de Alimentos,
INSA, v 7.1 – 2026; citazione della fonte obbligatoria per licenza). SOLO per decisione del
nutrizionista, voce per voce, quando le tre fonti sono incoerenti tra loro e INSA ha la
stessa specie e lo stesso stato (crudo/cotto). Mai per kcal e macro, che restano CREA. In
`fonte` si scrive `INSA(...)`, in `codice_fonte` `INSA<cod>`. Righe in eccezione: 122800
sardine (micronutrienti).

**Eccezione etichetta — solo su richiesta esplicita del nutrizionista, mai nel database.**
I valori di un'etichetta non entrano in `alimenti.csv`. Quando il nutrizionista lo chiede
per un piano, le voci da etichetta (TUTTE le colonne di `alimenti.csv`, `food_id` nuovo,
fonte compilata) vanno in un file a parte, fuori dalla cartella del motore, passato con
`--eccezione-etichetta` alla pipeline e, con il nome paziente in `--nomi-eccezione` (solo
per quelle voci), a `genera_zona_piano.py`. Il motore:
- tratta una voce da etichetta non dichiarata come `food_id` sconosciuto: blocca;
- blocca il file (`ECCEZIONE_ETICHETTA_NON_VALIDA`) se mancano colonne, se una riga ha
  campi in più o in meno, se `food_id`, nome o fonte sono vuoti, se un valore non è un
  numero finito e non negativo, se un `food_id` è duplicato o riusa una voce ufficiale (un'eccezione
  non sovrascrive un dato verificato), se proteine + carboidrati + grassi + fibra superano
  100 g per 100 g (soglia del nutrizionista, SOLO per le etichette: CREA esprime i
  carboidrati in equivalenti di monosaccaridi e voci verificate superano 100, es. pop corn
  109,2 g; non estenderla al database);
- dichiara l'eccezione al PASSO 1 (`ALIMENTO_FUORI_DATABASE_SU_RICHIESTA`), tratta come
  gap i micronutrienti a zero (totali sottostimati) e avvisa che gli accoppiamenti non
  controllano quelle voci.
Il file vale per quel piano: non si salva nel repository. Va dichiarato nella tabella di
approvazione (M2, PASSO 6).

**Il terzo livello va usato davvero.** CREA non pubblica calcio, ferro, vitamina D, folati
e B12 per pesci e carni. Quando una fonte tace su un campo si scende di livello, sempre.
Prima di dichiarare un gap si interroga la cache con `cerca_cache.py`.

**Tolleranze:** ±5% sulle kcal totali · ±5 punti percentuali sui macronutrienti.

---

## 5. SCHEMA CSV — CONGELATO, non modificare le colonne

**alimenti.csv** (valori per 100 g di parte edibile)
`food_id, nome, categoria, fonte, codice_fonte, data_verifica, kcal_100g, proteine_g,
carboidrati_g, grassi_g, fibra_g, calcio_mg, ferro_mg, vitamina_d_ug, folati_ug,
vitamina_b12_ug, zinco_mg, magnesio_mg, vitamina_c_mg`

**piano.csv** — `giorno, pasto, food_id, grammi` [+ `gruppo_scelta, opzione`, opzionali].
Pasti ammessi: `colazione | spuntino | pranzo | spuntino2 | cena`, al massimo 5.
`spuntino2` = secondo spuntino: minuscolo, tutto attaccato, senza spazi (altrimenti
`PASTO_NON_AMMESSO`).

**target.csv** — `parametro, valore`
**farmaci_paziente.csv** — `principio_attivo, nome_commerciale, orario_assunzione, note`
**interazioni.csv** — `principio_attivo, tipo_target, target, meccanismo, separazione_ore, gravita`
**orari_pasti.csv** — `giorno, pasto, orario (HH:MM)`

### File affiancati — fuori dallo schema congelato
Un dato nuovo va in un file affiancato, mai in una colonna nuova. Nessuno contiene valori
nutrizionali precalcolati (principio 2): chi dichiara alimenti dichiara solo ingredienti,
e i valori si ricalcolano da `alimenti.csv`.

**gap.csv** — `food_id, nome, nutriente, motivo` (sezione 6).

**larn.csv** — vedi `larn.py`.

**formati_confezione.csv** — `food_id, nome_riferimento, unita_g, tolleranza_g, fonte, stato`.
`unita_g` è una lista separata da `|` (es. `125|150|170`). Alimento PRESENTE = vincolato a
confezione intera o multiplo; ASSENTE = porzione libera. `stato`: `confermato` o
`da_confermare`.

**scambi_frutta.csv** — `food_id, nome_riferimento, grammi_porzione, stato`. Porzioni di
frutta equivalenti in energia (riferimento banana 100 g), per la tabella di scambio del
documento di spiegazione.

**nomi_paziente.csv** — `food_id, nome_paziente, nota_peso`. Nome leggibile dell'alimento
nel PDF e nota di peso (`crudo`, `sgocciolato e sciacquato`, `cotto`, `peso netto di
confezione`, `crude, peso sgusciato`...). Solo testo. **Un alimento nuovo fa fallire il
collaudo finché non ha la sua riga qui** (controllo 6): passo finale di ogni ampliamento
(M6).

**colazioni_spuntini.csv** — `alternativa_id, livello, tipo, ingredienti_food_id_grammi, nota`.
Catalogo di 4 colazioni + 2 spuntini per livello: `standard` (S1/S2/D1/D2 + SPA/SPB) e
`rinforzata_calcio` (Sr1/Sr2/Dr1/Dr2 + SPrA/SPrB). Si legge con `python3
struttura_pasti.py`. La scelta tra standard e rinforzato è UNA SOLA DECISIONE PER L'INTERO
PIANO SETTIMANALE, mai giorno per giorno (dettaglio in M2). Non si riempie di alternative:
quelle stanno nella libreria. Grammi nei formati di confezione (controllo 7 del collaudo;
dal 23/10/2026: S1 uova 104 g, S2 fiocchi 200 g + pane 45 g, D2 e SPA yogurt 125 g, SPrB
yogurt 250 g + nocciole 5 g). Il riconoscimento del livello confronta i grammi esatti: un
piano composto con il catalogo precedente risulta fuori catalogo.

**Libreria degli accoppiamenti** — `moduli_pasto.csv` (129 blocchi pranzo/cena) e
`moduli_colazione.csv` (55 blocchi colazione | spuntino), schema
`modulo_id, nome, categoria, tag, ingredienti_food_id_grammi`.
- **Tag scritti nel file**, pranzo/cena: halal_ok · mensa_ok · vegetariano · legumi ·
  pesce · carne · pratico. *pratico* = piatto unico freddo o da portar via (insalata,
  insalatona, bowl, cereali freddi, panino) o con la proteina già pronta (scatolame,
  affettati, latticini freschi, uova sode, legumi in scatola). *mensa_ok* = primo semplice
  (pasta o riso con legumi, pomodoro, verdure o tonno) o secondo semplice di pollo,
  tacchino, pesce bianco o uova con contorno. Colazioni/spuntini: dolce · salata ·
  halal_ok · vegetariano · carne.
- **Tag calcolati**, solo pranzo e cena, ricavati a ogni esecuzione dai valori ricalcolati
  (soglie decise dal nutrizionista il 21/10/2026): **vitD** ≥ 5 µg, **calcio** ≥ 300 mg,
  **leggero** ≤ 450 kcal. Non si scrivono nel file: scritti a mano fanno fallire il
  collaudo (controllo 8).
Si legge con `python3 moduli_pasto.py`.
- Raccoglie gli ACCOPPIAMENTI VALIDI di tutti i piani fatti, per non ricomporre ogni volta
  pasti mal accoppiati; nessun tetto al numero di blocchi.
- Un blocco entra solo se il suo NUCLEO non c'è già: alimenti portanti (proteine, cereali,
  patate, latticini, legumi, frutta secca, dolci); verdura, frutta e condimenti si
  scambiano e non contano.
- È una BASE DI PARTENZA da scalare, non un sostituto del calcolo caso per caso.
- Un blocco che viola una regola di accoppiamento si toglie.

**ruoli_alimenti.csv** — `food_id, ruolo`. Un ruolo per voce: carne, salume, pesce,
molluschi_crostacei, uova, legumi, latte, yogurt, formaggio, cereale, patate, verdura,
frutta, frutta_secca, condimento, dolce. Più fine della `categoria` di `alimenti.csv`.
Patate e patata dolce hanno un ruolo proprio (portano carboidrato, non contorno); i piselli
sono legumi; il mais dolce è cereale. Ogni voce nuova del database richiede la sua riga
qui (controllo 8).

**accoppiamenti_vietati.csv** — `regola_id, ruoli_a, ruoli_b, motivo, data_decisione, pasti`.
Più voci separate da `|`, ciascuna un ruolo o un `food_id`. `pasti` (vuota = tutti) limita
la regola a certi pasti; nella libreria un blocco `spuntino` vale per spuntino e spuntino2.
Regole attuali:
- A01 latte + yogurt
- A02 carne o salume + pesce o molluschi/crostacei
- A03 due formaggi diversi
- A04 merluzzo + pasta (semola o integrale)
- A05 carne rossa o maiale + pasta (vitellone, manzo, vitello, maiale, trippa); pollo e
  tacchino ammessi; i salumi NON sono inclusi
- A06 due tipi di frutta secca nello stesso pasto (in pasti diversi ammessi; i semi di lino
  hanno ruolo frutta_secca e contano)
Nuove coppie: si aggiungono man mano, durante la stesura delle diete.

---

## 6. GAP DICHIARATI

Lo schema non sa rappresentare «dato non disponibile»: un nutriente che la fonte non
pubblica finisce a 0 e viene sommato come assenza reale. `gap.csv` elenca le celle il cui
zero è un dato mancante; `calcolatore.py` marca il totale con ⛔ TOTALE SOTTOSTIMATO ed
elenca le voci responsabili.

Un valore sotto l'80% LARN con quel flag NON è una carenza accertata: prima di intervenire
clinicamente, verifica se dipende dal gap.

**Stato (verificato sul file il 21/10/2026):** 8 righe su 4 alimenti — latte parzialmente
scremato (vitamina D, B12), orata (vitamina D), salmone affumicato (vitamina D), trippa
(vitamina D, B12, folati, zinco).

**Fave secche cotte — caso a parte:** minerali e folati presi dalla voce BDA delle fave
CRUDE (proxy), quindi probabilmente SOVRASTIMATI. Non usarle come fonte portante di ferro o
folati.

Obiettivo: non «zero gap», ma **zero gap taciuti**.

---

## 7. RECUPERO USDA

**Chiave API:** non è qui (repository pubblico): sta nel nucleo M0. La `DEMO_KEY` (10
richieste/ora, quasi sempre esaurita) non si usa per un blocco di gap.

Ogni valore recuperato si scrive in `alimenti.csv` con fonte tracciata (es.
`CREA+BDA-IEO+USDA`), si toglie la riga da `gap.csv`, si rieseguono collaudo e
regressione. Ciò che nemmeno USDA copre resta in `gap.csv`.

**Verifica della derivazione — obbligatoria.** Un valore non si accetta dal solo
`/foods/search`: va controllato su `/v1/food/{fdcId}`, campo `foodNutrientDerivation`.
- **codice Z «Assumed zero»** → assunzione, non dato: non chiude il gap.
- **codice NC «Calculated»** → ricalcolato, non misurato: mai per le kcal.
- **dataPoints: 0** → senza campioni analitici: utilizzabile (livello 3 residuale), ma
  dichiarato come debole.

**Valori USA non trasferibili.** Il latte USDA porta vitamina D per la fortificazione
obbligatoria statunitense, assente nel latte italiano standard: non importarla, maschera la
carenza strutturale che il piano deve dichiarare. Stessa cautela per ogni alimento
arricchito per obbligo negli USA (cereali da colazione, farine, bevande vegetali, latti
fermentati). Nella cache BDA-IEO usare i FIOCCHI DI MAIS (CORNFLAKES) «non fortificati» per
i prodotti italiani standard.

**Audit da fare:** i 35 valori di magnesio scritti il 28/07/2026, presi prima della regola
sulla derivazione: controllare i loro `fdcId` (alcuni potrebbero essere imputati anziché
analitici).

---

## 8. CASI RISOLTI — non riaprire

**Atwater, doppio criterio.** `coerenza.py` segnala solo se lo scarto supera **sia** il
12% relativo **sia** 8 kcal/100 g in assoluto. Falsi positivi noti, attesi (quattro):
- **AGLIO** (`005000`) — atteso -15,5%, scarto 8,20 kcal: appena sopra soglia;
- **CARCIOFI** (`005120`) — atteso -31,5%, scarto 10,4 kcal: Southgate conta la fibra; kcal
  e macro coincidono con la scheda CREA;
- **SEMI DI LINO** (`9600_1`) — atteso -15,7%, scarto 70 kcal: BDA-IEO calcola l'energia
  «con fibra».
- **CAVOLI DI BRUXELLES** (`005170`) — atteso -18,9%, scarto 8,9 kcal: Southgate conta i 5 g
  di fibra; kcal e macro coincidono con la scheda CREA (28/10/2026).
Dal 23/10/2026 l'elenco sta nel codice (`coerenza.ATWATER_FALSI_POSITIVI_NOTI`), con lo
scarto atteso di ciascuno: la pipeline guarda solo gli alimenti del piano e non segnala
questi tre; il collaudo (controllo 9) controlla l'intero database e si ferma su
un'anomalia fuori elenco, su una voce dell'elenco non più anomala o su una voce con scarto
lontano più di 1 punto da quello atteso. Uno di questi con scarto diverso da quello atteso
non è più il falso positivo noto: va verificato come un segnalato nuovo. Un NUOVO segnalato dopo un ampliamento ferma il collaudo:
si esclude l'errore di trascrizione, poi si aggiunge all'elenco nello stesso commit. Non
si alza la soglia per farlo sparire, non si corregge il dato della fonte.

**Sardine, riga unica 122800.** «Sarda fresca» (BDA 1319) NON esiste più come voce
separata. Kcal e macro CREA; TUTTI i micronutrienti da INSA 882 «Sardinha gorda crua»
(decisione del nutrizionista). Limite dichiarato: sardina atlantica (Portogallo); la
vitamina D dei pesci varia per stagione e zona.

---

## 9. STATO DI VALIDAZIONE

Il motore è validato contro un piano reale già consegnato (P01, lunedì: -4,56% dopo la
correzione della regola sui legumi), oggi `caso_01_base`: la validazione è ripetibile. È
utilizzabile su pazienti reali alle condizioni del principio 7.

**Validazione sul campo ancora aperta (FASE 5):** l'orchestratore è passato da casi reali
(il primo ha fatto emergere due errori di processo); il protocollo struttura pasti e
`tdee.py` solo dal paziente fittizio: nessun paziente reale ha ancora attraversato per
intero il protocollo. Il flusso del 21-22/10/2026 (motore sciolto, salvataggio con commit,
accoppiamenti, distribuzione del calcio, avviso del livello rinforzato, fermi sui
segnaposto) non è ancora passato da un caso reale. Criterio di chiusura: tre
pazienti reali consecutivi senza errori di processo. Ogni caso reale è
anche un collaudo: cosa il motore ha intercettato da solo, cosa ha richiesto un intervento
manuale, cosa è sfuggito. Quello che sfugge diventa un caso golden.
