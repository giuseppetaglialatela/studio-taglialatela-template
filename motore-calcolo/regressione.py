#!/usr/bin/env python3
"""
Suite di regressione - Studio Nutrizionale Taglialatela
FASE 1 del progetto di consolidamento motore.

COSA FA
Riesegue tutte le giornate golden archiviate in golden/ e confronta i totali
prodotti dal motore con i valori attesi congelati in atteso.json.

QUANDO SI ESEGUE
Per regola dopo OGNI modifica al motore o al database alimenti, e comunque
prima di qualsiasi uso clinico. Il collaudo (collaudo.py) dice che i dati sono
integri; questa suite dice che il motore calcola ancora come prima.

COSA NON E'
Non e' una validazione clinica. Verifica che il motore produca gli stessi
numeri su input fissi e noti, non che quei numeri siano giusti per un
paziente. Un caso golden congelato con un valore atteso sbagliato continuera'
a passare: e' per questo che ogni atteso.json va generato solo dopo che il
risultato e' stato verificato, mai "preso per buono" perche' lo dice il motore.

STRUTTURA DI UN CASO
  golden/caso_NN_nome/
      piano.csv     input: composizione della giornata (schema congelato)
      target.csv    input: target e riferimenti LARN
      atteso.json   output atteso: totali giornalieri + metadati del caso

I casi non contengono dati identificativi di pazienti: solo food_id e
grammature. Identita', quadro clinico e terapia restano su Drive.

USO
  python3 regressione.py              esegue tutti i casi
  python3 regressione.py --genera     rigenera gli atteso.json (vedi sotto)

--genera va usato SOLO quando una modifica al motore cambia intenzionalmente
i risultati e il nuovo output e' gia' stato verificato a mano. Rigenerare per
far passare una suite rossa senza aver capito perche' era rossa annulla lo
scopo della suite.
"""

import csv
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GOLDEN_DIR = os.path.join(BASE, "golden")

# tolleranza di confronto: e' un test di regressione, i numeri devono tornare
# identici a meno dell'errore di rappresentazione in virgola mobile
TOLLERANZA = 0.001


def elenca_casi():
    if not os.path.isdir(GOLDEN_DIR):
        return []
    casi = []
    for nome in sorted(os.listdir(GOLDEN_DIR)):
        percorso = os.path.join(GOLDEN_DIR, nome)
        if os.path.isdir(percorso) and os.path.isfile(os.path.join(percorso, "piano.csv")):
            casi.append(nome)
    return casi


def rileva_tipo(nome_caso):
    """Determina il tipo di caso.

    'pipeline' se la cartella contiene pipeline.json: e' l'unico tipo
    DICHIARATO anziche' dedotto dal piano, perche' lo stesso piano.csv puo'
    essere legittimamente un caso di calcolo o un caso di orchestrazione, e
    dal solo contenuto non si distingue. Il file dichiara anche le opzioni con
    cui la pipeline va eseguita (deroghe, file di terapia).

    Altrimenti 'scelta_multipla' se piano.csv usa gruppo_scelta in almeno una
    riga, altrimenti 'fisso'. Questi due sono rilevati dal piano, non
    dichiarati a mano: cosi' il tipo non puo' disallinearsi da cosa il piano
    contiene davvero.
    """
    from scelte_multiple import carica_piano_esteso

    cartella = os.path.join(GOLDEN_DIR, nome_caso)
    if os.path.isfile(os.path.join(cartella, "pipeline.json")):
        return "pipeline"

    righe = carica_piano_esteso(os.path.join(cartella, "piano.csv"))
    return "scelta_multipla" if any(r["gruppo_scelta"] for r in righe) else "fisso"


def esegui_caso_pipeline(nome_caso):
    """Esegue un caso di ORCHESTRAZIONE: non verifica i numeri (lo fanno gia'
    gli altri tipi di caso) ma i VERDETTI che la pipeline emette.

    Congela l'elenco ordinato di (passo, codice) dei rilievi bloccanti e di
    quelli da dichiarare, piu' il codice di uscita. Non congela i messaggi:
    quelli sono per il nutrizionista e possono essere riformulati senza che
    il comportamento cambi.

    Il PASSO 0 (collaudo) e' escluso di proposito: la suite gira gia' dopo il
    collaudo, rieseguirlo dentro ogni caso lo renderebbe ricorsivo e lento.

    Come per gli altri tipi, invoca le funzioni che la pipeline usa in
    produzione: se un passo si rompe, questo caso deve accorgersene.
    """
    import io
    import json as _json
    from contextlib import redirect_stdout

    import pipeline as pl

    cartella = os.path.join(GOLDEN_DIR, nome_caso)
    with open(os.path.join(cartella, "pipeline.json"), encoding="utf-8") as f:
        opzioni = _json.load(f)

    def percorso_opzionale(chiave):
        valore = opzioni.get(chiave)
        return os.path.join(cartella, valore) if valore else None

    # la STESSA sequenza di pipeline.main(): pipeline.esegui() (30/10/2026). Prima la
    # suite ricostruiva la sequenza a mano, e un passo nuovo poteva mancare qui
    # senza che nessuno se ne accorgesse (successo con --metadati il 29/10).
    nt = opzioni.get("nessuna_terapia", False)
    with redirect_stdout(io.StringIO()):
        rilievi, _ = pl.esegui(
            os.path.join(cartella, "piano.csv"), os.path.join(cartella, "target.csv"),
            os.path.join(BASE, "gap.csv"),
            percorso_opzionale("farmaci"), percorso_opzionale("interazioni"),
            percorso_opzionale("orari"), opzioni.get("deroga_struttura"),
            nt, percorso_opzionale("metadati"), True,
            percorso_opzionale("eccezione_etichetta"))
    # il PASSO 0 (collaudo) e' saltato di proposito: la suite gira dopo il collaudo;
    # la sua attenzione COLLAUDO_SALTATO non fa parte dell'atteso del caso
    rilievi.attenzioni = [x for x in rilievi.attenzioni if x[1] != "COLLAUDO_SALTATO"]

    dati_rilievi = rilievi.come_dati()
    return {
        "tipo": "pipeline",
        "bloccanti": [list(x) for x in dati_rilievi["bloccanti"]],
        "attenzioni": [list(x) for x in dati_rilievi["attenzioni"]],
        "exit_code": 1 if dati_rilievi["bloccanti"] else 0,
    }


def esegui_caso_fisso(nome_caso):
    """Esegue un caso senza pasti a scelta multipla: totali per pasto e per
    giorno, calcolati riga per riga (comportamento originale, invariato).
    Cattura anche i verdetti di tolleranza (kcal e macro %) usando
    entro_tolleranza() - la stessa funzione usata in produzione da report():
    senza questo, la suite verificava solo i grammi, mai se il motore giudica
    correttamente un piano dentro o fuori tolleranza."""
    from calcolatore import (carica_alimenti, carica_piano, carica_target,
                             calcola_riga, somma_nutrienti, NUTRIENTI_PER_100G,
                             entro_tolleranza)

    percorso = os.path.join(GOLDEN_DIR, nome_caso)
    db = carica_alimenti(os.path.join(BASE, "alimenti.csv"))
    piano = carica_piano(os.path.join(percorso, "piano.csv"))
    target = carica_target(os.path.join(percorso, "target.csv"))

    sconosciuti = sorted({r["food_id"] for r in piano if r["food_id"] not in db})
    if sconosciuti:
        raise ValueError(
            f"food_id assenti dal database: {', '.join(sconosciuti)}. "
            f"Il caso golden e' disallineato rispetto ad alimenti.csv."
        )

    per_pasto = {}
    for r in piano:
        chiave = f"{r['giorno']}|{r['pasto']}"
        per_pasto.setdefault(chiave, []).append(
            calcola_riga(db[r["food_id"]], r["grammi"]))

    totali_pasto = {k: somma_nutrienti(v) for k, v in per_pasto.items()}
    totale_giorno = somma_nutrienti(
        [riga for righe in per_pasto.values() for riga in righe])

    verdetti = {}
    kcal = totale_giorno["kcal_100g"]
    if "kcal_target" in target:
        kt = target["kcal_target"]
        scarto = (kcal - kt) / kt * 100
        verdetti["kcal"] = "OK" if entro_tolleranza(scarto) else "FUORI TOLLERANZA"
    for nome_pct, valore_g, kcal_per_g, chiave_target in [
        ("proteine_pct", totale_giorno["proteine_g"], 4, "proteine_pct_target"),
        ("carboidrati_pct", totale_giorno["carboidrati_g"], 4, "carboidrati_pct_target"),
        ("grassi_pct", totale_giorno["grassi_g"], 9, "grassi_pct_target"),
    ]:
        if chiave_target in target and kcal:
            valore_pct = valore_g * kcal_per_g / kcal * 100
            scarto = valore_pct - target[chiave_target]
            verdetti[nome_pct] = "OK" if entro_tolleranza(scarto) else "FUORI TOLLERANZA"

    return {
        "tipo": "fisso",
        "totale_giorno": {n: round(totale_giorno[n], 6) for n in NUTRIENTI_PER_100G},
        "totali_pasto": {
            k: {n: round(v[n], 6) for n in NUTRIENTI_PER_100G}
            for k, v in sorted(totali_pasto.items())
        },
        "verdetti_tolleranza": verdetti,
    }


def esegui_caso_scelta_multipla(nome_caso):
    """Esegue un caso con pasti a scelta multipla: per ogni giorno, minimo e
    massimo garantiti per nutriente, calcolati da scelte_multiple.py - lo
    stesso modulo che il motore usa in produzione, non una riscrittura della
    sua logica qui dentro. E' il punto: se scelte_multiple.py si rompe, questo
    caso deve accorgersene."""
    from collections import defaultdict
    from calcolatore import carica_alimenti
    from scelte_multiple import carica_piano_esteso, calcola_intervallo_giorno, NUTRIENTI

    percorso = os.path.join(GOLDEN_DIR, nome_caso)
    db = carica_alimenti(os.path.join(BASE, "alimenti.csv"))
    righe = carica_piano_esteso(os.path.join(percorso, "piano.csv"))

    sconosciuti = sorted({r["food_id"] for r in righe if r["food_id"] not in db})
    if sconosciuti:
        raise ValueError(
            f"food_id assenti dal database: {', '.join(sconosciuti)}. "
            f"Il caso golden e' disallineato rispetto ad alimenti.csv."
        )

    per_giorno = defaultdict(list)
    for r in righe:
        per_giorno[r["giorno"]].append(r)

    risultato_giorni = {}
    for giorno in sorted(per_giorno):
        minimi, massimi, dettaglio = calcola_intervallo_giorno(per_giorno[giorno], db)
        risultato_giorni[giorno] = {
            "minimi": {n: round(minimi[n], 6) for n in NUTRIENTI},
            "massimi": {n: round(massimi[n], 6) for n in NUTRIENTI},
            "n_gruppi": len(dettaglio),
        }

    return {"tipo": "scelta_multipla", "per_giorno": risultato_giorni}


def esegui_caso(nome_caso):
    tipo = rileva_tipo(nome_caso)
    if tipo == "pipeline":
        return esegui_caso_pipeline(nome_caso)
    if tipo == "scelta_multipla":
        return esegui_caso_scelta_multipla(nome_caso)
    return esegui_caso_fisso(nome_caso)


def confronta(atteso, ottenuto):
    """Restituisce la lista degli scostamenti trovati. Il confronto dipende
    dal tipo di caso (rilevato dal piano, vedi rileva_tipo)."""
    tipo_atteso = atteso.get("tipo", "fisso")
    tipo_ottenuto = ottenuto.get("tipo", "fisso")
    if tipo_atteso != tipo_ottenuto:
        return [
            f"tipo di caso cambiato: atteso.json dice '{tipo_atteso}', "
            f"il piano attuale e' '{tipo_ottenuto}' - rigenerare consapevolmente"
        ]

    if tipo_atteso == "pipeline":
        return _confronta_pipeline(atteso, ottenuto)
    if tipo_atteso == "scelta_multipla":
        return _confronta_scelta_multipla(atteso, ottenuto)
    return _confronta_fisso(atteso, ottenuto)


def _confronta_fisso(atteso, ottenuto):
    scostamenti = []

    for n, val_atteso in atteso["totale_giorno"].items():
        val_ott = ottenuto["totale_giorno"].get(n)
        if val_ott is None:
            scostamenti.append(f"totale giorno - {n}: nutriente assente nell'output")
        elif abs(val_ott - val_atteso) > TOLLERANZA:
            scostamenti.append(
                f"totale giorno - {n}: atteso {val_atteso}, ottenuto {val_ott}")

    pasti_attesi = set(atteso.get("totali_pasto", {}))
    pasti_ottenuti = set(ottenuto.get("totali_pasto", {}))
    for mancante in sorted(pasti_attesi - pasti_ottenuti):
        scostamenti.append(f"pasto {mancante}: atteso ma assente nell'output")
    for in_piu in sorted(pasti_ottenuti - pasti_attesi):
        scostamenti.append(f"pasto {in_piu}: presente nell'output ma non atteso")

    for chiave in sorted(pasti_attesi & pasti_ottenuti):
        for n, val_atteso in atteso["totali_pasto"][chiave].items():
            val_ott = ottenuto["totali_pasto"][chiave].get(n)
            if val_ott is None or abs(val_ott - val_atteso) > TOLLERANZA:
                scostamenti.append(
                    f"pasto {chiave} - {n}: atteso {val_atteso}, ottenuto {val_ott}")

    for chiave, verdetto_atteso in atteso.get("verdetti_tolleranza", {}).items():
        verdetto_ott = ottenuto.get("verdetti_tolleranza", {}).get(chiave)
        if verdetto_ott != verdetto_atteso:
            scostamenti.append(
                f"verdetto tolleranza {chiave}: atteso '{verdetto_atteso}', "
                f"ottenuto '{verdetto_ott}'")

    return scostamenti


def _confronta_scelta_multipla(atteso, ottenuto):
    scostamenti = []
    giorni_attesi = set(atteso.get("per_giorno", {}))
    giorni_ottenuti = set(ottenuto.get("per_giorno", {}))

    for mancante in sorted(giorni_attesi - giorni_ottenuti):
        scostamenti.append(f"giorno {mancante}: atteso ma assente nell'output")
    for in_piu in sorted(giorni_ottenuti - giorni_attesi):
        scostamenti.append(f"giorno {in_piu}: presente nell'output ma non atteso")

    for giorno in sorted(giorni_attesi & giorni_ottenuti):
        att_g = atteso["per_giorno"][giorno]
        ott_g = ottenuto["per_giorno"][giorno]

        if att_g.get("n_gruppi") != ott_g.get("n_gruppi"):
            scostamenti.append(
                f"giorno {giorno} - n_gruppi: atteso {att_g.get('n_gruppi')}, "
                f"ottenuto {ott_g.get('n_gruppi')}")

        for chiave in ("minimi", "massimi"):
            att = att_g.get(chiave, {})
            ott = ott_g.get(chiave, {})
            for n, val_atteso in att.items():
                val_ott = ott.get(n)
                if val_ott is None or abs(val_ott - val_atteso) > TOLLERANZA:
                    scostamenti.append(
                        f"giorno {giorno} - {chiave} {n}: atteso {val_atteso}, "
                        f"ottenuto {val_ott}")

    return scostamenti


def _confronta_pipeline(atteso, ottenuto):
    """Confronta i verdetti dell'orchestratore.

    Un rilievo che sparisce e' grave quanto uno che compare: il primo e' una
    garanzia persa in silenzio, il secondo un falso allarme. Sono elencati
    separatamente perche' la diagnosi e' diversa.
    """
    scostamenti = []

    for categoria in ("bloccanti", "attenzioni"):
        att = [tuple(x) for x in atteso.get(categoria, [])]
        ott = [tuple(x) for x in ottenuto.get(categoria, [])]

        conta_att, conta_ott = {}, {}
        for x in att:
            conta_att[x] = conta_att.get(x, 0) + 1
        for x in ott:
            conta_ott[x] = conta_ott.get(x, 0) + 1

        for chiave in sorted(set(conta_att) | set(conta_ott)):
            n_att = conta_att.get(chiave, 0)
            n_ott = conta_ott.get(chiave, 0)
            if n_att == n_ott:
                continue
            passo, codice = chiave
            if n_ott == 0:
                scostamenti.append(
                    f"{categoria}: rilievo SCOMPARSO - PASSO {passo} "
                    f"{codice} (atteso {n_att} volte, ottenuto 0). "
                    f"Una garanzia che il motore non da' piu'.")
            elif n_att == 0:
                scostamenti.append(
                    f"{categoria}: rilievo NUOVO - PASSO {passo} {codice} "
                    f"(comparso {n_ott} volte, non era atteso)")
            else:
                scostamenti.append(
                    f"{categoria}: PASSO {passo} {codice} - atteso {n_att} "
                    f"volte, ottenuto {n_ott}")

    if atteso.get("exit_code") != ottenuto.get("exit_code"):
        scostamenti.append(
            f"codice di uscita: atteso {atteso.get('exit_code')}, "
            f"ottenuto {ottenuto.get('exit_code')}")

    return scostamenti


def modo_genera():
    casi = elenca_casi()
    if not casi:
        print("Nessun caso golden trovato in golden/")
        return 1
    print("MODO GENERAZIONE - gli atteso.json verranno sovrascritti.")
    print("Da usare solo se il nuovo output e' gia' stato verificato a mano.\n")
    for nome in casi:
        percorso_atteso = os.path.join(GOLDEN_DIR, nome, "atteso.json")
        try:
            risultato = esegui_caso(nome)
        except Exception as e:
            print(f"  [XX ] {nome}: {e}")
            continue
        esistente = {}
        if os.path.isfile(percorso_atteso):
            with open(percorso_atteso, encoding="utf-8") as f:
                esistente = json.load(f)
        risultato["descrizione"] = esistente.get("descrizione", "")
        risultato["riferimento"] = esistente.get("riferimento", "")
        with open(percorso_atteso, "w", encoding="utf-8") as f:
            json.dump(risultato, f, indent=2, ensure_ascii=False)
        if risultato["tipo"] == "pipeline":
            print(f"  [OK ] {nome}: atteso.json scritto "
                  f"({len(risultato['bloccanti'])} bloccanti, "
                  f"{len(risultato['attenzioni'])} attenzioni, "
                  f"exit {risultato['exit_code']})")
        elif risultato["tipo"] == "scelta_multipla":
            n_giorni = len(risultato["per_giorno"])
            print(f"  [OK ] {nome}: atteso.json scritto "
                  f"({n_giorni} giorni, tipo scelta_multipla)")
        else:
            kcal = risultato["totale_giorno"]["kcal_100g"]
            print(f"  [OK ] {nome}: atteso.json scritto (giornata {kcal:.2f} kcal)")
    return 0


def modo_verifica():
    casi = elenca_casi()
    print("=" * 60)
    print("SUITE DI REGRESSIONE - Motore di calcolo")
    print("=" * 60)

    if not casi:
        print("\nNessun caso golden trovato in golden/.")
        print("La suite e' vuota: non fornisce alcuna garanzia.")
        print("=" * 60)
        return 1

    passati, falliti = 0, 0
    for nome in casi:
        percorso_atteso = os.path.join(GOLDEN_DIR, nome, "atteso.json")
        if not os.path.isfile(percorso_atteso):
            print(f"\n  [XX ] {nome}")
            print(f"        atteso.json mancante: il caso non e' verificabile")
            falliti += 1
            continue

        with open(percorso_atteso, encoding="utf-8") as f:
            atteso = json.load(f)

        try:
            ottenuto = esegui_caso(nome)
        except Exception as e:
            print(f"\n  [XX ] {nome}")
            print(f"        errore in esecuzione: {e}")
            falliti += 1
            continue

        scostamenti = confronta(atteso, ottenuto)
        descrizione = atteso.get("descrizione", "")
        if not scostamenti:
            if ottenuto.get("tipo") == "pipeline":
                print(f"\n  [OK ] {nome} "
                      f"({len(ottenuto['bloccanti'])} bloccanti, "
                      f"{len(ottenuto['attenzioni'])} attenzioni, "
                      f"exit {ottenuto['exit_code']})")
            elif ottenuto.get("tipo") == "scelta_multipla":
                n_giorni = len(ottenuto.get("per_giorno", {}))
                print(f"\n  [OK ] {nome} ({n_giorni} giorni, scelta multipla)")
            else:
                kcal = ottenuto["totale_giorno"]["kcal_100g"]
                print(f"\n  [OK ] {nome} ({kcal:.2f} kcal)")
            if descrizione:
                print(f"        {descrizione}")
            passati += 1
        else:
            print(f"\n  [XX ] {nome}")
            if descrizione:
                print(f"        {descrizione}")
            for s in scostamenti:
                print(f"        {s}")
            falliti += 1

    # Riga di comando (23/10/2026): i casi chiamano i passi della pipeline
    # direttamente e non vedono il passaggio delle opzioni da argparse a main().
    # Un'esecuzione reale di pipeline.py lo verifica per --nessuna-terapia.
    ok_cli, msg_cli = verifica_riga_di_comando()
    print(f"\n  [{'OK ' if ok_cli else 'XX '}] riga di comando di pipeline.py: {msg_cli}")
    if not ok_cli:
        falliti += 1
    # --metadati (29/10/2026): l'abbinamento colazione -> spuntino deve
    # arrivare da argparse al calcolo delle giornate componibili
    ok_meta, msg_meta = verifica_riga_di_comando_metadati()
    print(f"\n  [{'OK ' if ok_meta else 'XX '}] riga di comando di pipeline.py: {msg_meta}")
    if not ok_meta:
        falliti += 1
        ok_cli = False
    # catena del PASSO 6 dalla riga di comando (30/10/2026): pipeline con collaudo,
    # verdetto, anteprima SU FILE e verifica dell'impronta
    ok_cat, msg_cat = verifica_catena_anteprima()
    print(f"\n  [{'OK ' if ok_cat else 'XX '}] catena del PASSO 6: {msg_cat}")
    if not ok_cat:
        falliti += 1
        ok_cli = False
    # Calcolo esatto dei pasti a scelta (tappa 1, 29/10/2026): giorno e
    # settimana confrontati con la forza bruta su casi casuali a seme fisso
    import combinazioni
    n_auto, diff_auto = combinazioni.autotest()
    ok_auto = diff_auto == 0
    print(f"\n  [{'OK ' if ok_auto else 'XX '}] pasti a scelta, calcolo esatto contro forza "
          f"bruta: {n_auto} casi casuali, {diff_auto} differenze")
    if not ok_auto:
        falliti += 1
        ok_cli = False

    print("\n" + "=" * 60)
    print(f"RISULTATO: {passati} passati, {len(casi) - passati} falliti su {len(casi)} casi; "
          f"controllo della riga di comando {'superato' if ok_cli else 'FALLITO'}")
    if falliti:
        print("SUITE ROSSA - non usare il motore su un paziente.")
        print("Capire la causa PRIMA di rigenerare qualunque atteso.json.")
    else:
        print("SUITE VERDE - il motore calcola come da riferimento.")
    print("=" * 60)
    return 1 if falliti else 0


def verifica_riga_di_comando():
    """pipeline.py eseguito davvero sul caso 45 (la suite chiama pipeline.esegui()
    e non vede il passaggio da argparse a main()):
    1. --nessuna-terapia con --metadati: nel verdetto TERAPIA_DICHIARATA_ASSENTE con
       la conferma dei metadati, e non TERAPIA_NON_DICHIARATA;
    2. --nessuna-terapia "testo" (uso precedente al 30/10/2026): blocca con
       TERAPIA_NON_CONFERMATA, un testo da riga di comando non e' una conferma;
    3. --out-verdetto: il file c'e', riporta i dati valutati e le attenzioni."""
    import subprocess, tempfile, json as _json
    cartella = os.path.join(GOLDEN_DIR, "caso_45_nessuna_terapia_dichiarata")
    base = [sys.executable, os.path.join(BASE, "pipeline.py"),
            "--piano", os.path.join(cartella, "piano.csv"),
            "--target", os.path.join(cartella, "target.csv"), "--salta-collaudo"]
    meta = os.path.join(cartella, "metadati.json")
    tmp = tempfile.mkdtemp()
    ver = os.path.join(tmp, "verdetto.json")
    try:
        buona = subprocess.run(base + ["--nessuna-terapia", "--metadati", meta,
                                       "--out-verdetto", ver],
                               capture_output=True, text=True, timeout=60)
        vecchia = subprocess.run(base + ["--nessuna-terapia", "prova riga di comando"],
                                 capture_output=True, text=True, timeout=60)
    except Exception as e:
        return False, f"esecuzione non riuscita: {e}"
    out = buona.stdout
    # solo il verdetto: la conferma e' stampata anche nel corpo del PASSO 5
    out = out[out.rfind("VERDETTO"):] if "VERDETTO" in out else ""
    if not out:
        return False, "il report non contiene il VERDETTO"
    if "TERAPIA_NON_DICHIARATA" in out:
        return False, "--nessuna-terapia non arriva al PASSO 5 (compare TERAPIA_NON_DICHIARATA)"
    if "TERAPIA_DICHIARATA_ASSENTE" not in out or "23/10/2026" not in out:
        return False, "nel verdetto manca TERAPIA_DICHIARATA_ASSENTE con la conferma"
    if vecchia.returncode != 1 or "TERAPIA_NON_CONFERMATA" not in vecchia.stdout:
        return False, "--nessuna-terapia \"testo\" non blocca (TERAPIA_NON_CONFERMATA)"
    try:
        v = _json.load(open(ver, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return False, f"--out-verdetto non scrive un verdetto leggibile ({e})"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    if not v.get("dati", {}).get("metadati") or \
            "TERAPIA_DICHIARATA_ASSENTE" not in [c for _, c, _ in v.get("attenzioni", [])]:
        return False, "il verdetto scritto non riporta metadati e attenzioni"
    return True, ("--nessuna-terapia arriva al PASSO 5 con la conferma dei metadati; "
                  "un testo da riga di comando blocca; --out-verdetto scrive il verdetto")


def verifica_catena_anteprima():
    """Come in chat A: pipeline.py (con il collaudo) --metadati --out-verdetto, poi
    genera_zona_piano.py --anteprima --verdetto. L'anteprima deve finire in un file
    con l'impronta nel nome e NON in chat (il 28/10/2026 si era approvato un
    estratto); scritta l'impronta nei metadati, --verifica-impronta deve passare."""
    import subprocess, tempfile, json as _json, shutil
    import genera_zona_piano as gzp
    tmp = tempfile.mkdtemp()
    try:
        _, piano, target = gzp._piano_di_collaudo(tmp)
        meta_p = os.path.join(tmp, "metadati_piano_v1.json")
        meta = {"versione_piano": "v1",
                "giorni": {"lavorativi": ["lun"], "libero": "dom", "range_kcal_libero": [1600, 1900]},
                "livello_colazione": "standard", "tdee_confermato_kcal": 2040,
                "intestazione": {"nome": "Paziente Fittizio", "eta": "40 anni",
                                 "condizione": "Caso di collaudo"},
                "avvertenze_box": "Nessuna allergia dichiarata.",
                "abbinamento_spuntino": {"A": "B", "B": "A"},
                "indicazioni_giorno_libero": {"pranzo": "a piacere", "cena": "a piacere"},
                "titoli_piatti": {"*|colazione|A": "Colazione A", "*|colazione|B": "Colazione B",
                                  "*|spuntino|A": "Spuntino A", "*|spuntino|B": "Spuntino B",
                                  "1|pranzo|": "Pranzo", "1|cena|": "Cena"},
                "obiettivo_intestazione": "collaudo", "criterio_rivalutazione": "collaudo",
                "terapia": "nessuna terapia, confermato dal nutrizionista il 23/10/2026 "
                           "(fonte: colloquio)",
                "assunzioni": [], "alimenti_desiderati": [],
                "profili": ["ipercolesterolemia"]}
        with open(meta_p, "w", encoding="utf-8") as f:
            _json.dump(meta, f)
        ver = os.path.join(tmp, "verdetto_v1.json")
        r1 = subprocess.run([sys.executable, os.path.join(BASE, "pipeline.py"), "--piano", piano,
                             "--target", target, "--nessuna-terapia", "--metadati", meta_p,
                             "--out-verdetto", ver], capture_output=True, text=True,
                            timeout=180, cwd=tmp)
        if r1.returncode != 0:
            return False, "la pipeline con il collaudo non da' un verdetto presentabile"
        base_g = [sys.executable, os.path.join(BASE, "genera_zona_piano.py"), "--piano", piano,
                  "--target", target, "--metadati", meta_p, "--verdetto", ver]
        r2 = subprocess.run(base_g + ["--anteprima"], capture_output=True, text=True,
                            timeout=120, cwd=tmp)
        file_a = [n for n in os.listdir(tmp) if n.startswith("anteprima_v1_") and n.endswith(".md")]
        if r2.returncode != 0 or len(file_a) != 1:
            return False, f"anteprima non scritta su file ({r2.stdout.strip()[-120:]})"
        imp = file_a[0][len("anteprima_v1_"):-3]
        testo = open(os.path.join(tmp, file_a[0]), encoding="utf-8").read()
        if "## Piano per esteso" in r2.stdout or "## Verdetto della pipeline" not in testo \
                or imp not in r2.stdout:
            return False, "l'anteprima compare in chat o il file e' incompleto"
        meta["impronta_approvata"] = imp
        with open(meta_p, "w", encoding="utf-8") as f:
            _json.dump(meta, f)
        r3 = subprocess.run(base_g + ["--verifica-impronta"], capture_output=True, text=True,
                            timeout=120, cwd=tmp)
        if r3.returncode != 0 or "IMPRONTA VERIFICATA" not in r3.stdout:
            return False, f"--verifica-impronta non passa ({r3.stdout.strip()[-120:]})"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True, ("pipeline con collaudo -> verdetto -> anteprima su file (non in chat) -> "
                  "impronta verificata")


def verifica_riga_di_comando_metadati():
    """pipeline.py eseguito davvero sul caso 52 con e senza --metadati: con
    l'abbinamento le giornate componibili sono 7 e la giornata a -6,26 punti
    (S2 + SPrA) sparisce; senza, sono 8 e compare."""
    import subprocess
    cartella = os.path.join(GOLDEN_DIR, "caso_52_abbinamento_restringe_giornate")
    base = [sys.executable, os.path.join(BASE, "pipeline.py"),
            "--piano", os.path.join(cartella, "piano.csv"),
            "--target", os.path.join(cartella, "target.csv"), "--salta-collaudo"]
    try:
        con = subprocess.run(base + ["--metadati", os.path.join(cartella, "metadati.json")],
                             capture_output=True, text=True, timeout=120).stdout
        senza = subprocess.run(base, capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"--metadati: esecuzione non riuscita ({e})"
    if "giornate realmente componibili: 7" not in con or "SCENARIO_MACRO_FUORI_TOLLERANZA" in con:
        return False, "--metadati non arriva al calcolo delle giornate componibili"
    if "giornate realmente componibili: 8" not in senza or "SCENARIO_MACRO_FUORI_TOLLERANZA" not in senza:
        return False, "senza --metadati le giornate componibili non sono tutte"
    return True, "--metadati restringe le giornate all'abbinamento (7 su 8)"


if __name__ == "__main__":
    if "--genera" in sys.argv:
        sys.exit(modo_genera())
    sys.exit(modo_verifica())
