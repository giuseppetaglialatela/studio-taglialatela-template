# M4 — SISTEMA DI PRESA IN CARICO

Modulo operativo. Si carica quando esiste un **fascicolo paziente strutturato a 8
sezioni** e si deve tradurlo nei vincoli che governano il piano. Dipende da **M2
(Workflow piano alimentare)**: quello che questo modulo produce è il PASSO 0, che
precede la ricerca e i calcoli.

Rimandi:
- gerarchia dei conflitti tra vincoli in applicazione → **M2**, PASSO 5
- traduzione della terapia nei CSV del motore → **M2**, PASSO 4
- messaggi M1-M13 e soglie di follow-up → **M7**

---

## 1. IL FASCICOLO

Otto sezioni:

1. identità
2. antropometria
3. quadro clinico
4. terapia farmacologica
5. vincoli alimentari
6. contesto di vita
7. storia e obiettivi
8. percorso

Provenienza: sezioni 1-4 dal **Form A**, sezioni 5-7 dal **Form B**, sezione 8
compilata dal nutrizionista — ed è l'unica che cresce nel tempo.

**Percorso del fascicolo di un paziente reale:**
`Drive > Andamento Dieta Pazienti > [Cognome Nome] > [CognomeNome]_Fascicolo.json`
(stessa cartella del JSON andamento).

Schema di riferimento: `FascicoloPaziente_ESEMPIO.json`
(Drive > Sistema Presa in Carico).

---

## 2. I DUE FORM DI INTAKE

Pubblicati su GitHub Pages e raggiungibili direttamente dal paziente.

**Form A** — sezioni 1-4, clinico, **prima** della presa in carico:
`https://giuseppetaglialatela.github.io/studio-taglialatela-template/FormA%20SchedaPrimoAccesso.html`

**Form B** — sezioni 5-7, preferenze e contesto, **dopo** la presa in carico:
`https://giuseppetaglialatela.github.io/studio-taglialatela-template/FormB%20SchedaAlimentare.html`

Sono questi i link da inserire nei messaggi M1/M2 (Form A) e M3/M4 (Form B) del
protocollo di follow-up.

Numero WhatsApp dello studio configurato nei form (costante `NUMERO_WA`):
`393895068729` — formato internazionale, senza `+` e senza spazi.
Se cambia, va aggiornato in **entrambi** i file e ricaricato.

### Modifica dei form

Si scarica il file da GitHub (canale raw), si modifica **solo il valore
necessario**, si ricarica con lo stesso nome sul repository — che sovrascrive.

Dopo il caricamento, verifica il contenuto effettivo online prima di dare conferma.
Attenzione al canale: la CDN di GitHub può servire per qualche minuto la versione
precedente, quindi **una verifica negativa immediata non è conclusiva** — riprova
dopo un paio di minuti. Per una verifica non soggetta a cache, leggi l'albero del
repository (`github.com/.../tree/main/...`) invece dell'endpoint raw.

---

## 3. PASSO 0 — DAL FASCICOLO ALLA TABELLA VINCOLI

Prima della ricerca scientifica e prima di qualsiasi calcolo:

1. Apri il fascicolo.
2. Applica le regole di traduzione della sezione 4 di questo modulo. Non serve
   rileggere alcun documento su Drive.
3. Genera la **Tabella Vincoli**, ordinata per gerarchia (i quattro livelli sono in
   M2, PASSO 5).

**La Tabella Vincoli APRE la fase di approvazione, non la chiude.** È il documento
su cui il nutrizionista corregge la lettura del fascicolo prima che quella lettura
si trasformi in grammature: un vincolo interpretato male qui costa un piano intero.

---

## 4. REGOLE DI TRADUZIONE FASCICOLO → VINCOLI

Queste regole sono la fonte operativa. Il documento
`Regole_Traduzione_Fascicolo_Piano_v1.docx` su Drive le rispecchia ma è archivio:
non va riletto al PASSO 0, e in caso di divergenza valgono queste.

**Sez2 — antropometria → Livello 1.**
Alimenta TDEE e target. Peso desiderato e tempi dichiarati sono il *target* del
piano, non un vincolo di sicurezza: se irrealistici si segnalano e si discutono, non
si applicano in automatico.

**Sez3 — quadro clinico → Livello 0 o 1, secondo il rischio.**
Le condizioni con impatto diretto diventano vincoli di composizione e di struttura
del pasto, non solo annotazioni.

**Sez4 — terapia → Livello 0/1 + derivazioni automatiche.**
La regolarità di assunzione dichiarata è contesto per il follow-up, non vincolo di
piano.
La terapia va **SEMPRE tradotta nei tre CSV del motore** (`farmaci_paziente.csv`,
`interazioni.csv`, `orari_pasti.csv`): annotarla solo nella Tabella Vincoli lascia
il PASSO 5 di `pipeline.py` senza dati, e la verifica non viene fatta. L'assenza del
file non è l'assenza di terapia.

**Sez5 — vincoli alimentari.**
Allergie e intolleranze a Livello 0. Alimenti non graditi o "solo se serve" a
Livello 3.
Estensione delle esclusioni: interpretale nella loro portata **reale, non massima**
(M2, PASSO 5). Un rifiuto generico può riguardare una sola categoria: chiedi
conferma prima di escludere alimenti che il paziente non ha davvero rifiutato.

**Sez6 — contesto di vita → Livello 2.**
Il piano si adatta a tempo di cucina, chi cucina, piatto separato sì/no, orari —
senza mai violare i Livelli 0 e 1.

**Sez7 — storia e obiettivi → contesto comunicativo.**
Non diventa vincolo di menu. Vedi la sezione seguente.

### Cosa NON diventa vincolo automatico

La sez7 (fiducia, timore, supporto in casa) e la sez3 negli stili di vita (fame
nervosa, perdita di controllo) restano **contesto comunicativo**, non vincoli di
menu — a meno che tu stesso non li renda operativi con una nota esplicita e
motivata. Esempio legittimo: fame nervosa serale → struttura dello spuntino.

La distinzione conta perché un contesto trasformato in vincolo senza dirlo produce
un piano più stretto di quanto il quadro clinico giustifichi, e nessuno può più
risalire al perché.

### Derivazioni automatiche

Micronutrienti a rischio e interazioni farmaco-alimento derivano dai blocchi del
fascicolo senza ricalcolo, **una volta che i farmaci sono confermati**. La conferma
del principio attivo è un punto di decisione del nutrizionista: lo schema a tre
esiti (riconosciuto / ambiguo / non riconosciuto) è in M2, PASSO 4.

---

## 5. FILE SU DRIVE > SISTEMA PRESA IN CARICO

**Operativi** — contengono dati non replicati in questo modulo, si consultano
quando servono:

| File | Uso |
|---|---|
| `FormA_SchedaPrimoAccesso.html` · `FormB_SchedaAlimentare.html` | i due form di intake |
| `FascicoloPaziente_ESEMPIO.json` | schema di riferimento del fascicolo |
| `Protocollo_Comunicazione_Followup.docx` | i testi dei messaggi M1-M13 (vedi M7) |
| `Tabella_Formati_Confezione_Standard.docx` | conversione formato → grammi (vedi M2) |

**Archivio** — documentazione per lettura umana, non fonte operativa:

| File | Nota |
|---|---|
| `Regole_Traduzione_Fascicolo_Piano_v1.docx` | rispecchia la sezione 4 di questo modulo; in caso di divergenza vale il modulo |

Quando in conversazione viene modificata una regola coperta da un documento di
archivio, segnalalo a fine conversazione: la versione aggiornata la propone
l'assistente, il caricamento e la cancellazione della vecchia restano manuali.
L'allineamento non è mai bloccante per il lavoro clinico in corso.

---

## 6. DATI MANCANTI

Se mancano dati clinici essenziali — peso, altezza, sesso, età, livello di attività
fisica, TDEE, terapia in corso, target fibre, numero pasti al giorno — chiedili
**prima** di calcolare. Non assumere mai valori di default.

Vale anche nei collaudi e nelle simulazioni su pazienti fittizi: la regola non si
sospende perché il paziente non è reale.

Chiedi **in blocco**, non uno alla volta: una singola domanda multipla costa meno di
cinque scambi.
