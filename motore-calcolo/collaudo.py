#!/usr/bin/env python3
"""
Collaudo di inizio sessione - Studio Nutrizionale Taglialatela
FASE 0.1 del progetto di consolidamento motore.

Certificato che va eseguito ad ogni apertura di sessione di calcolo, PRIMA
di qualsiasi calcolo su paziente. Se anche un solo controllo fallisce, lo
script esce con codice diverso da zero e non va usato il motore finche' il
problema non e' risolto.

CONTROLLI:
  1) Integrita' e presenza di tutti i CSV del motore (parsing senza errori
     E numero di colonne coerente con l'header su ogni riga)
  2) Conteggio righe di alimenti.csv contro il valore atteso dichiarato
  3) Assenza di food_id duplicati in alimenti.csv
  4) Esecuzione di una giornata golden, confrontata al risultato atteso
  5) Integrita' byte per byte dei file del motore contro SHA256SUMS
  6) Ogni food_id ha un nome per il paziente (nomi_paziente.csv)
  7) Formati confezione e scambi frutta coerenti con il database; catalogo
     colazioni/spuntini nei formati di confezione (23/10/2026)
  8) Ogni food_id ha un ruolo (ruoli_alimenti.csv), le regole di
     accoppiamenti_vietati.csv sono valide e la libreria dei blocchi non
     contiene accoppiamenti vietati (21/10/2026)

NOTA SUL VALORE ATTESO (punto 2):
  EXPECTED_ALIMENTI_COUNT va aggiornato ogni volta che il database cresce
  (criterio Key Foods, protocollo di estrazione). Non e' pensato per essere
  dedotto automaticamente: se il conteggio reale non corrisponde, il motivo
  puo' essere un aggiornamento legittimo non ancora registrato qui, oppure
  un problema reale (parsing rotto, file scaricato a meta'). Il collaudo
  non decide da solo quale dei due casi sia: si ferma e lo segnala.

NOTA SULLA GIORNATA GOLDEN (punto 4):
  Usa i CSV di test che accompagnano il motore (alimenti_test.csv,
  piano_test.csv), non dati di pazienti reali: i dati clinici non vivono in
  questo repository (separazione GitHub/Drive, vedi istruzioni di progetto).
  E' un test di REGRESSIONE DEL CODICE, non una validazione clinica: verifica
  che calcolatore.py produca ancora gli stessi numeri su un input fisso e
  noto, non che quei numeri siano clinicamente corretti per un paziente.
"""

import csv
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# --- valore da aggiornare manualmente quando il database cresce ---
EXPECTED_ALIMENTI_COUNT = 143

# File coperti dai checksum ma NON necessari a ogni sessione. Se presenti
# vengono verificati come tutti gli altri; se assenti, il collaudo lo dice e
# prosegue. Sono i dati di supporto al protocollo di estrazione (cache delle
# risposte BDA-IEO, foglio BDA, cache delle schede CREA): servono quando si amplia il database
# alimenti, non quando si calcola un piano. Richiederli sempre significherebbe
# far fallire il collaudo a ogni sessione in cui non si scaricano - e un
# collaudo che fallisce di routine smette di essere letto.
FILE_OPZIONALI = [
    "cache.zip",
    "BDA_alimenti.xlsx",
    "crea_cache.zip",
]

# file dello schema congelato + file di test che devono esistere ed essere
# parsabili. I _test.csv viaggiano con il motore; gli altri (piano.csv,
# target.csv, farmaci_paziente.csv, interazioni.csv, orari_pasti.csv) sono
# per-paziente e vivono su Drive: qui si controllano solo i file che DEVONO
# essere presenti in questa cartella ad ogni sessione.
FILE_DA_VERIFICARE = [
    "alimenti.csv",
    "gap.csv",
    "colazioni_spuntini.csv",
    "larn.csv",
    "formati_confezione.csv",
    "scambi_frutta.csv",
    "ruoli_alimenti.csv",
    "accoppiamenti_vietati.csv",
    "alimenti_test.csv",
    "piano_test.csv",
    "piano_test_scelte.csv",
    "target_test.csv",
    "farmaci_paziente_test.csv",
    "interazioni_test.csv",
    "orari_pasti_test.csv",
]

# riferimento golden: totali esatti attesi per la giornata 1 di
# piano_test.csv + alimenti_test.csv (calcolati una volta, congelati qui)
GOLDEN_ATTESO = {
    "kcal_100g": 1500.0,
    "proteine_g": 75.5,
    "carboidrati_g": 185.0,
    "grassi_g": 46.5,
    "fibra_g": 24.0,
    "calcio_mg": 290.0,
    "ferro_mg": 8.25,
    "vitamina_d_ug": 4.0,
    "folati_ug": 122.5,
    "vitamina_b12_ug": 2.5,
    "zinco_mg": 6.300000000000001,
    "magnesio_mg": 132.5,
    "vitamina_c_mg": 100.0,
}
GOLDEN_TOLLERANZA_ASSOLUTA = 0.01  # e' un test di regressione: deve tornare
                                    # identico, non solo "vicino"


def controllo_1_integrita_csv():
    """Presenza + parsing senza errori di tutti i file richiesti."""
    esiti = []
    for nome_file in FILE_DA_VERIFICARE:
        path = os.path.join(BASE, nome_file)
        if not os.path.isfile(path):
            esiti.append((nome_file, False, "file mancante"))
            continue
        try:
            with open(path, newline="", encoding="utf-8") as f:
                righe = list(csv.DictReader(f))
            if not righe:
                esiti.append((nome_file, False, "file presente ma vuoto (0 righe dati)"))
                continue
            righe_malformate = []
            for i, row in enumerate(righe, start=2):  # riga 1 = header
                if None in row or any(v is None for v in row.values()):
                    righe_malformate.append(i)
            if righe_malformate:
                esiti.append((nome_file, False,
                    f"{len(righe)} righe lette ma {len(righe_malformate)} "
                    f"malformate (colonne diverse dall'header) a riga {righe_malformate}"))
            else:
                esiti.append((nome_file, True, f"{len(righe)} righe, parsing ok"))
        except Exception as e:
            esiti.append((nome_file, False, f"errore di parsing: {e}"))
    return esiti


def controllo_2_conteggio_alimenti():
    path = os.path.join(BASE, "alimenti.csv")
    if not os.path.isfile(path):
        return False, "alimenti.csv non trovato, impossibile contare le righe"
    with open(path, newline="", encoding="utf-8") as f:
        n = len(list(csv.DictReader(f)))
    if n == EXPECTED_ALIMENTI_COUNT:
        return True, f"{n} righe, come atteso"
    return False, (
        f"{n} righe trovate, {EXPECTED_ALIMENTI_COUNT} attese. "
        f"Verifica se e' un aggiornamento legittimo del database non ancora "
        f"registrato in EXPECTED_ALIMENTI_COUNT, oppure un problema reale."
    )


def controllo_3_duplicati_food_id():
    path = os.path.join(BASE, "alimenti.csv")
    if not os.path.isfile(path):
        return False, "alimenti.csv non trovato, impossibile controllare i duplicati"
    with open(path, newline="", encoding="utf-8") as f:
        ids = [row["food_id"] for row in csv.DictReader(f)]
    duplicati = sorted(set(x for x in ids if ids.count(x) > 1))
    if not duplicati:
        return True, "nessun food_id duplicato"
    return False, f"food_id duplicati: {', '.join(duplicati)}"


def controllo_4_giornata_golden():
    try:
        from calcolatore import carica_alimenti, carica_piano, calcola_riga, somma_nutrienti
    except Exception as e:
        return False, f"impossibile importare calcolatore.py: {e}"

    path_alimenti = os.path.join(BASE, "alimenti_test.csv")
    path_piano = os.path.join(BASE, "piano_test.csv")
    if not (os.path.isfile(path_alimenti) and os.path.isfile(path_piano)):
        return False, "alimenti_test.csv o piano_test.csv mancanti"

    try:
        db = carica_alimenti(path_alimenti)
        piano = carica_piano(path_piano)
        righe = [calcola_riga(db[r["food_id"]], r["grammi"]) for r in piano]
        tot = somma_nutrienti(righe)
    except Exception as e:
        return False, f"errore durante l'esecuzione del calcolo golden: {e}"

    scarti = []
    for nutriente, atteso in GOLDEN_ATTESO.items():
        reale = tot.get(nutriente)
        if reale is None:
            scarti.append(f"{nutriente}: nutriente assente nel risultato")
            continue
        if abs(reale - atteso) > GOLDEN_TOLLERANZA_ASSOLUTA:
            scarti.append(f"{nutriente}: atteso {atteso}, ottenuto {reale}")

    if not scarti:
        return True, "output identico al riferimento golden"
    return False, "scostamenti dal riferimento golden -> " + "; ".join(scarti)


def controllo_6_nomi_paziente():
    """Ogni food_id di alimenti.csv deve avere un nome per il paziente.

    nomi_paziente.csv e' il file affiancato (schema di alimenti.csv congelato)
    da cui il PDF prende i nomi leggibili. Un food_id senza nome costringerebbe
    a inventarlo a mano in chat B: e' testo che arriva al paziente.
    """
    percorso = os.path.join(BASE, "nomi_paziente.csv")
    if not os.path.exists(percorso):
        return False, "nomi_paziente.csv assente"
    try:
        with open(percorso, newline="", encoding="utf-8-sig") as f:
            righe = list(csv.DictReader(f))
    except Exception as e:
        return False, f"nomi_paziente.csv illeggibile: {e}"
    attese = {"food_id", "nome_paziente", "nota_peso"}
    if not righe or attese - set(righe[0].keys()):
        return False, "nomi_paziente.csv: colonne attese food_id,nome_paziente,nota_peso"
    nomi = {}
    for r in righe:
        fid = (r["food_id"] or "").strip()
        if fid in nomi:
            return False, f"food_id duplicato in nomi_paziente.csv: {fid}"
        nomi[fid] = (r["nome_paziente"] or "").strip()
    with open(os.path.join(BASE, "alimenti.csv"), newline="", encoding="utf-8-sig") as f:
        alimenti = [(r["food_id"] or "").strip() for r in csv.DictReader(f)]
    senza = [f for f in alimenti if not nomi.get(f)]
    orfani = [f for f in nomi if f not in alimenti]
    if senza:
        return False, (f"{len(senza)} food_id senza nome paziente: "
                       + ", ".join(senza[:5]) + ("..." if len(senza) > 5 else ""))
    if orfani:
        return False, (f"{len(orfani)} righe di nomi_paziente.csv non hanno "
                       f"corrispondenza in alimenti.csv: " + ", ".join(orfani[:5]))
    return True, f"{len(alimenti)} alimenti, tutti con nome paziente"


def controllo_7_formati():
    """formati_confezione.csv e scambi_frutta.csv: food_id esistenti nel
    database, unita' e tolleranze valide; catalogo colazioni_spuntini.csv nei
    formati di confezione (23/10/2026)."""
    try:
        sys.path.insert(0, BASE)
        import formati
        with open(os.path.join(BASE, "alimenti.csv"), newline="", encoding="utf-8") as f:
            ids = {r["food_id"] for r in csv.DictReader(f)}
        problemi = formati.valida_file(ids)
        # Il catalogo colazioni_spuntini.csv deve rispettare i formati di
        # confezione: un'alternativa standard fuori formato fa scattare
        # FORMATO_CONFEZIONE_NON_RISPETTATO su ogni piano che la usa (rilievo
        # del primo piano reale, 23/10/2026). La libreria (moduli_*.csv) non e'
        # controllata qui: le sue violazioni attendono una decisione clinica.
        import struttura_pasti
        tabella = formati.carica_formati()
        for alt in struttura_pasti.carica_catalogo():
            righe = [{"food_id": fid, "grammi": g, "giorno": alt["alternativa_id"],
                      "pasto": ""} for fid, g in alt["ingredienti"]]
            for v in formati.controlla_piano(righe, tabella):
                problemi.append(f"colazioni_spuntini.csv: {alt['alternativa_id']} "
                                f"{v['nome']} {v['grammi']:g} g fuori formato "
                                f"(ammesse {v['ammesse']})")
    except Exception as e:
        return False, f"controllo formati non eseguibile: {e}"
    if problemi:
        return False, "; ".join(problemi)
    return True, ("formati e scambi frutta coerenti con alimenti.csv; "
                  "catalogo colazioni/spuntini nei formati di confezione")


def controllo_8_accoppiamenti():
    """ruoli_alimenti.csv copre tutto il database con ruoli ammessi, le regole
    di accoppiamenti_vietati.csv usano ruoli validi e nessun blocco della
    libreria (moduli_pasto.csv, moduli_colazione.csv) viola una regola:
    la libreria deve contenere solo accoppiamenti validi (21/10/2026)."""
    try:
        sys.path.insert(0, BASE)
        import accoppiamenti
        with open(os.path.join(BASE, "alimenti.csv"), newline="", encoding="utf-8") as f:
            ids = {r["food_id"] for r in csv.DictReader(f)}
        problemi = accoppiamenti.valida_file(ids)
        n_regole = len(accoppiamenti.carica_regole())
        # tag calcolati (vitD, calcio, leggero): si ricavano dai valori, scritti
        # a mano divergono (21/10/2026)
        import moduli_pasto
        for mid, tag in moduli_pasto.tag_calcolati_scritti(moduli_pasto.carica_moduli()):
            problemi.append(f"libreria: {mid} riporta a mano il tag calcolato '{tag}'")
    except Exception as e:
        return False, f"controllo accoppiamenti non eseguibile: {e}"
    if problemi:
        return False, "; ".join(problemi[:6]) + (" ..." if len(problemi) > 6 else "")
    return True, (f"{len(ids)} alimenti con ruolo, {n_regole} regole valide, "
                  f"libreria senza accoppiamenti vietati")


def _file_da_firmare():
    """Elenco ordinato dei file coperti da SHA256SUMS, relativi a BASE.

    Copre codice, CSV e casi golden. Esclusi di proposito:
      - SHA256SUMS stesso (non puo' contenere il proprio hash)
      - __pycache__ e .pyc (rigenerati a ogni esecuzione, cambiano da soli)
      - i file per-paziente che il nutrizionista appoggia qui durante una
        sessione (piano.csv, target.csv, farmaci_paziente.csv...): non fanno
        parte del motore e non devono comparire nei checksum
    """
    per_paziente = {"piano.csv", "target.csv", "farmaci_paziente.csv",
                    "interazioni.csv", "orari_pasti.csv"}
    elenco = []
    for radice, cartelle, file_trovati in os.walk(BASE):
        cartelle[:] = [c for c in cartelle if c != "__pycache__"]
        for nome in file_trovati:
            if nome in ("SHA256SUMS",) or nome.endswith(".pyc"):
                continue
            percorso = os.path.relpath(os.path.join(radice, nome), BASE)
            # i file per-paziente si escludono solo se stanno nella radice:
            # dentro golden/ sono input di test, e vanno firmati
            if os.path.dirname(percorso) == "" and nome in per_paziente:
                continue
            elenco.append(percorso)
    return sorted(elenco)


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blocco in iter(lambda: f.read(65536), b""):
            h.update(blocco)
    return h.hexdigest()


def controllo_5_checksum():
    """FASE 4 - verifica di integrita' contro SHA256SUMS.

    MOVENTE: due file si sono corrotti in silenzio su Drive (il docx delle
    regole di traduzione e il PDF del piano P01, ridotto a 238 byte). Un
    file corrotto non si annuncia. Su un CSV del motore non produce un errore
    visibile: produce numeri.

    I controlli 1-4 intercettano la corruzione che rompe il parsing o sposta i
    totali della giornata golden. Non intercettano una modifica che resta
    sintatticamente valida - un valore di calcio cambiato, una riga persa in
    un file che il golden non tocca. Questo controllo si accorge di qualsiasi
    differenza, byte per byte.

    COSA NON GARANTISCE: che i valori siano giusti, solo che siano quelli
    congelati l'ultima volta che i checksum sono stati generati. Se si
    rigenera SHA256SUMS senza aver capito perche' un file era cambiato, la
    garanzia si perde esattamente come rigenerando un atteso.json rosso.
    """
    path_sums = os.path.join(BASE, "SHA256SUMS")
    if not os.path.isfile(path_sums):
        return False, ("SHA256SUMS non trovato: l'integrita' dei file del "
                       "motore non e' verificabile. Generarlo con "
                       "'python3 collaudo.py --genera-checksums' dopo aver "
                       "controllato che i file siano quelli attesi.")

    attesi = {}
    try:
        with open(path_sums, encoding="utf-8") as f:
            for riga in f:
                riga = riga.strip()
                if not riga or riga.startswith("#"):
                    continue
                hash_atteso, _, nome = riga.partition("  ")
                if not nome:
                    return False, f"SHA256SUMS malformato alla riga: {riga}"
                attesi[nome] = hash_atteso
    except Exception as e:
        return False, f"SHA256SUMS illeggibile: {e}"

    if not attesi:
        return False, "SHA256SUMS presente ma vuoto: nessuna garanzia."

    mancanti, alterati, opzionali_assenti = [], [], []
    for nome, hash_atteso in sorted(attesi.items()):
        percorso = os.path.join(BASE, nome)
        if not os.path.isfile(percorso):
            if nome in FILE_OPZIONALI:
                opzionali_assenti.append(nome)
            else:
                mancanti.append(nome)
            continue
        if _sha256(percorso) != hash_atteso:
            alterati.append(nome)

    presenti = set(_file_da_firmare())
    non_dichiarati = sorted(presenti - set(attesi))

    if mancanti or alterati:
        parti = []
        if mancanti:
            parti.append(f"MANCANTI ({len(mancanti)}): {', '.join(mancanti)}")
        if alterati:
            parti.append(f"ALTERATI ({len(alterati)}): {', '.join(alterati)}")
        parti.append("Capire la causa PRIMA di rigenerare i checksum: un "
                     "aggiornamento legittimo non ancora registrato e una "
                     "corruzione silenziosa si presentano allo stesso modo.")
        return False, " | ".join(parti)

    verificati = len(attesi) - len(opzionali_assenti)
    messaggio = f"{verificati} file verificati, tutti integri"
    if opzionali_assenti:
        messaggio += (f" ({len(opzionali_assenti)} opzionali non scaricati, "
                      f"servono solo per ampliare il database: "
                      f"{', '.join(opzionali_assenti)})")
    if non_dichiarati:
        messaggio += (f" (non coperti da SHA256SUMS, informativo: "
                      f"{', '.join(non_dichiarati)})")
    return True, messaggio


def genera_checksums():
    """Scrive SHA256SUMS. Va usato solo dopo aver verificato che i file siano
    quelli attesi: rigenerare per far tornare verde un collaudo rosso senza
    aver capito perche' fosse rosso annulla lo scopo del controllo."""
    elenco = _file_da_firmare()
    if not elenco:
        print("Nessun file da firmare.")
        return 1
    righe = [f"{_sha256(os.path.join(BASE, nome))}  {nome}" for nome in elenco]
    with open(os.path.join(BASE, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    print("MODO GENERAZIONE - SHA256SUMS sovrascritto.")
    print("Da usare solo se i file sono gia' stati verificati.\n")
    for riga in righe:
        print(f"  {riga}")
    print(f"\n{len(righe)} file firmati.")
    return 0


def main():
    print("=" * 60)
    print("COLLAUDO DI INIZIO SESSIONE - Motore di calcolo")
    print("=" * 60)

    tutto_ok = True

    print("\n1) Integrita' e presenza dei CSV")
    for nome_file, ok, dettaglio in controllo_1_integrita_csv():
        simbolo = "OK " if ok else "XX "
        print(f"   [{simbolo}] {nome_file}: {dettaglio}")
        tutto_ok = tutto_ok and ok

    print("\n2) Conteggio righe alimenti.csv")
    ok, dettaglio = controllo_2_conteggio_alimenti()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n3) Duplicati food_id in alimenti.csv")
    ok, dettaglio = controllo_3_duplicati_food_id()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n4) Giornata golden (regressione codice, non validazione clinica)")
    ok, dettaglio = controllo_4_giornata_golden()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n5) Integrita' dei file del motore (SHA256SUMS)")
    ok, dettaglio = controllo_5_checksum()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n6) Nomi per il paziente (nomi_paziente.csv)")
    ok, dettaglio = controllo_6_nomi_paziente()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n7) Formati confezione e scambi frutta")
    ok, dettaglio = controllo_7_formati()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n8) Ruoli e accoppiamenti vietati")
    ok, dettaglio = controllo_8_accoppiamenti()
    print(f"   [{'OK ' if ok else 'XX '}] {dettaglio}")
    tutto_ok = tutto_ok and ok

    print("\n" + "=" * 60)
    if tutto_ok:
        print("COLLAUDO SUPERATO - motore utilizzabile per questa sessione")
    else:
        print("COLLAUDO FALLITO - non usare il motore su un paziente finche'")
        print("le anomalie sopra non sono state risolte")
    print("=" * 60)

    sys.exit(0 if tutto_ok else 1)


if __name__ == "__main__":
    if "--genera-checksums" in sys.argv:
        sys.exit(genera_checksums())
    main()
