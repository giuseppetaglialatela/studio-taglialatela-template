# PACCHETTO FORMATO 5 — elementi 3, 4, 5 e 6, unità 1-5

Riconciliazione della terapia nelle transizioni di cura nel modello
ospedale-territorio digitalizzato. Studio Taglialatela.

Sostituisce `dispensa-pacchetto-ud1-ud3-v1.md`, che copriva gli elementi 4 e 5
sulle sole unità 1-3. I contenuti di quel file sono qui riportati **invariati**.

Restano fuori solo l'elemento 1 (corpo) e l'elemento 2 (obiettivi formativi, in
`obiettivi_formativi.md`), che vivono in file propri. **Con l'elemento 6 il
pacchetto è completo.**

---

## ELEMENTO 3 — ARTICOLAZIONE IN UNITÀ DIDATTICHE E MONTE ORE

### La conversione, dichiarata

MD prescrive che la conversione fra parole, ore e CFU si dichiari e che si indichi
**quale unità fa fede in caso di scarto**. Questa è la proposta dello Studio; va
confermata dal committente prima della consegna, e finora non lo è stata.

> **Modulo da 2 CFU = 50 ore di impegno complessivo dello studente**, di cui circa
> la metà su materiale scritto. Di quelle 25 ore, **14 sono la lettura di studio
> della dispensa** e le restanti 11 vanno a autovalutazione, rilettura e
> approfondimento sulle fonti. **In caso di scarto fa fede il monte ore**, non il
> conteggio in parole: il committente accademico ragiona in ore, e il testo si
> adatta al monte ore concordato, non viceversa.

Corpo misurato: **17.002 parole** (convenzione: corpo, titoli esclusi, marcatori
`[Fxxx]` esclusi, marcatura Markdown esclusa; contatore `conta.py` nel
repository). Su 14 ore di lettura di studio la velocità implicita è di circa
**1.200 parole all'ora**, che è la velocità di lettura di studio su testo tecnico
— rilettura e annotazione comprese — non quella di lettura corrente.

**Rilievo aperto.** MD FORMATO 5 indica «circa 250 parole al minuto» e insieme
«fra le 12 e le 15 ore» per 15.000-18.000 parole. Le due cifre non stanno insieme:
a 250 parole al minuto 17.002 parole si leggono in poco più di un'ora. La cifra
usata qui è quella che regge il monte ore, cioè 1.200 parole all'ora, e la
divergenza è registrata come rilievo A9 in `rilievi_aperti.md`.

### Articolazione

| Unità | Titolo | OF | Parole | Ore di lettura di studio |
|---|---|---|---|---|
| 1 | La lista che nessuno ha | OF1 | 3.882 | 3,25 |
| 2 | Classificare le discrepanze | OF2 | 2.931 | 2,50 |
| 3 | I punti di rottura alla dimissione | OF3 | 3.830 | 3,00 |
| 4 | Cosa ogni flusso conserva e cosa perde | OF4 | 4.248 | 3,50 |
| 5 | Documentare l'esito e indirizzare | OF5 | 2.111 | 1,75 |
| | **Totale** | | **17.002** | **14,00** |

Le ore sono ripartite in proporzione alle parole e arrotondate al quarto d'ora.

**Due cose da dichiarare al committente insieme alla tabella.** La prima: l'unità
4 vale il doppio dell'unità 5, e lo squilibrio è dichiarato con la sua causa in
`obiettivi_formativi.md` — non è una svista di impaginazione. La seconda: se la
destinazione è un evento ECM e non un insegnamento universitario, l'assegnazione
dei crediti è del provider e segue regole proprie; questa tabella gli fornisce il
monte ore, non i crediti.

---

## ELEMENTI 4 E 5 — MESSAGGI CHIAVE E TEST DI AUTOVALUTAZIONE

Da 3 a 5 messaggi chiave e da 4 a 6 domande per unità, come prescrive MD. Le
risposte corrette portano la ragione, non solo la lettera: il test è materiale
didattico, non solo di verifica.

---

## UNITÀ 1 — LA LISTA CHE NESSUNO HA

### Messaggi chiave

1. La difformità fra le fonti sulla terapia in corso è la condizione normale
   delle transizioni di cura, non l'esito di una disattenzione individuale.
2. Ogni fonte disponibile risponde a una domanda diversa da «che cosa sta
   assumendo il paziente»: prescritto, erogato, dichiarato, documentato all'atto
   di un ricovero.
3. L'intervista strutturata al paziente e al caregiver è fonte primaria, non
   conferma di un elenco già formato: usarla per confermare significa ereditarne
   gli errori.
4. Lo strumento — modulo, checklist, applicativo — non produce da solo la lista:
   la variabilità fra organizzazioni pesa quanto il metodo adottato.

### Test di autovalutazione

**1.** In un paziente proveniente dal domicilio dopo un periodo in
lungodegenza, quale delle seguenti fonti documenta ciò che il paziente ha
effettivamente assunto?
a) la lettera di dimissione della lungodegenza
b) l'elenco delle ricette dematerializzate erogate
c) il foglio di terapia d'ingresso del reparto
d) nessuna delle precedenti
→ **d**. Ciascuna documenta un atto — una decisione, un ritiro, una sintesi —
e nessuna osserva l'assunzione.

**2.** L'intervista al paziente va condotta:
a) dopo aver formato l'elenco dalle fonti documentali, per confermarlo
b) come fonte primaria, con domande aperte prima di nominare i singoli farmaci
c) solo se le fonti documentali risultano discordanti
d) solo in presenza di un caregiver
→ **b**. Partire dall'elenco induce conferma e non fa emergere ciò che manca.

**3.** Il fatto che due fonti documentali concordino su un farmaco:
a) rende il dato verificato
b) consente di ometterlo dall'intervista
c) non esclude che entrambe derivino dalla stessa origine
d) sostituisce la verifica del dosaggio
→ **c**. Le fonti non sono indipendenti: molte discendono l'una dall'altra.

**4.** Quale elemento della terapia sfugge più facilmente a tutte le fonti
documentali?
a) l'antipertensivo cronico
b) il farmaco da banco assunto con regolarità
c) l'antibiotico prescritto la settimana precedente
d) l'anticoagulante orale
→ **b**. Ciò che non passa da una ricetta non lascia traccia nei flussi.

**5.** L'adozione di un modulo strutturato di ricognizione, da sola:
a) garantisce la completezza della lista
b) riduce le discrepanze indipendentemente dall'organizzazione
c) non è sufficiente: l'esito varia con il contesto organizzativo
d) sostituisce l'intervista
→ **c**.

---

## UNITÀ 2 — CLASSIFICARE LE DISCREPANZE

### Messaggi chiave

1. Una difformità fra liste non è di per sé un errore: le tre vie sono
   intenzionale documentata, intenzionale non documentata, non intenzionale.
2. La distinzione clinicamente utile non è fra grande e piccola discrepanza, ma
   fra quelle che richiedono intervento prima della somministrazione successiva e
   quelle che possono attendere il prescrittore in tempi ordinari.
3. La letteratura documenta bene la capacità di rilevare le discrepanze e molto
   meno quella di ridurre gli esiti clinici: la riduzione degli eventi avversi non
   è dimostrata con la stessa solidità.
4. I numeri che circolano su prevalenza e gravità vanno usati con cautela:
   definizioni eterogenee di riconciliazione rendono molte cifre non confrontabili.

### Test di autovalutazione

**1.** Una sospensione decisa in reparto e non riportata in lettera di
dimissione è:
a) una discrepanza non intenzionale
b) una discrepanza intenzionale non documentata
c) un errore di trascrizione
d) non una discrepanza
→ **b**. La decisione esiste, la sua tracciabilità no — ed è il caso che si
converte in errore alla transizione successiva.

**2.** Quale criterio determina la priorità dell'intervento?
a) il numero di farmaci coinvolti
b) la classe terapeutica
c) la prossimità della somministrazione successiva e il rischio dell'omissione
d) la fonte da cui emerge la discrepanza
→ **c**.

**3.** Sugli esiti clinici, la letteratura disponibile mostra:
a) riduzione significativa degli eventi avversi prevenibili
b) riduzione significativa delle discrepanze, senza dimostrazione altrettanto
   solida sugli esiti
c) nessun effetto su alcun indicatore
d) riduzione delle riammissioni ospedaliere
→ **b**.

**4.** Perché due studi sulla riconciliazione possono riportare prevalenze molto
diverse?
a) per differenze nella definizione di discrepanza e di riconciliazione
b) perché uno è ospedaliero e l'altro territoriale
c) per errore di calcolo
d) per la diversa numerosità campionaria
→ **a**. È la ragione che gli stessi autori indicano.

**5.** Una discrepanza intenzionale documentata:
a) va segnalata al prescrittore
b) non richiede intervento, ma va riportata nella documentazione dell'esito
c) è un errore di lieve entità
d) va corretta riportando la terapia precedente
→ **b**.

---

## UNITÀ 3 — I PUNTI DI ROTTURA ALLA DIMISSIONE

### Messaggi chiave

1. La lettera di dimissione è il documento in cui si concentrano i punti di
   rottura, e va letta cercando ciò che non contiene più che ciò che contiene.
2. Quattro rotture ricorrenti: sospensioni temporanee mai ripristinate,
   sostituzioni di prontuario non ricondotte al principio attivo, terapie a
   durata definita senza data di fine, farmaci del domicilio non ripresi.
3. Il dato che viaggia in mano al paziente è spesso l'unico canale reale verso il
   medico di medicina generale, che frequentemente riceve la lettera dal paziente
   stesso senza contatto con l'ospedale.
4. Gli indicatori difendibili di un servizio riguardano il processo — discrepanze
   rilevate, quota documentata, tempo alla risoluzione — non gli esiti clinici.

### Test di autovalutazione

**1.** Un farmaco sospeso in reparto per la procedura chirurgica e non ripreso in
lettera va trattato come:
a) sospensione definitiva decisa dallo specialista
b) omissione da verificare con il prescrittore prima della ripresa autonoma
c) errore del reparto da segnalare
d) terapia conclusa
→ **b**. La sospensione era temporanea; la sua natura non si deduce dal silenzio.

**2.** Una sostituzione di prontuario ospedaliero genera rischio soprattutto
perché:
a) il farmaco sostituito è meno efficace
b) il paziente può assumere insieme il prodotto ospedaliero e quello del
   domicilio, non riconoscendoli come lo stesso principio attivo
c) il dosaggio cambia sempre
d) non è rimborsabile
→ **b**. È la duplicazione terapeutica per nome commerciale diverso.

**3.** Una terapia a durata definita prescritta senza data di fine:
a) si interrompe alla fine della confezione
b) tende a proseguire indefinitamente, perché nessun documento successivo ne
   dichiara il termine
c) viene sospesa dal medico di medicina generale al primo controllo
d) non costituisce un problema di riconciliazione
→ **b**.

**4.** Quale informazione sulla terapia il medico di medicina generale riceve più
spesso per il tramite del paziente?
a) il referto degli esami
b) la lettera di dimissione
c) il piano terapeutico elettronico
d) la scheda di dimissione ospedaliera
→ **b**.

**5.** Quali indicatori è difendibile promettere a un committente per un servizio
di riconciliazione?
a) riduzione delle riammissioni a trenta giorni
b) riduzione degli eventi avversi prevenibili
c) discrepanze rilevate, quota documentata e tempo alla risoluzione
d) riduzione della mortalità
→ **c**. Gli altri tre non sono sostenuti dagli studi disponibili.

---

## UNITÀ 4 — COSA OGNI FLUSSO CONSERVA E COSA PERDE

### Messaggi chiave

1. Il contenuto del Fascicolo Sanitario Elettronico è tassativo — tredici
   tipologie di dati e documenti — e nessuna di quelle voci registra la
   somministrazione o l'assunzione. Un'informazione che non vi rientri non ha
   alcun canale istituzionale che la trasporti.
2. Il farmacista accede al Fascicolo, ma la matrice dei profili gli apre
   prescrizioni farmaceutiche ed erogazioni e gli chiude il profilo sanitario
   sintetico e la lettera di dimissione: i due documenti in cui la transizione
   vive. Il Fascicolo gli restituisce il dispensato, non la terapia in corso.
3. Il dossier farmaceutico è un servizio di estrazione dell'Ecosistema, non una
   banca dati, e riguarda per scelta dichiarata il prescritto e l'erogato, mai la
   somministrazione. Presentarlo come «la storia della terapia» promette una cosa
   che il sistema non costruisce.
4. Tre meccanismi distinti rendono un'assenza non dichiarata: l'oscuramento, che
   nasconde anche la propria esistenza; il campo delle terapie in atto del profilo
   sanitario sintetico, sospeso in attesa dei servizi dell'Ecosistema; il filtro
   discrezionale su ciò che dal telemonitoraggio arriva a valle.
5. Il farmacista compare dove il testo descrive e non compare dove obbliga:
   l'Allegato 1 del decreto sull'assistenza territoriale lo indica come referente
   per l'uso sicuro dei farmaci, e in nessuno standard di personale dell'Allegato
   2 — prescrittivo — è previsto un farmacista.

### Test di autovalutazione

**1.** Un paziente è dimesso venerdì pomeriggio. Lunedì mattina il farmacista
consulta il suo Fascicolo e non vi trova traccia del ricovero. Che cosa se ne può
concludere?
a) il ricovero non è avvenuto nella regione di residenza
b) il dato è stato oscurato dall'assistito
c) nulla: l'alimentazione del Fascicolo è dovuta entro cinque giorni
   dall'erogazione
d) il Fascicolo del paziente non è attivo
→ **c**. Cinque giorni sono la durata della finestra in cui una transizione si
compie: il ritardo è massimo proprio dopo una dimissione.

**2.** Nella matrice di accesso dell'allegato tecnico, al farmacista sono aperti:
a) tutti i documenti del Fascicolo, previa autocertificazione
b) dati identificativi e amministrativi, prescrizioni farmaceutiche, erogazione
   dei farmaci
c) il profilo sanitario sintetico e la lettera di dimissione
d) il solo taccuino personale dell'assistito
→ **b**. Il farmacista è nell'elenco dei soggetti che accedono per finalità di
cura, ma il suo profilo si ferma al dispensato.

**3.** Il profilo sanitario sintetico contiene oggi tutte le terapie in atto?
a) sì, è il documento che assolve a questa funzione
b) no: le terapie croniche prescritte dal medico di medicina generale sono un
   campo obbligatorio, le terapie in atto in senso pieno un campo sospeso in
   attesa dei servizi dell'Ecosistema
c) sì, ma solo se il paziente ha prestato il consenso
d) no, perché il documento non è mai stato attuato
→ **b**. Ciò che arriva dallo specialista, dalla dimissione o dall'acquisto
diretto cade nel campo sospeso — cioè proprio ciò che una transizione produce.

**4.** Quando il dossier farmaceutico sarà operativo, che cosa **non** conterrà?
a) le erogazioni effettuate in altre regioni
b) le prescrizioni farmaceutiche
c) l'informazione sull'avvenuta somministrazione
d) i dati dell'Anagrafe nazionale degli assistiti
→ **c**. È una scelta di progetto documentata, chiesta dall'autorità di controllo,
non un difetto di implementazione.

**5.** Perché una lista di farmaci estratta da un sistema informativo può essere
incompleta senza che nulla lo segnali?
a) perché l'alimentazione può essere intempestiva
b) perché l'oscuramento è realizzato in modo che non sia conoscibile nemmeno
   l'esistenza dei dati oscurati
c) perché il farmacista non ha accesso a tutti i documenti
d) perché il paziente può non aver prestato il consenso
→ **b**. Le risposte a), c) e d) sono tutte vere e tutte diverse: solo b) descrive
un'assenza che non lascia traccia di sé. È la ragione per cui la ricognizione con
il paziente non si salta perché il Fascicolo ha risposto.

**6.** Chi progetta oggi un servizio di telefarmacia deve costruirne la
descrizione su quali definizioni?
a) televisita e teleconsulto, che sono i servizi minimi obbligatori
b) teleconsulenza e teleassistenza, le sole aperte a professioni non mediche
c) telemonitoraggio, perché produce dati sulla terapia
d) nessuna: le linee guida nazionali nominano espressamente il farmacista
→ **b**. Nelle linee guida del 2022 il farmacista non è mai nominato, e televisita
e teleconsulto sono qualificati come atti medici.

---

## UNITÀ 5 — DOCUMENTARE L'ESITO E INDIRIZZARE

### Messaggi chiave

1. Ricognizione e riconciliazione sono due atti distinti e ordinati: la
   ricognizione entro ventiquattro ore dalla presa in carico, tracciata con data,
   ora e firma; la riconciliazione **prima** che la nuova prescrizione sia
   redatta. Una riconciliazione fatta dopo la prescrizione non previene l'errore,
   lo intercetta.
2. Un esito non trasmesso e non conservato non è un esito. Le linee di indirizzo
   del 2018 chiedono che la scheda sia trasmessa al prescrittore e conservata per
   almeno un anno: la trasmissione la mette in circolo, la conservazione rende
   calcolabile un indicatore.
3. Propone chi valuta, decide chi prescrive. Nei dati italiani l'accettazione dei
   suggerimenti del farmacista è alta — 309 casi su 455 — e gli autori la
   spiegano con il fatto che il clinico sa di essere il decisore ultimo. Il tasso
   alto e quella condizione vanno letti insieme.
4. Gli indicatori difendibili in sede locale sono di processo: quota di pazienti
   con elenco documentato in ammissione, discrepanze rilevate e classificate,
   segnalazioni con esito registrato. Promettere alla direzione riduzioni di
   riammissioni o di eventi avversi significa promettere ciò che gli studi
   disponibili non hanno mostrato.
5. Il riferimento nazionale che descrive come documentare la riconciliazione è del
   dicembre 2014 e prevede al proprio interno una revisione in funzione del
   Fascicolo, del dossier farmaceutico e della telemedicina. Nell'elenco ufficiale
   delle raccomandazioni non risulta pubblicata alcuna revisione: tutto il
   disallineamento descritto nell'unità 4 è successivo al documento che dovrebbe
   governarlo.

### Test di autovalutazione

**1.** In quale momento va compiuta la riconciliazione?
a) entro ventiquattro ore dalla presa in carico
b) prima che sia redatta la prescrizione del nuovo setting
c) al momento della dimissione
d) quando emerge una discrepanza
→ **b**. Le ventiquattro ore sono il termine della **ricognizione**, che è l'atto
precedente e distinto: confondere i due termini sposta la riconciliazione dopo la
prescrizione, dove non previene più nulla.

**2.** Che cosa distingue un esito documentato da una comunicazione verbale?
a) la firma di chi lo redige
b) la trasmissione al prescrittore e la conservazione per almeno un anno
c) l'uso di un modulo aziendale approvato
d) l'inserimento nella cartella clinica informatizzata
→ **b**. Senza conservazione nessun indicatore si può calcolare a distanza di
tempo; senza trasmissione il documento non entra nel processo di cura.

**3.** In uno studio italiano i suggerimenti dei farmacisti ospedalieri sono stati
accolti nel 68% dei casi. Che cosa dimostra quel dato?
a) che l'intervento del farmacista riduce gli eventi avversi
b) che i clinici accolgono la maggior parte delle proposte, in un contesto in cui
   restano il decisore ultimo
c) che il farmacista può modificare la terapia in autonomia nei casi accolti
d) che il 32% dei suggerimenti era clinicamente errato
→ **b**. È un dato sull'accettazione delle proposte, non sull'esito clinico, e gli
autori collegano espressamente l'accettazione alla titolarità della decisione.

**4.** Quale contenuto rende una segnalazione al prescrittore utile e verificabile
a fine anno?
a) rilievo, motivazione, opzione proposta, decisione lasciata a chi prescrive, e
   la risposta registrata anche quando è un rifiuto
b) rilievo e opzione proposta, senza registrare l'esito per non appesantire
c) il solo elenco delle discrepanze non intenzionali
d) una comunicazione verbale seguita da annotazione interna
→ **a**. Registrare anche il rifiuto è l'unico modo per sapere se il servizio stia
proponendo cose che i clinici ritengono utili.

**5.** Un servizio di riconciliazione va presentato alla propria direzione:
a) come adempimento di un obbligo normativo che impone il ruolo del farmacista
b) sull'attuazione dell'obbligo di adottare liste di controllo coerenti con le
   raccomandazioni ministeriali, con tempo per paziente e indicatori di processo
   dichiarati
c) con la promessa di ridurre le riammissioni a trenta giorni
d) rinviando alla revisione della Raccomandazione n. 17
→ **b**. Non esiste oggi una norma che imponga il servizio: presentarlo come
adempimento è una strategia che il primo controllo smonta, e la revisione della
Raccomandazione non risulta pubblicata.

---

## ELEMENTO 6 — BIBLIOGRAFIA

Da `fonti.csv` filtrato su `usata_in`, in stile Vancouver, **numerata secondo
l'ordine di prima comparsa nel testo** e non secondo l'ordine degli `id`, che è di
registro. Quaranta voci: tante quante le fonti citate nel corpo, nessuna in più.
MB chiede **un solo identificatore** per voce, il più stabile disponibile: dove
esiste un DOI è quello, altrimenti il PMID, altrimenti il PMCID o l'URL. Per gli
atti normativi l'identificatore è il codice redazionale con gli estremi di
Gazzetta Ufficiale.

1. Bonaudo M, Martorana M, Dimonte V, D'Alfonso A, Fornero G, Politano G, Gianino MM. Medication discrepancies across multiple care transitions: a retrospective longitudinal cohort study in Italy. PLoS One. 2018;13(1):e0191028. doi:10.1371/journal.pone.0191028
2. Linee di indirizzo. Riconciliazione della terapia farmacologica sul territorio durante le transizioni di cura: paziente anziano ricoverato in RSA/struttura sanitaria protetta e paziente oncologico ed oncoematologico dimesso da struttura ospedaliera e viceversa. Ministero della Salute, Regione del Veneto, Regione Emilia-Romagna. Settembre 2018. salute.gov.it/imgs/C_17_pubblicazioni_2839_allegato.pdf [consultato il 16/08/2026]
3. Raccomandazione per la Riconciliazione della terapia farmacologica. Raccomandazione n. 17. Ministero della Salute, Direzione generale della programmazione sanitaria, Ufficio III. Dicembre 2014. buonepratiche.agenas.it/documents/recommendations/ [consultato il 16/08/2026]
4. Mueller SK, Sponsler KC, Kripalani S, Schnipper JL. Hospital-based medication reconciliation practices: a systematic review. Arch Intern Med. 2012;172(14):1057-69. doi:10.1001/archinternmed.2012.2246
5. Schnipper JL, Reyes Nieva H, Mallouk M, Mixon A, Rennke S, Chu E, et al. Effects of a refined evidence-based toolkit and mentored implementation on medication reconciliation at 18 hospitals: results of the MARQUIS2 study. BMJ Qual Saf. 2022;31(4):278-286. doi:10.1136/bmjqs-2020-012709
6. Schnipper JL, Reyes Nieva H, Yoon C, Mallouk M, Mixon AS, Rennke S, et al. What works in medication reconciliation: an on-treatment and site analysis of the MARQUIS2 study. BMJ Qual Saf. 2023;32(8):457-469. doi:10.1136/bmjqs-2022-014806
7. Kripalani S, Roumie CL, Dalal AK, Cawthon C, Businger A, Eden SK, et al. Effect of a pharmacist intervention on clinically important medication errors after hospital discharge: a randomized controlled trial. Ann Intern Med. 2012;157(1):1-10. doi:10.7326/0003-4819-157-1-201207030-00003
8. Chiarelli MT, Antoniazzi S, Cortesi L, Pasina L, Novella A, Venturini F, Nobili A, Mannucci PM; ad hoc Deprescribing Study Group. Pharmacist-driven medication recognition/reconciliation in older medical patients. Eur J Intern Med. 2021;83:39-44. doi:10.1016/j.ejim.2020.07.011
9. Mekonnen AB, McLachlan AJ, Brien JE. Pharmacy-led medication reconciliation programmes at hospital transitions: a systematic review and meta-analysis. J Clin Pharm Ther. 2016;41(2):128-44. doi:10.1111/jcpt.12364
10. Jost M, Kerec Kos M, Kos M, Knez L. Effectiveness of pharmacist-led medication reconciliation on medication errors at hospital discharge and healthcare utilization in the next 30 days: a pragmatic clinical trial. Front Pharmacol. 2024;15:1377781. doi:10.3389/fphar.2024.1377781
11. Mekonnen AB, McLachlan AJ, Brien JE. Effectiveness of pharmacist-led medication reconciliation programmes on clinical outcomes at hospital transitions: a systematic review and meta-analysis. BMJ Open. 2016;6(2):e010003. doi:10.1136/bmjopen-2015-010003
12. Mekonnen AB, Abebe TB, McLachlan AJ, Brien JE. Impact of electronic medication reconciliation interventions on medication discrepancies at hospital transitions: a systematic review and meta-analysis. BMC Med Inform Decis Mak. 2016;16:112. PMID: 27549581
13. Wang H, Meng L, Song J, Yang J, Li J, Qiu F. Electronic medication reconciliation in hospitals: a systematic review and meta-analysis. Eur J Hosp Pharm. 2018;25(5):245-250. PMID: 31157034
14. Linee di indirizzo sugli strumenti per concorrere a ridurre gli errori in terapia farmacologica nell'ambito dei servizi assistenziali erogati dalle Farmacie di comunità. Ministero della Salute, Direzione generale della programmazione sanitaria, Ufficio III. Maggio 2014. salute.gov.it/imgs/C_17_pubblicazioni_2189_allegato.pdf [consultato il 20/08/2026]
15. Chua D, Chu E, Lo A, Lo M, Pataky F, Tang L, Bains A. Effect of misalignment between hospital and provincial formularies on medication discrepancies at discharge: PPITS (Proton Pump Inhibitor Therapeutic Substitution) study. Can J Hosp Pharm. 2012;65(2):98-102. PMCID: PMC3329923
16. Wang JS, Fogerty RL, Horwitz LI. Effect of therapeutic interchange on medication reconciliation during hospitalization and upon discharge in a geriatric population. PLoS One. 2017;12(10):e0186075. doi:10.1371/journal.pone.0186075
17. Linea guida inter-societaria per la gestione della multimorbilità e polifarmacoterapia. SIGG, SIGOT, SIMG, SIMI, FADOI, SIF. Roma: Sistema Nazionale Linee Guida, Istituto Superiore di Sanità; 4 giugno 2021, codice LG-314; rivista l'8 novembre 2024 senza modifiche a direzione e forza delle raccomandazioni. iss.it/-/snlg-gestione-multimorbilita-polifarmacoterapia [consultato il 23/08/2026]
18. Carollo M, Boccardi V, Crisafulli S, Conti V, Gnerre P, Miozzo S, et al.; Italian Scientific Consortium on medication review and deprescribing. Medication review and deprescribing in different healthcare settings: a position statement from an Italian scientific consortium. Aging Clin Exp Res. 2024;36(1):63. doi:10.1007/s40520-023-02679-2
19. Raccomandazione per la prevenzione degli errori in terapia con farmaci antineoplastici. Raccomandazione n. 14. Ministero della Salute, Direzione generale della programmazione sanitaria, Ufficio III. Ottobre 2012. agenas.gov.it/images/agenas/rischio_clinico/raccomandazioni/ [consultato il 20/08/2026]
20. Decreto legislativo 3 ottobre 2009, n. 153. Individuazione di nuovi servizi erogati dalle farmacie nell'ambito del Servizio sanitario nazionale, nonché disposizioni in materia di indennità di residenza per i titolari di farmacie rurali. GU Serie Generale n. 257 del 04/11/2009, codice redazionale 09G0162.
21. Cheema E, Alhomoud FK, Kinsara ASAL-D, Alsiddik J, Barnawi MH, Al-Muwallad MA, et al. The impact of pharmacists-led medicines reconciliation on healthcare outcomes in secondary care: a systematic review and meta-analysis of randomized controlled trials. PLoS One. 2018;13(3):e0193510. doi:10.1371/journal.pone.0193510
22. McNab D, Bowie P, Ross A, MacWalter G, Ryan M, Morrison J. Systematic review and meta-analysis of the effectiveness of pharmacist-led medication reconciliation in the community after hospital discharge. BMJ Qual Saf. 2018;27(4):308-320. PMID: 29248878
23. Killin L, Hezam A, Anderson KK, Welk B. Advanced medication reconciliation: a systematic review of the impact on medication errors and adverse drug events associated with transitions of care. Jt Comm J Qual Patient Saf. 2021;47(7):438-451. doi:10.1016/j.jcjq.2021.03.011
24. Tabja Bortesi JP, Becerra MP, Ranisau J, Wen B, Nadesan P, Devereaux PJ, McGillion M, Petch J. AI-based automation for medication reconciliation: scoping review. J Med Internet Res. 2026;28:e86760. doi:10.2196/86760
25. Decreto del Ministro della salute e del Sottosegretario di Stato alla Presidenza del Consiglio dei ministri con delega all'innovazione tecnologica, di concerto con il Ministro dell'economia e delle finanze, 7 settembre 2023. Fascicolo sanitario elettronico 2.0. GU Serie Generale n. 249 del 24/10/2023, codice redazionale 23A05829.
26. Decreto del Ministro della salute 23 maggio 2022, n. 77. Regolamento recante la definizione di modelli e standard per lo sviluppo dell'assistenza territoriale nel Servizio sanitario nazionale. GU Serie Generale n. 144 del 22/06/2022, codice redazionale 22G00085.
27. Decreto del Ministero della salute 11 novembre 2025. Modifiche al decreto 7 settembre 2023 concernente il Fascicolo sanitario elettronico 2.0. GU Serie Generale n. 286 del 10/12/2025, codice redazionale 25A06570.
28. Ministero della salute, Sottosegretario di Stato alla Presidenza del Consiglio dei ministri con delega all'innovazione tecnologica, Ministero dell'economia e delle finanze. Decreto 30 dicembre 2024. Modifiche al decreto 7 settembre 2023, in materia di Fascicolo sanitario elettronico 2.0. GU Serie Generale n. 33 del 10/02/2025, codice redazionale 25A00808.
29. Decreto del Ministero della salute 27 giugno 2025. Indicazioni attuative per la definizione dei contenuti informativi del Profilo sanitario sintetico previsto dall'articolo 4 del decreto 7 settembre 2023, recante il «Fascicolo sanitario elettronico 2.0». GU Serie Generale n. 202 del 01/09/2025, codice redazionale 25A04814.
30. Parere sullo schema di decreto recante Ecosistema dati sanitari. Garante per la protezione dei dati personali, provvedimento del 26 settembre 2024, doc. web n. 10062302. garanteprivacy.it [consultato il 17/08/2026]
31. Decreto del Ministero della salute 31 dicembre 2024, n. 334, di concerto con il Ministero dell'economia e delle finanze e il Sottosegretario alla Presidenza del Consiglio con delega all'innovazione tecnologica. Istituzione dell'Ecosistema dati sanitari (EDS). GU Serie Generale n. 53 del 05/03/2025, codice redazionale 25A01321.
32. Decreto del Ministero della salute 8 luglio 2025. Modifica del decreto 31 dicembre 2024 recante «Istituzione dell'Ecosistema dati sanitari». GU Serie Generale n. 194 del 22/08/2025, codice redazionale 25A04732.
33. FAQ sul Fascicolo sanitario elettronico. Garante per la protezione dei dati personali. Aggiornamento maggio 2026. garanteprivacy.it/faq/fascicolo-sanitario [consultato il 16/08/2026]
34. Decreto del Ministro della salute 21 settembre 2022. Approvazione delle Linee guida per i servizi di telemedicina — Requisiti funzionali e livelli di servizio (Allegato A). GU Serie Generale n. 256 del 02/11/2022, codice redazionale 22A06184.
35. Elenco delle raccomandazioni ministeriali per la sicurezza dei pazienti. Agenas, Osservatorio nazionale delle buone pratiche sulla sicurezza nella sanità. Pagina aggiornata al 17 dicembre 2020. agenas.gov.it/aree-tematiche/qualita-e-sicurezza/ [consultato il 16/08/2026]
36. Pollice MG, Degli Esposti L, Procacci C, Lenti S, Ancona D, Nappi C, et al. D.I.Ri.M.O. project: deprescription, inappropriateness evaluation and therapeutic reconciliation in hospital medicine. Glob Reg Health Technol Assess. 2025;12:61-69. doi:10.33393/grhta.2025.3194
37. Canning ML, Barras M, McDougall R, Yerkovich S, Coombes I, Sullivan C, Whitfield K. Defining quality indicators, pharmaceutical care bundles and outcomes of clinical pharmacy service delivery using a Delphi consensus approach. Int J Clin Pharm. 2024;46(2):451-462. PMID: 38240963
38. Mahomedradja RF, Tichelaar J, Mokkink LB, Sigaloff KCE, van Agtmael MA. Quality indicators for appropriate in-hospital pharmacotherapeutic stewardship: an international modified Delphi study. Br J Clin Pharmacol. 2024;90(5):1280-1300. doi:10.1111/bcp.16015
39. Phang YY, Kuan JW, Oh AL, Ting CY, Osman NA, Moses S. Effectiveness of digital platform in reducing unintentional medication discrepancies at transition of care from hospital discharge to primary healthcare settings: a randomised controlled trial. BMC Prim Care. 2025;26:206. PMCID: PMC12219133
40. Moretti F, Mazzi MA, Montresor S, Colpo S, Tocco Tussardi I, Facchinello D, et al. Proximity care pathways and digitalization: opportunities and concerns for medication safety management. Insights from the ProSafe study on community perspectives. Front Public Health. 2025;13:1486814. doi:10.3389/fpubh.2025.1486814

### Due note che appartengono alla bibliografia

**Voci 4, 5 e 6** hanno `conflitto_dichiarato = si_concorde` a registro. Nessuna
regge da sola un'affermazione portante: la voce 4 è trattata con il vincolo
dichiarato in `note_uso_fonti.md`, e le voci 5 e 6 sono lo stesso studio, con la
non indipendenza dichiarata nel testo oltre che nel registro.

**Voci 24 e 37** sono verificate sul solo abstract e nel testo sono usate con la
sola conclusione generale, come MB §6.3 prescrive: nessun numero, sottogruppo o
dettaglio di metodo ne è tratto.
