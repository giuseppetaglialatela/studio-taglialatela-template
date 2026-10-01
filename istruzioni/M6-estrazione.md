# M6 — ESTRAZIONE ALIMENTI

Modulo operativo. Si carica quando si amplia il database alimenti: un piano
richiede una voce che non esiste ancora, oppure va chiuso un gap dichiarato.
Dipende da **M1 (Motore di calcolo)**: schema CSV, gerarchia fonti, gap.csv,
verifica di derivazione USDA e chiave API stanno lì, non qui.

Rimandi:
- gerarchia fonti, schema congelato, gap.csv, controllo derivazione USDA → **M1**
- regole pesi e formati confezione → **M0** (ripetute per intero in **M2**)

Non si amplia il database durante la composizione di un piano senza dichiararlo:
ogni riga aggiunta cambia i checksum e obbliga a rieseguire collaudo e
regressione (passo 8).

In caso di divergenza tra questo modulo e il Protocollo_Estrazione_Alimenti.docx
su Drive, vale questo modulo (nucleo M0, principio 6).

---

## 1. I NOVE PASSI

**1. Spoglia il piano.** Elenca ogni ingrediente con grammatura. Distingui gli
ingredienti reali dei piatti dalle voci presenti solo nelle tabelle di
equivalenza: queste hanno priorità più bassa.

**2. Chiedi le specifiche ambigue PRIMA di cercare**, in un'unica domanda
multipla: ingredienti senza grammatura, categorie generiche ("frutta fresca",
"verdura a foglia", "pesce bianco"), varianti grasse (yogurt/latte magro o
intero), frutta secca generica. È il passo che fa risparmiare più tempo.

**3. Chiedi la regola crudo/cotto per quel piano.** Non darla per scontata
(→ M2, regole pesi).

**4. Cerca PRIMA nella cache locale.** La cache delle risposte API BDA-IEO
(`cache.zip`, 1.109 alimenti JSON con fonte citata per ogni valore) sta su
GitHub nella cartella `motore-calcolo`, insieme a `BDA_alimenti.xlsx`.
Scaricala accanto ai moduli e interrogala in blocco:

```
python3 cerca_cache.py ricerca "nome1" "nome2" "nome3"
python3 cerca_cache.py ricerca --file nomi.txt
python3 cerca_cache.py estrai <idFood>
```

Una sola ricerca su tutti i nomi: evita una ricerca web per alimento, che è
lenta e fragile. `estrai` applica già le regole del passo 6 su tracce e dati
assenti.

Cerca anche i **sinonimi**: "kefir" non dà risultati e "latte fermentato"
nemmeno, ma "cornetto" trova CORNETTO O BRIOCHE e "caffè" trova undici voci. Un
nome non trovato al primo tentativo non significa che l'alimento non ci sia.

**5. CREA dalla cache locale, non dal sito.** CREA è il livello 1 (kcal, macro, fibra,
minerali) e va consultata per OGNI alimento nuovo, in coppia con la cache BDA-IEO del passo
4. `crea_cache.zip` (832 schede, stessa cartella `motore-calcolo`) si interroga con
`python3 cerca_crea.py ricerca "nome"` e `python3 cerca_crea.py estrai <codice>`: riporta i
valori con il codice di origine, segnala campi assenti, tracce, valori imputati e parte
edibile. Il fetch delle pagine del sito non è più il percorso normale: passa da un
riassunto di modello, non da una copia, e il 01/10/2026 il confronto con la cache ha
trovato 7 kcal del database diverse dalla scheda. Resta solo per una scheda che manca dalla
cache (ricerca web per il link, poi fetch; i valori vanno riletti due volte).

**6. Estrai e gestisci i casi speciali.**

| Caso | Cosa scrivere |
|---|---|
| `tr` (traccia) | il valore di soglia (`vltraccia`, BDA-IEO), **non** zero. La cache CREA non porta la soglia: `estrai` segnala la traccia, il valore si decide |
| campo assente | scendi al livello successivo della gerarchia, fino a USDA compreso; solo se manca ovunque lascia 0 **e aggiungi una riga a gap.csv** con il motivo |
| zero biologico reale | 0 senza segnalazione (es. B12 in un vegetale) |

Non basta segnalare un dato mancante a voce: se non è in `gap.csv`, il motore
non lo sa e lo somma come zero reale.

La differenza tra dato mancante e zero reale è la più importante di tutto il
protocollo: confonderli produce falsi allarmi di carenza. È già successo due
volte — la vitamina D delle sardine (5,8% LARN apparente su una giornata che ne
conteneva sette volte tanto) e il magnesio del cornetto lasciato a zero
fermandosi a CREA, quando BDA-IEO lo pubblica a 73 mg/100 g: il 21% del LARN
giornaliero invisibile, nella direzione che fa inseguire un deficit inesistente.

Anche USDA può presentare uno zero che è un'assunzione e non una misura: la
verifica di derivazione (`foodNutrientDerivation`, codici Z / NC / dataPoints 0)
è obbligatoria ed è descritta in **M1**.

Quando due fonti indipendenti concordano su uno zero **esplicito** (non un
silenzio, non "tr"), trattalo come zero reale e non dichiararlo in gap.csv: due
fonti che tacciono insieme non è la stessa cosa di due fonti che misurano e
concordano.

**7. Scrivi le righe con la fonte tracciata.** Il campo `fonte` dice da dove
viene ciascun dato (es. `CREA+BDA-IEO`, `CREA+BDA-IEO(proxy)+USDA`). Se usi una
voce generica al posto di quella specifica, marcala come proxy e dichiarala.

- **`codice_fonte`:** codice CREA e id BDA-IEO separati da `+` (es. `135030+1604`), come
  nelle righe già presenti; per USDA si aggiunge l'`fdcId`; per l'eccezione INSA
  (M1 sezione 4) si aggiunge `INSA<cod>` (es. `122800+INSA882`).
- **Un alimento = una riga.** Prima di aggiungere, controlla che non esista già
  sotto un altro nome (sarda/sardina): due righe per lo stesso alimento non sono
  un duplicato di `food_id`, quindi nessun controllo automatico le vede, e chi
  compone un piano può prendere quella sbagliata.
- **Mai food_id inventati** (999xxx) né valori "di convenzione": ogni riga deve
  avere `codice_fonte` e `data_verifica` compilabili. Se non lo sono, l'alimento
  non entra — si usa un proxy dichiarato oppure si esclude.

**8. Chiudi il ciclo tecnico.** In quest'ordine:

```
python3 cerca_crea.py verifica   # kcal, macro e fibra delle righe CREA = cache
python3 coerenza.py          # sull'INTERO database, non solo sulle righe nuove
# aggiorna EXPECTED_ALIMENTI_COUNT in collaudo.py
python3 collaudo.py --genera-checksums
python3 collaudo.py
python3 regressione.py
```

Se il numero di alimenti caricati non è quello atteso, è un errore di formato
nel CSV.

**9. Riporta quattro cose:** quanti alimenti aggiunti e quali; quali non trovati
e perché; quali flag e se sono reali o falsi positivi noti; quali righe sono
state aggiunte a gap.csv. Poi indica i **due** file da ricaricare su GitHub:
`alimenti.csv` sciolto e `motore calcolo.zip` (checksum e conteggio atteso
aggiornati). Caricarne uno solo fa fallire il collaudo alla sessione dopo.

Link di upload:
`https://github.com/giuseppetaglialatela/studio-taglialatela-template/upload/main/motore-calcolo`

---

## 2. COSA NON ENTRA NEL DATABASE

- **Prodotti di marca** — se esiste una voce generica equivalente si usa quella,
  altrimenti si esclude.
- **Integratori** (whey, proteine in polvere, formulazioni): non sono alimenti e
  nessuna delle tre fonti li censisce. Il loro apporto si dichiara a parte nel
  piano, non si trasforma in una riga del database.
- **Preparazioni composte e ricette non censite** (hamburger confezionati, misti
  in busta, muesli): sono assemblaggi. Da non confondere con le preparazioni che
  CREA pubblica con un codice proprio (pane, cornetti, pasta all'uovo): quelle
  sono dati di livello 1 a pieno titolo.
- **Alimenti non censiti da nessuna delle tre fonti**: si segnala e si propone il
  proxy più vicino, ma non si inventa la riga.
- **Valori da etichetta commerciale**: non sono una fonte della gerarchia. Un
  cartellino nutrizionale UE dichiara solo energia, grassi, saturi, carboidrati,
  zuccheri, proteine e sale — 4 delle 13 colonne nutrizionali dello schema — e
  lascerebbe 9 campi a zero, tra cui il calcio su un latticino. L'uso legittimo
  della foto di una confezione (formato in grammi, variante del prodotto) è in
  **M2**.

---

## 3. CRITERIO DI AMPLIAMENTO

"Key Foods": un alimento si aggiunge solo quando un piano reale lo richiede e
non è già presente. Oltre le 150 voci solo su richiesta esplicita del
nutrizionista.

Stesso criterio per `moduli_pasto.csv`: un blocco si aggiunge quando un piano
reale lo richiede. Range utile a regime 20-30 blocchi; oltre, la libreria
diventa più lenta da consultare che ricostruire il pasto.

---

## 4. PIANI GIÀ SPOGLIATI — non rifarli

Mattei · Ivan Vitale · Renata de Angelis (piano + nuove alternative) ·
Mariapia Florio · Marta · Antonio Taglialatela · Federica Coppola ·
Sollazzi Giuseppe (da cui le voci di pesce/molluschi del 27/07) · Marco Giaccio
(01/10/2026, prova di conversione di una dieta esterna: mais in scatola, burro d'arachidi,
farina d'avena, latte scremato, fette biscottate, fuso di pollo, filetto di manzo, yogurt
greco 0%).

Da questi piani sono già stati estratti anche i blocchi pasto riutilizzabili
confluiti in `moduli_pasto.csv`.

---

## 5. CERCATI E NON TROVATI — non riprovare

primo sale · muesli · misto cereali e legumi precotti in busta · condimento
verdure Saclà · hamburger di tacchino confezionato.

**Kefir** — cercato su tutte e tre le fonti il 28/07/2026, anche come "latte
fermentato". CREA e BDA-IEO non lo hanno; USDA ha solo prodotti di marca
(LIFEWAY, lowfat), fortificati con vitamina D per l'arricchimento obbligatorio
statunitense e quindi non trasferibili. SmartFood-IEO dichiara la composizione
del kefir paragonabile a quella dello yogurt: usare come **proxy dichiarato** lo
yogurt di latte intero (kefir intero) o parzialmente scremato (kefir magro), già
in database, senza creare una riga nuova.

**Cercati su USDA e non risolti** (non riprovare senza una fonte nuova) —
vitamina D di: orata (USDA non ha *Sparus aurata*, solo generici commerciali) ·
latte parzialmente scremato (né CREA né BDA-IEO la pubblicano; il dato USDA viene
da fortificazione — vedi M1). La sardina fresca è stata risolta il 01/10/2026 con
la tabella portoghese INSA (eccezione dichiarata, M1 sezione 4): la stessa tabella
ha anche orata cruda e latte parzialmente scremato, candidati per chiudere i
rispettivi gap, sempre su decisione del nutrizionista.

**Esclusi per scelta del nutrizionista** (non riproporre): trippa.

---

## 6. PROXY DICHIARATI — 28/07/2026

Restano scritti qui perché siano verificabili in seguito.

**Da cache BDA-IEO**
- Vitello filetto crudo (`folati_ug`, `vitamina_b12_ug`): la cache non ha il
  taglio "filetto", usato "vitello 4 mesi, carne magra" generico. Fonte marcata
  `CREA+BDA-IEO(proxy)+USDA`.

**Da USDA, blocco magnesio** — sei valori da match non univoco:
- cipolline (proxy su cipolla generica cruda)
- lattuga (media generica, non iceberg né romana)
- olive nere (voce USDA "ripe canned" stile californiano, composizione diversa
  dall'oliva nera mediterranea)
- peperoni dolci (varietà rossa come rappresentativa)
- pomodori pelati (proxy su "crushed canned")
- zucca gialla (proxy su butternut)

**Audit ancora da fare**: i 35 valori di magnesio scritti il 28/07/2026 sono
stati presi prima che la verifica di derivazione diventasse regola. Essendo
tutti non-zero, la trappola dello "zero assunto" non li riguarda, ma alcuni
potrebbero essere imputati anziché analitici: una passata di controllo sui loro
`fdcId` resta da fare.

**Fave secche cotte** — caso a parte: minerali e folati presi dalla voce BDA
delle fave *crude* (proxy), quindi probabilmente **sovrastimati**, non
sottostimati. Non usarle come fonte portante di ferro o folati.

---

## 7. PROXY E DATI DEBOLI — 01/10/2026

Dal piano Giaccio. Restano scritti qui perché siano verificabili in seguito.

- **Filetto di manzo (101170):** la dieta originale diceva «Scottona»; usata la scheda CREA
  «Bovino adulto o vitellone, filetto, crudo» come proxy (fonte marcata `proxy scottona`).
- **Burro d'arachidi (009010):** CREA riporta magnesio 18 mg, BDA-IEO 180 mg. Entrambe
  citano McCance & Widdowson (BDA riporta il nome originale «Peanuts butter, smooth»).
  Il 180 è confermato da CREA arachidi tostate (175, analitico), USDA (168 su 18 campioni,
  193 su 8) e INSA arachidi (160-180): il 18 di CREA è un errore di trascrizione della sua
  stessa fonte. Scritto 180 da BDA-IEO, confermato il 01/10/2026.
- **Sardine (122800):** micronutrienti passati a INSA 882 «Sardinha gorda crua» il
  01/10/2026 (decisione del nutrizionista; motivazione e valori in M1 sezione 8).
  Metodo che l'ha fatto emergere: confronto della stessa voce tra fonti diverse con
  segnalazione degli scarti di almeno 3 volte. Limite: CREA e BDA-IEO non sono
  indipendenti per molti alimenti italiani (valori identici), quindi il loro accordo
  prova meno dell'accordo con USDA o INSA.
- **Fuso di pollo senza pelle (106410):** parte edibile 66%: il peso nel piano va espresso
  senza osso. La variante con pelle (106400, 125 kcal) esiste in cache ma non è nel
  database: nessun piano la richiede.
- **Yogurt greco 0% (150030):** macro da CREA; CREA non pubblica i minerali. Calcio, ferro,
  zinco, magnesio e B12 da USDA Foundation 330137 (analitici, 18 campioni; B12 9). Vitamina D
  0 da USDA (analitica, 1 campione: debole). Folati 7 µg da USDA SR Legacy 170894
  (derivazione DA, 0 campioni) e vitamina C 0 (label claim, 1 campione): **dati deboli**.
  Formato confezione 125|150|170 copiato da 8053, stato `da_confermare`.
- **Mais dolce in scatola (000070):** nessun formato di confezione registrato in
  `formati_confezione.csv` (da confermare prima dell'uso nei piani).
- **Ravanelli (005670) e fuso con pelle (106400):** presenti in cache CREA, non aggiunti
  (criterio Key Foods: nessun piano li richiede).
