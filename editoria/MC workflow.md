# MC — WORKFLOW DI STESURA
Motore di scrittura scientifica — settore farmacia
Ultima modifica: 13/08/2026 · Dipendenze: MB

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
chiedono tutte insieme e ci si ferma.

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

**Questo passo si chiude con l'approvazione dell'autore.** Gli obiettivi
determinano tutto ciò che segue: modificarli dopo la stesura costa una riscrittura.

---

## PASSO 2 — Ricognizione normativa

Normattiva, Gazzetta Ufficiale, AIFA. Cosa dice la legge oggi sul tema.

Si registra ogni testo trovato in `fonti.csv` con livello 1. Se il tema non ha
base normativa, si dichiara e si passa oltre — non si forza un aggancio
normativo che non esiste.

Attenzione ai testi consolidati: si cita la norma vigente da Normattiva, mai il
riassunto che ne fa un articolo di rivista.

---

## PASSO 3 — Ricognizione delle linee guida

ISS/SNLG, società scientifiche accreditate, documenti FOFI, EMA.

Per ciascuna si annota **la data di pubblicazione** e **se contiene già un
grading delle raccomandazioni**. Se sì, il grading si riporterà citandolo
(principio 4 di MA).

Se la linea guida più recente ha più di cinque anni, si segnala nel contenuto.

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
`da_verificare` e non sono utilizzabili finché non cambiano stato.

Misura attesa a fine passo: 25-40 fonti candidate per un modulo FAD, 10-15 per
un articolo.

---

## PASSO 5 — Scheletro ⛔ GATE 2

Indice a due livelli. Accanto a **ogni** sezione, due cose:

- il codice dell'obiettivo che serve (`OF2`)
- gli `id` delle fonti che la reggeranno (`F014, F022`)

Formato di lavoro:

```
2. Le associazioni a rischio           [OF2] [F014, F022, F031]
   2.1 Anticoagulanti e vitamina K     [OF2] [F014]
   2.2 Statine e pompelmo              [OF2] [F022, F031]
```

Due controlli obbligatori prima di chiudere il passo:

- **Copertura**: ogni obiettivo `OF` compare accanto ad almeno una sezione. Un
  obiettivo scoperto è un obiettivo da togliere o una sezione da aggiungere.
- **Giustificazione**: ogni sezione ha un `OF`. Una sezione senza obiettivo è
  materiale interessante che non serve: si toglie.

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

Regole di stesura:
- Ogni affermazione tecnica porta `[Fxxx]` in linea, scritto contestualmente
- Dove la fonte ha un grading, si riporta citandolo
- Dove non ce l'ha e la questione è discussa, si usa la scala propria
  (`consolidato` / `ragionevole ma discusso` / `preliminare`), dichiarata come
  propria
- I dati numerici (prevalenze, consumi, percentuali) vengono sempre da fonte
  primaria: Rapporto OsMed, ISS, studio originale. Mai da una rivista di settore
- Le fonti nuove che emergono durante la stesura si accumulano in coda al
  registro, non si raccolgono alla fine
- Le fonti in inglese si rendono secondo MB sezione 9: la forza
  dell'affermazione non si aumenta mai in traduzione. `may reduce` è
  «potrebbe ridurre», `is associated with` non è «causa»
- Dalle fonti `abstract_verificato` si ricava solo la conclusione generale, mai
  un numero specifico o un sottogruppo

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
non marcate.

Secondo controllo: ogni `OF` è effettivamente coperto dal testo scritto, non
solo dallo scheletro.

Terzo controllo: ogni fonte citata ha stato `verificata`. Le `da_verificare`
vanno aperte adesso o rimosse.

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

**Il committente chiede più di quanto le fonti reggano**
Si dice cosa le fonti permettono di affermare davvero e si propone la
riformulazione. Non si gonfia una raccomandazione per soddisfare un brief.

**Il tema tocca un prodotto del committente**
Si applica il principio 6 di MA. Se il committente è l'azienda che produce o
distribuisce il medicinale, ci si ferma e si segnala.
