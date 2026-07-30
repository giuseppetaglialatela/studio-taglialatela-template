# M2 — WORKFLOW PIANO ALIMENTARE

Modulo operativo. Si carica quando si compone, si modifica o si valuta un piano
alimentare. Dipende da **M1 (Motore di calcolo)**: nessun passo di questo modulo
è eseguibile senza il motore collaudato.

Rimandi:
- il motore, i CSV, i gap e la gerarchia fonti → **M1**
- la generazione del PDF del piano e del documento di spiegazione → **M3**
- il fascicolo paziente e la Tabella Vincoli (PASSO 0) → **M4**
- l'ampliamento del database alimenti → **M6**

In caso di divergenza tra questo modulo e un documento di archivio su Drive,
vale questo modulo (nucleo M0, principio 6).

---

## 1. REGOLE PESI

Da leggere PRIMA di ogni calcolo. Sbagliare qui invalida tutto ciò che segue:
l'errore realmente rilevato su questa regola valeva +42% su un singolo pasto e
+9,3% sul totale giornata.

**Regola generale: pesi sempre a CRUDO.**

Due eccezioni, e solo queste:

1. Inscatolati e simili → **peso netto di confezione**
2. Legumi lessati (ceci, fagioli, lenticchie cotti in casa) → **peso COTTO**

Carne e pesce restano SEMPRE a peso crudo, anche quando il piatto è descritto
come cotto: "merluzzo 140 g al vapore" significa 140 g crudi, non 140 g di
prodotto cotto nel piatto.

In caso di dubbio su una preparazione, CHIEDI prima di calcolare. Non dedurre
dalla formulazione del piatto: la stessa dicitura può significare cose diverse
a seconda dell'alimento.

### Conversione formato confezione → grammi

Quando il paziente descrive una porzione in termini commerciali ("una scatoletta
di tonno", "un vasetto di yogurt"), usa la **Tabella Formati Confezione Standard**
(Drive > Sistema Presa in Carico). NON è un documento nutrizionale: converte solo
il formato in grammi da inserire in `piano.csv`. Il dato nutrizionale resta quello
di `alimenti.csv`, già espresso per 100 g di prodotto sgocciolato/edibile.

Le percentuali di sgocciolamento non tratte da CREA/BDA/USDA sono stime di
mercato: riferimento pratico, non dato verificato.

La foto di una confezione è utile per DUE cose e solo quelle: il formato in
grammi, e la variante del prodotto (intero/scremato) che determina quale voce del
database usare. I valori nutrizionali dell'etichetta NON entrano nel database:
non sono una delle tre fonti e non hanno un codice tracciabile.

---

## 2. REGOLE STRUTTURA PASTI

Protocollo di DEFAULT per ogni piano, derogabile caso per caso quando il
fascicolo del paziente lo richiede esplicitamente (es. spuntino dichiarato come
saltato in sez6).

**COLAZIONE — 4 alternative fisse: 2 salate, 2 dolci.**
Le quattro vanno calcolate con kcal tra loro il più possibile vicine, così che la
scelta del paziente non sposti il bilancio della giornata.
Queste 4 alternative sono LE STESSE per tutti i giorni strutturati del piano: non
cambiano da un giorno all'altro. Il paziente sceglie liberamente ogni giorno tra
le stesse 4; non gli si assegna una colazione diversa per calendario.

**SPUNTINO — 2 alternative, legate alla colazione scelta (salata/dolce).**
Il criterio di abbinamento (compensativo: salata→dolce, dolce→salato/proteico;
oppure in continuità: salata→salato, dolce→dolce) NON è fissato a priori: si
decide col nutrizionista caso per caso, in base al bilancio micronutrienti del
giorno. Come la colazione, questi 2 spuntini sono fissi per tutta la settimana.

**DEROGA:** se il fascicolo dichiara lo spuntino saltato, un'allergia che esclude
un'intera alternativa, o altra indicazione esplicita del paziente, la deroga vince
sempre sul protocollo di default — non forzare la struttura standard.
Nel motore la deroga si dichiara con `--deroga-struttura "motivo"`: il rilievo
resta scritto nel report ma non blocca.

### Tensione nota con i micronutrienti — da gestire, non da ignorare

Fissare la stessa colazione e lo stesso spuntino su tutti i giorni toglie la leva
che serviva a compensare calcio e vitamina D nei giorni deboli, e sposta l'intero
peso del bilanciamento su pranzo e cena. Su un paziente con pranzo vincolato
(mensa, halal, patologia) il margine può non bastare.

Contromisura: `colazioni_spuntini.csv` (M1) contiene un secondo livello
**rinforzata_calcio**. Il passaggio al livello rinforzato vale per L'INTERO PIANO
(tutti i giorni strutturati), mai per il singolo giorno critico. È **una sola
decisione per l'intero piano settimanale**.

> **DA DECIDERE — unica soglia giornaliera rimasta nel sistema**
> Il criterio storico per passare al livello rinforzato era: "se anche un solo
> giorno scende sotto l'80% LARN di calcio". Dal 29/07/2026 il principio 8
> stabilisce che il giudizio sui micronutrienti è settimanale, e questo criterio
> è l'unico punto in cui sopravvive una soglia giornaliera.
> Non è necessariamente un residuo da eliminare: il calcio è l'unico nutriente
> con un argomento reale a favore della lettura per giorno, perché l'assorbimento
> satura intorno ai 500 mg per singola assunzione. Ma il criterio così com'è
> scritto usa l'80% LARN giornaliero, che è una soglia, non un argomento di
> distribuzione.
> Le due formulazioni possibili: **(a)** media settimanale del calcio sotto l'80%
> LARN, coerente con il principio 8; **(b)** calcio concentrato su meno di 3
> giorni su 6, coerente con l'argomento della saturazione.
> Finché non è deciso, vale il criterio storico e la scelta va esposta al
> nutrizionista.

Prima di passare al livello rinforzato, verifica comunque che il calcio sotto
soglia non sia marcato ⛔ TOTALE SOTTOSTIMATO: in quel caso la carenza può essere
apparente.

NON si abbina la colazione di un livello con lo spuntino dell'altro: il PASSO 6 di
`pipeline.py` lo blocca, ed è un'incoerenza che il solo controllo di uniformità tra
giorni non vedrebbe, perché i giorni resterebbero tutti uguali tra loro.

### Verifica obbligatoria sugli scenari di scelta

Poiché il paziente può scegliere liberamente una qualsiasi delle 4 colazioni (con
il relativo spuntino abbinato) ogni giorno, il piano NON è verificato finché non
sono stati calcolati, per OGNI giorno strutturato, tutti gli scenari possibili —
non un'unica combinazione scelta come esempio. Il momento esatto in cui farlo è
nel PASSO 2 qui sotto.

Nota: questa verifica riguarda kcal e macro, che restano un giudizio per giorno.
Per i micronutrienti vale il principio 8.

**STATO:** protocollo introdotto dopo test su paziente fittizio (Vittorio
Taglialatela), non ancora attraversato da un paziente reale per intero. Da
confermare o rivedere dopo il primo caso vero che lo percorre tutto.

---

## 3. I NOVE PASSI

Per ogni nuovo piano o modifica, esegui i passi IN QUESTO ORDINE.
Se è disponibile un fascicolo paziente strutturato, c'è un **PASSO 0** che precede
tutto: vedi **M4**.

### PASSO 1 — RICERCA SCIENTIFICA

Cerca gli studi più recenti pertinenti al profilo clinico del paziente (patologie,
farmaci in terapia, obiettivi nutrizionali). Sintetizza i punti rilevanti che
influenzano il piano, comprese eventuali evidenze che ridimensionano l'efficacia
attesa di una scelta già concordata (es. fonti omega-3 vegetali vs marine):
segnalale comunque, anche dopo l'approvazione della scelta.

### PASSO 2 — CALCOLI (prima di qualsiasi bozza grafica)

Esegui i calcoli con il motore deterministico (M1), mai a mente, su grammature
reali e secondo le regole pesi della sezione 1.
**Precondizione:** `collaudo.py` deve aver dato esito positivo (principio 7).

**MODO RACCOMANDATO:** esegui `pipeline.py`, che impone l'ordine dei passi e
produce in un colpo solo collaudo, calcoli, scenari di scelta multipla,
micronutrienti, coerenza, interazioni e verifica del livello colazione. I moduli
singoli restano utili per approfondire un punto, ma l'ordine dei passi non va
ricostruito a mano: entrambi gli errori di processo del primo caso reale sono nati
da lì.

Se il TDEE o i target non sono già stati concordati, usa `tdee.py` per proporli: la
proposta va sempre confermata dal nutrizionista prima di calcolare il piano.

Per pranzo e cena, parti dai blocchi di `moduli_pasto.csv` quando esiste un blocco
compatibile con i vincoli del paziente: risparmia cicli di aggiustamento
grammature. Consultali con `python3 moduli_pasto.py --tag ...`, che filtra e
ricalcola. Il blocco va comunque riscalato e ricalcolato nel piano del paziente,
mai copiato tal quale.

**ORDINE OBBLIGATORIO PER I PASTI A SCELTA MULTIPLA (colazione+spuntino):**
per ogni giorno, subito DOPO aver fissato pranzo e cena di quel giorno e PRIMA di
passare al giorno successivo, calcola tutti gli scenari possibili di
colazione+spuntino su quel giorno e verifica che ciascuno rientri in tolleranza.
Se anche un solo scenario esce di tolleranza, risolvi (aggiustando pranzo/cena di
quel giorno, o le alternative stesse) PRIMA di passare al giorno successivo. Non
arrivare alla presentazione finale (PASSO 6) avendo verificato una sola
combinazione "esemplare" per giorno: è il punto in cui l'errore è più costoso da
scoprire, perché emerge dopo che il nutrizionista ha già visto una tabella.
`pipeline.py` fa questo da solo, al suo PASSO 2, e prima di ogni riepilogo.

Produci:

- kcal per ogni singolo pasto
- totale kcal giornaliero, verificato pasto per pasto
- macronutrienti in grammi E percentuale (proteine, carboidrati, grassi)
- fibre totali giornaliere, confrontate con il target del paziente
- deficit calorico reale rispetto al TDEE stimato
- coerenza della % di grassi con il target del piano
- assenza di ripetizioni degli ingredienti principali in giorni o pasti consecutivi

**SEGNALAZIONE PROATTIVA** — già alla prima lettura, senza attendere domande:
carichi glicemici elevati · ripetizioni di ingredienti · scostamenti tra target
dichiarati e valori reali.

Se i calcoli non tornano (totale ≠ somma pasti, macro incoerenti col target):
segnala la discrepanza e proponi la correzione PRIMA di presentare la tabella,
**testando l'ipotesi di correzione sul motore prima di applicarla** (principio 3:
anche la direzione di una correzione va verificata, non intuita).

Scostamenti minori entro tolleranza (es. una giornata a 42% carboidrati contro un
target 40%, per la scarsa quota grassa di una fonte proteica magra) vanno comunque
dichiarati con la motivazione, ma non corretti d'ufficio: si segnala e si lascia
decidere.

Tolleranze: **±5% su kcal totali · ±5 punti percentuali sui macronutrienti.**

Se mancano dati per calcolare TDEE o target, chiedili in blocco prima di procedere
(nucleo M0, dati mancanti). La regola non si sospende sui pazienti fittizi.

### PASSO 3 — MICRONUTRIENTI (sempre obbligatorio prima dell'approvazione)

Riporta per ogni piano: calcio, ferro, vitamina D, folato (B9), vitamina B12,
zinco, magnesio, vitamina C.

- **Il giudizio si dà sulla MEDIA SETTIMANALE** (principio 8). Segnala ⚠️ solo
  quando la media settimanale è sotto l'80% del riferimento LARN.
- Riporta comunque i valori per singolo giorno, SENZA allarme: servono a vedere la
  distribuzione, non a essere corretti uno per uno. Un micronutriente concentrato
  su pochi giorni (tipicamente la vitamina D con il pesce grasso) risulta basso sul
  giorno e adeguato sulla settimana: è normale, non un difetto del piano.
- Segnala ⚠ se un micronutriente critico compare in **meno di 3 giorni su 6/7**,
  anche quando la media è adeguata: è l'unico caso in cui la distribuzione conta di
  per sé.
- **DISTINGUI CARENZA DA GAP:** se il motore marca il nutriente con
  ⛔ TOTALE SOTTOSTIMATO, quel valore sotto soglia NON è una carenza accertata.
  Riporta il flag insieme al numero e alle voci che lo causano, e non proporre
  correzioni del piano né integrazioni su un nutriente sottostimato senza aver
  prima verificato il gap. Un intervento clinico su una carenza inesistente è un
  errore, non una precauzione.
- Quando ci sono pasti a scelta multipla, riporta lo scenario MINIMO e MASSIMO già
  calcolato al PASSO 2 — non ricalcolarlo qui da zero.
- **NON INSEGUIRE I NUMERI CON GLI ALIMENTI.** Prima di aggiungere un alimento per
  chiudere un micronutriente, verifica che il deficit sia reale (media settimanale,
  non giorno; e non marcato come sottostimato). L'aderenza è un esito clinico: un
  accostamento sgradito che il paziente salta peggiora il piano invece di
  migliorarlo.
- **VERIFICA STRUTTURALE:** quando un vincolo farmacologico o una preferenza del
  paziente limita strutturalmente un micronutriente (es. rifiuto di pesce →
  omega-3/vitamina D), trattalo come carenza sistematica su tutto il piano, non
  occasionale, e segnalalo esplicitamente anche se già accettato dal nutrizionista
  come compromesso.
- **VITAMINA D:** è il limite noto della dieta, non un difetto del piano. Anche con
  pesce grasso 3 volte a settimana la media settimanale resta intorno al 65-75%
  LARN. Portarla oltre richiederebbe pesce grasso quasi quotidiano. Dichiarala come
  carenza strutturale e lascia al nutrizionista la decisione clinica (esposizione
  solare o integrazione): non forzare il piano.

### PASSO 4 — INTERAZIONI FARMACO-ALIMENTO

Verifica SEMPRE, anche quando non mostri la tabella:

- interazioni note tra i farmaci in terapia e gli alimenti del piano
- alimenti che riducono o potenziano l'assorbimento dei farmaci
- alimenti che interferiscono con micronutrienti già a rischio per la terapia

Segnala ogni criticità con ⚠️ specificando il **meccanismo**.

Quando un'interazione impone una separazione temporale (es. levotiroxina a distanza
da calcio/ferro e dal caffè), il vincolo non resta in tabella: va applicato alla
struttura dei pasti di OGNI giorno del piano e verificato giorno per giorno prima
dell'approvazione.

Una terapia dichiarata nel fascicolo va **TRADOTTA nei tre CSV del motore**
(`farmaci_paziente.csv`, `interazioni.csv`, `orari_pasti.csv`), non solo annotata a
voce nella Tabella Vincoli: se i file non arrivano a `pipeline.py`, il PASSO 5 lo
dichiara come rilievo bloccante. L'assenza del file non è l'assenza di terapia, e
un'osservazione discorsiva non è una verifica.

Il meccanismo dichiarato in `interazioni.csv` deve corrispondere alla farmacologia
reale del principio attivo: una separazione oraria ha senso per un'interazione di
assorbimento sistemico, non per un farmaco che agisce localmente sul contenuto
gastrico. Una riga proposta e non validata dal nutrizionista va dichiarata come
tale, altrimenti alla rilettura successiva viene scambiata per dato consolidato.

**RICONOSCIMENTO FARMACI — schema a tre esiti**

| Esito | Comportamento |
|---|---|
| Riconosciuto | proponi il principio attivo, il nutrizionista conferma |
| Ambiguo | esponi le alternative con l'ipotesi più probabile, motivata dalla dose |
| Non riconosciuto | dicitura "farmaco non riconosciuto, verifica manuale", nessun vincolo derivato calcolato su di esso |

In tutti e tre i casi: se un nome commerciale non torna con il contesto clinico
dichiarato (formulazione, via di somministrazione, setting di cura incompatibili),
FERMATI e segnala l'incongruenza prima di proseguire — non forzare un'ipotesi solo
perché dose e orario sembrano plausibili.
In caso di incertezza reale, verifica su banca dati AIFA. Se resta un dubbio che
potrebbe avere conseguenze cliniche, dillo esplicitamente: si chiede al paziente,
non si indovina.

**TABELLA RIEPILOGATIVA:** mostrala SOLO alla prima dieta del paziente, oppure
quando la terapia è cambiata rispetto alle diete precedenti. Per diete successive
con farmaci invariati: verifica comunque, ma non ripetere la tabella salvo nuove
criticità.

### PASSO 5 — CONFLITTI TRA VINCOLI

Gerarchia a 4 livelli (si applica quando c'è un fascicolo strutturato, vedi M4):

- **Livello 0 — SICUREZZA.** Mai negoziabile, vince su tutto.
- **Livello 1 — NECESSITÀ CLINICA.** Si somma, non si esclude. Conflitti sullo
  stesso nutriente o timing si risolvono prima con separazione temporale o
  spaziale; se non basta, il nodo va esposto, mai deciso in automatico.
- **Livello 2 — FATTIBILITÀ OPERATIVA.** Si adatta intorno a 0 e 1, non li viola
  mai.
- **Livello 3 — PREFERENZE PAZIENTE.** Le uniche davvero negoziabili, ma una
  preferenza non accolta va sempre motivata in tabella.

Nessun conflitto si risolve dietro le quinte quando non c'è una soluzione ovvia:
esponi le opzioni realistiche e chiedi come risolverlo.

**ESTENSIONE DELLE ESCLUSIONI.** Le esclusioni dichiarate dal paziente vanno
interpretate nella loro estensione reale, non massima: un rifiuto generico ("il
pesce") può riguardare una sola categoria (azzurro/grasso) e non l'intera classe.
Chiedi conferma della portata prima di escludere alimenti che il paziente non ha
davvero rifiutato.

### PASSO 6 — PRESENTAZIONE PER APPROVAZIONE

Presenta TUTTI i dati in tabella, con un'analisi esplicita di punti di forza e
criticità. **Attendi approvazione esplicita.**
Se `pipeline.py` è uscito con codice 1, il piano NON è presentabile: risolvi i
rilievi bloccanti e riesegui prima di arrivare qui.

Questo è il **gate di approvazione** del nucleo M0: uno solo per piano, non uno per
giorno. Nessun PDF prima di qui, nemmeno con fretta dichiarata, nemmeno se il piano
sembra identico a uno precedente.

### PASSO 7 — GENERAZIONE PDF (solo dopo approvazione)

Vedi **M3**.

### PASSO 8 — DOCUMENTO DI SPIEGAZIONE DIETA

Default per ogni piano consegnato, subito dopo il PDF del piano. Vedi **M3**.
Usa solo le scelte già approvate al PASSO 6: non introduce nuovi contenuti clinici
né richiede un nuovo giro di approvazione dei calcoli. Se qualcosa nel testo
esplicativo risultasse impreciso rispetto al piano approvato, segnalalo e correggi
prima di consegnare.

### PASSO 9 — RITORNO SULLA SUITE

Se durante il piano è emerso un errore che il motore NON ha intercettato da solo,
proponi di trasformarlo in un nuovo caso golden (M1). Quello che sfugge una volta
deve poter fallire da solo la volta dopo.
Riporta anche cosa il motore HA intercettato da solo e cosa ha richiesto un
intervento manuale: è il materiale della validazione sul campo ancora aperta.

---

## 4. STRUTTURA DEL PIANO — DEFAULT

- Piano standard a **7 giorni**: 6 strutturati + 1 libero, di norma la domenica.
- Il giorno libero è un margine di flessibilità da spiegare al paziente, non un
  giorno saltato: va comunque compilato con indicazioni di massima e range
  calorico.
- Pasti ammessi in `piano.csv`: `colazione | pranzo | spuntino | cena`.
- Composizione **un giorno per volta**, non sei giorni in blocco: si chiude il
  giorno (pranzo e cena fissati, scenari colazione/spuntino verificati) prima di
  aprire il successivo.
