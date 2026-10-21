# ARCHIVIO — Motivazioni ed episodi del modulo M2

NON è un modulo operativo e NON si carica nelle sessioni: le regole stanno in
`istruzioni/M2_workflow_piano.md`. Qui sta il PERCHÉ delle regole e la loro storia.
Spostato da M2 il 21/10/2026 con la versione asciutta.

---

## Cronologia di M2 (prima della versione asciutta)
- 21/10/2026: libreria degli accoppiamenti anche per colazioni e spuntini; accoppiamenti
  vietati segnalati dal PASSO 4 della pipeline; rimando all'eccezione etichetta.
- 30/09/2026: struttura fino a 5 pasti (secondo spuntino, `spuntino2`).
- 29/09/2026: confezionati senza spreco.
- 18/09/2026: kcal e macro giudicati sulla media settimanale; limite di sicurezza ±10%.
- 29/07/2026: micronutrienti giudicati sulla media settimanale (principio 8).

## Regole pesi — perché si leggono prima di ogni calcolo
L'errore realmente rilevato su questa regola valeva +42% su un singolo pasto e +9,3% sul
totale giornata. La stessa dicitura («al vapore», «lessati») può significare cose diverse
a seconda dell'alimento: per questo nel dubbio si chiede. Il documento Word dei formati
su Drive è archivio; la fonte è `formati_confezione.csv`.

## Colazioni uguali tutti i giorni — la tensione con i micronutrienti
Fissare la stessa colazione e lo stesso spuntino su tutti i giorni toglie la leva che
serviva a compensare calcio e vitamina D nei giorni deboli, e sposta il bilanciamento su
pranzo e cena. Su un paziente con pranzo vincolato (mensa, halal, patologia) il margine
può non bastare: da qui il livello `rinforzata_calcio`.

## Criterio del livello rinforzato — perché è «da decidere»
Il criterio storico («anche un solo giorno sotto l'80% LARN di calcio») è dal 29/07/2026
l'unico punto in cui sopravvive una soglia giornaliera, contro il principio 8. Non è
necessariamente un residuo: il calcio è l'unico nutriente con un argomento reale per la
lettura per giorno (assorbimento saturato intorno ai 500 mg per singola assunzione). Ma il
criterio usa l'80% LARN giornaliero, che è una soglia, non un argomento di distribuzione.

## Livelli misti
Una colazione di un livello con lo spuntino dell'altro lascia i giorni tutti uguali tra
loro: il solo controllo di uniformità non la vedrebbe. Per questo il PASSO 6 della
pipeline riconosce anche il livello.

## Scenari di scelta — perché per ogni giorno e prima della tabella
Verificare una sola combinazione «esemplare» per giorno fa emergere l'errore dopo che il
nutrizionista ha già visto una tabella: è il punto in cui è più costoso. Entrambi gli
errori di processo del primo caso reale sono nati dall'ordine dei passi ricostruito a mano.

## Correzioni naturali — esempi da evitare
400 g di merluzzo in un pasto, 7 albumi in una frittata: correzioni forzate per far
rientrare un giorno. L'aderenza è un esito clinico.

## Vitamina D
Anche con pesce grasso 3 volte a settimana la media resta intorno al 65-75% LARN; oltre
servirebbe pesce grasso quasi quotidiano.

## Interazioni — perché la terapia va tradotta nei CSV
Un'osservazione discorsiva nella Tabella Vincoli non è una verifica: se i file non arrivano
alla pipeline, il motore non controlla nulla. Il meccanismo deve corrispondere alla
farmacologia reale: una separazione oraria ha senso per un'interazione di assorbimento
sistemico, non per un farmaco che agisce localmente sul contenuto gastrico. Una riga
proposta e non validata, se non dichiarata, alla rilettura viene scambiata per dato
consolidato.

## Metadati del piano
Nati per separare la chat A (calcoli e approvazione) dalla chat B (PDF): le istruzioni di
passaggio rimandano al file invece di riassumerlo. Indicazioni del giorno libero solo per
pranzo e cena: decisione del 19/09/2026.

## Stato del protocollo struttura pasti
Introdotto dopo il test sul paziente fittizio P00.

## Gap e carenze
Un intervento clinico su una carenza inesistente (un nutriente sottostimato per un gap) è un
errore, non una precauzione. Non inseguire i micronutrienti con gli alimenti perché
l'aderenza è un esito clinico.

## 21/10/2026 notte — revisione indipendente della versione asciutta
Trovati e corretti nel testo, verificati sul codice: campi dei metadati (lo script usa anche
`versione_piano` e `abbinamento_spuntino` senza fermarsi se mancano; giorno libero
condizionale); «non concordato» accettato dallo script anche per obiettivo, criterio e
avvertenze, che finirebbero così nel PDF del paziente; livelli misti declassati ad
attenzione da una deroga di struttura presa per altro motivo; terapia dichiarata nel
fascicolo senza i tre CSV, che lasciava il piano apparentemente presentabile; definizione
di «presente» del motore (valore > 0, scenario massimo, tracce comprese); limite ±10% esteso
agli scenari come nel nucleo. Gli ultimi quattro difetti c'erano già nel vecchio M2.
