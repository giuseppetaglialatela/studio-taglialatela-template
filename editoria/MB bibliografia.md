# M-B — REGISTRO BIBLIOGRAFICO
Modulo operativo del progetto editoriale e formativo — Studio Taglialatela
Ultima modifica: 13/08/2026 · Dipendenze: nessuna

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

## 2. CARICAMENTO A INIZIO SESSIONE

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
| `stato` | `verificata`, `da_verificare`, `da_reperire`, `superata` | Vedi sezione 6 |

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
| `T0` | Trasversale (dati di settore, contesto normativo generale) |

Una fonte può servire più temi. È il caso normale, non l'eccezione: gli RCP
valgono per T1 e T2 insieme, e questo è esattamente il punto del progetto.

---

## 5. GERARCHIA DELLE FONTI

| Livello | Cosa | Esempi |
|---|---|---|
| 1 | Regolatorie | RCP da AIFA, EPAR EMA, testi da Normattiva |
| 2 | Linee guida e consenso | ISS/SNLG, società scientifiche, Manuale FOFI |
| 3 | Revisioni sistematiche | Cochrane, review indicizzate |
| 4 | Studi primari | Singoli trial, studi osservazionali |

**Non entrano nel registro** riviste di settore, siti divulgativi, schede
prodotto aziendali, blog. Si leggono per orientarsi; poi si risale alla fonte
che citano e si registra quella. Se un'affermazione esiste solo su una rivista
di settore e non è tracciabile a monte, non si usa.

Regola: mai una raccomandazione operativa basata su un solo studio di livello 4.

---

## 6. STATI

- `verificata` — testo integrale letto, citazione controllata sulla fonte
- `abstract_verificato` — letto l'abstract completo, full text non accessibile
  (paywall). **Usabile**, ma solo per ciò che l'abstract afferma davvero: le
  conclusioni sintetiche, non i dettagli di metodo o i sottogruppi. Va
  dichiarato nell'`esito_sintetico` cosa si è potuto leggere
- `da_verificare` — citazione presa da un riferimento indiretto, non ancora
  aperta di persona. **Non usabile in un deliverable** finché non diventa
  `verificata` o `abstract_verificato`
- `da_reperire` — si sa che esiste, non si è ancora trovato il testo
- `superata` — sostituita da una versione più recente. Non si cancella: si
  marca, così un modulo vecchio che la cita resta interpretabile

**Perché `abstract_verificato` esiste.** Molte revisioni sistematiche hanno il
full text a pagamento. Pretendere il testo integrale per ogni fonte renderebbe
la regola impossibile da rispettare, e una regola impossibile viene aggirata:
si finirebbe per marcare `verificata` una fonte letta a metà, che è esattamente
il rischio da cui il registro deve proteggere. Meglio uno stato onesto e un uso
limitato.

Regola d'uso: da un `abstract_verificato` si può ricavare la conclusione
generale, mai un numero specifico, un sottogruppo o un dettaglio di metodo. Per
quelli serve il testo.

La distinzione tra ciò che si è letto e ciò che si è dedotto è la sola che
protegge dal citare una fonte che non dice quello che si crede. Va rispettata
anche quando sembra pedante.

---

## 7. COMPORTAMENTO OPERATIVO — cosa faccio io

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

Il file completo serve perché il caricamento su GitHub sullo stesso percorso
sostituisce il file (a differenza di Drive, dove creerebbe un duplicato).

**Assegnazione degli ID**
Leggo l'ultimo `id` presente e proseguo. Mai ripartire da `F001`. Mai riusare un
id di una riga rimossa.

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

Misura attesa: 20-30 voci per un modulo FAD, 8-12 per un articolo di rivista.
Cinquanta voci su un modulo di due ore segnalano accumulo, non rigore.
