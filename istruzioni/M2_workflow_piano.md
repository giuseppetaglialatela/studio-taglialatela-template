# M2 — WORKFLOW PIANO ALIMENTARE

Modulo operativo: si carica quando si compone, si modifica o si valuta un piano.
Dipende da **M1**: nessun passo è eseguibile senza il motore collaudato.
Ultima modifica: 23/10/2026 (PASSO 6 con anteprima completa e impronta, metadati in bozza prima dell'approvazione, un giorno chiuso = una riga in chat; condimenti a porzione libera; `--nessuna-terapia`; 22/10:
distribuzione del solo calcio, avviso del livello rinforzato, fermi sui segnaposto). Motivazioni, episodi e date in
`istruzioni/archivio/M2-motivazioni.md`, che non si carica.

Rimandi: motore, CSV, gap, fonti → **M1** · PDF del piano e documento di spiegazione →
**M3** · fascicolo e Tabella Vincoli (PASSO 0) → **M4** · ampliamento del database →
**M6**. Se un documento d'archivio su Drive diverge, vale questo modulo (principio 6).

---

## 1. REGOLE PESI (ripetute per intero dal nucleo M0, sezione 5; se cambiano, cambiano in entrambi; il nucleo prevale)

Da leggere PRIMA di ogni calcolo: un errore qui invalida tutto ciò che segue.

**Pesi sempre a CRUDO**, con due sole eccezioni:
1. inscatolati e simili → **peso NETTO di confezione**;
2. legumi lessati cotti in casa (ceci, fagioli, lenticchie) → **peso COTTO**.

Carne e pesce SEMPRE a crudo, anche se il piatto è descritto cotto («merluzzo 140 g al
vapore» = 140 g crudi). Nel dubbio su una preparazione, CHIEDI prima di calcolare: non
dedurre dalla formulazione del piatto.

**Formati di confezione — nessuno spreco.** Fonte: `formati_confezione.csv`, nella cartella
del motore.
1. **Monoporzione o deperibile una volta aperto** (yogurt, fiocchi di latte, scatolame
   tranne i condimenti, uova): confezione intera o multiplo esatto del formato.
2. **A peso al banco** (affettati, formaggi, carne, pesce, pane): qualsiasi grammatura.
3. **Non deperibile o consumabile in famiglia** (pasta, riso, couscous, cereali, frutta
   secca, gallette, cioccolato, latte, olive) e **condimenti, sempre** (olio, pomodori
   pelati e passata, aceto…): porzione libera.
Assente dal CSV = porzione libera. Il controllo E del PASSO 4 di `pipeline.py` SEGNALA (non
blocca) le quantità fuori formato: si compone già a formato, e le segnalazioni residue si
dichiarano al PASSO 6. Formato nuovo: stato `da_confermare` finché il nutrizionista non lo
conferma. Il CSV converte un formato commerciale in grammi (es. «una scatoletta di tonno»,
«un vasetto di yogurt» → grammi in `piano.csv`), non è un dato nutrizionale: il dato resta
quello di `alimenti.csv`, già per 100 g di prodotto sgocciolato/edibile. Le percentuali di
sgocciolamento non tratte da CREA/BDA/USDA sono stime di mercato, non dati verificati.

**Foto di una confezione:** serve solo per il formato in grammi e la variante (intero o
scremato), che determina quale voce del database usare. I valori dell'etichetta NON
entrano nel database. Deroghe alle tre fonti: INSA, voce per voce su decisione del
nutrizionista e solo per i micronutrienti, mai per kcal e macro (M1, sezione 4); etichetta, SOLO su richiesta esplicita del nutrizionista e
per il singolo piano, con `--eccezione-etichetta` (M1, sezione 4), mai in `alimenti.csv`.
L'eccezione si dichiara nella tabella del PASSO 6.

**Scambio frutta:** nel piano la voce di riferimento (banana 100 g), le alternative a
parità di energia in `scambi_frutta.csv`. La tabella di scambio va nel documento di
spiegazione; le alternative non si calcolano come scenari uno per uno, e lo scarto (pochi
kcal e grammi) si dichiara.

---

## 2. STRUTTURA DEI PASTI

Protocollo di DEFAULT, derogabile caso per caso quando il fascicolo lo richiede
esplicitamente.

**COLAZIONE — 4 alternative fisse: 2 salate, 2 dolci**, con kcal tra loro il più vicine
possibile, così che la scelta del paziente non sposti il bilancio. Sono LE STESSE in tutti
i giorni strutturati: il paziente sceglie ogni giorno tra le stesse 4, non gli si assegna
una colazione per calendario.

**SPUNTINO — 2 alternative, legate alla colazione scelta (salata/dolce)**, fisse per tutta
la settimana. Il criterio di abbinamento (compensativo: salata→dolce, dolce→salato o
proteico; oppure in continuità: salata→salato, dolce→dolce) NON è fissato a priori: si
decide col nutrizionista caso per caso, in base al bilancio dei micronutrienti.

**SECONDO SPUNTINO — quinto pasto, facoltativo.** Fino a 5 pasti: colazione, spuntino,
pranzo, secondo spuntino, cena; in `piano.csv` si scrive `spuntino2`, e un pasto senza
righe non esiste in quel piano.
- Con il secondo spuntino, lo SPUNTINO è di metà mattina e il SECONDO SPUNTINO sta nel
  pomeriggio o prima di dormire; nei piani a 4 pasti lo spuntino resta del pomeriggio.
- Nel PDF: etichette SPUNTINO e SECONDO SPUNTINO, stessa icona; con gli orari, l'ordine
  dei pasti segue gli orari.
- Segue le regole dello spuntino: se c'è, è lo stesso in tutti i giorni strutturati
  (altrimenti il PASSO 6 della pipeline blocca, salvo deroga) e il suo livello si
  confronta con gli spuntini del catalogo.
- Spuntino fisso e secondo spuntino fisso: se presi dal catalogo danno `LIVELLO_PARZIALE`
  (il catalogo ne prevede 2 per livello), se costruiti su misura `LIVELLO_FUORI_CATALOGO`;
  in entrambi i casi si dichiara, non blocca.

**DEROGA:** spuntino saltato, allergia che esclude un'intera alternativa o altra
indicazione esplicita del paziente nel fascicolo: la deroga vince SEMPRE sul protocollo,
non si forza la struttura standard. Nel motore: `--deroga-struttura "motivo"`, il rilievo
resta nel report ma non blocca.

**Livello rinforzato.** `colazioni_spuntini.csv` (M1) ha due livelli, `standard` e
`rinforzata_calcio`. Il passaggio al rinforzato è **una sola decisione per l'intero piano
settimanale** (tutti i giorni strutturati), mai per il singolo giorno critico.
- **Quando valutarlo.** La pipeline dà l'avviso `VALUTARE_LIVELLO_RINFORZATO` (PASSO 6,
  mai bloccante: la scelta resta del nutrizionista) se **(a)** la media settimanale del
  calcio è sotto l'80% del LARN, oppure **(b)** il calcio è presente (almeno il 30% del
  LARN nel giorno) in meno di 3 giorni, su un piano di almeno 6 giorni. Nei giorni a
  scelta conta lo scenario MINIMO. Un solo giorno sotto l'80% non basta più.
- L'avviso tace se colazione e spuntino, quelli presenti nel piano, sono tutti del
  livello `rinforzata_calcio`, anche parziale (o rinforzati con alternative su misura
  accanto, caso già bloccato da `LIVELLO_MISTO`); il secondo spuntino non conta. Con il
  catalogo assente o disallineato l'avviso compare con una nota: il livello va verificato
  a mano. **Senza il LARN del calcio in `target.csv` né l'avviso né
  `DISTRIBUZIONE_CONCENTRATA` girano, e nessun rilievo lo dice**: verificare che ci sia.
- `MEDIA_SOTTO_LARN` (PASSO 3) guarda invece lo scenario MASSIMO (carenza anche nel caso
  migliore): le due letture sono diverse per scelta.
- Prima di passare al rinforzato, verificare che il calcio sotto soglia non sia marcato
  ⛔ TOTALE SOTTOSTIMATO: la carenza può essere apparente.
- NON si abbina la colazione di un livello con lo spuntino dell'altro: il PASSO 6 della
  pipeline lo blocca. Con `--deroga-struttura` diventa un'attenzione
  (`LIVELLO_INCOERENTE_IN_DEROGA`), ma la deroga di struttura non autorizza livelli misti:
  si correggono; restano solo su decisione esplicita del nutrizionista, motivata nella
  tabella del PASSO 6.

**Scenari di scelta — verifica obbligatoria.** Il paziente può scegliere ogni giorno una
qualsiasi delle 4 colazioni con lo spuntino abbinato: il piano NON è verificato finché non
sono calcolati, per OGNI giorno strutturato, tutti gli scenari possibili, non una sola
combinazione d'esempio (momento esatto: PASSO 2). Kcal e macro si giudicano comunque sulla
media settimanale (principio 8): il giorno fuori tolleranza si dichiara; blocca solo un
giorno o uno scenario oltre ±10% di kcal.

**Stato:** protocollo testato su paziente fittizio, non ancora attraversato per intero da
un paziente reale: da confermare o rivedere dopo il primo caso vero che lo percorre tutto.

---

## 3. I NOVE PASSI

Per ogni nuovo piano o modifica, IN QUESTO ORDINE. Con un fascicolo strutturato c'è prima
un **PASSO 0**: vedi M4.

### PASSO 1 — RICERCA SCIENTIFICA
Studi più recenti pertinenti al profilo clinico (patologie, farmaci, obiettivi). Sintetizza
i punti che influenzano il piano, comprese le evidenze che ridimensionano l'efficacia
attesa di una scelta già concordata (es. omega-3 vegetali vs marini): segnalale comunque,
anche dopo l'approvazione della scelta.

### PASSO 2 — CALCOLI (prima di qualsiasi bozza grafica)
Con il motore (M1), mai a mente, su grammature reali e con le regole pesi della sezione 1.
**Precondizione:** `collaudo.py` superato (principio 7).

**Modo raccomandato: `pipeline.py`**, che impone l'ordine dei passi e produce in un colpo
collaudo, calcoli, scenari, micronutrienti, coerenza, interazioni e livello colazione. I
moduli singoli servono ad approfondire un punto, ma l'ordine dei passi non si ricostruisce
a mano.

TDEE o target non concordati: proponili con `tdee.py`; la proposta va sempre confermata
dal nutrizionista prima di calcolare il piano.

**Libreria degli accoppiamenti.** Per OGNI pasto si parte dalla libreria quando esiste un
blocco compatibile con i vincoli del paziente: `moduli_pasto.csv` (pranzo/cena) e
`moduli_colazione.csv` (colazioni/spuntini), accoppiamenti già approvati in piani reali.
Si consulta con `python3 moduli_pasto.py --categoria ... --tag ...` (tag in M1, sezione 5).
Il blocco si riscala e si ricalcola nel piano del paziente, mai copiato tal quale. Un pasto
composto da zero, fuori libreria, passa comunque dal controllo degli accoppiamenti vietati
prima di essere presentato: `python3 accoppiamenti.py --piano piano_vN.csv`.

**Ordine obbligatorio per colazione e spuntino a scelta:** per ogni giorno, subito DOPO
aver fissato pranzo e cena e PRIMA di passare al giorno successivo, calcola tutti gli
scenari colazione+spuntino e guarda dove cadono rispetto alla tolleranza. Un giorno o uno
scenario fuori tolleranza NON si corregge d'ufficio: si corregge solo se la correzione è
naturale (porzione ragionevole, pasto che il paziente mangerebbe davvero); se servono
porzioni fuori scala o accostamenti forzati, si lascia e si DICHIARA in tabella. Non si
arriva al PASSO 6 avendo verificato una sola combinazione «esemplare» per giorno.
`pipeline.py` lo fa da solo, al suo PASSO 2, prima di ogni riepilogo.

**Produci:**
- kcal per ogni pasto e totale giornaliero, verificato pasto per pasto;
- macronutrienti in grammi E percentuale (proteine, carboidrati, grassi);
- fibre totali giornaliere, confrontate con il target del paziente;
- deficit calorico reale rispetto al TDEE;
- coerenza della % di grassi con il target del piano;
- assenza di ripetizioni degli ingredienti principali in giorni o pasti consecutivi.

**Segnalazione proattiva**, alla prima lettura e senza attendere domande: carichi
glicemici elevati · ripetizioni di ingredienti · scostamenti tra target dichiarati e
valori reali.

Calcoli che non tornano (totale ≠ somma dei pasti, macro incoerenti col target): segnala e
proponi la correzione PRIMA della tabella, **testandola sul motore prima di applicarla**
(principio 3: anche la direzione si verifica). Scostamenti minori entro tolleranza (es.
42% di carboidrati contro un target del 40% per la scarsa quota grassa di una proteina
magra): si dichiarano con la motivazione, non si correggono d'ufficio; decide il
nutrizionista.

**Tolleranze:** ±5% sulle kcal totali · ±5 punti percentuali sui macro, giudicate sulla
**media settimanale** (bloccante in `pipeline.py`). Il singolo giorno fuori tolleranza si
dichiara, purché le kcal del giorno e di ogni suo scenario restino entro **±10%** (limite
di sicurezza, bloccante).

Dati mancanti per TDEE o target: chiedili in blocco prima di procedere (nucleo, sezione
6), anche sui pazienti fittizi.

### PASSO 3 — MICRONUTRIENTI (sempre, prima dell'approvazione)
Calcio, ferro, vitamina D, folati (B9), vitamina B12, zinco, magnesio, vitamina C.
- **Giudizio sulla MEDIA SETTIMANALE** (principio 8): ⚠️ solo se la media è sotto l'80% del
  LARN.
- I valori per giorno si riportano SENZA allarme, per vedere la distribuzione, e non si
  correggono uno per uno: un micronutriente concentrato su pochi giorni (tipicamente la
  vitamina D con il pesce grasso) è basso sul giorno e adeguato sulla settimana, ed è
  normale.
- ⚠ anche se il **calcio** è presente in **meno di 3 giorni**, su un piano di almeno 6
  giorni, pur con media adeguata (`DISTRIBUZIONE_CONCENTRATA`): è l'unico caso in cui la
  distribuzione conta di per sé, per la saturazione dell'assorbimento (circa 500 mg per
  assunzione). «Presente» = almeno il 30% del LARN nel giorno; nei giorni a scelta conta lo
  scenario MINIMO. Vale SOLO per il calcio: gli altri micronutrienti concentrati su pochi
  giorni (vitamina D) non danno rilievo. Sotto i 6 giorni il motore non controlla: la
  distribuzione si guarda a mano sui valori per giorno.
- **Distingui carenza da gap:** un nutriente marcato ⛔ TOTALE SOTTOSTIMATO sotto soglia
  NON è una carenza accertata. Riporta il flag con il numero e le voci che lo causano;
  nessuna correzione del piano né integrazione su un nutriente sottostimato prima di aver
  verificato il gap.
- Con pasti a scelta, riporta gli scenari MINIMO e MASSIMO già calcolati al PASSO 2, senza
  ricalcolarli.
- **Non inseguire i numeri con gli alimenti:** prima di aggiungere un alimento per chiudere
  un micronutriente, verifica che il deficit sia reale (media settimanale, non giorno; e
  non marcato sottostimato). Un accostamento sgradito che il paziente salta peggiora il
  piano.
- **Verifica strutturale:** un vincolo farmacologico o una preferenza che limita
  strutturalmente un micronutriente (es. rifiuto del pesce → omega-3, vitamina D) è una
  carenza sistematica su tutto il piano: si segnala esplicitamente anche se già accettata
  dal nutrizionista come compromesso.
- **Vitamina D:** limite noto della dieta, non un difetto del piano; anche con pesce grasso
  3 volte a settimana la media resta intorno al 65-75% LARN. Si dichiara come carenza
  strutturale e la decisione clinica (sole o integrazione) resta al nutrizionista: non si
  forza il piano.

### PASSO 4 — INTERAZIONI FARMACO-ALIMENTO
Verifica SEMPRE, anche quando non mostri la tabella: interazioni note tra farmaci in
terapia e alimenti del piano; alimenti che riducono o potenziano l'assorbimento dei
farmaci; alimenti che interferiscono con micronutrienti già a rischio per la terapia.
Ogni criticità con ⚠️ e il **meccanismo**.

- Una separazione temporale imposta da un'interazione (es. levotiroxina lontano da calcio,
  ferro e caffè) si applica alla struttura dei pasti di OGNI giorno e si verifica giorno
  per giorno prima dell'approvazione: non resta solo in tabella.
- Una terapia dichiarata nel fascicolo si **TRADUCE nei tre CSV del motore**
  (`farmaci_paziente.csv`, `interazioni.csv`, `orari_pasti.csv`), non solo annotata nella
  Tabella Vincoli. Senza nessun file il PASSO 5 della pipeline dà
  `TERAPIA_NON_DICHIARATA` (attenzione: va confermato che il paziente non sia in
  terapia); con i file solo in parte blocca (`TERAPIA_INCOMPLETA`). Verificato che il
  paziente non assume farmaci, si esegue con `--nessuna-terapia "fonte"` (da dove viene la
  verifica: colloquio, Form A, con la data): al posto di `TERAPIA_NON_DICHIARATA` il
  verdetto riporta `TERAPIA_DICHIARATA_ASSENTE` con la fonte. Senza fonte, o insieme ai
  file di terapia, blocca (`TERAPIA_CONTRADDITTORIA`). L'assenza del file non
  è l'assenza di terapia, e un'osservazione discorsiva non è una verifica: con una terapia
  dichiarata nel fascicolo, `TERAPIA_NON_DICHIARATA` vale come bloccante e il piano non si
  presenta finché i tre CSV non arrivano alla pipeline. Senza terapia, la conferma si
  scrive nella tabella del PASSO 6.
- Il meccanismo in `interazioni.csv` deve corrispondere alla farmacologia reale del
  principio attivo: una separazione oraria vale per un'interazione di assorbimento
  sistemico, non per un farmaco ad azione locale sul contenuto gastrico. Una riga proposta
  e non validata dal nutrizionista si dichiara come tale.

**Riconoscimento dei farmaci — tre esiti**

| Esito | Comportamento |
|---|---|
| Riconosciuto | proponi il principio attivo, il nutrizionista conferma |
| Ambiguo | esponi le alternative con l'ipotesi più probabile, motivata dalla dose |
| Non riconosciuto | «farmaco non riconosciuto, verifica manuale», nessun vincolo derivato calcolato su di esso |

In tutti e tre i casi: un nome commerciale che non torna con il contesto clinico
(formulazione, via di somministrazione, setting di cura) → FERMATI e segnala prima di
proseguire, anche se dose e orario sembrano plausibili. Incertezza reale: banca dati AIFA.
Un dubbio con possibili conseguenze cliniche si dice esplicitamente: si chiede al paziente,
non si indovina.

**Tabella riepilogativa:** SOLO alla prima dieta del paziente o quando la terapia è
cambiata. Per le diete successive con farmaci invariati si verifica comunque, senza
ripetere la tabella salvo nuove criticità.

### PASSO 5 — CONFLITTI TRA VINCOLI
Gerarchia a 4 livelli (con fascicolo strutturato, M4):
- **Livello 0 — SICUREZZA.** Mai negoziabile, vince su tutto.
- **Livello 1 — NECESSITÀ CLINICA.** Si somma, non si esclude. Conflitti sullo stesso
  nutriente o timing: prima separazione temporale o spaziale; se non basta, il nodo si
  espone, mai deciso in automatico.
- **Livello 2 — FATTIBILITÀ OPERATIVA.** Si adatta intorno a 0 e 1, non li viola mai.
- **Livello 3 — PREFERENZE DEL PAZIENTE.** Le sole negoziabili; una preferenza non accolta
  si motiva sempre in tabella.

Nessun conflitto senza soluzione ovvia si risolve dietro le quinte: si espongono le
opzioni realistiche e si chiede.
**Estensione delle esclusioni:** un'esclusione dichiarata va letta nella sua estensione
reale, non massima (un rifiuto generico del «pesce» può riguardare solo quello azzurro):
chiedi la portata prima di escludere alimenti che il paziente non ha davvero rifiutato.

### PASSO 6 — PRESENTAZIONE PER APPROVAZIONE
Tutti i dati, in verdetto e anteprima, con analisi esplicita di punti di forza e criticità. **Attendi
approvazione esplicita.** Se `pipeline.py` esce con codice 1 il piano NON è presentabile:
risolvi i bloccanti e riesegui.

È il **gate** del nucleo: uno solo per piano, non uno per giorno. Nessun PDF prima di qui,
né con fretta dichiarata né con un piano identico a uno precedente.

**Cosa si presenta, in un solo messaggio** (primo piano reale, 23/10/2026: il
nutrizionista ha dovuto chiedere le grammature prima di approvare, e testi del giorno
libero e una regola operativa sono finiti nei metadati senza essergli mai mostrati):
1. verdetto e rilievi di `pipeline.py`, con punti di forza, criticità e l'elenco qui sotto;
2. l'**anteprima INTERA**, copiata così come la stampa lo script, senza riassunti né
   riformattazioni:
   ```
   python3 genera_zona_piano.py --anteprima --piano piano_vN.csv --target target.csv
       --metadati metadati_piano_vN.json [--orari orari_pasti.csv]
       [--eccezione-etichetta voci.csv --nomi-eccezione nomi.csv]
   ```
   Contiene i **testi del PDF** parola per parola (intestazione, obiettivo, criterio di
   rivalutazione, avvertenze, box target, indicazioni del giorno libero), i **contenuti
   del documento di spiegazione** (regole operative, scelte principali, limiti noti,
   contenuti da escludere: campi da cui la chat B scrive la prosa, mostrati anche se
   vuoti), gli **altri campi** dei metadati (TDEE confermato, giorni, abbinamento,
   livello colazione…) e il **piano per esteso** (tutti i giorni, tutti i pasti e le
   alternative, con titolo, grammatura, nota di peso e kcal; le alternative uguali in
   tutti i giorni si scrivono una volta in testa). Per questo i metadati si scrivono IN
   BOZZA PRIMA del PASSO 6, con tutti i testi: il nutrizionista li corregge
   sull'anteprima, non dopo. L'anteprima si FERMA se obiettivo, criterio o avvertenze
   mancano o sono segnaposto: si chiedono PRIMA, nelle domande in blocco all'apertura
   (nucleo, sezione 4), con i titoli dei piatti proposti. Se il piano usa
   `orari_pasti.csv`, l'anteprima va generata con `--orari`: gli orari compaiono nei
   pasti e cambiano l'impronta;
3. l'**impronta** stampata in fondo all'anteprima.

Ogni correzione chiesta (grammatura, titolo, testo) si fa in `piano.csv` o nei metadati,
poi si rieseguono pipeline e anteprima e si ripresenta l'anteprima con la nuova impronta:
si approva sempre l'ultima mostrata. **Dopo l'approvazione esplicita** si aggiunge ai
metadati `"impronta_approvata": "<impronta dell'anteprima approvata>"`. Da lì piano e
testi non si toccano: `genera_zona_piano.py` in chat B ricalcola l'impronta e si ferma se
manca o non coincide. Un testo per il paziente aggiunto dopo l'approvazione è una nuova
anteprima da approvare, mai una scrittura diretta nei metadati. Fuori dall'impronta solo i
riferimenti `drive` e il mese del PDF; dentro anche le kcal, quindi una voce del database
corretta tra approvazione e PDF ferma la chat B e l'anteprima si fa riapprovare. Limite:
l'impronta ferma la svista, non un'impronta rigenerata senza approvazione; il gate resta
una regola di questo modulo.

**Nel verdetto, nello stesso messaggio, non in un secondo giro:**
- obiettivo in intestazione e criterio di rivalutazione: se il fascicolo non li ha
  (es. `peso_obiettivo_concordato` = null) si sono chiesti nelle domande in blocco
  all'apertura e sono nella bozza dei metadati; la chat B non li inventa mai;
- le attenzioni `FORMATO_CONFEZIONE_NON_RISPETTATO`, con la motivazione;
- le attenzioni `ACCOPPIAMENTO_VIETATO`: non bloccano, ma un accoppiamento vietato rimasto
  nel piano va motivato, non lasciato passare in silenzio;
- l'eccezione etichetta, se usata (`ALIMENTO_FUORI_DATABASE_SU_RICHIESTA`);
- la conferma che il paziente non è in terapia, con la sua fonte
  (`TERAPIA_DICHIARATA_ASSENTE`, oppure `TERAPIA_NON_DICHIARATA` da confermare) (PASSO 4);
- l'attenzione `LIVELLO_INCOERENTE_IN_DEROGA`, se presente, con la decisione del
  nutrizionista (sezione 2);
- l'avviso `VALUTARE_LIVELLO_RINFORZATO`, se presente, con il motivo che lo ha fatto
  scattare: la scelta del livello è del nutrizionista, una sola per il piano (sezione 2).

**`metadati_piano_vN.json` (obbligatorio): bozza prima del PASSO 6, impronta dopo.** Si
scrive in bozza prima della presentazione (l'anteprima lo legge), si completa con
`impronta_approvata` dopo l'approvazione, con lo stesso numero di versione del
`piano.csv` approvato, e a fine chat A si salva su Drive nella cartella del paziente
accanto al CSV. È ciò che legge la chat B
(M3): le istruzioni di passaggio rimandano al file invece di riassumerlo.

```json
{
  "versione_piano": "vN",
  "drive": {"cartella_id": "...", "piano_csv": "piano_vN.csv",
            "fascicolo": "...", "altri_file": ["..."]},
  "giorni": {"lavorativi": ["lun", "..."], "libero": "dom",
             "range_kcal_libero": [min, max]},
  "livello_colazione": "standard | rinforzata_calcio",
  "tdee_confermato_kcal": 0,
  "intestazione": {"nome": "...", "eta": "XX anni", "condizione": "..."},
  "avvertenze_box": "allergie ed esclusioni obbligatorie, o \"Nessuna allergia dichiarata.\"",
  "abbinamento_spuntino": {"<opzione colazione>": "<opzione spuntino>"},
  "indicazioni_giorno_libero": {"pranzo": "...", "cena": "..."},
  "titoli_piatti": {"<giorno>|<pasto>|<opzione>": "titolo approvato"},
  "obiettivo_intestazione": "...",
  "criterio_rivalutazione": "...",
  "regole_operative": ["testo in registro impersonale", "..."],
  "scelte_principali": ["decisione + motivo in una riga", "..."],
  "limiti_noti": ["senza percentuali", "..."],
  "da_escludere": ["...", "..."],
  "differenze_da_versione_precedente": ["riga/pasto modificato", "..."],
  "impronta_approvata": "impronta dell'anteprima approvata (12 caratteri)"
}
```
- Nessuna kcal, nessun grammo, nessun valore nutrizionale: i numeri li ricalcola il motore
  in chat B da `piano.csv` (principio 2). Sole eccezioni, perché DATI DI INGRESSO
  confermati dal nutrizionista: `tdee_confermato_kcal` e `range_kcal_libero`.
- `titoli_piatti`: per un pasto fisso l'opzione è vuota (`"3|pranzo|"`); colazione,
  spuntino e secondo spuntino, uguali tutti i giorni, possono usare `*` al posto del
  giorno (`"*|colazione|A"`, `"*|spuntino2|A"`). L'opzione è quella della colonna
  `opzione` di `piano.csv`.
- `abbinamento_spuntino` usa le opzioni di `piano.csv` (non le lettere del PDF), può
  indicare più spuntini con una lista, riguarda solo colazione → spuntino (il secondo
  spuntino è una scelta indipendente); non fissato → `"non concordato"`, e nel PDF non
  compare.
- Giorno libero: stesse colazioni e spuntini dei giorni strutturati, secondo spuntino
  compreso se il piano lo ha; in `indicazioni_giorno_libero` solo pranzo e cena.
- Piano con eccezione etichetta: il file delle voci e quello dei loro nomi paziente vanno
  in `drive.altri_file`, perché la chat B li chiede allegati. Lo stesso per
  `orari_pasti.csv`, se il piano lo usa: senza, il PDF esce senza orari o si ferma
  sull'impronta.
- `genera_zona_piano.py` (M1) si ferma se mancano `giorni` (con `lavorativi`, e
  `range_kcal_libero` se c'è il giorno libero), `titoli_piatti`, `intestazione` (nome, età,
  condizione), `tdee_confermato_kcal`, `obiettivo_intestazione`, `criterio_rivalutazione`,
  `avvertenze_box`, `impronta_approvata` (o se non coincide con l'anteprima di oggi) e,
  se c'è il giorno libero, `indicazioni_giorno_libero`. Usa anche
  `versione_piano` e `abbinamento_spuntino` ma NON si ferma se mancano: vanno scritti
  sempre. Gli altri campi li legge la chat B. Nessun campo si inventa in chat B.
- Si ferma anche su un **segnaposto nei testi del paziente** (obiettivo, criterio,
  avvertenze, intestazione, indicazioni del giorno libero, titoli): valore non testo; vuoto
  o solo simboli; campo intero uguale a un segnaposto («non concordato» e varianti, «da
  concordare/definire», «N/D», «N/A», «n.d.» minuscolo, «TBD»…) o a uno di questi testi
  d'esempio: «Nome Cognome», «XX kg», «XX anni», «Da rivalutare dopo N settimane»,
  «Indicare qui allergie…», «titolo approvato». Elenco chiuso: i titoli d'esempio della
  zona dati del template («Nome piatto pranzo», «Colazione dolce 1», «Spuntino 1»,
  «Pasto libero o indicazioni»…) NON sono intercettati e si controllano a vista. Passano le
  frasi vere che contengono le stesse parole e sigle o nomi brevi («NA», «N.D.»). Si
  ferma se `giorni`, `intestazione`, `indicazioni_giorno_libero` o `titoli_piatti` non
  sono oggetti, e se `versione_piano` non è un numero, con o senza «v» o «versione»
  davanti, anche con lettera finale (`"v3"`, `"2b"`); se manca, la nota del PDF esce
  «versione » vuota: va scritta sempre.
- Testi già nel registro impersonale del documento di spiegazione (M3).
- Campo lasciato vuoto per scelta del nutrizionista: `"non concordato"`, mai null. NON vale
  per nessun testo che finisce nel PDF del paziente (obiettivo, criterio, avvertenze,
  intestazione, indicazioni del giorno libero, titoli) né per `versione_piano`: lo script
  si ferma. In `abbinamento_spuntino` si scrive esattamente `"non concordato"` (minuscolo,
  senza punto). Obiettivo, criterio e avvertenze si chiedono nelle domande in blocco, prima dell'anteprima del PASSO 6 (le avvertenze senza allergie si scrivono
  «Nessuna allergia dichiarata.»).

### PASSO 7 — GENERAZIONE PDF (solo dopo approvazione)
Vedi **M3**. Di norma in una chat B separata, che parte da `metadati_piano_vN.json` e non
ricarica questo modulo.

### PASSO 8 — DOCUMENTO DI SPIEGAZIONE
Default per ogni piano consegnato, subito dopo il PDF (M3). Usa solo le scelte approvate
al PASSO 6 e scritte nei metadati: nessun contenuto clinico nuovo, nessun nuovo giro di
approvazione dei calcoli. Un'imprecisione rispetto al piano approvato si segnala e si
corregge prima di consegnare.

### PASSO 9 — RITORNO SULLA SUITE
Un errore emerso che il motore NON ha intercettato da solo diventa una proposta di nuovo
caso golden (M1): ciò che sfugge una volta deve poter fallire da solo la volta dopo.
Riporta anche cosa il motore HA intercettato da solo e cosa ha richiesto un intervento
manuale: è il materiale della validazione sul campo.

---

## 4. STRUTTURA DEL PIANO — DEFAULT

- **7 giorni**: 6 strutturati + 1 libero, di norma la domenica. Il giorno libero è un
  margine di flessibilità da spiegare al paziente, non un giorno saltato: si compila
  comunque con indicazioni di massima e range calorico.
- Pasti ammessi in `piano.csv`: `colazione | spuntino | pranzo | spuntino2 | cena`, al
  massimo 5; `spuntino2` minuscolo e senza spazi, altrimenti la pipeline si ferma
  (`PASTO_NON_AMMESSO`).
- Il numero di pasti non si scrive da nessuna parte: si conta dai dati (intestazione del
  PDF compresa).
- Composizione **un giorno per volta**, non sei giorni in blocco: si chiude il giorno
  (pranzo e cena fissati, scenari colazione/spuntino verificati con `pipeline.py` sul
  piano fino a quel giorno) prima di aprire il successivo. Ogni giorno chiuso si mostra
  in chat in una riga, PRIMA di comporre il successivo: piatti di pranzo e cena, kcal
  min–max degli scenari con lo scarto dal target, rilievi del giorno. Non è
  un'approvazione (il gate resta uno, al PASSO 6) e non si aspetta risposta: serve al
  nutrizionista per correggere la rotta subito. Nel primo piano reale (23/10/2026) la
  regola c'era ma i giorni 2-6 sono stati composti in blocco, perché il ritmo non era
  visibile.
