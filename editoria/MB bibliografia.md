# MB — REGISTRO BIBLIOGRAFICO
Modulo operativo del progetto editoriale e formativo — Studio Taglialatela
Ultima modifica: 17/08/2026 · Dipendenze: nessuna · Rilievo R34

---

## 1. COSA FA QUESTO MODULO

Elimina la ricerca ripetuta. Ogni fonte trovata una volta resta disponibile per
sempre, con la citazione già formattata e la sintesi di cosa dice.

Due file, due funzioni diverse:

| File | Natura | Cambia |
|---|---|---|
| `MB_bibliografia.md` (questo) | Regole. Come si annota, come si cita. | Raramente |
| `fonti.csv` | Dati. Il registro delle fonti effettive. | A ogni sessione |

Il registro NON è un archivio da consultare a fine lavoro. È una **cache**: si
legge PRIMA di cercare, perché una fonte già presente non va ricercata.

---

## 2. CARICAMENTO E ACCESSO ALLE FONTI

### 2.1 Caricamento del registro — da GitHub, con `curl`

Base raw:
`https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/editoria/`

Con `bash` + `curl`, non con web_fetch (su GitHub fallisce spesso per robots.txt).

```
curl -s .../editoria/MB_bibliografia.md
curl -s .../editoria/fonti.csv
```

Si carica UNA VOLTA per sessione. Se il caricamento fallisce, si dichiara e ci
si ferma: non si procede a memoria su un registro non letto, perché il rischio
è duplicare ID e produrre due righe con lo stesso numero.

### 2.2 Accesso alle FONTI — non con `curl`

*Sezione aggiunta il 14/08/2026. Prima di questa revisione il modulo lasciava
intendere che `curl` fosse la via generale di accesso: non lo è.*

**Il `bash` del motore ha rete limitata a una whitelist** — GitHub, PyPI, npm,
USDA e poco altro. `curl` **non raggiunge** PubMed Central, Normattiva, ISS,
AIFA, bjgp.org né alcuna rivista. Vale per il download di un PDF quanto per una
pagina HTML. Tentare `curl` su un dominio fuori whitelist non produce un errore
di rete interpretabile: produce un fallimento che somiglia a un sito irraggiungibile.

Per tutto ciò che non è GitHub si usa **`web_fetch`**, con un vincolo:

> **`web_fetch` accetta solo URL già comparsi in conversazione** — forniti
> dall'autore o restituiti da una ricerca precedente. Un indirizzo composto a
> mano viene respinto con `PERMISSIONS_ERROR`, anche quando il pattern è noto e
> corretto.

Sequenza obbligatoria: **prima `web_search`, poi `web_fetch` sul risultato.**
Mai comporre l'indirizzo a mano per risparmiare una ricerca. Verificato per
contrasto nella stessa sessione: URL da ricerca accettati, URL costruito
respinto.

### 2.3 Ostacoli noti — da dichiarare, non da ritentare

| Fonte | Stato | Via praticabile |
|---|---|---|
| PubMed Central | reCAPTCHA anche su `web_fetch` | consegna manuale del PDF |
| Wiley | bot detection | consegna manuale |
| LWW, Ovid | **402** anche su open access | consegna manuale |
| `parlamento.it` | blocca | **`leg14.camera.it` funziona** |
| `normattiva.it` | richiede sessione | `gazzettaufficiale.it/eli/id/AAAA/MM/GG/<codice>/sg`, poi `vediMenuHTML` |
| `aifa.gov.it` | rifiuta `curl` con 403 | **`web_fetch` sui PDF AIFA funziona** |
| `medicinali.aifa.gov.it` | SPA, API gateway in 400 | lettura per immagine (sezione 5.3) |
| `bjgp.org` | nessun ostacolo | `web_fetch` diretto |
| `salute.gov.it` | sfida browser Gcore: respinge `web_fetch` e `curl` | consegna manuale del PDF |
| `utifar.it/articoli/…` | nessun ostacolo | **`web_fetch` diretto sull'indice per categoria** |
| `utifar.it/flip`, `publications.mazzmedia.com` | visore sfogliabile, testo non nel markup | trascrizione manuale |
| `api.github.com` | rate limit | pagina HTML dell'albero del repo |

**Indice per categoria di `utifar.it`** *(R22, 15/08/2026 — corregge quanto
dichiarato in un passaggio precedente).* L'indirizzo
`utifar.it/articoli/127.html?cat=N` **è leggibile** con `web_fetch` e restituisce
gli URL degli articoli di quella rubrica. È il canale rapido: una chiamata dà
tutti i link, senza `web_search` preliminare. Il vincolo generale della sezione
2.2 resta — l'URL dell'indice deve essere già comparso in conversazione — ma una
volta comparso l'indice, gli URL dei singoli articoli arrivano da lì e sono
quindi utilizzabili.

**Regola sugli ostacoli.** Dopo due tentativi falliti su una via, si dichiara
l'ostacolo reale e si chiede la consegna manuale del documento, invece di
insistere in silenzio. La consegna manuale ha funzionato ogni volta che è stata
usata: due full text in una sessione, tre RCP in un'altra. Non è un ripiego di
serie B, è il canale normale per le fonti dietro barriera.

**Ogni richiesta di consegna manuale porta il link** *(R34, 17/08/2026)*
Una richiesta di apertura di una fonte contiene sempre l'**indirizzo diretto da
incollare**, uno per fonte, in elenco. Mai «cerca su PubMed», mai il solo PMID:
l'onere di comporre l'indirizzo non si scarica sull'autore, che lavora spesso da
cellulare, e un indirizzo composto a mano da lui corre lo stesso rischio di
errore di uno composto da qui.

Forme canoniche:
- PubMed: `https://pubmed.ncbi.nlm.nih.gov/<PMID>/`
- full text libero: `https://pmc.ncbi.nlm.nih.gov/articles/<PMCID>/`
- DOI: `https://doi.org/<doi>`
- Gazzetta Ufficiale: la scheda ELI, `.../eli/id/AAAA/MM/GG/<codice>/sg`

Se l'identificatore non è ancora stato riscontrato, il link si dà lo stesso e si
dichiara accanto che è da confermare: una pagina sbagliata si riconosce in due
secondi, una ricerca mancata costa un giro di sessione.
Si dichiara anche **che cosa serve** di quella fonte — abstract o testo
integrale — perché sono due fatiche diverse (sezione 6.3).

---

## 3. SCHEMA DEL CSV

Separatore `|` — la barra verticale. Non la virgola (presente in ogni citazione)
e non il punto e virgola, che il formato Vancouver usa internamente
(`Anno;volume(fascicolo):pagine`). La barra è l'unico carattere che non compare
mai in una citazione biomedica.

| Campo | Contenuto | Note |
|---|---|---|
| `id` | `F001`, `F002`, … | Progressivo, mai riutilizzato anche se una riga viene rimossa |
| `livello` | `1`-`4` | Gerarchia delle fonti (sezione 5) |
| `tipo` | `RCP`, `normativa`, `linea_guida`, `review`, `studio`, `dato_istituzionale` | Vocabolario chiuso |
| `citazione` | Riferimento completo in stile Vancouver | Punto e virgola ammessi: il separatore è `\|` |
| `identificatore` | PMID, DOI o URL | Uno solo, il più stabile disponibile |
| `data_documento` | `AAAA-MM-GG` o `AAAA-MM` o `AAAA` | La data DELLA FONTE, non della consultazione |
| `data_consultazione` | `AAAA-MM-GG` | Obbligatoria per fonti web |
| `temi` | `T1`,`T2`,… separati da virgola | Vedi sezione 4 |
| `usata_in` | Nome del modulo o articolo | `-` se raccolta ma non ancora usata |
| `esito_sintetico` | Cosa dice, in una riga | Il campo più importante |
| `stato` | `verificata`, `abstract_verificato`, `da_verificare`, `da_reperire`, `superata` | Vedi sezione 6 |
| `conflitto_dichiarato` | `na`, `no`, `non_dichiarato`, `si_neutro`, `si_concorde` | **Campo aggiunto il 14/08/2026.** Vedi sezione 5.4 |

**Posizione del campo nuovo: ultima.** Un campo aggiunto in coda non sposta la
posizione dei campi esistenti, quindi non rompe una lettura posizionale già
scritta. Le righe preesistenti sono state completate a mano, non lasciate corte:
un CSV con righe di lunghezza diversa è un CSV che si romperà più avanti, in
silenzio.

**Valori di `conflitto_dichiarato`**

| Valore | Quando |
|---|---|
| `na` | Non applicabile: normativa, RCP, documento regolatorio |
| `no` | Gli autori dichiarano esplicitamente di non avere conflitti |
| `non_dichiarato` | **La fonte non contiene alcuna dichiarazione.** Vedi sotto |
| `si_neutro` | Conflitto dichiarato, ma non allineato alla conclusione |
| `si_concorde` | **Conflitto dichiarato allineato alla conclusione.** Richiede azione |

**Perché `no` e `non_dichiarato` sono due valori diversi** *(R18b, 15/08/2026)*.
Il vocabolario originale ne aveva uno solo, e obbligava a scrivere `no` — cioè
«nessun conflitto» — anche per una fonte che semplicemente non dice nulla.
Sono due situazioni opposte quanto ad affidabilità: chi dichiara di non avere
conflitti si è assunto la responsabilità di quell'affermazione; chi tace non ha
detto niente, e il silenzio non è una smentita. Molti documenti istituzionali e
quasi tutte le fonti anteriori al 2010 stanno nel secondo caso.

Uso: `non_dichiarato` non richiede azione, ma **non conta come ancoraggio
indipendente** ai sensi della sezione 5.4. Se un'affermazione portante poggia su
una fonte `si_concorde` e l'unica seconda fonte disponibile è `non_dichiarato`,
la nota nel testo va scritta lo stesso.

**Sul campo `esito_sintetico`.** È quello che rende il registro utile invece che
solo ordinato. Una fonte di cui non si ricorda la conclusione va riletta, e
rileggerla costa quanto ricercarla. Scrivere la conclusione operativa, non il
titolo riformulato: «nessuna differenza significativa vs placebo a 12 settimane»
è utile, «studio sull'efficacia di X» non lo è.

---

## 4. CODICI TEMA

| Codice | Tema |
|---|---|
| `T1` | Ricognizione e riconciliazione della terapia farmacologica |
| `T2` | Interazioni farmaco-alimento e farmaco-integratore |
| `T3` | Privacy, consenso informato e dati sanitari nei servizi |
| `T4` | Deprescribing e paziente anziano polifarmaco |
| `T5` | Counseling nelle affezioni minori |
| `T6` | Categorie di integratori al banco: interazioni per prodotto |
| `T0` | Trasversale (dati di settore, contesto normativo generale) |

Una fonte può servire più temi. È il caso normale, non l'eccezione: gli RCP
valgono per T1 e T2 insieme, e questo è esattamente il punto del progetto.

---

## 5. GERARCHIA DELLE FONTI

### 5.1 I quattro livelli

| Livello | Cosa | Esempi |
|---|---|---|
| 1 | Regolatorie | RCP da AIFA, EPAR EMA, testi da Normattiva |
| 2 | Linee guida e consenso | ISS/SNLG, società scientifiche, Manuale FOFI |
| 3 | Revisioni sistematiche | Cochrane, review indicizzate |
| 4 | Studi primari | Singoli trial, studi osservazionali |

Regola: mai una raccomandazione operativa basata su un solo studio di livello 4.

### 5.2 Cosa NON entra nel registro

Riviste di settore, siti divulgativi, schede prodotto aziendali, blog,
aggregatori di foglietti illustrativi. Si leggono per orientarsi; poi si risale
alla fonte che citano e si registra quella. Se un'affermazione esiste solo su
una rivista di settore e non è tracciabile a monte, non si usa.

**Indagini commissionate da associazioni di categoria — escluse.**
*Regola aggiunta il 14/08/2026.* Le cifre di consumo che circolano sul settore
integratori (decine di milioni di utilizzatori, mercato da miliardi) provengono
da indagini di società di ricerca commissionate dall'associazione dei
produttori. Non sono dati istituzionali e non hanno metodo pubblicato
verificabile: si escludono con la stessa logica delle riviste di settore, anche
quando sono le uniche cifre disponibili sul mercato italiano.
Conseguenza accettata: talvolta l'unico dato utilizzabile sarà straniero. Si usa
**dichiarandolo come straniero nel testo**, che è preferibile a un dato italiano
di provenienza interessata. Nessuna classifica di vendita si afferma su questa
base; ciò che si può dire è cosa arriva più spesso al banco, dichiarato
esplicitamente come esperienza professionale.

### 5.3 Modalità di lettura ammesse per il livello 1

Gli RCP sono la fonte di riferimento per gli intervalli di somministrazione, e
l'accesso è ostacolato: `medicinali.aifa.gov.it` è una SPA il cui markup non
contiene i documenti, e il gateway che serve i PDF risponde 400 sia in ricerca
sia in download. Le copie su siti terzi sono spesso verbatim ma **di versione
non verificabile: non sono la fonte.**

È quindi modalità legittima di verifica di livello 1 la
**lettura per immagine dello stampato AIFA**: schermate del documento aperto sul
portale, consegnate in conversazione.

Obblighi quando si usa:
- registrare nell'`esito_sintetico` la formula «letto per immagine dello
  stampato AIFA»
- registrare la data **«documento reso disponibile da AIFA il …»**, leggibile
  nel piè di pagina di ogni schermata: è quella la data del documento, non
  quella della consultazione
- verificare che le schermate coprano la sezione citata per intero (4.2, 4.5),
  non solo il capoverso che serve

Ha funzionato: tre RCP in due giri.

### 5.4 Conflitto di interessi degli autori della fonte

*Regola aggiunta il 14/08/2026. Colma un vuoto reale: MA principio 6 copre il
conflitto dell'autore verso il committente, e nessun modulo diceva cosa fare del
conflitto degli autori di una fonte citata.*

Il caso che l'ha prodotta: una review indicizzata di livello 3, formalmente
ineccepibile, con tre autori su quattro dipendenti di un produttore, e una
conclusione che raccomanda proprio la categoria di prodotto del datore di
lavoro. Il conflitto era dichiarato dagli autori — cioè il sistema aveva
funzionato — ma il registro non aveva un posto dove metterlo.

**La dichiarazione di conflitto si legge sempre**, e si registra in
`conflitto_dichiarato`. Quando vale `si_concorde`, cioè quando l'interesse punta
nella stessa direzione della conclusione, si sceglie una delle due strade:

1. **Ancoraggio indipendente** — si cerca una seconda fonte senza quel conflitto
   che sostenga lo stesso punto, e si cita quella. Preferibile.
2. **Dichiarazione in nota** — si usa la fonte, dichiarando il conflitto nel
   testo. Ammessa quando l'ancoraggio non si trova.

Nel caso reale entrambe hanno funzionato: la nota era stata scritta, e
l'ancoraggio indipendente è poi arrivato da un RCP che elencava la stessa
sostanza fra gli induttori enzimatici.

**Una fonte con conflitto dichiarato non è squalificata.** Chi dichiara è più
affidabile di chi non dichiara. Il campo serve a sapere cosa si sta usando, non
a escludere.

---

## 6. STATI

- `verificata` — testo integrale letto, citazione controllata sulla fonte
- `abstract_verificato` — letto l'**abstract completo sulla pagina della fonte o
  su PubMed**, full text non accessibile (paywall). **Usabile**, ma solo per ciò
  che l'abstract afferma davvero: le conclusioni sintetiche, non i dettagli di
  metodo o i sottogruppi
- `da_verificare` — citazione presa da un riferimento indiretto o da uno
  snippet, non ancora aperta di persona. **Non usabile in un deliverable**
- `da_reperire` — si sa che esiste, non si è ancora trovato il testo
- `superata` — sostituita da una versione più recente. Non si cancella: si
  marca, così un modulo vecchio che la cita resta interpretabile

### 6.1 Uno snippet di ricerca NON è un abstract verificato

*Regola resa esplicita il 14/08/2026 dopo tre errori documentati, tutti e tre
plausibili e tutti e tre sbagliati.*

Il frammento di testo che un motore di ricerca mostra sotto un risultato è
selezionato per pertinenza alla query, non per rappresentatività della fonte.
Sistematicamente restituisce l'affermazione più netta e lascia fuori la
condizione che la qualifica. Un contenuto costruito su snippet non è
approssimativo: è **specificamente** sbagliato nel punto che conta.

I tre casi:

- una review sul pompelmo, da snippet: «distanziare non evita l'interazione».
  Full text: distanziare **attenua** — effetto dimezzato a 10 ore, un quarto a
  24. Il senso pratico si salvava, il meccanismo era sbagliato
- una review sugli anticoagulanti: **citazione attribuita agli autori
  sbagliati**, presi da un riferimento indiretto. Sarebbe finita in bibliografia
- una review sull'iperico, da snippet: «l'iperico induce CYP3A4». Vero e
  inutile: il full text mostra che il determinante è la dose giornaliera di
  iperforina, con soglia di 1 mg/die e variabilità di trenta volte fra prodotti
  commerciali. La conclusione pratica sarebbe stata sbagliata

Conseguenze operative:

1. Una fonte letta solo nello snippet entra a registro come `da_verificare`, mai
   come `abstract_verificato`. `abstract_verificato` richiede di aver **aperto**
   la pagina dell'abstract
2. **La citazione — autori, rivista, anno, volume — si controlla sulla fonte
   primaria o su PubMed, mai sullo snippet e mai su un riferimento indiretto.**
   Una citazione sbagliata è l'errore che sopravvive più a lungo, perché nessuna
   rilettura del proprio testo lo rivela
3. Quando lo snippet e il testo integrale divergono, l'`esito_sintetico`
   registra la versione del testo integrale e, se utile, che cosa lo snippet
   faceva credere: è un'informazione che serve alla sessione dopo

### 6.2 Una fonte verificata può avere incoerenze interne

Promemoria, non regola bloccante. In una review verificata il testo discorsivo
dichiarava tre trial di intervento dove il diagramma PRISMA e la tabella dei
risultati ne riportavano due.

Quando un numero compare sia in prosa sia in tabella, **si prende dalla
tabella**. La prosa è il punto in cui gli errori di redazione si accumulano;
tabelle e diagrammi sono generati dai dati.

### 6.3 Perché `abstract_verificato` esiste

Molte revisioni sistematiche hanno il full text a pagamento. Pretendere il testo
integrale per ogni fonte renderebbe la regola impossibile da rispettare, e una
regola impossibile viene aggirata: si finirebbe per marcare `verificata` una
fonte letta a metà, che è esattamente il rischio da cui il registro deve
proteggere. Meglio uno stato onesto e un uso limitato.

Regola d'uso: da un `abstract_verificato` si può ricavare la conclusione
generale, mai un numero specifico, un sottogruppo o un dettaglio di metodo. Per
quelli serve il testo.

La distinzione tra ciò che si è letto e ciò che si è dedotto è la sola che
protegge dal citare una fonte che non dice quello che si crede. Va rispettata
anche quando sembra pedante.

---

## 7. COMPORTAMENTO OPERATIVO

**All'apertura del lavoro su un tema**
Leggo `fonti.csv` filtrando sul codice tema. Dichiaro cosa c'è già. Solo dopo
cerco il mancante. Se una fonte serve ed è già a registro, la uso senza
ricercarla.

**Durante la stesura**
Ogni affermazione tecnica riceve l'`id` della fonte nel momento in cui viene
scritta, in linea, nella forma `[F014]`. Non a fine paragrafo, non a fine
sezione. Le fonti nuove vengono accumulate in coda man mano, non raccolte alla
fine.

**Se un'affermazione non ha fonte**
La segnalo come buco e mi fermo su quel punto. Non la scrivo «in attesa di
riferimento»: un'affermazione senza fonte in una bozza tende a sopravvivere fino
al deliverable.

**A fine sessione**
Produco due cose, sempre, senza che vengano richieste:
1. Le righe NUOVE in formato CSV pronte da incollare, con gli ID già assegnati
   in continuità con l'ultimo presente nel file
2. Il file `fonti.csv` completo e aggiornato, come allegato scaricabile

**Assegnazione degli ID**
Leggo l'ultimo `id` presente e proseguo. Mai ripartire da `F001`. Mai riusare un
id di una riga rimossa.

**Stato reale del file online**
Prima di dichiarare che il registro online è indietro rispetto alla copia di
lavoro, lo si scarica e si contano le righe. Il 14/08/2026 un documento di
passaggio dichiarava il file online fermo a 3 righe: ne conteneva 15, già
aggiornate. Un conteggio costa una riga di comando.

---

## 8. AGGIORNAMENTO DEL FILE — passaggio manuale

Il caricamento su GitHub non è automatizzabile da qui: va fatto a mano.

Pagina di upload della cartella:
`https://github.com/giuseppetaglialatela/studio-taglialatela-template/upload/main/editoria`

Si trascina il `fonti.csv` aggiornato, stesso nome, e si preme «Commit changes»
in fondo alla pagina — passaggio che da cellulare finisce sotto la piega.

**Questo è il punto debole del sistema e va detto chiaramente**: se il file non
viene ricaricato a fine sessione, il lavoro di annotazione di quella sessione è
perso e alla successiva le stesse fonti verranno ricercate da capo. Il registro
vale quanto la costanza con cui viene aggiornato.

Mitigazione: il file completo va consegnato in conversazione a fine sessione
insieme al link diretto sopra, così il caricamento è un gesto di trenta secondi
e non un compito da ricordare.

---

## 9. FONTI IN LINGUA INGLESE — REGOLE DI RESA

La maggior parte delle fonti di livello 3 e 4 è in inglese; il contenuto è in
italiano. La traduzione è il punto in cui una fonte corretta diventa
un'affermazione falsa, e nessun controllo formale lo intercetta.

**La forza dell'affermazione non si aumenta mai in traduzione.**

| Inglese | Resa corretta | Resa VIETATA |
|---|---|---|
| may reduce | potrebbe ridurre | riduce |
| is associated with | è associato a | causa, determina |
| suggests | suggerisce | dimostra, prova |
| in a small cohort | in una casistica limitata | negli studi |
| further research is needed | i dati non sono conclusivi | *omissione* |
| trend towards | tendenza non significativa | miglioramento |
| significant | statisticamente significativo | rilevante, importante |

**Tre regole**

1. **`significant` non è «significativo» in senso comune.** In italiano
   divulgativo «significativo» suggerisce rilevanza clinica; in statistica
   indica solo che il risultato non è attribuibile al caso. Si scrive sempre
   «statisticamente significativo», o si riporta la rilevanza clinica come cosa
   distinta.

2. **I limiti dichiarati dagli autori si riportano.** Se l'abstract dice
   *further research is needed*, quella frase fa parte del risultato. Ometterla
   non è sintesi: è alterazione.

3. **I termini regolatori non si traducono a intuito.** `off-label`,
   `black box warning`, `boxed warning`, `contraindication`, `precaution`,
   `interaction` hanno un corrispettivo italiano preciso nell'RCP AIFA: si
   verifica lì, non si improvvisa.

**Quando la resa è incerta**, si riporta anche il termine originale tra
parentesi. Appesantisce, ma è preferibile a un'affermazione più forte
dell'originale.

---

## 10. PRODUZIONE DELLA BIBLIOGRAFIA FINALE

Da `fonti.csv` filtrato su `usata_in`, in stile Vancouver numerato secondo
l'ordine di prima comparsa nel testo — non l'ordine degli `id`, che è di
registro.

Formato: Autori. Titolo. Rivista. Anno;volume(fascicolo):pagine. DOI o PMID.

Per documenti istituzionali e RCP: Titolo del documento. Ente. Data del
documento. URL [consultato il GG/MM/AAAA].

Per un RCP letto per immagine: Riassunto delle caratteristiche del prodotto.
Nome. AIFA, documento reso disponibile il GG/MM/AAAA.

Misura attesa: 20-30 voci per un modulo FAD, 8-12 per un articolo di rivista.
Cinquanta voci su un modulo di due ore segnalano accumulo, non rigore.

**Quando l'intervallo non è raggiungibile** *(R17, 15/08/2026)*. Se la ricerca
bibliografica è stata **esclusa a monte** — perché il lavoro riusa solo fonti già
a registro, perché il committente ha imposto un perimetro chiuso, o perché il
tema non ha letteratura indicizzata — l'intervallo di MD diventa irraggiungibile
per costruzione. In quel caso:

1. non si gonfia la bibliografia con voci non usate nel testo, per arrivare al
   numero. Una voce in bibliografia che non regge alcuna affermazione è arredo;
2. si dichiara nel verdetto di collaudo **perché** l'intervallo non è
   raggiungibile, con la formula «ricerca esclusa a monte: [motivo]»;
3. il rilievo Q5 di ME si scrive come **rilievo dichiarato e giustificato**, non
   come scarto.

Il caso opposto — bibliografia sotto l'intervallo perché la ricerca è stata
fatta male — non si distingue dal precedente guardando il numero. Si distingue
solo dalla dichiarazione, ed è il motivo per cui la dichiarazione è obbligatoria.

Una fonte con `conflitto_dichiarato = si_concorde` usata senza ancoraggio
indipendente porta la nota nel testo, non solo nel registro: il lettore della
bibliografia non vede il CSV.

---

## 11. FONTI E MODELLI SONO DUE COSE DIVERSE

*Sezione aggiunta il 15/08/2026 (R20).*

Il caso che l'ha prodotta: otto articoli di `Nuovo Collegamento` sono stati letti
e misurati per capire come scrive quella testata. Nessuno di essi regge
un'affermazione tecnica del nostro testo, e nessuno deve entrare in `fonti.csv`.

| | **Fonte** | **Modello di forma** |
|---|---|---|
| A che serve | reggere un'affermazione | capire come si scrive per quella destinazione |
| Dove si registra | `fonti.csv` | `schede_testata.md` |
| Che cosa se ne estrae | il contenuto | la misura: lunghezza, capoverso, apparati, registro |
| Entra in bibliografia | sì | **mai** |
| Gerarchia dei livelli | si applica | non si applica |

**Perché la distinzione va tenuta.** Una rivista di settore è esclusa dal
registro delle fonti (sezione 5.2) e resta preziosa come modello: sono due
giudizi su due proprietà diverse dello stesso oggetto. Confonderli produce
entrambi gli errori possibili — citare una rivista di settore come se fosse una
fonte, oppure rifiutarsi di leggerla perché «non è una fonte» e scrivere alla
cieca per quella testata.

**Regola operativa.** Un pezzo letto come modello:

- non riceve mai un `id` `Fxxx`;
- non porta mai un marcatore `[Fxxx]` nel testo;
- si annota nella scheda della testata, con firma, numero, data e le misure;
- se contiene un'affermazione tecnica che serve davvero, **non si cita il pezzo**:
  si risale alla fonte che cita e si registra quella (sezione 5.2).

Le regole di compilazione delle schede di testata stanno in MD; il file di dati
è `schede_testata.md`, che sta a MD come `fonti.csv` sta a questo modulo.

---

## 12. CONTROLLO DI CORRISPONDENZA DEI RICHIAMI

La passata di CORRISPONDENZA si esegue **dal corpo del testo verso
l'apparato**, mai nella direzione opposta.

**Perché la direzione conta.** Partendo dall'elenco delle note e verificando che
ciascuna punti alla voce giusta si trovano le note mal assegnate, ma NON si
trova una nota che nel testo non è mai richiamata: quel controllo non guarda il
corpo, quindi un richiamo mancante gli è invisibile per costruzione. Partendo
invece dai richiami presenti nel testo si trovano entrambe le classi di difetto.

**I tre difetti che il controllo deve isolare.**

| Difetto | Definizione | Come si manifesta |
|---|---|---|
| Nota orfana | voce nell'apparato senza alcun richiamo nel corpo | numero assente dall'insieme dei richiami |
| Richiamo cieco | richiamo nel corpo senza voce corrispondente | numero presente nel corpo, assente dall'apparato |
| Buco di numerazione | serie non contigua | un numero manca da entrambi gli insiemi |

**Procedura.** Si estraggono i richiami dal corpo con una espressione regolare,
si costruisce l'insieme dei numeri richiamati, lo si confronta con l'insieme dei
numeri dell'apparato, si riportano le differenze nelle due direzioni. Il testo
del corpo va isolato dall'apparato prima dell'estrazione, altrimenti gli anni e
i numeri di volume delle voci bibliografiche entrano nel conteggio come falsi
richiami.

```python
import re
corpo, apparato = testo.split(MARCATORE_APPARATO)
richiami = {int(d) for m in re.finditer(r'[.\u2019a-z\u00e0-\u00f9)]((?:\d{1,2})(?: \d{1,2})*)(?=\s|$)', corpo)
            for d in m.group(1).split()}
note = {int(m.group(1)) for m in re.finditer(r'^\*\*(\d+)\.', apparato, re.M)}
print('orfane:', sorted(note - richiami))
print('cieche:', sorted(richiami - note))
```

L'espressione va tarata sul documento: le note cumulative con richiami adiacenti
(`.17 18`) vanno lette come due numeri, e i decimali con la virgola non vanno
confusi con i richiami. Il risultato dell'estrazione si ispeziona una volta con
il contesto a fianco prima di fidarsene, per riconoscere i falsi positivi
(tipicamente i rimandi interni del tipo «paragrafo 2.1»).

**Quando si esegue.** Dopo ogni riscrittura, non solo alla chiusura della
passata. Una riscrittura può far cadere un paragrafo intero senza che nulla lo
segnali: il titolo del sottoparagrafo resta, il testo sparisce, e con esso il
richiamo che conteneva.

**Occorrenza documentata.** 27/08/2026, tesi tirzepatide, capitolo 2. La passata
di corrispondenza era stata dichiarata chiusa «su tutti e 21 i richiami», ma i
richiami effettivi erano venti: mancava il 13. Il sottoparagrafo che lo
conteneva aveva perso il testo fra due versioni conservando il titolo, e con
esso era sparita una discussione sostanziale. Il controllo condotto dalle note
verso la bibliografia non poteva vederlo; il controllo inverso lo ha isolato in
una riga.
