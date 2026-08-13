# ISTRUZIONI DI PASSAGGIO — Chat di stesura
Lavoro di prova · Tema 2 · 13/08/2026

Da incollare come primo messaggio nella nuova chat.

---

## MESSAGGIO DI APERTURA — copia da qui

Sono Giuseppe Taglialatela, farmacista. Apriamo una sessione di stesura
scientifica con il motore editoriale.

**Prima di tutto**, carica i moduli con `bash` + `curl` (non con web_fetch, su
GitHub fallisce per robots.txt):

```
BASE=https://raw.githubusercontent.com/giuseppetaglialatela/studio-taglialatela-template/refs/heads/main/editoria
curl -s $BASE/MA_nucleo.md
curl -s $BASE/MB_bibliografia.md
curl -s $BASE/MC_workflow.md
curl -s $BASE/MD_formati.md
curl -s $BASE/fonti.csv
```

Se un caricamento fallisce, dichiaralo e fermati.

**Stato del lavoro**

- Tema: T2 — Interazioni farmaco-alimento e farmaco-integratore nel consiglio
  al banco
- Formato: articolo per rivista di settore (8.000-12.000 battute)
- Committente: nessuno ancora individuato. Destinazione probabile Tema Farmacia
  News (Tecniche Nuove) o Punto Effe (Edra). Registro professionale, non
  divulgativo
- Target: farmacista collaboratore di farmacia territoriale
- Passo raggiunto: PASSO 0 da fare
- Fonti già a registro: 3 (F001-F003), nessuna sul tema T2
- Conflitti di interesse: nessuno

**Nota**: è un lavoro di prova, serve anche a collaudare il motore. Se una
regola dei moduli si rivela impraticabile durante la stesura, segnalalo invece
di aggirarla.

Partiamo dal PASSO 0.

---

## PROMEMORIA PER LA SESSIONE

**Cosa aspettarsi**
- PASSO 0-1 nella prima parte: delimitazione e obiettivi formativi. Il PASSO 1
  è un gate: va approvato prima di procedere
- PASSO 2-4: ricerca. È la parte più lunga
- PASSO 5: scheletro, secondo gate
- PASSO 6-7: buchi e stesura

**Divisione consigliata**
Per un articolo, una sola chat può bastare. Se diventa pesante, si divide dopo
il PASSO 5 (scheletro approvato) e si riparte con le istruzioni di passaggio
generate in quel momento.

**A fine sessione — obbligatorio**
Farsi consegnare:
1. Le righe nuove di `fonti.csv` in formato incollabile
2. Il file `fonti.csv` completo aggiornato
3. Il link di upload

Upload:
`https://github.com/giuseppetaglialatela/studio-taglialatela-template/upload/main/editoria`

Se il file non viene ricaricato, il lavoro bibliografico della sessione è perso.

---

## PERCHÉ QUESTO TEMA COME PROVA

È il tema con il vantaggio competitivo più difendibile: un farmacista che fa
anche consulenza nutrizionale è un profilo raro, e l'incrocio farmaco-alimento
è esattamente il punto in cui quelle due competenze si sommano invece di
affiancarsi.

È anche il più adatto a collaudare il motore, per tre ragioni:
- le fonti sono in gran parte in inglese, quindi mette alla prova le regole di
  resa appena introdotte (MB sezione 9, controllo B9)
- diverse review sono paywalled, quindi mette alla prova lo stato
  `abstract_verificato`
- gli RCP AIFA sono fonte di livello 1 accessibile, quindi permette di
  verificare che la gerarchia delle fonti funzioni davvero

Se il motore regge qui, regge ovunque.
