# ME — COLLAUDO PRE-CONSEGNA
Motore di scrittura scientifica — settore farmacia
Ultima modifica: 17/08/2026 · Dipendenze: MB, MD, MA · Rilievi R25, R30

---

## PRINCIPIO

Un contenuto formativo difettoso non si annuncia: passa il controllo del
committente, viene erogato, e il problema emerge quando qualcuno lo verifica.
Per questo il collaudo si esegue sempre, anche quando il lavoro sembra pulito, e
soprattutto quando c'è fretta.

**Se un controllo bloccante fallisce, non si consegna.** Si segnala e si
corregge.

---

## CONTROLLI BLOCCANTI

Il fallimento di uno solo di questi impedisce la consegna.

**B1 — Tracciabilità**
Ogni affermazione tecnica porta un `[Fxxx]`.
*Come si verifica*: rilettura mirata alle frasi di raccordo e alle
introduzioni di sezione, dove le affermazioni non marcate si annidano. In un
caso reale il controllo ne ha trovate sette, di cui una priva di qualsiasi fonte.

*Registrazione della casistica* — **R16, aggiunto il 15/08/2026.** B1 non si
chiude con un sì o un no: si scrive nel verdetto **quante** affermazioni non
marcate sono state trovate, **dove** stavano e **quante di esse erano prive di
fonte** e non solo di marcatore. Le due cose sono diverse: un marcatore
dimenticato è un difetto di trascrizione, un'affermazione senza fonte è un
difetto di merito, e solo la seconda avrebbe reso il contenuto indifendibile.

Formula nel verdetto: `B1 — 7 non marcate (5 raccordi, 2 aperture di sezione),
di cui 1 priva di fonte`. Un `B1 superato` senza numeri non dice se il controllo
ha trovato zero o non è stato fatto.

Perché si registra: la casistica accumulata su più lavori dice **dove** il
motore perde i marcatori, e quella è l'unica informazione che permette di
correggere la stesura invece di ripararla ogni volta in collaudo. Finché i punti
sono sempre gli stessi — raccordi e aperture — la correzione sta in MC PASSO
7.2, non qui.

**B2 — Fonti verificate**
Ogni fonte citata ha stato `verificata` o `abstract_verificato`. Nessuna
`da_verificare` o `da_reperire` compare nel deliverable.
*Controllo aggiuntivo sulle `abstract_verificato`*: da queste non deve essere
stato tratto alcun numero specifico, sottogruppo o dettaglio di metodo — solo la
conclusione generale.
*Controllo aggiuntivo sulle citazioni*: autori, rivista e anno di ogni voce di
bibliografia risultano controllati sulla fonte primaria o su PubMed, **mai su un
riferimento indiretto o su uno snippet di ricerca**. È già accaduto che una
review venisse attribuita agli autori sbagliati, presi da una citazione di
seconda mano: nessuna rilettura del proprio testo rivela quell'errore.

**B3 — Copertura degli obiettivi**
Ogni `OF` è coperto da almeno una sezione del testo scritto — non solo dallo
scheletro — e, per i moduli FAD, da almeno 3 domande del test.

**B4 — Giustificazione delle sezioni**
Ogni sezione è riconducibile a un `OF`. Nessuna sezione orfana.
*Eccezione ammessa nel formato articolo*: una chiusura narrativa non mappata su
alcun obiettivo è ammissibile, purché dichiarata come tale nel verdetto. Nel
formato FAD non lo è.

**B5 — Metodo non millantato**
La parola «GRADE» compare solo dove si riporta il grading di una fonte che lo
possiede, con la citazione. Non compare mai accanto a un giudizio prodotto
internamente.
Lo stesso per «revisione sistematica», «meta-analisi», «consenso di esperti».

**B6 — Dati numerici**
Ogni numero (prevalenza, consumo, percentuale, costo) risale a una fonte
primaria di livello 1 o 2. Nessun dato proveniente da rivista di settore, sito
divulgativo o **indagine commissionata da un'associazione di produttori**
(MB sezione 5.2). Un dato straniero dichiarato come straniero passa il
controllo; un dato italiano di provenienza interessata no.
Dove un numero compare sia in prosa sia in tabella della fonte, è stato preso
dalla tabella.

**B7 — Indipendenza**
Due verifiche distinte, che non vanno confuse:
1. *Verso il committente*: se ha interessi commerciali sul tema, la situazione è
   stata dichiarata e valutata. Nessun contenuto su un medicinale soggetto a
   prescrizione commissionato da chi lo produce o distribuisce.
2. *Verso le fonti*: nessuna fonte con `conflitto_dichiarato = si_concorde`
   regge un'affermazione portante **senza** ancoraggio indipendente o nota nel
   testo (MB sezione 5.4). Il campo si legge sul registro, non a memoria.
   Una fonte `non_dichiarato` **non vale come ancoraggio indipendente**: il
   silenzio della fonte sul conflitto non è una smentita (MB sezione 3).

La seconda verifica sta qui e non fra i controlli di qualità perché è dello
stesso tipo della prima: entrambe riguardano se il lettore può fidarsi di chi
scrive.

**B8 — Completezza del pacchetto**
Tutti gli elementi previsti da MD per il formato di destinazione sono presenti.
Un elemento consegnato con segnaposto espliciti (tipicamente la nota biografica)
conta come presente, purché il segnaposto sia dichiarato nel verdetto.

**B9 — Fedeltà della traduzione**
Per ogni affermazione derivata da fonte in inglese, la forza dell'enunciato
italiano non supera quella dell'originale. Si controllano in particolare:
- i verbi modali (`may`, `might`, `could`) non resi con l'indicativo
- `is associated with` non reso con un nesso causale
- `significant` reso come «statisticamente significativo»
- i limiti dichiarati dagli autori riportati e non omessi

*Come si verifica*: si riapre la fonte per le affermazioni portanti — quelle su
cui poggia una raccomandazione operativa — e si confronta. Non per tutte: per
quelle che, se sbagliate, cambierebbero il comportamento del lettore al banco.

**B10 — Le misure sono state eseguite**
*Controllo aggiunto il 14/08/2026.*

Bloccante è **il fatto di aver misurato**, non il valore che ne esce. Tre
grandezze, tutte calcolate sul testo finito e nessuna stimata:

| Grandezza | Come si ottiene |
|---|---|
| Lunghezza del corpo | conteggio, con la convenzione di MD dichiarata accanto |
| Ripartizione sostanza / strumentale | conteggio per sezione, secondo la classificazione di MC PASSO 1.1 |
| Posizione della prima informazione usabile | battute dall'inizio ÷ totale |

Il controllo fallisce quando una di queste è dichiarata a stima, o non è stata
calcolata affatto. Un «rientra nel formato» senza numero **non passa B10**.

*Perché è bloccante la misura e non la soglia.* Le tre soglie — 65% di sostanza,
15% per la prima informazione usabile, 15 punti di scostamento dalla stima del
GATE 1 — nascono da un caso solo e non sono ancora tarate su una serie. Una
soglia mal calibrata resa bloccante costringerebbe a riscritture non
giustificate. La misura, invece, o c'è o non c'è: renderla obbligatoria costa
tre conteggi e restituisce all'autore un numero su cui decidere. Le soglie
stanno quindi in Q9, e si valuterà se promuoverle dopo tre o quattro lavori.

---

## CONTROLLI DI QUALITÀ

Il fallimento non blocca la consegna ma va segnalato all'autore.

**Q1 — Verbi degli obiettivi**
Nessun obiettivo usa «conoscere», «comprendere», «essere consapevole».

**Q2 — Attualità dichiarata**
La data di aggiornamento riflette la fonte più recente utilizzata, non la data
di consegna. Se una linea guida o un RCP di riferimento ha più di 5 anni, è
segnalato nel testo.

**Q3 — Applicabilità**
Ogni sezione tecnica si chiude con l'implicazione operativa al banco.

**Q4 — Qualità dei distrattori**
Nel test, nessuna domanda ha distrattori implausibili. Nessun doppio negativo,
nessun trabocchetto.

**Q5 — Misura**
I numeri prodotti da B10 rientrano negli intervalli di MD, **limite operativo
incluso**: un testo sopra il limite meno il 5% è un rilievo anche se sta sotto
il limite dichiarato, perché la redazione aggiunge. Il limite operativo si
calcola sul **tetto scelto al PASSO 5**, non sul massimo di formato (MD regola 3,
R30): se la scheda della testata colloca il tetto a 11.000, al collaudo vale
10.450 anche se il formato ne ammette 12.000. Numero di slide e voci
bibliografiche negli intervalli previsti: cinquanta voci su un modulo di due ore
segnalano accumulo, non rigore.
Quando la bibliografia sta **sotto** l'intervallo perché la ricerca era esclusa a
monte, il rilievo si scrive comunque, con il motivo accanto (MB sezione 10). Non
si colma il numero con voci non usate nel testo.

**Q6 — Registro linguistico**
Il lettore è un farmacista laureato: nessuna spiegazione di nozioni di base.

**Q7 — Slide non testuali**
Nessuna slide supera le 6 righe. I titoli affermano, non nominano.

**Q8 — Bibliografia formalmente corretta**
Stile Vancouver, numerazione secondo ordine di prima comparsa nel testo, non
secondo l'ordine degli `id` di registro.

**Q9 — Bilancio di destinazione**
*Controllo aggiunto il 14/08/2026.* Si valutano i numeri prodotti da B10 contro
tre soglie:

| Soglia | Rilievo se |
|---|---|
| Sostanza ≥ 65% del corpo | la quota misurata scende sotto |
| Prima informazione usabile entro il 15% | arriva più tardi |
| Scostamento dalla stima del GATE 1 | supera i 15 punti percentuali |

Il terzo è il più informativo dei tre, e non riguarda solo il testo: uno
scostamento ampio dice che la **classificazione degli obiettivi** al GATE 1 era
sbagliata, e quella diagnosi vale per il lavoro successivo più che per questo.
Va scritta nel verdetto, non solo rilevata.

Rimedi, in ordine: ridurre gli obiettivi strumentali, riscrivere le aperture di
sezione perché aprano sul caso e non sul meccanismo, scindere in due pezzi.

**Q10 — Indice di dispersione**
*Controllo aggiunto il 15/08/2026 (R25). Mai bloccante, per costruzione.*

Misura la piattezza del ritmo. Su un campione di quattro pezzi umani della stessa
testata, il coefficiente di variazione della lunghezza dei capoversi sta fra
**0,52 e 0,72**: la regolarità eccessiva è la firma più riconoscibile di un testo
generato, e nessun altro controllo la intercetta.

Rilievo se, sul corpo finito:

| # | Rilievo se |
|---|---|
| 1 | CV della lunghezza dei capoversi **sotto 0,45** |
| 2 | **nessun** capoverso sotto 120 battute |
| 3 | **nessuna** frase sotto 8 parole |
| 4 | escursione fra frase minima e massima **sotto 5 volte** |

**Perché non diventerà mai bloccante.** Un indice di dispersione non produce una
voce: intercetta un testo piatto. Un testo che insegue il CV inserendo frasi
brevi a comando è peggiore di un testo regolare e sincero, e renderlo bloccante
produrrebbe esattamente quello. L'irregolarità non si fabbrica, si controlla
(MA sezione 8.3).

Quattro rilievi su quattro significano una cosa sola, e va scritta nel verdetto:
**il testo va riletto ad alta voce da una persona**, che è il controllo che
questo collaudo dichiara di non poter sostituire.

---

## PROCEDURA

1. Si eseguono i controlli in ordine, B prima di Q
2. Si produce un **verdetto sintetico**: quali controlli passano, quali no
3. Per ogni fallimento: cosa manca e dove
4. Se tutti i bloccanti passano, si dichiara la consegna possibile
5. I fallimenti di qualità si elencano come rilievi, lasciando all'autore la
   decisione

**Formato del verdetto**

```
COLLAUDO — [nome del lavoro]
Bloccanti: 10/10 superati
Misure (B10): corpo 11.240 battute (corpo, spazi inclusi, marcatori esclusi)
              sostanza 81% / strumentale 19%
              prima informazione usabile al 2%
Bloccanti (dettaglio): B1 — 7 non marcate (5 raccordi, 2 aperture),
                            di cui 1 priva di fonte, tutte sanate
Qualità: 7/10 — rilievi su Q3 (sezione 2.2 senza implicazione operativa),
                Q5 (margine di formato nullo),
                Q9 (scostamento +19 punti dalla stima del GATE 1)
Q10: CV capoversi 0,58 — nessun rilievo
ESITO: consegnabile con rilievi
```

Le misure di B10 si riportano **sempre nel verdetto**, anche quando tutto passa:
sono il dato che rende confrontabili i lavori fra loro e che permetterà, fra
qualche pezzo, di decidere se le soglie di Q9 vanno promosse a bloccanti.

Non si scrive un verdetto positivo per controlli non eseguiti. Se un controllo
non è stato possibile, si dichiara come non eseguito, non come superato.

---

## COSA IL COLLAUDO NON FA

Non verifica la correttezza scientifica dei contenuti: quella dipende dalla
qualità delle fonti e dal giudizio dell'autore, e nessuna lista di controllo la
sostituisce.

Il collaudo verifica che il contenuto sia **tracciabile, coerente con gli
obiettivi e formalmente conforme**. Un contenuto che passa il collaudo può
comunque essere scientificamente debole se le fonti scelte lo sono.

**E non verifica che si legga.** È il limite emerso con più chiarezza: un
articolo che aveva superato ogni controllo formale è risultato al destinatario
«eccessivamente meccanico». B10 e Q9 riducono quel divario misurando una
proprietà che prima nessuno contava, ma non lo chiudono. La lettura di una
persona resta il controllo che nessun collaudo sostituisce.

Questa distinzione va tenuta presente: il collaudo protegge dall'errore
procedurale, non dall'errore di merito.
