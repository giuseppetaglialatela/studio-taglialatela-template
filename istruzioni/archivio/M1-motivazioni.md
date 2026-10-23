# ARCHIVIO — Motivazioni ed episodi del modulo M1

NON è un modulo operativo e NON si carica nelle sessioni: le regole stanno in
`istruzioni/M1_motore.md`. Qui sta il PERCHÉ delle regole e la loro storia, per chi le
rivede o le vuole cambiare. Spostato da M1 il 21/10/2026 con la versione asciutta.

---

## Cronologia delle versioni di M1 (prima della versione asciutta)
- 21/10/2026, quarto giro: niente più zip, motore sciolto in `motore-calcolo`, scaricato con
  un comando; modifiche salvate da Claude con un commit.
- 21/10/2026, terzo giro: regole di accoppiamento su alimento preciso e per pasto; A03
  formaggi diversi, A04 merluzzo + pasta, A05 carne rossa o maiale + pasta, A06 due frutte
  secche nello stesso pasto; M01 e C37 tolti; casi golden 16 e 17.
- 21/10/2026: database a 144 voci (crema di nocciole e cacao, pangrattato, semi di lino);
  semi di lino tra i falsi positivi Atwater; libreria a 129 blocchi pranzo/cena e 56
  colazioni/spuntini; M11 corretto a pasta integrale.
- 21/10/2026, prima: controllo degli accoppiamenti vietati (`ruoli_alimenti.csv`,
  `accoppiamenti_vietati.csv`, `accoppiamenti.py`, PASSO 4 controllo F, collaudo controllo 8,
  caso golden 15); libreria estesa a 105 blocchi pranzo/cena e 43 colazioni/spuntini;
  database a 141 voci.
- 01/10/2026: `cerca_crea.py` e cache CREA; kcal di 7 voci allineate a CREA; carciofi tra i
  falsi positivi Atwater; eccezione INSA per i micronutrienti delle sardine.
- 30/09/2026: struttura a 5 pasti (valore `spuntino2`, controllo PASTO_NON_AMMESSO, casi
  golden 12-14).

---

## Avvio — perché una sola copia di tutto
Lo zip era nato per il caricamento manuale; con il salvataggio diretto via commit non serve
più. Il 28/07/2026 quattro copie sciolte obsolete divergevano dallo zip da tre fasi, e un
`gap.csv` duplicato dichiarava mancanti dati già recuperati.

## collaudo.py — perché il controllo 5 (impronte)
I primi quattro controlli non vedono una modifica che resta sintatticamente valida.
Verificato il 28/07/2026 cambiando il calcio del pane integrale da 25 a 26 mg: conteggio
giusto, nessun duplicato, giornata golden identica (usa `alimenti_test.csv`), tutto verde.
Solo il controllo delle impronte se ne accorgeva.

## collaudo.py — perché i file opzionali non sono obbligatori
Dal 01/10/2026 `cache.zip`, `BDA_alimenti.xlsx` e `crea_cache.zip` sono elencati in
`SHA256SUMS`: prima non c'erano e il collaudo li segnalava solo come informativi, quindi una
cache corrotta non veniva vista. Richiederli sempre farebbe fallire il collaudo di routine,
e un collaudo che fallisce di routine smette di essere letto.

## collaudo.py — perché rigenerare le impronte solo dopo aver capito
Un ampliamento legittimo non ancora registrato e una corruzione silenziosa si presentano
allo stesso modo. Rigenerare per far tornare verde un collaudo rosso annulla il controllo.

## pipeline.py — perché esiste
L'ordine dei passi era imposto per convenzione e viveva nelle istruzioni, non nel software.
Entrambi gli errori di processo del primo caso reale sono nati da lì.

## pipeline.py — perché PASTO_NON_AMMESSO blocca
Un refuso come `spuntino 2` verrebbe sommato nei totali ma scartato dal PDF.

## pipeline.py — giudizio settimanale
Micronutrienti settimanali dal 29/07/2026; kcal e macro settimanali e limite di sicurezza
giornaliero ±10% dal 18/09/2026 (decisione clinica). Prima del 18/09 il giorno fuori
tolleranza bloccava.

## pipeline.py — perché la verifica (b) del PASSO 6
I giorni sono tutti uguali tra loro, quindi la sola verifica di uniformità (a) lascia
passare una colazione standard abbinata a uno spuntino rinforzato.

## pipeline.py — secondo spuntino
Segue le regole dello spuntino per decisione del 30/09/2026.

## regressione.py — perché un controllo nuovo va in una funzione condivisa
La suite ripete la sequenza di `pipeline.main()` invece di chiamarla: un controllo scritto
solo dentro `main()` non viene visto dalla suite. Esempio: `controlla_pasti_ammessi`.

## regressione.py — perché i casi pipeline congelano i codici e non la prosa
Riformulare un messaggio non deve far diventare rossa la suite.

## Kcal allineate a CREA — 01/10/2026 (e lezione sul caso 04)
Il confronto con la cache CREA ha trovato 7 righe con kcal diverse dalla scheda: riso
332→334, carciofi 22→33, porri 29→35, barbabietole 19→25, arance 34→37, mandarini 72→76,
olive verdi 142→148. In quattro casi il valore era vicino al ricalcolo 4/4/9 dei macro,
contro la regola «kcal lette da CREA, mai ricalcolate». Allineate. Effetto sulla suite: i
casi 02 (olive), 04 (riso) e 12 (arance) cambiano di +1,20, +1,60 e +6,00 kcal, verificati
a mano riga per riga prima di rigenerare gli attesi. Nel caso 04, tarato sul confine ±5
punti, rigenerare l'atteso NON bastava: i totali nuovi avevano spostato le percentuali e il
verdetto sulle proteine era passato da FUORI a OK. I target sono stati ricalibrati con gli
stessi scarti di prima (+5.001 e +4.999).

## Casi golden — regole verificate al contrario
Le regole del 30/09/2026 sono state verificate togliendole dal codice: la suite diventa
rossa esattamente sul caso che le sorveglia. Lo stesso per i casi 15-17 (21/10/2026),
svuotando le regole di accoppiamento.

## Casi golden — dettagli di costruzione
- caso 01: validato contro il collaudo archiviato del 26/07/2026.
- caso 05: giorni a -4,56% e -2,03% di kcal, dentro tolleranza anche su tutti e tre i macro.
- caso 07: complementare al caso 06 (quello sorveglia i flag per giorno del PASSO 2, questo
  quelli del PASSO 3).
- casi 08-10: generati il 18/09/2026 con la decisione sul giudizio settimanale e sul limite
  di sicurezza; caso 11 il 29/09/2026 come copia del caso 07.
- caso 13: target tarati sui macro reali perché non compaiano altri rilievi.
- caso 15: verificato al contrario svuotando le regole.

## Casi golden — limite di copertura, episodio
Il 28/07/2026 l'aggiornamento della vitamina D di branzino, gambero, maiale e vitello ha
lasciato la suite verde senza rigenerazione: quegli alimenti non sono in nessun caso.

## calcolatore.py — unica fonte dei pasti
Il 30/09/2026 i 4 pasti erano scritti a mano in quattro file.

## formati.py
Non bloccante per decisione del 29/09/2026.

## accoppiamenti.py
Segnala e non blocca, coppie aggiunte man mano: decisioni del 21/10/2026.
Falso allarme sui piani anteriori al 30/09/2026, caso reale: latte nello spuntino del
pomeriggio, yogurt in quello del mattino, registrati entrambi come `spuntino`.

## cerca_cache.py / cerca_crea.py
`cerca_cache.py` traduce in comando il PASSO 4 del protocollo di estrazione (M6), che prima
era una procedura a memoria. `crea_cache.zip` (scaricata il 20/09/2026) sostituisce la
lettura delle pagine del sito CREA, che passava da un riassunto di modello e non lasciava
traccia di un valore trascritto male.

## tdee.py e genera_zona_piano.py
Entrambi nel motore dal 19/09/2026; `tdee.py` era l'ultima cosa tecnica rimasta su Drive.
Prima del 30/09/2026 le kcal di un pasto a scelta diverso da colazione e spuntino restavano
fuori dal totale del giorno del PDF. Convenzione 7.700 kcal/kg e totale del giorno libero
da `range_kcal_libero`: decisioni del 19/09/2026.

## larn.csv — perché la V revisione
Decisione del nutrizionista del 19/09/2026. I valori usati prima erano un ibrido IV/V
revisione tarato sull'uomo adulto: B12 2,4 µg, folati 400 µg, calcio 1000 mg.

## colazioni_spuntini.csv — perché solo ingredienti
La prima versione portava i valori precalcolati, e il 28/07/2026 il ricalcolo ha trovato 71
valori su 72 corretti e uno sbagliato: l'alternativa S1 dichiarava 0,20 µg di vitamina D
contro 2,10 reali, un fattore dieci sul nutriente che è già il limite noto della dieta, e
nella direzione che fa sembrare coperto ciò che non lo è. Il dato a monte era sano:
l'errore stava nel derivato.

## moduli_pasto.csv — perché solo ingredienti
Portava valori precalcolati fino al 29/07/2026, quando il ricalcolo ha trovato 165 valori su
168 corretti e tre sbagliati: la vitamina D di M18, M20 e M22. NON erano errori di
trascrizione: erano corretti il 27/07 e sono diventati falsi il 28/07, quando la vitamina D
di gambero e polpo è stata recuperata da USDA. La fonte è migliorata sotto il derivato: via
di divergenza più insidiosa di quella di S1, perché non richiede alcun errore umano.

## moduli_pasto.csv — storia dei blocchi
M25-M105 dal 21/10/2026, tag ricavati dai ruoli. M106-M129 dal 21/10/2026 sera (P01,
P06, P07, P04). M11 corretto lo stesso giorno: riportava la pasta di
semola dove il calcolo approvato di P01 (caso golden 01) usa la pasta integrale. M01
(pasta + merluzzo) tolto con la regola A04; C37 tolto con la regola A06. Il vecchio tetto di
20-30 blocchi è superato dalla decisione del 21/10/2026.

## nomi_paziente.csv — perché esiste
`alimenti.csv` porta il nome tecnico della fonte («Bovino magro vitellone senza grasso
visibile»): riscriverlo a mano a ogni piano è testo non controllato che arriva al paziente.

## Gerarchia fonti — perché scendere di livello sempre
CREA non pubblica calcio, ferro, vitamina D, folati e B12 per pesci e carni. Uno zero da
dato mancante si comporta esattamente come uno zero biologico: abbassa il totale e produce
un falso allarme di carenza. Fermarsi al livello 1 e scrivere «gap» è l'errore più comune,
ed è già costato una lettura falsata del magnesio.

## Gap chiusi
Il blocco magnesio (35 celle) è chiuso dal 28/07/2026 via USDA. Il gap calcio dell'olio
d'oliva è chiuso dal 28/07/2026: CREA e BDA-IEO concordano su uno zero esplicito, non un
silenzio. La riga vitamina D delle sardine è chiusa dal 01/10/2026 (micronutrienti INSA).

## USDA — episodio della derivazione
Il 28/07/2026 la verifica della derivazione ha evitato tre errori: cozza, polpo e trippa
risultavano a 0,0 di vitamina D con derivazione Z e dataPoints 0. Importare uno zero Z
significa ereditare in silenzio lo zero di qualcun altro.

## USDA — audit del magnesio
I 35 valori di magnesio scritti il 28/07/2026 sono stati presi prima che la verifica di
derivazione diventasse regola. Essendo tutti non-zero, la trappola dello zero assunto non
li riguarda, ma alcuni potrebbero essere imputati anziché analitici.

## Atwater — doppio criterio e falsi positivi
Su alimenti molto ipocalorici il cross-check sforava per puro effetto percentuale su numeri
piccoli: doppio criterio dal 28/07/2026. Numeri dei residui:
- AGLIO: 53 kcal dichiarate vs 44,8 ricalcolate, -15,5%, scarto 8,20 kcal, appena sopra
  soglia.
- CARCIOFI (dal 01/10/2026): 33 kcal CREA vs 22,6 ricalcolate, -31,5%, scarto 10,4 kcal; il
  metodo Southgate conta la fibra (5,5 g per 100 g, circa 11 kcal); macro e kcal coincidono
  con la scheda CREA.
- SEMI DI LINO `9600_1` (dal 21/10/2026): 447 kcal BDA-IEO vs 377 ricalcolate, -15,7%,
  scarto 70 kcal; BDA-IEO calcola l'energia «con fibra», 34,8 g × 2 kcal = 69,6 kcal;
  377 + 69,6 = 446,6.

## Sardine — storia della riga unificata
Esistevano due righe per lo stesso pesce: CREA 122800 (225 kcal, 15,4 g lipidi, ma
calcio/ferro/vitD/folati/B12 a zero perché CREA non li pubblica) e BDA 1319 «Sarda fresca»
(129 kcal, 4,5 g lipidi, micronutrienti completi). Entrambe corrette: la differenza è
variabilità stagionale reale del tenore lipidico. Fuse in 122800 secondo gerarchia. La
vitamina D veniva dal campione magro abbinato ai macro del campione grasso, quindi
probabilmente sottostimata.
01/10/2026: le due schede CREA delle sardine (122800 e 122700) citano lo stesso studio
(Karakoltsidis et al.) con valori incompatibili (Mg 70 contro 10, Zn 3,9 contro 0,8). INSA
v 7.1 – 2026, voce 882 «Sardinha gorda crua», misura Mg 31 e Zn 1,6, confermati da USDA
(39 / 1,31, in scatola) e da uno studio 2024 su sardine italiane crude (39,6 / 1,91 sul
peso fresco). La voce INSA corrisponde al campione dei macro CREA (221 kcal, 16,4 g lipidi
contro 225 e 15,4). Valori adottati: Ca 72, Fe 1,0, vitamina D 21, folati 15, B12 10, Zn 1,6,
Mg 31, vitamina C 0. La vitamina D era sottostimata di circa 4,7 volte.

## Stato di validazione — dettaglio
Il motore è stato validato ricalcolando riga per riga un piano reale già consegnato
(P01, lunedì): totale giornata rientrato in tolleranza (-4,56%) dopo la correzione della
regola sui legumi. Collaudo archiviato su Drive in `Motore di calcolo >
Collaudo_Motore_PianoP01_Lunedi`. Dal 28/07/2026 quella giornata è `caso_01_base`.

---

## 21/10/2026 notte — decisioni del nutrizionista dopo la versione asciutta
- **Eccezione etichetta.** La vellutata surgelata zucca e carote (`ETI001`, valori da
  etichetta, entrata il 17/10/2026) era nel database con 8 righe di gap; il blocco M81 la
  conteneva. Decisione: un'eccezione da etichetta passa solo su richiesta del
  nutrizionista e non va nel database. Tolte la voce (database a 143) e M81 (libreria a
  127). La prova sulla pipeline di allora ha mostrato tre difetti: una voce fuori database
  passava senza alcun avviso, i suoi micronutrienti a zero entravano nei totali senza flag
  di sottostima, gli accoppiamenti la ignoravano in silenzio. Da qui il controllo
  `ALIMENTO_FUORI_DATABASE` e l'opzione `--eccezione-etichetta`.
- **Gravità delle interazioni.** Riprodotto il difetto: ogni gravità diversa esattamente da
  «alta» diventava «media», per cui «Alta» con la maiuscola o un refuso facevano perdere il
  blocco a un'interazione grave. Corretto con lettura in minuscolo, codice per la gravità
  bassa, blocco sulle gravità non riconosciute (scelta tecnica delegata).
- **Gerarchia delle fonti.** La revisione aveva proposto di scrivere al livello 2 che kcal e
  macro vengono da BDA-IEO quando manca la scheda CREA (86 voci). Decisione: il testo della
  gerarchia resta com'era, le regole erano già state fatte.
- **Regole confermate come obbligo:** verifica al contrario di ogni regola nuova;
  ricalibrazione del target sui casi tarati su un confine.
- **Tag della libreria:** completamento approvato, criteri da fissare. I tag esistenti
  erano incoerenti (M10, tonno con 24,5 µg di vitamina D, senza tag vitD; M13 con 3,2 µg
  taggato; M20 con 309 mg di calcio senza tag calcio, M08 con 359 mg taggato).

## 21/10/2026 notte — esito della revisione indipendente sulle modifiche al motore
La revisione ha trovato un punto bloccante: con l'opzione `--alimenti` (copia di
`alimenti.csv`) un'eccezione etichetta poteva sostituire in silenzio una voce ufficiale,
perché il controllo dei doppioni confrontava con la copia. Tolta `--alimenti` dalla
pipeline (nessun modulo la usava): la pipeline usa sempre il database ufficiale, e la
voce non dichiarata diventa un `food_id` sconosciuto (il codice `ALIMENTO_FUORI_DATABASE`
non serve più). Corretti anche: file di eccezione malformati che facevano crollare lo
script o passavano (`nan`, negativi, righe corte, BOM di Excel); caricamento del database
e controllo dei food_id ora in funzioni comuni a pipeline e suite; `tipo_target` scritto
con la maiuscola o sbagliato, che annullava l'interazione in silenzio (stesso difetto
della gravità, già presente); caso 20 esteso alla gravità media; `genera_zona_piano.py`
con file mancante o nomi non corrispondenti. Tag della libreria: mensa_ok e pratico
assegnati da Claude a M25-M129 con criteri scritti (da confermare dal nutrizionista);
vitD, calcio e leggero calcolati con le soglie scelte dal nutrizionista (5 µg, 300 mg,
450 kcal). Effetto: M10 (tonno, 24,5 µg) prende vitD, M13 (sgombro, 3,2 µg) lo perde;
M20 (309 mg) prende calcio; M15 (501 kcal) e M19 (452 kcal) perdono «leggero». Secondo giro
di revisione: commit approvato; aggiunti i casi 23-24 e il nutriente maiuscolo nel caso 20
perché alcuni controlli del file di eccezione non erano sorvegliati dalla suite.

## 21/10/2026 notte — soglia di plausibilità delle etichette
Proposta dal revisore, approvata dal nutrizionista: proteine + carboidrati + grassi +
fibra non oltre 100 g per 100 g, solo per i file di eccezione etichetta. Verifica sul
database prima di applicarla: pop corn (109,2) e crema di nocciole e cacao (100,4)
superano 100 senza errori, perché CREA esprime i carboidrati disponibili in equivalenti
di monosaccaridi (amido circa ×1,1); per questo la soglia non si estende al database. La
revisione ha trovato che la somma in virgola mobile di un'etichetta esattamente a 100
(95,9 + 3,9 + 0,2) dava 100,00000000000001 e la bloccava: confronto arrotondato, caso 26.

## 23/10/2026 — catalogo ai formati di confezione
Il primo piano reale ha mostrato FORMATO_CONFEZIONE_NON_RISPETTATO scattare sul catalogo
standard stesso: 5 alternative fuori formato (S1 uova 120 g, S2 fiocchi 150 g, D2 e SPA
yogurt 150 g, SPrB yogurt 180 g). Decisione del nutrizionista: grammi ai formati. S2 con
pane ridotto da 60 a 45 g (395 kcal contro 371); SPrB a yogurt 250 g + nocciole 5 g (199
kcal, calcio 320 mg), perché con yogurt 125 g + nocciole 10 g lo spuntino rinforzato (171
mg) sarebbe stato più povero di calcio dello standard SPA (192 mg). Il collaudo ora ferma
un catalogo fuori formato. La libreria ha 29 blocchi fuori formato, 32 violazioni (pelati,
tonno, salmone, ceci, fagioli, uova, yogurt, fiocchi di latte): non controllata dal
collaudo finché il nutrizionista non decide come trattarli.
Ripiego d'avvio con git clone: nella chat clinica del 23/10 codeload.github.com era
bloccato (403), nella sessione di consolidamento dello stesso giorno no.

## 23/10/2026 — libreria ai formati, condimenti liberi, Atwater solo sul piano, nessuna terapia
Decisione del nutrizionista: i condimenti sono sempre a porzione libera (pomodori pelati
tolti da `formati_confezione.csv`, anche dove nella libreria fanno da porzione di verdura:
M84, M90, M95, M103, M105, M114). Il resto della libreria ai formati. Come è stato fatto
davvero (descrizione delle scelte, non una regola generale; revisione indipendente, due
giri): uova al formato più vicino, 104 g (due uova), anche dove sono l'unica proteina
(M04, M21, M24: 156 g sarebbero tre uova); tonno come unica proteina al formato più grande
(M14, 92 g), negli altri blocchi al più vicino; legumi in scatola a scatola intera (145 g),
non sostituiti da legumi da cuocere perché i blocchi sono «pratico», facendo posto con
meno cereale e, in M59 e M61, con meno tonno o uova (tonno 80→52, uova 104→52); yogurt al
vasetto singolo più vicino (125 o 150 g), mai al doppio; compensazione con un altro
ingrediente quando le kcal si spostavano oltre il 10%, e in qualche blocco anche sotto
(M14, M79, M108). Unica eccezione oltre il 10%: C36, i fiocchi di latte non si vendono
sotto 200 g. Il nutrizionista può rivedere ogni blocco: sono composizioni di partenza,
le grammature si adattano nel piano. Prima → dopo (kcal, proteine g, calcio mg):
- M04 607→587, P 28,6→26,6; M21 450→430 (diventa «leggero»); M24 643→610: uova a 104 g.
- M14 544→531, P 36,6→40,7: tonno 70→92 g (due scatolette), farro 80→70.
- M59 503→492, P 35,4→31,1: ceci 50→145 g (scatola), tonno 80→52, farro 70→45.
- M61 334→361: ceci 60→145 g, uova 104→52 (nome «uovo sodo»).
- M129 502→499: ceci 50→145 g, couscous 70→40.
- M79 492→506, P 29,4→36,3, calcio 256→120: salmone 75→135 g, pasta 55→50, olio 10→7,
  senza parmigiano (nome aggiornato). M128 429→458 (perde «leggero»): salmone 120→135.
- M84 528→540, M118 487→499: tonno 80→92. M88 587→615: ceci 215→240.
- M108 587→571: fagioli 90→145, tonno 40→46, riso 90→75, olio 12→10.
- C22 209→207: yogurt greco 100→125, mandorle 15→10. C34 295→306: yogurt greco 100→125,
  avena 30→25. C36 197→252 (+28%): fiocchi 100→200, mela 100→50, senza mandorle (nome
  aggiornato). C42 301→284, C44 373→363, C54 113→104, C55 93→84, C56 136→127: yogurt
  150→125. C47 273→248 (-9,3%), C48 243→237 (mandorle 12→15), C53 190→194 (gallette
  24→32): yogurt greco 0% 200→150, proteine da circa 20 a 16-17 g.
Il collaudo ora controlla anche la libreria.
Atwater e terapia, scelte delegate a Claude («la cosa migliore»): la pipeline guarda solo
gli alimenti del piano e non segnala i tre falsi positivi verificati; il collaudo controlla
l'intero database contro l'elenco in codice, con lo scarto atteso di ciascuno (±1 punto).
Prima un segnalato nuovo si perdeva tra i noti in ogni report. `--nessuna-terapia
"fonte"`: la verifica va dichiarata con la sua fonte, come una deroga; resta nel verdetto
come `TERAPIA_DICHIARATA_ASSENTE`; insieme ai file di terapia blocca, ma i file si valutano
comunque, perché un blocco per contraddizione non nasconda interazioni di gravità alta.
