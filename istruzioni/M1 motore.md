# M1 — MOTORE DI CALCOLO

Modulo operativo (principio 6: nucleo + moduli sono l'unica fonte operativa).
Dipendenze: nessuna. Dipendono da questo modulo: M2 (workflow piano), M6 (estrazione).
Ultimo aggiornamento: 29/07/2026.

Questo modulo copre: come si avvia una sessione di calcolo, i moduli software, i casi
golden, il database alimenti e la gerarchia fonti, lo schema CSV congelato, i file
affiancati, i gap dichiarati, il recupero USDA e lo stato di validazione.
NON copre: come si compone un piano (M2), come si allarga il database (M6).

---

## 1. AVVIO DI SESSIONE — obbligatorio prima di qualsiasi calcolo

All'inizio di ogni sessione che coinvolge calcoli:

1. Scarica ed estrai `motore calcolo.zip` in una cartella **pulita**
   (il `%20` nel link è uno spazio nel nome, è corretto così):
   `https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/motore-calcolo/motore%20calcolo.zip`
2. Scarica `alimenti.csv` accanto ai moduli (sta **fuori** dallo zip, stessa cartella
   su GitHub). Serve sempre, in ogni sessione di calcolo.
3. Esegui `collaudo.py`. Nessun calcolo su paziente prima dell'esito positivo
   (principio 7).

`cache.zip` e `BDA_alimenti.xlsx` servono **solo** per ampliare il database (M6), non
per calcolare un piano.

**Convenzione:** il CODICE sta dentro lo zip, i DATI stanno fuori. Non tenere copie
sciolte dei `.py` nel repository: due copie divergono in silenzio. Non è teorico — il
28/07/2026 sono state eliminate quattro copie sciolte obsolete, divergenti dallo zip
da tre fasi; il `gap.csv` sciolto aveva 67 righe contro 8, cioè dichiarava come
mancanti dei dati già recuperati.

**Legame zip ↔ database.** `SHA256SUMS` sta dentro lo zip ma firma anche
`alimenti.csv`, che sta fuori. Quando il database cresce servono quindi DUE
caricamenti: `alimenti.csv` sciolto e lo zip (che contiene checksum aggiornati e
`EXPECTED_ALIMENTI_COUNT`). Caricarne uno solo fa fallire il collaudo alla sessione
successiva — fallisce correttamente, ma fallisce. È il prezzo del quinto controllo.

**Sessioni lunghe.** Una chat che ha scaricato il motore all'inizio continua a
lavorare sulla copia estratta allora, che invecchia in silenzio. Oltre una giornata di
lavoro: riscarica e riesegui il collaudo prima di fidarti dei numeri.

---

## 2. MODULI SOFTWARE

### collaudo.py — certificato di inizio sessione
Cinque controlli:
1. presenza e integrità di tutti i CSV, incluso il numero di colonne per riga
   (`csv.DictReader` da solo NON lo segnala)
2. conteggio righe di `alimenti.csv` contro `EXPECTED_ALIMENTI_COUNT`
3. assenza di `food_id` duplicati
4. giornata golden confrontata al riferimento congelato
5. integrità byte per byte contro `SHA256SUMS`

Esce con codice 0 (superato) o 1 (fallito).

*Perché il controllo 5:* i primi quattro non vedono una modifica che resta
sintatticamente valida. Verificato il 28/07/2026 cambiando il calcio del pane integrale
da 25 a 26 mg — conteggio giusto, nessun duplicato, giornata golden identica (usa
`alimenti_test.csv`), tutto verde. Solo il quinto se ne accorgeva.

*File opzionali* (`cache.zip`, `BDA_alimenti.xlsx`): se presenti vengono verificati come
gli altri, se assenti il collaudo lo dichiara e prosegue. Richiederli sempre farebbe
fallire il collaudo di routine, e un collaudo che fallisce di routine smette di essere
letto.

`python3 collaudo.py --genera-checksums` riscrive `SHA256SUMS`. Si usa dopo aver
aggiornato `alimenti.csv` o un modulo, e **solo dopo aver capito perché** il file era
cambiato: un ampliamento legittimo non ancora registrato e una corruzione silenziosa si
presentano allo stesso modo. Rigenerare per far tornare verde un collaudo rosso annulla
il controllo.

Attenzione: firma **tutto** ciò che si trova nella cartella. Un file appoggiato lì per
una verifica finisce nei checksum e fa fallire il collaudo alla sessione dopo, quando
non c'è più. Estrai sempre in una cartella pulita e riesegui il collaudo prima di
consegnare lo zip.

`EXPECTED_ALIMENTI_COUNT` va aggiornato a mano quando il database cresce.
Il formato di `SHA256SUMS` è standard: verificabile anche con `sha256sum -c SHA256SUMS`.

### pipeline.py — orchestratore, il modo raccomandato di valutare un piano
Un comando esegue i passi sempre nello stesso ordine e produce un report unico:

0. collaudo (si ferma se fallisce)
1. calcolo per pasto e per giorno
2. scenari min/max dei pasti a scelta multipla, PRIMA di ogni riepilogo
3. micronutrienti per giorno e media settimanale, con flag LARN e gap
4. coerenza dei dati + gap dichiarati
5. interazioni farmaco-alimento
6. livello unico di colazione e spuntino su tutto il piano

```
python3 pipeline.py --piano piano.csv --target target.csv
  [--farmaci f.csv --interazioni i.csv --orari o.csv]
  [--deroga-struttura "motivo"] [--salta-collaudo]
```

Esce 0 se non ci sono rilievi bloccanti, 1 altrimenti. Il report viene stampato per
intero in entrambi i casi: serve a capire cosa correggere.

*Perché esiste:* l'ordine dei passi era imposto per convenzione e viveva nelle
istruzioni, non nel software. Entrambi gli errori di processo del primo caso reale sono
nati da lì.

**Rilievi BLOCCANTI** (piano non presentabile): kcal o macro fuori tolleranza, uno
scenario di scelta fuori tolleranza sulle kcal, target incoerenti, interazione di
gravità ALTA, orario pasto mancante, terapia dichiarata solo in parte, struttura pasti
non uniforme, livelli colazione/spuntino incoerenti.

**Rilievi DA DICHIARARE** (non bloccano): micronutrienti sotto l'80% LARN *in media
settimanale*, distribuzione concentrata, gap dichiarati, falsi positivi Atwater,
interazioni di gravità media, estremi macro degli scenari di scelta (sono limiti di
garanzia, non giornate componibili), alternative fuori catalogo.

Ogni rilievo porta un CODICE stabile oltre al messaggio: la suite di regressione congela
`(passo, codice)` e non la prosa, così riformulare un messaggio non fa diventare rossa
la suite.

**Micronutrienti:** dal 29/07/2026 il giudizio è settimanale (principio 8). I valori per
singolo giorno restano stampati ma non portano più allarme. Il PASSO 2 riporta gli
estremi per giorno come informazione, non come verdetto.

**Il PASSO 6 fa due verifiche distinte:**
- (a) colazione e spuntino identici su tutti i giorni strutturati
- (b) a quale livello appartengono, confrontandoli con `colazioni_spuntini.csv`

La (b) intercetta una colazione standard abbinata a uno spuntino rinforzato: i giorni
sono tutti uguali tra loro, quindi la (a) da sola la lascia passare. Se il piano usa
alternative costruite su misura non è un errore: viene segnalato come fuori catalogo e
il livello non è verificabile.

`--deroga-struttura "motivo"` declassa i blocchi del PASSO 6 ad attenzione, per le
deroghe legittime (spuntino saltato, giorno libero). Il rilievo resta scritto nel report
con il motivo dichiarato.

### regressione.py
Suite sui casi golden in `golden/`. Va rieseguita **dopo ogni modifica** al motore o al
database alimenti, e comunque prima di qualsiasi uso clinico. Un comando, esito
pass/fail per caso.

`python3 regressione.py --genera` rigenera gli attesi: si usa SOLO quando una modifica
cambia intenzionalmente i risultati e il nuovo output è già stato verificato a mano.
Rigenerare per far passare una suite rossa senza aver capito perché era rossa annulla lo
scopo della suite.

Non è una validazione clinica: verifica che il motore produca gli stessi numeri su input
fissi, non che quei numeri siano giusti per un paziente.

### calcolatore.py
Totali per pasto e per giorno, confronto con i target, flag LARN sui micronutrienti.
Legge anche `gap.csv` e marca come SOTTOSTIMATI i totali che pescano da voci con dati
mancanti. È il modulo principale.

### interazioni.py
Incrocia la tabella interazioni — curata e validata dal nutrizionista — con gli orari di
pasti e farmaci. Il motore NON contiene conoscenza farmacologica propria e non inventa
interazioni: segnala esplicitamente i principi attivi assenti dalla tabella, così che
l'assenza di allarme non venga scambiata per assenza di rischio.

### coerenza.py
Cross-check Atwater, coerenza interna dei target, righe con micronutrienti tutti a zero.
Intercetta errori nei DATI prima che si propaghino nei piani. Non ha entry point
standalone: si importa. Vedi §7 per il doppio criterio Atwater.

### scelte_multiple.py
Intervalli min/max per nutriente sui pasti a scelta. Sono limiti garantiti, non una
giornata realmente componibile. Distingue ciò che è sotto soglia anche nel best case da
ciò che dipende dalla scelta del paziente.
Va eseguito per OGNI giorno del piano subito dopo aver fissato pranzo e cena di quel
giorno — non a posteriori, dopo aver già presentato una tabella con una singola
combinazione "esemplare". `pipeline.py` lo fa da solo, al PASSO 2.

### struttura_pasti.py
Legge `colazioni_spuntini.csv` e riconosce il livello di un piano.
`python3 struttura_pasti.py` ristampa il catalogo con i valori RICALCOLATI da
`alimenti.csv`: serve a leggerlo a occhio senza che i numeri possano divergere dalla
fonte. Segnala anche se le 4 colazioni di un livello hanno kcal troppo distanti tra loro.

### moduli_pasto.py
Legge `moduli_pasto.csv`, la libreria dei 24 blocchi pranzo/cena, ricalcolando i valori
da `alimenti.csv` e marcando i nutrienti sottostimati da `gap.csv`.

```
python3 moduli_pasto.py                     tutta la libreria
python3 moduli_pasto.py --categoria cena    solo le cene
python3 moduli_pasto.py --tag pesce vitD    blocchi con TUTTI i tag
python3 moduli_pasto.py --scala M07 1.15    grammature riscalate del 15%
```

Il flag ⛔ sui gap serve a non far scartare un blocco per la ragione sbagliata: l'orata
mostra vitamina D 0.00 perché CREA non la pubblica, non perché non ne contenga.

### cerca_cache.py
Interroga la cache BDA-IEO. Traduce in comando il PASSO 4 del protocollo di estrazione
(M6), che prima era una procedura a memoria.

```
python3 cerca_cache.py ricerca "sgombro" "farro" "kefir"
python3 cerca_cache.py ricerca --file nomi.txt
python3 cerca_cache.py estrai 1321_2
```

La ricerca interroga l'indice `_foods.json` in un solo passaggio su tutti i nomi e dice
quali mancano davvero. L'estrazione riporta i nutrienti dello schema con la fonte citata
per ciascuno, applicando le regole del protocollo: "tr" diventa il valore di soglia
(`vltraccia`) e non zero, un campo assente viene dichiarato come DA CERCARE SU USDA e non
lasciato a zero in silenzio. Energia e macronutrienti non vengono proposti: per quelli la
fonte è CREA. Non scrive niente in `alimenti.csv`: riporta, la trascrizione resta una
scelta.

### Estensione ancora su Drive — tdee.py
`Drive > Motore di calcolo > tdee.py`. Stima TDEE e propone un `target.csv` di partenza
da peso/altezza/età/sesso/livello di attività (Mifflin-St Jeor + PAL). Testato solo
contro il TDEE di Vittorio Taglialatela, paziente fittizio (2040 kcal, coincidente). Il
valore resta SEMPRE da confermare dal nutrizionista: il modulo propone, non decide.
È l'ultima cosa tecnica rimasta su Drive: andrebbe migrata nello zip.

---

## 3. CASI GOLDEN

Cartella `golden/` dentro lo zip. Ogni caso è una sottocartella con `piano.csv`,
`target.csv`, `atteso.json`. `atteso.json` contiene i valori attesi più due campi di
documentazione: `descrizione` (cosa copre il caso) e `riferimento` (come è stato validato).

- **caso_01_base** — giornata validata contro il collaudo archiviato del 26/07/2026,
  riprodotta al decimale su tutti e quattro i pasti. Copre legumi lessati a peso cotto e
  pesce a peso crudo.
- **caso_02_legumi_inscatolati** — legumi in scatola, pesce in scatola e olive a peso
  netto nella stessa giornata; esercita anche il percorso "macro fuori tolleranza".
- **caso_03_scelta_colazione_spuntino** — colazione e spuntino a scelta multipla (2
  alternative ciascuno), pranzo e cena fissi. Verifica minimo/massimo per nutriente
  prodotti da `scelte_multiple.py`, non solo i totali a combinazione fissa.
- **caso_04_limite_tolleranza** — target tarati a ridosso del confine ±5 punti
  percentuali (scarti di +4.999/+5.001), non un piano realistico. Limite noto dichiarato
  nel caso stesso: non distingue un confine incluso da uno escluso scritto male
  esattamente a scarto = 5.000.
- **caso_05_livelli_colazione_misti** — piano a 2 giorni con colazioni diverse tra loro.
  Entrambi i giorni sono deliberatamente dentro tolleranza su kcal (-4,56% e -2,03%) e su
  tutti e tre i macro: è il punto del caso. Un piano che supera ogni controllo numerico e
  viene fermato solo dalla regola strutturale del PASSO 6.
- **caso_06_livelli_incoerenti_tra_pasti** — le 4 colazioni del livello standard con i 2
  spuntini del rinforzato. I due giorni sono identici tra loro, quindi il controllo di
  uniformità li dichiara conformi: solo il riconoscimento del livello vede l'incoerenza.
- **caso_07_micro_basso_giorno_ok_settimana** — calcio al 65% LARN sul giorno 1 e all'85%
  in media settimanale. NESSUN rilievo deve comparire, exit code 0: protegge il principio
  8. Complementare al caso_06 — quello sorveglia i flag per giorno del PASSO 2, questo
  quelli del PASSO 3.

**Tipi di caso.** `fisso` e `scelta_multipla` sono dedotti dal piano (presenza di
`gruppo_scelta`), così il tipo non può disallinearsi da cosa il piano contiene davvero.
`pipeline` è l'unico DICHIARATO, dalla presenza di un `pipeline.json` nella cartella del
caso (che porta anche le opzioni di esecuzione, es. `deroga_struttura`): dallo stesso
`piano.csv` non si distingue un caso di calcolo da uno di orchestrazione. I casi
`pipeline` congelano i VERDETTI dell'orchestratore — passo, codice del rilievo, codice di
uscita — non i numeri, già coperti dai casi 01-04.

**Copertura reale — limite noto.** I casi coprono pesi, scelta multipla, soglia di
tolleranza, struttura pasti e lettura settimanale dei micronutrienti, ma toccano solo gli
alimenti dei rispettivi piani. Carni e pesci diversi non sono coperti: una modifica ai
loro valori passa la suite senza che nulla la intercetti — è il controllo 5 di
`collaudo.py` a intercettarla, non la regressione. Verificato il 28/07/2026, quando
l'aggiornamento della vitamina D di branzino, gambero, maiale e vitello ha lasciato la
suite verde senza rigenerazione.

Quando un caso reale fa emergere un errore che il motore non ha intercettato, quell'errore
diventa un nuovo caso golden.

---

## 4. DATABASE ALIMENTI E GERARCHIA FONTI

**Stato:** 122 alimenti verificati e tracciati alla fonte (verificato su GitHub il
29/07/2026, nessun `food_id` duplicato).

**Criterio di ampliamento "Key Foods":** un alimento si aggiunge solo quando un piano
reale lo richiede e non è già presente. Oltre le 150 voci solo su richiesta esplicita del
nutrizionista.

**Gerarchia fonti — congelata, non riaprire:**
1. **CREA eTCA 2019** (alimentinutrizione.it) — kcal, macronutrienti, fibra, minerali.
   Le kcal si LEGGONO da CREA, mai ricalcolate con 4/4/9: CREA usa il metodo Southgate,
   con scarto fisiologico noto del 4-8% rispetto ad Atwater.
2. **BDA-IEO** — vitamina D, folati, B12 e minerali non coperti da CREA.
3. **USDA FoodData Central** — solo residuale, quando le prime due tacciono. Mai per le
   kcal.

**Il terzo livello va usato davvero.** CREA non pubblica calcio, ferro, vitamina D, folati
e B12 per pesci e carni. Fermarsi al livello 1 lascia quei campi a zero, e uno zero da
dato mancante si comporta esattamente come uno zero biologico: abbassa il totale e produce
un falso allarme di carenza. Quando una fonte tace su un campo si scende di livello —
sempre, non solo quando conviene. Prima di dichiarare un gap, interroga la cache con
`cerca_cache.py`: fermarsi al livello 1 e scrivere "gap" è l'errore più comune, ed è già
costato una lettura falsata del magnesio.

**Tolleranze:** ±5% su kcal totali · ±5 punti percentuali sui macronutrienti.

---

## 5. SCHEMA CSV — CONGELATO, non modificare le colonne

**alimenti.csv**
`food_id, nome, categoria, fonte, codice_fonte, data_verifica, kcal_100g, proteine_g,
carboidrati_g, grassi_g, fibra_g, calcio_mg, ferro_mg, vitamina_d_ug, folati_ug,
vitamina_b12_ug, zinco_mg, magnesio_mg, vitamina_c_mg`
(tutti i valori per 100 g di parte edibile)

**piano.csv**
`giorno, pasto, food_id, grammi` [+ `gruppo_scelta, opzione` — opzionali]
pasti ammessi: `colazione | pranzo | spuntino | cena`

**target.csv** — `parametro, valore`
**farmaci_paziente.csv** — `principio_attivo, nome_commerciale, orario_assunzione, note`
**interazioni.csv** — `principio_attivo, tipo_target, target, meccanismo, separazione_ore, gravita`
**orari_pasti.csv** — `giorno, pasto, orario (HH:MM)`

### File affiancati — non fanno parte dello schema congelato
Serve un dato nuovo? Va in un file affiancato, mai in una colonna nuova. Nessuno di questi
contiene valori nutrizionali precalcolati (principio 2).

**gap.csv** — `food_id, nome, nutriente, motivo`

**colazioni_spuntini.csv** — `alternativa_id, livello, tipo, ingredienti_food_id_grammi, nota`
Catalogo delle 4 colazioni + 2 spuntini nei due livelli, `standard` e `rinforzata_calcio`
(S1/S2/D1/D2 + SPA/SPB — Sr1/Sr2/Dr1/Dr2 + SPrA/SPrB). Per leggerlo:
`python3 struttura_pasti.py`.
*Perché dichiara solo gli ingredienti:* la prima versione portava i valori precalcolati, e
il 28/07/2026 il ricalcolo ha trovato 71 valori su 72 corretti e uno sbagliato:
l'alternativa S1 dichiarava 0,20 µg di vitamina D contro 2,10 reali — un fattore dieci sul
nutriente che è già il limite noto della dieta, e nella direzione che fa sembrare coperto
ciò che non lo è. Il dato a monte era sano: l'errore stava nel derivato.
*Livello di applicazione:* la scelta tra standard e rinforzato è UNA SOLA DECISIONE PER
L'INTERO PIANO SETTIMANALE, mai giorno per giorno (dettaglio clinico in M2).

**moduli_pasto.csv** — `modulo_id, nome, categoria, tag, ingredienti_food_id_grammi`
Libreria di 24 blocchi pranzo/cena riutilizzabili, con tag (halal_ok · mensa_ok ·
vegetariano · legumi · pesce · carne · vitD · calcio · pratico · leggero). Sono una BASE DI
PARTENZA da scalare, non un sostituto del calcolo caso per caso. Per leggerla:
`python3 moduli_pasto.py`.
*Perché anche questo dichiara solo gli ingredienti:* portava valori precalcolati fino al
29/07/2026, quando il ricalcolo ha trovato 165 valori su 168 corretti e tre sbagliati — la
vitamina D di M18, M20 e M22. NON erano errori di trascrizione: erano corretti il 27/07 e
sono diventati falsi il 28/07, quando la vitamina D di gambero e polpo è stata recuperata
da USDA. La fonte è migliorata sotto il derivato. È una via di divergenza più insidiosa di
quella di S1, perché non richiede alcun errore umano.
*Ampliamento:* stesso criterio Key Foods. Range utile a regime 20-30 blocchi; oltre, la
libreria diventa più lenta da consultare che ricostruire il pasto. Previa conferma del
nutrizionista.

---

## 6. GAP DICHIARATI

Lo schema congelato non sa rappresentare "dato non disponibile": un nutriente che la fonte
non pubblica finisce a 0 e viene sommato come assenza reale. `gap.csv` elenca le celle il
cui zero è un dato mancante. `calcolatore.py` lo legge e marca il totale con ⛔ TOTALE
SOTTOSTIMATO, elencando le voci responsabili.

Un valore sotto l'80% LARN accompagnato da quel flag NON è una carenza accertata: prima di
intervenire clinicamente, verifica se dipende dal gap.

**Stato attuale:** 8 righe su 4 alimenti — vitamina D (4: latte, orata, sardine, trippa),
vitamina B12 (2: latte, trippa), folati (1: trippa), zinco (1: trippa).
Il blocco magnesio (35 celle) è chiuso dal 28/07/2026 via USDA. Il gap calcio dell'olio
d'oliva è stato chiuso il 28/07/2026: CREA e BDA-IEO concordano su uno zero esplicito, non
un silenzio.

**Fave secche cotte — caso a parte:** minerali e folati presi dalla voce BDA delle fave
CRUDE (proxy), quindi probabilmente SOVRASTIMATI, non sottostimati. Non usarle come fonte
portante di ferro o folati.

Obiettivo del sistema: non "zero gap", ma **zero gap taciuti**.

---

## 7. RECUPERO USDA

**API key FoodData Central:** non è scritta qui. Questo modulo è pubblicato su un
repository pubblico: la chiave sta nel nucleo M0, che resta nelle istruzioni di progetto.
La `DEMO_KEY` pubblica ha 10 richieste/ora ed è quasi sempre esaurita: non usarla per un
blocco di gap.

Ogni valore recuperato: si scrive in `alimenti.csv` con fonte tracciata (es.
`CREA+BDA-IEO+USDA`), si rimuove la riga da `gap.csv`, si rieseguono collaudo e
regressione. Quello che nemmeno USDA copre resta in `gap.csv`.

### Verifica obbligatoria della derivazione — non saltarla
Un valore USDA non si accetta dal solo endpoint `/foods/search`: va controllato su
`/v1/food/{fdcId}`, campo `foodNutrientDerivation`.

- **codice Z "Assumed zero"** → NON è un dato, è un'assunzione. Non chiude il gap.
  Importarlo significa ereditare in silenzio lo zero di qualcun altro.
- **codice NC "Calculated"** → ricalcolato, non misurato. Mai per le kcal.
- **dataPoints: 0** → valore pubblicato senza campioni analitici a supporto. Utilizzabile
  (livello 3 residuale), ma va dichiarato come debole.

Il 28/07/2026 questo controllo ha evitato tre errori: cozza, polpo e trippa risultavano a
0,0 di vitamina D con derivazione Z e dataPoints 0.

### Valori USA non trasferibili — caso latte
Il latte USDA riporta vitamina D per effetto della fortificazione obbligatoria
statunitense, che il latte italiano standard non ha. Non importare quel valore:
maschererebbe la carenza strutturale di vitamina D che il piano deve dichiarare. Stessa
cautela per ogni alimento soggetto ad arricchimento obbligatorio negli USA (cereali da
colazione, farine, bevande vegetali, latti fermentati). La cache BDA-IEO distingue
esplicitamente FIOCCHI DI MAIS (CORNFLAKES) "non fortificati" dalla versione
"fortificati" — usare sempre la prima per prodotti italiani standard.

### Audit ancora da fare
I 35 valori di magnesio scritti il 28/07/2026 sono stati presi prima che la verifica di
derivazione diventasse regola. Essendo tutti non-zero, la trappola dello "zero assunto" non
li riguarda, ma alcuni potrebbero essere imputati anziché analitici: una passata di
controllo sui loro `fdcId` resta da fare.

---

## 8. CASI RISOLTI — non riaprire

**Falso positivo strutturale di coerenza.py.** Su alimenti molto ipocalorici il cross-check
Atwater sforava per puro effetto percentuale su numeri piccoli. Dal 28/07/2026 l'allarme
richiede il **doppio criterio** (>12% relativo E >8 kcal/100 g in assoluto).
Unico residuo atteso: **AGLIO** (53 kcal dichiarate vs 44,8 ricalcolate, -15,5%, scarto
assoluto 8,20 kcal — appena sopra soglia). Non correggere il dato: dichiara il falso
positivo e prosegui.
Se compaiono NUOVI segnalati con l'ampliamento del database, vanno verificati uno a uno:
non si alza la soglia per farli sparire.

**Voci unificate — sardine.** Esistevano due righe per lo stesso pesce, CREA 122800 (225
kcal, 15,4 g lipidi, ma calcio/ferro/vitD/folati/B12 a zero perché CREA non li pubblica) e
BDA 1319 "Sarda fresca" (129 kcal, 4,5 g lipidi, micronutrienti completi). Entrambe
corrette: la differenza è variabilità stagionale reale del tenore lipidico. Fuse in
un'unica riga 122800 secondo gerarchia — CREA per energia e macro, BDA per i micronutrienti
mancanti. "Sarda fresca" NON esiste più come voce separata. La vitamina D di questa riga
viene dal campione magro abbinato ai macro del campione grasso: essendo liposolubile è
probabilmente sottostimata, ed è dichiarata in `gap.csv`.

---

## 9. STATO DI VALIDAZIONE

Motore validato ricalcolando riga per riga un piano reale già consegnato (paziente Mattei,
Lunedì): totale giornata rientrato in tolleranza (-4,56%) dopo la correzione della regola
sui legumi. Collaudo archiviato su Drive in `Motore di calcolo >
Collaudo_Motore_PianoMattei_Lunedi`. Dal 28/07/2026 quella giornata è anche
`caso_01_base` della suite di regressione, riprodotta al decimale: la validazione è
ripetibile e non più un documento.

Il motore è utilizzabile su pazienti reali, alle condizioni del principio 7.

**Validazione sul campo ancora aperta:** orchestratore, protocollo struttura pasti e
`tdee.py` sono validati su paziente fittizio e su un solo caso reale, che ha già fatto
emergere due errori di processo. Ogni caso reale successivo va usato anche come collaudo:
cosa il motore ha intercettato da solo, cosa ha richiesto un intervento manuale, cosa è
sfuggito. Quello che sfugge diventa un caso golden.
