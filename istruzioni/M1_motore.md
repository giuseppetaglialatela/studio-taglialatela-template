# M1 — MOTORE DI CALCOLO

Modulo operativo (principio 6). Dipendenze: nessuna. Ne dipendono M2 e M6.
Ultima modifica: 21/10/2026 sera (versione asciutta: motivazioni, episodi e date in
`istruzioni/archivio/M1-motivazioni.md`, che non si carica).

Copre: avvio della sessione, moduli software, casi golden, database e fonti, schema CSV e
file affiancati, gap, recupero USDA, falsi positivi, stato di validazione.
NON copre: composizione del piano (M2), ampliamento del database (M6).

---

## 1. AVVIO E SALVATAGGIO

**Avvio, obbligatorio prima di qualsiasi calcolo.** UN comando scarica in una cartella
pulita l'intera cartella `motore-calcolo` (codice, dati, casi golden, cache) ed esegue
collaudo e regressione:
```
rm -rf /tmp/motore && mkdir /tmp/motore && cd /tmp/motore && curl -sfL https://codeload.github.com/giuseppetaglialatela/studio-taglialatela-template/tar.gz/refs/heads/main | tar xz --strip-components=2 studio-taglialatela-template-main/motore-calcolo && python3 collaudo.py && python3 regressione.py
```
Poi si lavora in `/tmp/motore`. Nessun calcolo su paziente prima dell'esito positivo
(principio 7). Il download è pubblico: non serve il repository collegato.
`cache.zip`, `BDA_alimenti.xlsx` e `crea_cache.zip` servono solo per ampliare il database
(M6), ma arrivano con lo stesso comando e il collaudo li verifica.

**Una sola copia di tutto.** Ogni file esiste una volta sola, in `motore-calcolo`. Non
reintrodurre zip né copie parallele.

**Salvare una modifica.** La salva Claude con un commit, dalle sessioni del progetto di
consolidamento con il repository collegato: `git clone`, modifica, collaudo e regressione,
commit e push, poi comando d'avvio e nuovo collaudo. Il nutrizionista non carica niente a
mano. `git log` è il registro delle versioni; ogni modifica è annullabile.
Ripiego solo senza collegamento: caricamento manuale dalla pagina di upload della
cartella, poi verifica delle impronte.

**Sessioni lunghe.** La copia estratta all'avvio invecchia in silenzio: oltre una giornata
di lavoro, riscarica e ricollauda prima di fidarti dei numeri.

---

## 2. MODULI SOFTWARE

### collaudo.py — certificato di inizio sessione
Otto controlli:
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
   `alimenti.csv`, unità e tolleranze valide
8. ogni `food_id` ha un ruolo ammesso in `ruoli_alimenti.csv`; le regole di
   `accoppiamenti_vietati.csv` usano voci valide (ruoli o `food_id`); nessun blocco della
   libreria (`moduli_pasto.csv`, `moduli_colazione.csv`) contiene un accoppiamento vietato

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

Prima del PASSO 1 si ferma (bloccante) su un `food_id` sconosciuto o su un valore di pasto
non ammesso (`PASTO_NON_AMMESSO`, es. `spuntino 2` con lo spazio).
```
python3 pipeline.py --piano piano.csv --target target.csv
  [--farmaci f.csv --interazioni i.csv --orari o.csv]
  [--deroga-struttura "motivo"] [--salta-collaudo]
```
Esce 0 senza rilievi bloccanti, 1 altrimenti; il report si stampa per intero in entrambi i
casi.

**Rilievi BLOCCANTI** (piano non presentabile): collaudo fallito o assente; `food_id`
sconosciuto; valore di pasto non ammesso; **media settimanale delle kcal** fuori tolleranza
(basta un estremo dell'intervallo); **media settimanale di un macro** fuori tolleranza su
tutto l'intervallo, dallo stesso lato; **giorno o scenario oltre ±10% di kcal**; target incoerenti; file dei formati o
degli accoppiamenti illeggibili o accoppiamenti non verificati; interazione di gravità ALTA;
orario di un pasto mancante; terapia dichiarata solo in parte; struttura pasti non uniforme;
livelli colazione/spuntino misti o incoerenti tra pasti; catalogo disallineato.

**Rilievi DA DICHIARARE** (non bloccano): giorno con kcal fuori ±5% (entro ±10%) o macro
fuori ±5 punti; scenario di scelta fuori tolleranza entro ±10%; estremi macro degli scenari
(limiti di garanzia, non giornate componibili); un solo estremo della media settimanale
di un macro fuori tolleranza; fibra sotto l'80% del target;
micronutrienti sotto l'80% LARN *in media settimanale* (con o senza gap); target privo di
LARN (micronutrienti non confrontati con niente); distribuzione concentrata; falsi positivi
Atwater; micronutrienti tutti a zero; quantità fuori formato; accoppiamenti vietati;
interazioni di gravità media o bassa (entrambe sotto il codice `INTERAZIONE_GRAVITA_MEDIA`);
principi attivi assenti dalla tabella; terapia non dichiarata; pasto assente su tutto il
piano; livello parziale o fuori catalogo; catalogo assente (livello verificato solo come
uniforme); collaudo saltato. I totali sottostimati per gap si stampano nel report.

Ogni rilievo porta un CODICE stabile: la suite congela `(passo, codice)`, non la prosa.

**Micronutrienti — giudizio settimanale (principio 8).** I valori di micronutrienti del
singolo giorno restano stampati senza allarme; il PASSO 2 riporta gli estremi dei
micronutrienti per giorno come informazione, non come verdetto.

**PASSO 6, due verifiche distinte:**
- (a) colazione e spuntino identici su tutti i giorni strutturati;
- (b) a quale livello appartengono, confrontandoli con `colazioni_spuntini.csv`: intercetta
  una colazione standard con uno spuntino rinforzato, che la (a) lascia passare.
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
Suite sui 17 casi golden in `golden/`: un comando, pass/fail per caso. Si riesegue **dopo
ogni modifica** al motore o al database, e comunque prima di qualsiasi uso clinico.
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
pasti e farmaci. Nessuna conoscenza farmacologica propria, nessuna interazione inventata:
segnala esplicitamente i principi attivi assenti dalla tabella, perché l'assenza di
allarme non sia scambiata per assenza di rischio.

### formati.py
Regola anti-spreco (nucleo, sezione 5). Legge `formati_confezione.csv` e
`scambi_frutta.csv`. Al PASSO 4, controllo E: per ogni alimento vincolato verifica che i
grammi siano una confezione intera o un multiplo (fino a 6) entro la tolleranza. Esito:
`FORMATO_CONFEZIONE_NON_RISPETTATO`, **non bloccante**. Funzioni: `carica_formati`,
`carica_scambi_frutta`, `controlla_piano(piano, formati)`, `quantita_valida`. Controllo
senza pipeline (chat B), stampa `[]` se tutto è a formato:
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
colazioni/spuntini), ricalcolando i valori da `alimenti.csv` e marcando i nutrienti
sottostimati da `gap.csv`.
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
Testato solo contro P00, paziente fittizio (2040 kcal, coincidente):
`python3 tdee.py` rifà il confronto e fallisce con `assert` se la formula cambia. Il valore
è SEMPRE da confermare dal nutrizionista: il modulo propone, non decide.
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
    --out-py piano_Cognome_vN.py --out-pdf piano_Cognome_vN.pdf
    [--orari orari_pasti.csv] [--mese "Settembre 2026"]
python3 genera_zona_piano.py --autotest --template TEMPLATE_..._v5.py
```
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
- **Si ferma, nominando il problema**, se manca un campo dei metadati o un titolo di piatto,
  se un `food_id` non ha nome paziente, se i giorni di `piano.csv` non coincidono con quelli
  dichiarati, o se un pasto mescola alimenti fissi e alternative.
- `--autotest` genera il caso golden 03 con metadati fittizi e verifica: kcal uguali al
  calcolatore, motore grafico identico al template, PDF senza segnaposto, abbinamento
  risolto in lettere, fermo su metadato mancante. Scrive solo in una cartella temporanea:
  non sporca i checksum.

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
  attenzione `FORMATO_CONFEZIONE_NON_RISPETTATO`, non bloccante. I casi 05-07 la
  contengono anch'essi, perché i loro input di test non seguono i formati commerciali.
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

**Tipi di caso.** `fisso` e `scelta_multipla` si deducono dal piano (presenza di
`gruppo_scelta`). `pipeline` è l'unico DICHIARATO, da un `pipeline.json` nella cartella del
caso, che porta anche le opzioni di esecuzione (es. `deroga_struttura`). I casi `pipeline`
congelano i VERDETTI (passo, codice del rilievo, codice di uscita), non i numeri.

**Limite di copertura.** I casi toccano solo gli alimenti dei rispettivi piani: una
modifica ai valori di carni e pesci non presenti passa la suite. La intercetta il controllo
5 del collaudo, non la regressione.

Una regola nuova si verifica anche al contrario: togliendola, la suite deve diventare rossa
sul caso che la sorveglia. Un errore di un caso reale che il motore non ha intercettato
diventa un nuovo caso golden.

---

## 4. DATABASE ALIMENTI E GERARCHIA FONTI

**Stato:** 144 alimenti verificati e tracciati alla fonte; il numero vincolante è
`EXPECTED_ALIMENTI_COUNT` in `collaudo.py`. Conformità kcal/macro/fibra a CREA:
`python3 cerca_crea.py verifica`.

**Criterio «Key Foods»:** un alimento si aggiunge solo quando un piano reale lo richiede e
non è già presente. Oltre le 150 voci solo su richiesta esplicita del nutrizionista.

**Gerarchia fonti — congelata, non riaprire:**
1. **CREA eTCA 2019** (alimentinutrizione.it) — kcal, macronutrienti, fibra, minerali. Le
   kcal si LEGGONO da CREA, mai ricalcolate con 4/4/9 (CREA usa il metodo Southgate, scarto
   fisiologico noto del 4-8% rispetto ad Atwater).
2. **BDA-IEO** — vitamina D, folati, B12 e minerali non coperti da CREA. Quando
   l'alimento non ha scheda CREA, anche kcal e macro vengono da BDA-IEO (oggi 86 voci con
   fonte `BDA-IEO` o `BDA-IEO+USDA`).
3. **USDA FoodData Central** — residuale, quando le prime due tacciono. Mai per le kcal.

**Eccezione INSA** (tabella nazionale portoghese, Base de Dados da Composição de Alimentos,
INSA, v 7.1 – 2026; citazione della fonte obbligatoria per licenza). SOLO per decisione del
nutrizionista, voce per voce, quando le tre fonti sono incoerenti tra loro e INSA ha la
stessa specie e lo stesso stato (crudo/cotto). Mai per kcal e macro, che restano CREA. In
`fonte` si scrive `INSA(...)`, in `codice_fonte` `INSA<cod>`. Righe in eccezione: 122800
sardine (micronutrienti).

**Eccezione etichetta — regola generale ancora da scrivere.** `ETI001` (vellutata
surgelata zucca e carote) ha TUTTI i valori, kcal comprese, da un'etichetta, per decisione
del nutrizionista del 17/10/2026; i micronutrienti sono gap. È l'unica voce che non viene
da CREA, BDA-IEO, USDA o INSA: non estendere ad altre voci finché la regola non è decisa.

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
quelle stanno nella libreria.

**Libreria degli accoppiamenti** — `moduli_pasto.csv` (128 blocchi pranzo/cena) e
`moduli_colazione.csv` (55 blocchi colazione | spuntino), schema
`modulo_id, nome, categoria, tag, ingredienti_food_id_grammi`. Tag pranzo/cena: halal_ok ·
mensa_ok · vegetariano · legumi · pesce · carne · vitD · calcio · pratico · leggero.
**Limite:** vitD, calcio, mensa_ok, pratico e leggero sono assegnati solo nei blocchi
M02-M24; da M25 i tag sono solo quelli ricavati dai ruoli (halal_ok, vegetariano, legumi,
pesce, carne). Un filtro su quei cinque tag ignora M25-M129 senza avvisare. Tag
colazioni/spuntini: dolce · salata · halal_ok · vegetariano · carne.
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

**Stato (verificato sul file il 21/10/2026):** 16 righe su 5 alimenti — latte parzialmente
scremato (vitamina D, B12), orata (vitamina D), salmone affumicato (vitamina D), trippa
(vitamina D, B12, folati, zinco), vellutata surgelata `ETI001` (tutti gli 8
micronutrienti: eccezione etichetta, il cartellino UE non li dichiara).

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
12% relativo **sia** 8 kcal/100 g in assoluto. Falsi positivi noti, attesi:
- **AGLIO** (`005000`) — atteso -15,5%, scarto 8,20 kcal: appena sopra soglia;
- **CARCIOFI** (`005120`) — atteso -31,5%, scarto 10,4 kcal: Southgate conta la fibra; kcal
  e macro coincidono con la scheda CREA;
- **SEMI DI LINO** (`9600_1`) — atteso -15,7%, scarto 70 kcal: BDA-IEO calcola l'energia
  «con fibra».
Uno di questi con scarto diverso da quello atteso non è più il falso positivo noto: va
verificato come un segnalato nuovo.
Non correggere il dato: dichiara il falso positivo e prosegui. Un NUOVO segnalato dopo un
ampliamento si verifica uno a uno: non si alza la soglia per farlo sparire.

**Sardine, riga unica 122800.** «Sarda fresca» (BDA 1319) NON esiste più come voce
separata. Kcal e macro CREA; TUTTI i micronutrienti da INSA 882 «Sardinha gorda crua»
(decisione del nutrizionista). Limite dichiarato: sardina atlantica (Portogallo); la
vitamina D dei pesci varia per stagione e zona.

---

## 9. STATO DI VALIDAZIONE

Il motore è validato contro un piano reale già consegnato (P01, lunedì: -4,56% dopo la
correzione della regola sui legumi), oggi `caso_01_base`: la validazione è ripetibile. È
utilizzabile su pazienti reali alle condizioni del principio 7.

**Validazione sul campo ancora aperta (FASE 5):** orchestratore e protocollo struttura
pasti sono validati su paziente fittizio e su casi reali, `tdee.py` solo sul paziente
fittizio; il primo ha già fatto
emergere due errori di processo. Il flusso del 21/10/2026 (motore sciolto, salvataggio con
commit, accoppiamenti) non è ancora passato da un caso reale. Criterio di chiusura: tre
pazienti reali consecutivi senza errori di processo. Ogni caso reale è
anche un collaudo: cosa il motore ha intercettato da solo, cosa ha richiesto un intervento
manuale, cosa è sfuggito. Quello che sfugge diventa un caso golden.
