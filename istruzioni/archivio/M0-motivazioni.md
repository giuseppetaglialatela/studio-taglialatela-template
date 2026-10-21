# ARCHIVIO — Motivazioni ed episodi del nucleo M0

NON è un modulo operativo e NON si carica nelle sessioni: le regole stanno nel nucleo M0
(istruzioni del progetto). Qui sta il PERCHÉ delle regole, per chi le rivede o le vuole
cambiare. Spostato dal nucleo il 21/10/2026 con la versione asciutta.

---

## Principio 2 — valori derivati
Un numero calcolato una volta e scritto accanto agli ingredienti diverge dalla fonte per
due vie: può essere sbagliato dalla nascita, o diventare falso quando il database migliora
sotto di lui. Nessuna rilettura rivela la seconda: bisogna ricalcolare.

## Principio 3 — direzione delle correzioni
La direzione di una correzione ("serve più grasso", "serve più fibra") non si decide per
intuito tecnico: un'ipotesi sbagliata nella direzione è lo stesso tipo di errore di un
calcolo a mente.

## Principio 7 — perché il collaudo è obbligatorio e sempre intero
Un CSV corrotto non si annuncia: produce numeri. Il 19/09/2026 un «collaudo breve»
proposto per risparmiare tempo è caduto alla prima misura: il collaudo completo durava
0,05 secondi.

## Principio 8 — perché il giudizio è settimanale
Tutti e otto i micronutrienti tracciati hanno riserve che tamponano su finestre più lunghe
di ventiquattr'ore: B12 anni, folati e ferro mesi, vitamina D settimane. La variabilità
giorno per giorno è attesa e fisiologicamente irrilevante. Inseguire il target ogni giorno
produce accostamenti che il paziente non mangia, e l'aderenza è un esito clinico: un piano
non seguito vale meno di un piano buono che viene seguito. Kcal e macro sulla media
settimanale: decisione clinica del 18/09/2026. Casi reali di correzione forzata da evitare:
400 g di merluzzo in un pasto, 7 albumi in una frittata.

## Sezione 5 — perché le regole pesi stanno nel nucleo
Un modulo non caricato è una regola non applicata, e su questa regola l'errore realmente
rilevato valeva +42% su un singolo pasto e +9,3% sul totale giornata. Confezionati senza
spreco: decisione del 29/09/2026. Le percentuali di sgocciolamento non tratte da
CREA/BDA/USDA sono stime di mercato, non dati verificati. Il documento Word «Tabella
Formati Confezione Standard» su Drive è archivio leggibile. I valori di un'etichetta non
hanno codice tracciabile e non sono una delle tre fonti. Banana 100 g = 68-69 kcal,
riferimento dello scambio frutta.

## Sezione 7 — Drive e GitHub
- Corruzione silenziosa su Drive, verificata due volte: il docx delle regole di traduzione
  e il PDF del piano P01 (ridotto a 238 byte, senza xref né %%EOF), senza alcun segnale.
- Il connettore Drive restituisce base64 e ogni lettura rientra in contesto; un allegato
  alla chat sta nella cartella uploads e non costa token di trasferimento (perché in chat B
  si chiedono allegati).
- La DEMO_KEY USDA ha 10 richieste/ora ed è quasi sempre esaurita.
- Fino al 21/10/2026 il motore viaggiava in uno zip caricato a mano da telefono, con
  `alimenti.csv` anche sciolto: due caricamenti da fare insieme, impronte da confrontare,
  nomi con underscore trasformati in spazi dal passaggio chat→telefono. Il 28/07/2026
  quattro copie sciolte obsolete divergevano dallo zip da tre fasi, e un `gap.csv`
  duplicato dichiarava mancanti dati già recuperati. Dal 21/10/2026 il motore è sciolto
  nel repository e le modifiche le salva Claude con un commit.
- Percorsi utili per il ripiego manuale su GitHub: cancellare con
  `github.com/<utente>/<repo>/delete/main/<percorso>` (poi "Commit changes" in fondo, che
  da cellulare finisce sotto la piega); rinominare con
  `github.com/<utente>/<repo>/edit/main/<percorso>` (più rapido che ricaricare, non lascia
  doppioni).

## Form ai pazienti
Si mandano come link e non come allegato perché un HTML aperto da un allegato sul telefono
non esegue JavaScript e i pulsanti non rispondono.

## Sezione 8 — episodi
- 28/07/2026: l'ipotesi che la cache fosse comprimibile è caduta alla prima misura (era
  già compressa 14:1). Lo stesso giorno, uno zip dichiarato «verificato a freddo da GitHub»
  era stato estratto dalla copia locale, e un documento affermava vuota una cartella Drive
  mai letta: conclusioni corrette per caso, controlli dichiarati ma non fatti.
- 19/09/2026: M2 caricato come `M2_workflow piano.md` (con uno spazio): il file nuovo era
  online ma nessuna sessione lo avrebbe mai letto. Da qui il controllo del nome dopo ogni
  modifica di un modulo.
- L'endpoint raw di GitHub è servito da CDN e può restituire per qualche minuto un file già
  cancellato: per presenza o assenza si guarda l'albero o la copia del repository. La
  cronologia dei commit (`github.com/.../commits/main.atom`) dice se un'operazione è stata
  davvero salvata.
- Una chat lunga continua a lavorare sulla copia del motore estratta all'inizio, che
  invecchia in silenzio.
