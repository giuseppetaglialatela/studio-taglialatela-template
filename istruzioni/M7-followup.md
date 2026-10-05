# M7 — FOLLOW-UP

Modulo operativo. Si carica quando si gestisce il contatto con un paziente già
in carico: messaggi standard, controllo del lunedì, risposte del Form C
(controllo periodico), decisione se e quando rivedere il piano.

Non dipende da M1 né da M2: si può caricare da solo. Rimandi:
- l'aggiornamento delle pesate e il grafico di andamento → **M5**
- la revisione vera e propria del piano → **M2** (che richiede **M1**)
- il fascicolo paziente e la sezione 8 "percorso" → **M4**

> **Attenzione ai nomi.** In questo modulo `M1`–`M13` sono i **messaggi
> standard** del protocollo di comunicazione, non i moduli di istruzioni. I
> moduli sono citati in grassetto (**M1**, **M2**, …); i messaggi in codice
> (`M10`, `M11`, …).

---

## 1. DOVE STANNO I TESTI

Il protocollo dei messaggi standard `M1`–`M13` e del controllo del lunedì è in
**Protocollo_Comunicazione_Followup.docx** (Drive > Sistema Presa in Carico).

È un file **operativo**, non di archivio: contiene i testi dei messaggi, che non
sono replicati qui. Va letto quando serve mandare un messaggio, non a ogni
sessione.

I link dei form da inserire nei messaggi (`M1`/`M2` → Form A, `M3`/`M4` →
Form B) sono in **M4**. Sempre come link, mai come allegato.

Il **Form C** (controllo periodico) serve al paziente già in carico; il link è
in **M4**. Non è ancora legato a un messaggio numerato del protocollo: finché
non lo è, si manda con un testo libero breve.

---

## 2. FORM C — COSA RACCOGLIE E DOVE VA

Sezioni: chi sei · come si condisce a casa (chi mette l'olio, come lo dosa,
quanto per piatto, olio in cottura, pane/pasta/riso e carne/pesce/formaggi pesati
o a occhio) · il periodo appena passato (aderenza, pasti fuori, giorno libero,
strappi) · quello che non sembra un pasto (bevande, assaggi, fuori pasto, dopo
cena) · misure · salute · una proposta (diario fotografico) · note libere.

Destinazione delle risposte:

| risposta | dove va |
|---|---|
| peso di oggi | `misurazioni` del JSON andamento (**M5**) — **solo se è una pesata nuova** |
| circonferenza vita | `circ_vita.attuale_cm` + `data_attuale` del JSON andamento (**M5**) |
| giorno di pesata accettato | sezione 8 del fascicolo |
| tutto il resto | sezione 8 del fascicolo, con la data del form |

Regole:
- **Peso dichiarato identico all'ultima pesata registrata → NON è una pesata
  nuova.** Il paziente ricopia il numero che conosce: aggiungerlo duplicherebbe
  un punto e falserebbe la regressione del grafico. (Caso reale 05/10/2026.)
- Il peso dichiarato in un form si registra solo se dichiarato come pesata
  di oggi; in caso di dubbio si chiede.
- Una variazione di vita di 1-2 cm è nell'errore di misura: si registra, non si
  interpreta.
- Le voci "fuori piano" (bevande, dolce dopo cena, assaggi) arrivano **senza
  quantità**: sono una pista, non un dato. Prima di trasformarle in una
  correzione del piano si chiedono le quantità al paziente, in un solo messaggio.

Il JSON andamento si aggiorna seguendo **M5**. La sezione 8 del fascicolo è
dati del paziente: resta su Drive, mai su GitHub.

---

## 3. SOGLIE OPERATIVE

| Situazione | Azione |
|---|---|
| Aderenza sotto 3 giorni su 7 per **due settimane consecutive** | revisione del piano (`M11`) |
| **Due settimane di silenzio** | telefonata, non messaggio (`M10`) |
| **Nessun calo a 4 settimane** con aderenza alta | approfondimento (`M12`) |

La telefonata di `M10` è l'unico contatto che resta volutamente umano e diretto:
non va sostituita con un testo.

---

## 4. INTEGRAZIONE CLINICA SU `M12`

In un paziente in terapia tiroidea — o comunque con patologia endocrina in
trattamento — un plateau con aderenza alta non è solo una questione di piano
alimentare. Prima di attribuirlo a porzioni o composizione, segnala la verifica
del quadro ormonale e dell'adeguatezza della titolazione. La stessa logica vale
ogni volta che una terapia in corso può giustificare l'assenza di risposta.

Va segnalato anche il **calo che si avvicina a `weight_floor_kg`**: è un plateau
minimo cautelativo, non un obiettivo. Quando ci si avvicina, la decisione se
proseguire è clinica e va esposta, non applicata in automatico.

> Queste due righe sono ripetute in **M5** *per scelta*, non per errore: chi
> aggiorna una pesata carica solo M5, e una segnalazione che nessuno legge al
> momento giusto vale zero. Se cambiano, vanno cambiate in entrambi i moduli.

---

## 5. ADERENZA BASSA — COSA GUARDARE PRIMA

Prima di rivedere le porzioni, guarda **quali** alimenti il paziente salta.

Se sono concentrati su voci entrate nel piano per chiudere un micronutriente, il
problema è la composizione, non la quantità — e va riletto alla luce del
**principio 8** (nucleo M0): il giudizio sui micronutrienti si dà sulla media
settimanale, quindi è possibile che quel deficit non esistesse e che l'alimento
sia stato aggiunto per inseguire un numero.

L'aderenza è un esito clinico: un piano non seguito vale meno di un piano buono
che viene seguito. Un alimento sgradito rimosso è spesso un miglioramento del
piano, non un compromesso.

---

## 6. COSA RESTA AL NUTRIZIONISTA

- La decisione di rivedere il piano, anche quando una soglia è superata: la
  soglia apre la discussione, non la chiude.
- Ogni ipotesi su titolazione, quadro ormonale o terapia in corso: si segnala,
  non si conclude.
- Il contenuto di un messaggio che esce dai testi standard del protocollo.
