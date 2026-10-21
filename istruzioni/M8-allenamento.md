# M8 — ALLENAMENTO: SCHEDA E ARCHIVIO DEI MODELLI

Modulo operativo. Si carica quando si prepara, trascrive o modifica una scheda di
allenamento, o quando si cercano protocolli di riferimento.
Creato: 19/10/2026 · aggiornato 21/10/2026 (template su GitHub). Non dipende da M1-M7: si carica da solo.
Rimandi: se l'allenamento cambia il livello di attività del paziente, il ricalcolo
di TDEE e target segue **M2** (richiede **M1**) e passa dal gate di approvazione.

---

## 1. TEMPLATE DELLA SCHEDA

**File:** `TEMPLATE SchedaAllenamento StudioTaglialatela v1.py` (formato telefono,
100 × 222 mm, un giorno di allenamento per pagina).
**Dove sta:** GitHub, nella radice del repository (verificato il 21/10/2026: 5.452 byte,
come la copia su Drive, che resta archivio). Il nome contiene SPAZI, non trattini bassi:
`https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/TEMPLATE%20SchedaAllenamento%20StudioTaglialatela%20v1.py`

**Uso:** `python3 TEMPLATE_..._v1.py dati.json uscita.pdf` (richiede `wkhtmltopdf`).
Motore grafico congelato (principio 4): si modifica SOLO il JSON dei dati.

**Schema del JSON** (chiavi lette dal template):
- `titolo`, `paziente`, `autore`, `data`, `intro`
- `progressione`: `testo`, `colonne`, `righe`, `nota`. **Il numero di righe fissa il
  numero di colonne B1, B2, …** di ogni esercizio: ogni `blocchi` deve avere
  esattamente quella lunghezza.
- `regole`: lista di stringhe
- `prima`, `dopo`: lista di riquadri `{titolo, sottotitolo, testo, punti}`
- `sedute`: lista di `{nome, sedute, esercizi}`; ogni esercizio
  `{nome, dettaglio, blocchi, recupero, focus}` (`recupero` obbligatorio).
- `**grassetto**` e a capo sono ammessi nei testi; in `blocchi` la stringa " + "
  va a capo.
- Chiavi in più (es. `archivio`) sono ignorate dal template.

**Regole di contenuto**
- Una scheda trascritta da appunti o redatta da altri si riporta com'è. Ogni
  lettura incerta (sigle, frecce, numeri ambigui) si DICHIARA al nutrizionista e
  si verifica con chi ha scritto la scheda o con il paziente: non si risolve a
  intuito. Un dato mancante (es. recuperi) resta "—", non si inventa.
- I riquadri `prima` e `dopo` (alimentazione e idratazione) sono di competenza
  dello Studio: se li redige l'assistente, vanno approvati.
- Numerazione file: progressiva del paziente (es. `06_SchedaAllenamento_Cognome_v1`),
  versioni `_vN` come da nucleo.

---

## 2. ARCHIVIO DEI MODELLI DI ALLENAMENTO

**Cartella Drive:** `Studio Nutrizionale Taglialatela/Modelli_Allenamento`,
ID `1vCnAUzERColfAAq32IcquA8n-WhP3mbj`. Gemella di `Modelli_Dieta`.

**Scopo:** riferimenti riutilizzabili per le schede nuove. Non è un fascicolo: la
scheda nominativa resta nella cartella del paziente.

**Contenuto**
- un file per protocollo: `ALL-NNN_<descrittore>_vN.json`, **anonimo** (nessun
  nome, contatto o dato identificativo; `paziente` = "Modello di riferimento").
  È lo stesso JSON del template più un blocco `archivio`:
  `id, nome, origine, obiettivo, livello, frequenza, luogo_attrezzatura,
  struttura, progressione, condizioni_cliniche_considerate, recuperi,
  letture_non_verificate, riquadri_prima_dopo`
- l'indice `INDICE_ModelliAllenamento_vN.csv`, una riga per protocollo:
  `id, nome, file, origine, obiettivo, livello, frequenza, luogo, struttura,
  progressione, condizioni_cliniche, data_inserimento`

**`origine`** distingue `studio` (scheda redatta dal nutrizionista) da `esterna`
(redatta da altri, es. personal trainer). Un modello esterno è un riferimento di
ciò che il paziente fa, non un protocollo approvato dallo Studio.

**Quando si archivia:** ogni scheda nuova o modificata, una volta confermata dal
nutrizionista, entra in archivio anonimizzata. Le `letture_non_verificate`
restano nel file finché non vengono sciolte.

**Come si aggiorna (limiti del connettore, nucleo §7):** il connettore non
sovrascrive. Si carica il JSON nuovo e una NUOVA versione dell'indice
(`_v2`, `_v3`) con tutte le righe precedenti più quella nuova; la cancellazione
della versione vecchia resta manuale e facoltativa. Upload sempre con
`disableConversionToGoogleType: true`, e dimensione verificata dopo il caricamento.
L'indice corrente è quello con il numero di versione più alto.

**Come si consulta per una scheda nuova:** si legge l'indice corrente, si filtra
per obiettivo, livello, luogo e condizioni cliniche, si propongono al
nutrizionista i 2-3 modelli più vicini con il motivo in una riga. Si scarica il
JSON solo del modello scelto. Un modello si adatta, non si copia tal quale.

**Stato al 19/10/2026:** 1 modello (`ALL-001`, origine esterna), indice `_v1`.
