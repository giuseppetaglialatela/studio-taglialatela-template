# MC — WORKFLOW DI STESURA
Motore di scrittura scientifica — settore farmacia
Ultima modifica: 15/08/2026 · Dipendenze: MB, MD

---

## SEQUENZA FISSA

Nove passi. Non si salta un passo perché sembra ovvio, e non si anticipa la
stesura perché il tema è familiare. I due gate di approvazione sono ai passi 1
e 5: tra un gate e l'altro il lavoro procede senza chiedere conferma.

---

## PASSO 0 — Delimitazione

Una frase che dice cosa il contenuto copre e, soprattutto, **cosa non copre**.
Scritta prima di cercare qualsiasi cosa.

La delimitazione negativa è quella che salva tempo: «questo modulo non tratta la
gestione ospedaliera» impedisce tre giorni di ricerca inutile.

Si verificano anche le informazioni minime di MA sezione 6. Se mancano, si
chiedono tutte insieme e ci si ferma. Fra queste rientra la **convenzione di
conteggio** del committente quando il formato ha un limite di lunghezza: senza,
il tetto di battute del PASSO 7 non è calcolabile.

---

## PASSO 1 — Obiettivi formativi ⛔ GATE 1

Si scrivono da tre a cinque obiettivi. Formulazione obbligatoria:

> Al termine il discente sarà in grado di [verbo osservabile] + [oggetto] +
> [contesto operativo].

Verbi ammessi: identificare, riconoscere, distinguere, applicare, selezionare,
calcolare, classificare, spiegare a un paziente, documentare, indirizzare.

Verbi vietati: conoscere, comprendere, essere consapevole, apprezzare,
familiarizzare. Non sono verificabili con un test, e Agenas chiede obiettivi
proporzionati e verificabili.

**Esempio corretto**
> Al termine il discente sarà in grado di identificare, in una lista di terapia
> comprensiva di integratori, le associazioni che richiedono segnalazione al
> medico prescrittore.

**Esempio da rifiutare**
> Al termine il discente conoscerà le interazioni tra farmaci e integratori.

Ogni obiettivo riceve un codice `OF1`, `OF2`, … usato in tutto il resto del
lavoro.

### 1.1 Bilancio di destinazione — controllo aggiunto il 14/08/2026

*Perché esiste.* Un articolo che rispettava ogni controllo formale — ogni
sezione mappata su un obiettivo, ogni affermazione con fonte verificata, nessun
aggregatore — è risultato al destinatario «eccessivamente meccanico, e
l'interazione si evince poco: si evince il contesto». La misura ha poi mostrato
che il **56% del corpo era contesto** e solo il 44% sostanza.

La causa non era stilistica. Due obiettivi formativi su quattro chiedevano
contesto («identificare in una lista», «selezionare la fonte»), e il testo ha
obbedito. **Il motore ha eseguito correttamente una specifica sbagliata**, e
nessun controllo a valle poteva accorgersene: il difetto era negli obiettivi.

Prima di approvarli, quindi, ciascun obiettivo si classifica e se ne stima la
quota di testo.

| Categoria | Verbi tipici | Cosa produce |
|---|---|---|
| **SOSTANZA** | applicare, riconoscere, distinguere *un contenuto*, calcolare | ciò che il lettore non sa e per cui legge |
| **STRUMENTALE** | selezionare la fonte, collocare nel contesto, conoscere la procedura, segnalare | perché conta, dove si verifica, cosa si fa dopo |

**Soglia: la sostanza non scende sotto il 65% del corpo.**

Sotto quella soglia ci sono due rimedi, in quest'ordine:
1. ridurre il numero di obiettivi strumentali
2. **scindere in due pezzi**, portando il materiale strumentale nel secondo

La scissione è la soluzione adottata nel caso reale, e ha funzionato: la
sostanza è passata dal 44% all'81%. Non è un ripiego — un obiettivo strumentale
tagliato via è materiale che serve comunque a qualcuno, semplicemente non a chi
sta leggendo questo.

**Prova del lettore.** La prima informazione concreta e usabile compare **entro
il primo 15% del testo**. Nella versione difettosa la prima associazione
specifica arrivava al 16%, dopo due sezioni di inquadramento; nella versione
corretta alla terza riga. È il controllo più veloce da fare e il più vicino a
come il testo verrà letto davvero.

**Questo passo si chiude con l'approvazione dell'autore**, che riguarda gli
obiettivi **e il bilancio di destinazione insieme**. Approvare gli obiettivi
significa approvare la forma che il testo prenderà: modificarli dopo la stesura
costa una riscrittura.

---

## PASSO 2 — Ricognizione normativa

Normattiva, Gazzetta Ufficiale, AIFA. Cosa dice la legge oggi sul tema.

Si registra ogni testo trovato in `fonti.csv` con livello 1. Se il tema non ha
base normativa, si dichiara e si passa oltre — non si forza un aggancio
normativo che non esiste. Il caso si è già presentato: nessun obbligo di
verifica alla vendita di un integratore esiste nell'ordinamento, e l'articolo
che sembrava fondarlo riguarda la pubblicità, non la dispensazione. La base era
deontologica e di prassi professionale, e va scritta così.

Attenzione ai testi consolidati: si cita la norma vigente da Normattiva, mai il
riassunto che ne fa un articolo di rivista.

### 2.1 Quando Normattiva non è accessibile — ripiego dichiarato

*Aggiunto il 14/08/2026.* Normattiva richiede sessione e non è raggiungibile dal
motore (MB sezione 2.3). Il ripiego praticabile è il **testo originario** in
Gazzetta Ufficiale o su `leg14.camera.it`, ed è ammesso a tre condizioni:

1. si registra nell'`esito_sintetico` **quale versione si è letta**, con la
   formula «letto nel testo originario, non nel consolidato»
2. si dichiara **quali articoli non sono coperti**: quelli modificati da norme
   successive, sui quali nulla si può affermare quanto allo stato vigente
3. nel testo dell'articolo non compare alcuna affermazione sullo stato vigente
   di quegli articoli

Il testo originario regge senza problemi definizioni, elenchi di etichetta,
impianto generale — cioè quasi sempre quello che serve. Non regge «la norma oggi
prevede».

---

## PASSO 3 — Ricognizione delle linee guida

ISS/SNLG, società scientifiche accreditate, documenti FOFI, EMA.

Per ciascuna si annota **la data di pubblicazione** e **se contiene già un
grading delle raccomandazioni**. Se sì, il grading si riporterà citandolo
(principio 4 di MA).

Se la linea guida più recente ha più di cinque anni, si segnala nel contenuto.

**L'assenza di linea guida è un risultato, non un difetto.** Su alcuni temi non
esiste alcun documento italiano — è il caso delle interazioni
farmaco-integratore al banco. Si dichiara nel testo e si cerca un **gancio
istituzionale** alternativo: un sistema di sorveglianza, una piattaforma di
segnalazione, un obbligo di vigilanza. Dà al lettore un riferimento
istituzionale vero al posto di uno inesistente.

---

## PASSO 4 — Ricerca bibliografica

Prima si legge `fonti.csv` filtrato sul tema: quello che c'è già non si ricerca.

Poi PubMed, con filtri: `Review`, `Free full text`, ultimi 5 anni. Per un
contenuto formativo le review bastano quasi sempre; gli studi primari servono
solo dove la review tace.

Cochrane per le domande di efficacia: anche il solo abstract con le conclusioni
è citabile.

Ogni fonte va a registro **nel momento in cui viene trovata**, con PMID o DOI e
l'`esito_sintetico`. Le fonti non ancora aperte di persona si segnano
`da_verificare` e non sono utilizzabili finché non cambiano stato. **Uno snippet
di ricerca non fa stato**: vale MB sezione 6.1, e la citazione si controlla su
PubMed o sulla fonte primaria.

Si compila anche `conflitto_dichiarato` (MB sezione 5.4) leggendo la
dichiarazione degli autori: è il momento in cui costa meno, perché la fonte è
già aperta.

Misura attesa a fine passo: 25-40 fonti candidate per un modulo FAD, 10-15 per
un articolo.

---

## PASSO 5 — Scheletro e budget ⛔ GATE 2

Indice a due livelli. Accanto a **ogni** sezione, tre cose:

- il codice dell'obiettivo che serve (`OF2`)
- gli `id` delle fonti che la reggeranno (`F014, F022`)
- il **tetto in battute** assegnato alla sezione

Formato di lavoro:

```
2. Le associazioni a rischio           [OF2] [F014, F022, F031]  3.200
   2.1 Anticoagulanti e vitamina K     [OF2] [F014]              1.600
   2.2 Statine e pompelmo              [OF2] [F022, F031]        1.600
```

Quattro controlli obbligatori prima di chiudere il passo:

- **Copertura**: ogni obiettivo `OF` compare accanto ad almeno una sezione. Un
  obiettivo scoperto è un obiettivo da togliere o una sezione da aggiungere.
- **Giustificazione**: ogni sezione ha un `OF`. Una sezione senza obiettivo è
  materiale interessante che non serve: si toglie.
- **Bilancio di destinazione**: sommando i tetti delle sezioni che servono
  obiettivi di sostanza, la quota deve stare sopra il 65% stimato al GATE 1. Qui
  la stima diventa un numero verificabile, prima che una riga sia scritta.
- **Somma dei tetti**: il totale sta sotto il limite di formato con il margine
  del PASSO 7. Se non ci sta, si toglie una sezione adesso — non si conta di
  «stringere in stesura», che non funziona mai. La somma punta al **bersaglio**
  dichiarato (PASSO 7.1e), non al limite superiore: un bersaglio non dichiarato
  qui diventa, di fatto, la lunghezza che il testo ha preso da solo.

**Ordine interno delle sezioni.** Ogni sezione apre sull'associazione o sul
caso, non sul meccanismo. Il meccanismo segue e serve a generalizzare. Il
contesto normativo, se serve, **chiude** il pezzo spiegando perché quel problema
sfugge — non lo apre chiedendo pazienza al lettore.

**Questo passo si chiude con l'approvazione dell'autore.**

---

## PASSO 6 — Individuazione dei buchi

Le sezioni dello scheletro senza fonti accanto sono i buchi. Si elencano
esplicitamente.

Per ciascuno, tre esiti possibili e nessun altro:
- si trova la fonte e si registra
- si toglie la sezione
- si mantiene la sezione dichiarando nel testo che si tratta di prassi
  professionale non supportata da evidenza formale

**Non esiste il quarto esito «lo scrivo a memoria e poi cerco la fonte».** È
l'origine più frequente di un contenuto indifendibile.

---

## PASSO 7 — Stesura

Sezione per sezione, nell'ordine dello scheletro. Ritmo interno: non si chiede
conferma a ogni sezione.

### 7.1 Il budget di testo — regola aggiunta il 14/08/2026

*Perché esiste.* Una stima dichiarata di 12.300 battute corrispondeva a 16.669
battute reali: **errore del 45%**, scoperto solo eseguendo il conteggio. Sono
seguite otto iterazioni di taglio per rientrare nel formato, con perdita di
controllo su cosa veniva sacrificato, e il testo è atterrato a quattro battute
dal limite.

Quattro regole, tutte non negoziabili:

**(a) La lunghezza si misura, non si stima.** Un conteggio costa una riga di
comando. Nessuna dichiarazione di conformità a un formato senza aver contato
(MA principio 8).

**(b) Il tetto si assegna per sezione, prima della stesura**, al PASSO 5.
Assegnarlo dopo significa decidere cosa tagliare quando il testo è già scritto,
cioè nel momento in cui si è meno lucidi e più affezionati.

**(c) Margine minimo del 5% sotto il limite superiore.** La redazione interviene
**aggiungendo**: sigle sciolte, nomi commerciali fra parentesi, box, didascalie,
occhielli. Un testo consegnato al limite esatto sfora in redazione, e il taglio
lo fa qualcun altro.

**(d) La convenzione di conteggio si dichiara insieme al numero.** Un conteggio
senza convenzione non è confrontabile con quello della testata. Convenzione
predefinita, da confermare con il committente:

> corpo dell'articolo, spazi inclusi; marcatori `[Fxxx]` esclusi; titolo,
> occhiello e sommario esclusi

Se la convenzione del committente è diversa, **il conteggio va rifatto**, non
convertito a stima.

**(e) Il tetto è un bersaglio nei due sensi.** *(R15, 15/08/2026.)* Un formato
che dichiara 8.000–12.000 battute ha un limite inferiore quanto uno superiore, e
il limite inferiore non è un suggerimento: un pezzo consegnato a 7.100 battute
dove la media della testata è 9.000 si presenta come contributo minore, e
occuperà lo spazio che gli somiglia. Stare corti non è prudenza, è
posizionamento — solo non scelto.

Da qui la regola di posizionamento: fissato l'intervallo di formato, si dichiara
al PASSO 5 **il bersaglio**, non solo il tetto, e i tetti di sezione si sommano a
quello. Il bersaglio si sceglie guardando la scheda della testata quando esiste
(media, mediana e dispersione del campione), non l'intervallo astratto del
formato.

**Misura a metà stesura.** Il conteggio non si fa solo alla fine. Quando è
scritta all'incirca **metà delle sezioni previste**, si contano le battute
prodotte e si confrontano con la somma dei tetti di quelle sezioni. È il momento
in cui una deriva costa una sezione da riscrivere e non otto iterazioni di
taglio; alla fine costa il triplo e si paga sul materiale a cui si è più
affezionati. Lo scarto si dichiara in una riga e si decide subito: si stringe, si
toglie una sezione, o si sposta il bersaglio dentro l'intervallo motivandolo.

Crescere per arrivare al bersaglio si fa **in sostanza** — un'associazione in
più, una sezione di risultati negativi, un caso al banco — mai allungando le
aperture di sezione. Un testo portato a misura con il contesto peggiora esattamente
la grandezza che il bilancio di destinazione misura (PASSO 1.1, ME Q9).

### 7.2 Regole di stesura

- Ogni affermazione tecnica porta `[Fxxx]` in linea, scritto contestualmente
- Ogni sezione apre sull'associazione o sul caso, non sul meccanismo
- Dove la fonte ha un grading, si riporta citandolo
- Dove non ce l'ha e la questione è discussa, si usa la scala propria
  (`consolidato` / `ragionevole ma discusso` / `preliminare`), dichiarata come
  propria
- I dati numerici vengono sempre da fonte primaria: Rapporto OsMed, ISS, studio
  originale. Mai da una rivista di settore, mai da un'indagine commissionata da
  un'associazione di produttori (MB sezione 5.2). Un dato straniero dichiarato
  come tale è preferibile a un dato italiano di provenienza interessata
- Un numero presente sia in prosa sia in tabella si prende **dalla tabella**
  (MB sezione 6.2)
- Le fonti nuove che emergono durante la stesura si accumulano in coda al
  registro, non si raccolgono alla fine
- Le fonti in inglese si rendono secondo MB sezione 9: la forza
  dell'affermazione non si aumenta mai in traduzione
- Dalle fonti `abstract_verificato` si ricava solo la conclusione generale, mai
  un numero specifico o un sottogruppo
- Una fonte con `conflitto_dichiarato = si_concorde` usata senza ancoraggio
  indipendente porta la nota nel testo

**Registro linguistico**: professionale, diretto, senza divulgazione
semplificata. Il lettore è un farmacista laureato. Non si spiega cosa sia un
principio attivo.

**Applicabilità**: ogni sezione tecnica si chiude con l'implicazione operativa
al banco. Agenas chiede competenze aderenti alle situazioni lavorative reali —
un contenuto teorico senza traduzione pratica è formalmente conforme e
sostanzialmente debole.

---

## PASSO 8 — Verifica incrociata

Rilettura mirata a cercare le affermazioni prive di `[Fxxx]`. Sono sempre più di
quanto sembri: le frasi di raccordo tendono a contenere affermazioni tecniche
non marcate. In un caso reale il controllo ne ha trovate sette, di cui una priva
di qualsiasi fonte.

Secondo controllo: ogni `OF` è effettivamente coperto dal testo scritto, non
solo dallo scheletro.

Terzo controllo: ogni fonte citata ha stato `verificata` o
`abstract_verificato`. Le `da_verificare` vanno aperte adesso o rimosse.

Quarto controllo: le citazioni in bibliografia — autori, rivista, anno — sono
state controllate sulla fonte primaria o su PubMed, non su un riferimento
indiretto.

---

## PASSO 9 — Pacchetto e collaudo

Si producono tutti gli elementi definiti in MD per il formato di destinazione,
si esegue il collaudo di ME, e solo se l'esito è positivo si consegna.

---

## GESTIONE DEGLI IMPREVISTI

**La letteratura è discorde**
Non si sceglie per conto dell'autore. Si espone la divergenza, si indica
l'opzione ritenuta migliore con il perché, si lascia l'ultima parola. Nel testo
finale la divergenza si dichiara: «le posizioni non sono concordi».

**Una fonte attesa non esiste**
Si dichiara. Non si sostituisce con una fonte di livello inferiore facendola
passare per equivalente.

**Una fonte è dietro barriera**
Dopo due tentativi si dichiara l'ostacolo e si chiede la consegna manuale del
documento (MB sezione 2.3). Non si ripiega su un aggregatore.

**Il committente chiede più di quanto le fonti reggano**
Si dice cosa le fonti permettono di affermare davvero e si propone la
riformulazione. Non si gonfia una raccomandazione per soddisfare un brief.

**Il testo sfora il formato**
Si torna al PASSO 5 e si toglie una sezione intera, invece di limare ovunque.
Otto iterazioni di taglio uniforme producono un testo peggiore di una sezione in
meno, e consumano il tempo che serviva a scriverla bene.

**Il tema tocca un prodotto del committente**
Si applica il principio 6 di MA. Se il committente è l'azienda che produce o
distribuisce il medicinale, ci si ferma e si segnala.
