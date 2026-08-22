# RILIEVI APERTI
Coda delle modifiche ai moduli in attesa di una sessione dedicata.
Studio Taglialatela · settore editoria · Ultima modifica: 22/08/2026 · Governato da MA

**Perché esiste.** MA §2.1 (R39) vieta di toccare i moduli durante una sessione di
stesura: i rilievi si accumulano e si applicano in una sessione dedicata. Fino a
oggi si accumulavano nei pacchetti di passaggio, che sono **effimeri**. Un
rilievo che sopravvive solo lì è un rilievo che si perde. È lo stesso motivo per
cui esiste `note_uso_fonti.md`.

**Due vincoli, e sono la condizione perché questo file non diventi apparato.**

1. **Non si legge durante una stesura.** Si apre solo nella sessione di
   manutenzione dei moduli, e in nessun altro momento. Non entra nel router dei
   compiti di scrittura.
2. **Si svuota.** Un rilievo applicato si **cancella** da qui, non si marca come
   fatto. Un file che solo cresce è un modulo in incognito.

**Regola di ammissione.** Per MA §2.1 un rilievo entra solo con **il fatto
osservato che lo produce**, con la data. Un rilievo senza fatto non si scrive
qui: si scarta.

---

## A. MODIFICHE AI MODULI — da applicare in sessione dedicata

### A1 · MC PASSO 5 — controllo di stato delle fonti nello scheletro
**Modifica.** Nessuna sezione dello scheletro può essere chiusa al GATE 2 con
fonti in stato diverso da `verificata` o `abstract_verificato`, salvo che sia
dichiarata accanto una fonte di riserva già verificata.

**Fatto (21/08/2026).** Lo scheletro dell'elaborato Mediserve assegnava alla
sezione 4.2 la fonte F025 e alla 4.6 la fonte F002, entrambe `da_verificare`.
Il GATE 2 le ha approvate senza che alcun controllo lo intercettasse. Il difetto
è emerso a stesura in corso, dove costa di più: le due sezioni sono state
riinstradate su F034-F035-F036-F037-F038 e su F032.

**Dove.** MC, PASSO 5, fra i quattro controlli esistenti.

---

### A2 · MD FORMATO 6 — rimozione
**Modifica.** Togliere il FORMATO 6 da MD.

**Fatto.** MA §2.1 lo marca già come **regola speculativa, scritta senza
committente**, e stabilisce che una parte di modulo priva del fatto che l'ha
prodotta è candidata alla rimozione, non alla manutenzione. Alla data non è
arrivata alcuna commessa che lo riguardi.

**Dove.** MD. È l'unica potatura a costo zero oggi disponibile: nessun lavoro in
corso vi poggia.

---

### A3 · MB — due rilievi ereditati, da riformulare con il fatto
**Modifica attesa.** (a) trattamento delle fonti dietro paywall; (b) valore di
stato per una fonte accertata come inesistente.

**Fatto (b).** F051 è stata chiusa come fonte non esistente, ma MB non prevede
un valore di stato corrispondente: la riga resta `da_reperire` con un avviso in
chiaro nel campo esito. È una soluzione che funziona e non è dichiarata.

**Fatto (a) — DA COMPLETARE.** Il rilievo è ereditato senza il fatto che lo ha
prodotto. Per la regola di ammissione va ricostruito o scartato.

---

### A4 · ME — rilievo ereditato, difetto di ciclo
**Modifica attesa.** Correzione del difetto di ciclo segnalato nella sessione
del 19/08/2026.

**DA COMPLETARE.** Come A3(a): ereditato senza il fatto. Va ricostruito sul
diff o scartato.

---

### A5 · MA — l'editor «Create new file» committa file vuoti senza avvisare
**Modifica.** Aggiungere alle regole GitHub di MA: dopo aver creato un file
dall'editor, verificarne il contenuto sull'albero o sulla pagina blob, non solo
la presenza. La presenza del commit non dimostra la presenza del contenuto.

**Fatto (21/08/2026).** Il commit `Create rilievi_aperti.md for module
modification tracking` è stato registrato regolarmente alle 07:07, il file
compare nell'albero, ma il file è **vuoto**: il contenuto non era stato incollato
prima del commit e l'editor non ha segnalato nulla. L'endpoint raw rispondeva
404, che a prima lettura sembrava ritardo di CDN.

**Dove.** MA, sezione sulle regole GitHub, accanto alla regola che distingue
albero e endpoint raw.

---

### A6 · MA — l'albero di una cartella non prova l'appartenenza alla cartella
**Modifica.** Correggere la regola di lettura del repository. Oggi MA prescrive di
leggere l'albero (`/tree/main/...`) invece dell'endpoint raw per accertare
presenza o assenza di un file. Non basta: la pagina dell'albero di una cartella
elenca anche nomi che **non appartengono a quella cartella**. La verifica valida
è la **cronologia del percorso**, `commits/main/<percorso>.atom`, che restituisce
zero voci se il file a quel percorso non esiste.

Aggiungere inoltre: l'editor `/new/main/<cartella>` **non garantisce la
cartella**. Prima di digitare il nome va controllato che sopra il campo compaia
il percorso di destinazione.

**Fatto (21/08/2026).** `rilievi_aperti.md` è stato creato in **radice** anziché
in `editoria/`, pur essendo stato aperto l'editor su `/new/main/editoria`. La
pagina dell'albero di `editoria` lo elencava comunque, e su quella lettura errata
sono stati costruiti tre tentativi falliti di modifica e cancellazione. Il difetto
è stato smontato dalla cronologia del percorso: un commit su
`editoria/scheletro.md.atom`, zero su `editoria/rilievi_aperti.md.atom`.

**Dove.** MA, sezione sulle regole GitHub, a sostituzione della regola vigente
sull'albero.

---

### A7 · MC PASSO 5 — il controllo di copertura gira sul documento sbagliato
**Modifica.** Il controllo di copertura degli obiettivi formativi al PASSO 5 va
eseguito confrontando lo scheletro con **il testo approvato degli OF**, non con lo
scheletro stesso. Presuppone che il testo degli OF esista in un file del
repository: il PASSO 1 deve produrlo, non lasciarlo in conversazione.

**Fatto (21/08/2026).** Lo scheletro aveva sostituito i flussi nominati in OF4
(ricetta dematerializzata, scheda di dimissione, piattaforme territoriali) con
altri, e il GATE 2 non l'ha rilevato perché il confronto avveniva contro lo
scheletro. Il difetto è emerso al PASSO 8, a testo scritto. Stessa famiglia di A1:
un controllo che gira sul documento intermedio invece che sull'originale.

**Dove.** MC, PASSO 5 e PASSO 1.

---

### A8 · MC PASSO 8 — manca il controllo di conformità al formato
**Modifica.** Aggiungere ai quattro controlli del PASSO 8 un quinto controllo:
**conformità del testo alle prescrizioni del formato di consegna in MD**. Per il
FORMATO 5 comprende almeno la prova del lettore adattata (primo esempio clinico
entro le prime 900 parole, almeno un esempio applicabile per unità didattica), il
vincolo del solo testo con mantenimento della funzione di checklist, e il bilancio
di sostanza misurato **per unità** e non solo sul totale.

**Fatto (22/08/2026).** Le unità 4 e 5 sono state scritte senza alcun esempio
clinico applicabile, in violazione della prova del lettore del FORMATO 5, e la
4.2 e la 4.3 riversano in periodi lunghi materiale che il formato vuole in
elenchi numerati in linea. Nessuno dei quattro controlli del PASSO 8 lo ha
rilevato: il difetto è emerso perché il committente ha letto la prosa e ha
segnalato di non capirla. Un controllo che dipende dalla lettura del committente
non è un controllo.

**Nota.** Lo scheletro assegna a ogni sezione fonti e tetto di parole, non la
presenza di un caso. Valutare se il vincolo vada anche al PASSO 5, dove
costerebbe meno che a testo scritto.

**Dove.** MC, PASSO 8. Eventualmente PASSO 5.

---

## B. CANDIDATI — non sono rilievi finché non hanno un fatto

Stanno qui per non essere riscoperti da capo, **non** per essere applicati.
Nessuno dei due diventa regola senza un difetto osservato su un lavoro reale.

- **B1 · Accessibilità dichiarata all'ingresso a registro.** Annotare, quando una
  fonte entra, se sia ad accesso libero o dietro barriera. *Contro:*
  l'informazione spesso non è conoscibile prima di aprire la fonte — F066 è
  risultata ad accesso libero solo dopo la consegna del PDF.
- **B2 · Profondità di verifica proporzionata all'uso.** Portare a testo
  integrale solo le fonti già assegnate a una sezione dallo scheletro,
  fermandosi prima a `abstract_verificato`. *Contro:* MB 6.3 limita fortemente
  ciò che si può usare da un abstract, e una fonte non aperta non si può
  assegnare (vedi A1). I due vincoli tirano in direzioni opposte e la cosa va
  risolta prima, non dopo.

---

## C. PENDENTI OPERATIVI — non sono modifiche ai moduli

### C1 · Rinomina dei cinque file di estratti — NON è una cancellazione
`F024 estratti.md`, `F034 estratti.md`, `F035 estratti.md`, `F036 estratti.md`,
`F037 estratti.md`.

**Correzione del 21/08/2026, importante.** I pacchetti precedenti li elencavano
fra le «copie col nome corrotto da cancellare». **Non sono copie: sono gli unici
esemplari.** Non esiste alcuna versione con l'underscore. Sono stati usati tutti
e cinque per scrivere l'unità 4. Cancellarli avrebbe distrutto il materiale su
cui poggiano le sezioni 4.2, 4.4 e 4.5.

**Azione corretta:** rinomina dall'editor di GitHub (MA R14), un file alla volta,
`F0xx estratti.md` → `F0xx_estratti.md`. Non prima della chiusura del PASSO 7.

Restano invece cancellabili, questi sì duplicati o superati:
`schede testata addendum.md`, `moduli editoria 20260817.zip`.

### C2 · Identificatori non letti alla fonte (MB 6.1)
Da dichiarare come non confermati finché non letti sulla pagina della fonte:
PMID di F059, F063, F064, F066 · PMCID di F058 e F061 · data di revisione ISS
di F062.

### C3 · Consegne manuali ancora aperte
F025 (DM 20 maggio 2022, GU SG n. 160 dell'11/07/2022) · F002 (L. 2 dicembre
2025, n. 182) · F003 (D.lgs. 24 aprile 2006, n. 219) · Accordo Stato-Regioni
17/12/2020 rep. 215/CSR · F029 art. 5.

Nota: F025 e F002 non sono più bloccanti per la stesura — le sezioni 4.2 e 4.6
sono state scritte su fonti verificate. Restano necessarie per sciogliere il
rinvio dell'art. 1 c. 2 lett. e-sexies) del D.lgs. 153/2009.

### C4 · Convenzione di conteggio — scarto rilevato
Il contatore usato il 21/08/2026 misura **10.639** parole di corpo sulle unità
1-3, contro le **10.791** dichiarate dal pacchetto precedente: scarto 1,4%.
Convenzione in uso: corpo, titoli esclusi, marcatori `[Fxxx]` esclusi, marcatura
Markdown esclusa. **Tutti i conteggi successivi usano questa.** Al PASSO 8 il
totale si rimisura per intero, non si somma per unità.

### C5 · Approvazione del titolo dell'elaborato
Aperta.

### C6 · Da dichiarare nel testo finale
Conflitto sponsor Pfizer per F001. Modalità di accesso non editoriali per F040,
F050, F061 (`note_uso_fonti.md` §9).
