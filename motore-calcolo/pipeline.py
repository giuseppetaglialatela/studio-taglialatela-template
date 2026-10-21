#!/usr/bin/env python3
"""
Orchestratore del motore di calcolo - Studio Nutrizionale Taglialatela
FASE 3 del consolidamento.

PERCHE' ESISTE
Il motore calcolava gia' bene, ma l'ORDINE dei passi era imposto per
convenzione: viveva nelle istruzioni e nella memoria della sessione, non nel
software. Entrambi gli errori di processo del primo caso reale sono nati da
li' - scenari di scelta multipla verificati DOPO aver gia' presentato una
tabella, livello colazione applicato giorno per giorno anziche' su tutto il
piano.

pipeline.py esegue i sei passi SEMPRE nello stesso ordine e produce un unico
report. Cio' che era "una regola da ricordare" diventa "una cosa su cui il
motore si ferma".

COSA NON FA
Non e' una validazione clinica. Verifica che il piano rispetti i vincoli
strutturali e le tolleranze dichiarate; NON dice che il piano sia giusto per
quel paziente. Il gate di approvazione resta del nutrizionista: il motore
propone e calcola, il nutrizionista decide.

USO
  python3 pipeline.py --piano piano.csv --target target.csv
                      [--farmaci farmaci_paziente.csv
                       --interazioni interazioni.csv
                       --orari orari_pasti.csv]
                      [--gap gap.csv]
                      [--deroga-struttura "motivo dichiarato"]
                      [--eccezione-etichetta voci_etichetta.csv]
                      [--salta-collaudo]

ESITO
  exit 0 - nessun rilievo bloccante: il report e' utilizzabile per la tabella
           di approvazione del PASSO 6 del workflow.
  exit 1 - almeno un rilievo BLOCCANTE. Il report viene comunque stampato per
           intero (serve a capire cosa correggere), ma il piano NON e'
           presentabile per l'approvazione finche' il rilievo non e' risolto.

NOTA SUL SIGNIFICATO DI "BLOCCANTE"
In una esecuzione batch non c'e' interattivita': tutti i passi girano sempre.
Il blocco non e' sull'esecuzione ma sul VERDETTO finale e sul codice di uscita.
Cio' che l'ordine fisso garantisce e' che gli scenari di scelta multipla
(PASSO 2) siano calcolati e stampati PRIMA del riepilogo, mai dopo: e' il punto
in cui l'errore reale si era prodotto.
"""

import argparse
import os
import subprocess
import sys
from collections import defaultdict

from calcolatore import (
    carica_alimenti, carica_piano, carica_target, carica_gap,
    carica_eccezioni_etichetta,
    calcola_riga, somma_nutrienti, nutrienti_sottostimati,
    entro_tolleranza, formatta_num,
    NUTRIENTI_PER_100G, MICRONUTRIENTI_LARN, TOLLERANZA_PCT,
    PASTI_AMMESSI, ordine_pasti, pasti_non_ammessi,
)
from scelte_multiple import carica_piano_esteso, calcola_intervallo_giorno
import coerenza
import formati as mod_formati
import accoppiamenti as mod_accoppiamenti
import struttura_pasti
import interazioni as mod_interazioni

BASE = os.path.dirname(os.path.abspath(__file__))
# Ordine dei pasti: da calcolatore.ordine_pasti (unica fonte, 30/09/2026).

# Pasti soggetti alle regole di struttura del PASSO 6. Il secondo spuntino
# segue le stesse regole dello spuntino (decisione del 30/09/2026), ma solo
# se il piano lo contiene: un piano a 4 pasti non riceve rilievi su di lui.
PASTI_STRUTTURATI = ("colazione", "spuntino")
PASTI_STRUTTURATI_SE_PRESENTI = ("spuntino2",)


def pasti_strutturati(righe):
    presenti = {r["pasto"] for r in righe}
    return PASTI_STRUTTURATI + tuple(p for p in PASTI_STRUTTURATI_SE_PRESENTI
                                     if p in presenti)


# --------------------------------------------------------------------------
# Raccolta dei rilievi
# --------------------------------------------------------------------------

class Rilievi:
    """Accumula i rilievi emersi lungo la pipeline.

    BLOCCANTE  -> il piano non e' presentabile per l'approvazione cosi' com'e'
    ATTENZIONE -> va dichiarato al nutrizionista, non blocca

    Ogni rilievo porta un CODICE stabile oltre al messaggio. Il messaggio e'
    per il nutrizionista e puo' essere riformulato in qualsiasi momento; il
    codice e' per la suite di regressione, che congela (passo, codice) e non
    la prosa. Senza questa separazione, una modifica di sola formulazione
    farebbe diventare rossa la suite, e l'abitudine a rigenerare gli attesi
    per far tornare il verde e' esattamente cio' che ne annullerebbe lo scopo.
    """

    def __init__(self):
        self.bloccanti = []
        self.attenzioni = []

    def blocca(self, passo, codice, messaggio):
        self.bloccanti.append((passo, codice, messaggio))

    def segnala(self, passo, codice, messaggio):
        self.attenzioni.append((passo, codice, messaggio))

    def come_dati(self):
        """Vista serializzabile per la suite di regressione: solo passo e
        codice, ordinati. La prosa resta fuori di proposito."""
        return {
            "bloccanti": sorted((p, c) for p, c, _ in self.bloccanti),
            "attenzioni": sorted((p, c) for p, c, _ in self.attenzioni),
        }


def titolo(n, testo):
    print(f"\n{'=' * 68}")
    print(f"PASSO {n} - {testo}")
    print("=" * 68)


# --------------------------------------------------------------------------
# PASSO 0 - collaudo (principio 7)
# --------------------------------------------------------------------------

def passo_0_collaudo(rilievi, saltato):
    titolo(0, "COLLAUDO DI INIZIO SESSIONE")
    if saltato:
        print("\n  Collaudo SALTATO su richiesta esplicita (--salta-collaudo).")
        rilievi.segnala(0, "COLLAUDO_SALTATO", "collaudo non eseguito: i risultati non sono "
                           "certificati dal principio 7")
        return

    percorso = os.path.join(BASE, "collaudo.py")
    if not os.path.isfile(percorso):
        rilievi.blocca(0, "COLLAUDO_ASSENTE", "collaudo.py non trovato: impossibile certificare "
                          "l'integrita' dei dati prima del calcolo")
        print("\n  ERRORE: collaudo.py non trovato accanto a pipeline.py.")
        return

    esito = subprocess.run([sys.executable, percorso],
                           capture_output=True, text=True)
    if esito.returncode == 0:
        print("\n  Collaudo superato: CSV integri, conteggio atteso, nessun "
              "food_id duplicato, giornata golden invariata.")
        print("  (dettaglio completo: python3 collaudo.py)")
    else:
        print("\n  COLLAUDO FALLITO - output integrale:\n")
        print(esito.stdout)
        rilievi.blocca(0, "COLLAUDO_FALLITO", "collaudo.py fallito: nessun calcolo su paziente "
                          "e' valido finche' l'anomalia non e' risolta")


# --------------------------------------------------------------------------
# PASSO 1 - totali per pasto e per giorno
# --------------------------------------------------------------------------

def carica_database(rilievi, eccezione_path):
    """Database del piano: SEMPRE quello ufficiale del motore, piu' le eventuali
    voci da etichetta dichiarate con --eccezione-etichetta (decisione del
    21/10/2026: solo su richiesta del nutrizionista, mai in alimenti.csv).
    Un file di eccezione non valido blocca. Chiamata da main() e dalla suite.
    Restituisce (db, eccezioni, fermo).
    """
    db = carica_alimenti(os.path.join(BASE, "alimenti.csv"))
    if not eccezione_path:
        return db, {}, False
    try:
        eccezioni = carica_eccezioni_etichetta(eccezione_path, db)
    except (OSError, ValueError) as e:
        rilievi.blocca(1, "ECCEZIONE_ETICHETTA_NON_VALIDA", str(e))
        return db, {}, True
    db.update(eccezioni)
    return db, eccezioni, False


def controlla_food_id(rilievi, piano, db, gap, eccezioni):
    """food_id del piano: sconosciuti = blocco; voci da etichetta dichiarate =
    rilievo da dichiarare, con i micronutrienti a zero trattati come gap
    (totali sottostimati) e l'avviso che gli accoppiamenti non le controllano
    (non hanno un ruolo). Modifica gap sul posto. Restituisce True se blocca.
    """
    sconosciuti = sorted({r["food_id"] for r in piano if r["food_id"] not in db})
    if sconosciuti:
        print(f"\n  ERRORE: food_id assenti dal database: {', '.join(sconosciuti)}")
        rilievi.blocca(1, "FOOD_ID_SCONOSCIUTO",
                       f"food_id non presenti in alimenti.csv: {', '.join(sconosciuti)}. "
                       f"Una voce da etichetta passa solo su richiesta del "
                       f"nutrizionista, con --eccezione-etichetta")
        return True
    usate = sorted({r["food_id"] for r in piano if r["food_id"] in eccezioni})
    for f in usate:
        for nutriente in MICRONUTRIENTI_LARN:
            if not db[f].get(nutriente):
                gap.setdefault(f, {}).setdefault(
                    nutriente, "eccezione etichetta: dato non dichiarato")
    if usate:
        elenco = ", ".join(f"{f} ({db[f]['nome']})" for f in usate)
        rilievi.segnala(1, "ALIMENTO_FUORI_DATABASE_SU_RICHIESTA",
                        f"eccezione etichetta su richiesta del nutrizionista: "
                        f"{elenco}. Valori non da CREA/BDA-IEO/USDA; "
                        f"micronutrienti a zero trattati come gap; "
                        f"accoppiamenti non controllati per queste voci")
    return False


def controlla_pasti_ammessi(rilievi, piano):
    """Blocca se piano.csv usa un valore di pasto fuori da PASTI_AMMESSI.
    Restituisce True se ha bloccato: il chiamante si ferma, come per un
    food_id sconosciuto. Usata da main() e da regressione.py (30/09/2026)."""
    non_ammessi = pasti_non_ammessi(piano)
    if not non_ammessi:
        return False
    elenco = ", ".join(f"giorno {g} '{p}'" for g, p in non_ammessi)
    print(f"\n  ERRORE: valori di pasto non ammessi: {elenco}")
    rilievi.blocca(1, "PASTO_NON_AMMESSO",
                   f"valori di pasto non ammessi in piano.csv: {elenco}. "
                   f"Ammessi: {' | '.join(PASTI_AMMESSI)}. Un refuso "
                   f"verrebbe sommato nei totali ma scartato dal PDF.")
    return True


def totali_per_giorno(piano, db):
    per_pasto = defaultdict(list)
    for r in piano:
        per_pasto[(r["giorno"], r["pasto"])].append(
            calcola_riga(db[r["food_id"]], r["grammi"]))
    giorni = sorted({g for g, _ in per_pasto})
    ordine = ordine_pasti(p for _, p in per_pasto)
    risultato = {}
    for giorno in giorni:
        chiavi = sorted([k for k in per_pasto if k[0] == giorno],
                        key=lambda k: ordine.get(k[1], 99))
        righe_giorno = [r for k in chiavi for r in per_pasto[k]]
        risultato[giorno] = {
            "pasti": [(k[1], somma_nutrienti(per_pasto[k])) for k in chiavi],
            "totale": somma_nutrienti(righe_giorno),
        }
    return risultato


def percentuali_macro(tot):
    kcal = tot["kcal_100g"]
    if not kcal:
        return 0.0, 0.0, 0.0
    return (tot["proteine_g"] * 4 / kcal * 100,
            tot["carboidrati_g"] * 4 / kcal * 100,
            tot["grassi_g"] * 9 / kcal * 100)


def passo_1_calcolo(rilievi, piano, db, target, giorni_con_scelte):
    titolo(1, "CALCOLO PER PASTO E PER GIORNO")

    dati = totali_per_giorno(piano, db)

    for giorno, d in dati.items():
        nota = ""
        if giorno in giorni_con_scelte:
            nota = ("   [giorno con scelta multipla: i totali qui sotto usano "
                    "TUTTE le alternative insieme e NON rappresentano una "
                    "giornata reale - vedi PASSO 2]")
        print(f"\n  --- GIORNO {giorno} ---{nota}")
        for pasto, tp in d["pasti"]:
            print(f"    {pasto:<11} kcal {formatta_num(tp['kcal_100g']):>8}  "
                  f"P {formatta_num(tp['proteine_g']):>6}g  "
                  f"C {formatta_num(tp['carboidrati_g']):>6}g  "
                  f"F {formatta_num(tp['grassi_g']):>6}g  "
                  f"Fib {formatta_num(tp['fibra_g']):>5}g")

        tot = d["totale"]
        p_pct, c_pct, g_pct = percentuali_macro(tot)
        print(f"    {'TOTALE':<11} kcal {formatta_num(tot['kcal_100g']):>8}  "
              f"P {formatta_num(tot['proteine_g']):>6}g  "
              f"C {formatta_num(tot['carboidrati_g']):>6}g  "
              f"F {formatta_num(tot['grassi_g']):>6}g  "
              f"Fib {formatta_num(tot['fibra_g']):>5}g")

        if giorno in giorni_con_scelte:
            continue  # i verdetti di tolleranza si danno al PASSO 2

        if "kcal_target" in target:
            kt = target["kcal_target"]
            scarto = (tot["kcal_100g"] - kt) / kt * 100
            ok = entro_tolleranza(scarto)
            print(f"      kcal vs target {formatta_num(kt)}: "
                  f"{scarto:+.2f}% -> {'OK' if ok else 'FUORI TOLLERANZA'}")
            controlla_limite_giorno(rilievi, 1, giorno, [scarto])
            if not ok:
                rilievi.segnala(1, "KCAL_FUORI_TOLLERANZA", f"giorno {giorno}: kcal fuori tolleranza "
                                  f"({scarto:+.2f}%, limite +/-{TOLLERANZA_PCT}%). "
                                  f"Non bloccante: il giudizio si da' sulla media "
                                  f"settimanale (VERIFICA SETTIMANALE, PASSO 2).")

        for nome, valore, chiave in [("Proteine", p_pct, "proteine_pct_target"),
                                     ("Carboidrati", c_pct, "carboidrati_pct_target"),
                                     ("Grassi", g_pct, "grassi_pct_target")]:
            if chiave not in target:
                continue
            scarto = valore - target[chiave]
            ok = entro_tolleranza(scarto)
            print(f"      {nome} {formatta_num(valore)}% vs target "
                  f"{formatta_num(target[chiave])}%: {scarto:+.2f} punti -> "
                  f"{'OK' if ok else 'FUORI TOLLERANZA'}")
            if not ok:
                rilievi.segnala(1, "MACRO_FUORI_TOLLERANZA", f"giorno {giorno}: {nome.lower()} fuori "
                                  f"tolleranza ({scarto:+.2f} punti). Non bloccante: "
                                  f"il giudizio si da' sulla media settimanale.")

        if "fibra_g_target" in target:
            ft = target["fibra_g_target"]
            print(f"      Fibra {formatta_num(tot['fibra_g'])}g vs target "
                  f"{formatta_num(ft)}g")
            if tot["fibra_g"] < ft * 0.8:
                rilievi.segnala(1, "FIBRA_SOTTO_TARGET", f"giorno {giorno}: fibra sotto l'80% del "
                                   f"target ({formatta_num(tot['fibra_g'])}g "
                                   f"su {formatta_num(ft)}g)")

    return dati


# --------------------------------------------------------------------------
# PASSO 2 - scenari min/max colazione+spuntino, per OGNI giorno
# --------------------------------------------------------------------------

def passo_2_scenari(rilievi, righe_estese, db, target):
    titolo(2, "SCENARI MIN/MAX DEI PASTI A SCELTA MULTIPLA")
    print("\n  Ordine non negoziabile: gli scenari si calcolano PRIMA di ogni")
    print("  riepilogo. Presentare una sola combinazione 'esemplare' e'")
    print("  l'errore che questo passo esiste per impedire.")

    per_giorno = defaultdict(list)
    for r in righe_estese:
        per_giorno[r["giorno"]].append(r)

    intervalli = {}
    for giorno in sorted(per_giorno):
        righe = per_giorno[giorno]
        if not any(r["gruppo_scelta"] for r in righe):
            print(f"\n  Giorno {giorno}: nessuna scelta multipla "
                  f"(valore unico, gia' valutato al PASSO 1).")
            continue

        minimi, massimi, dettaglio = calcola_intervallo_giorno(righe, db)
        intervalli[giorno] = (minimi, massimi)

        print(f"\n  --- GIORNO {giorno} ---")
        for d in dettaglio:
            print(f"    gruppo '{d['gruppo']}' ({d['pasto']}): "
                  f"{d['n_opzioni']} alternative -> {', '.join(d['opzioni'])}")

        print(f"    kcal        {minimi['kcal_100g']:8.1f} - {massimi['kcal_100g']:.1f}")
        print(f"    Proteine    {minimi['proteine_g']:8.1f} - {massimi['proteine_g']:.1f} g")
        print(f"    Carboidrati {minimi['carboidrati_g']:8.1f} - {massimi['carboidrati_g']:.1f} g")
        print(f"    Grassi      {minimi['grassi_g']:8.1f} - {massimi['grassi_g']:.1f} g")
        print(f"    Fibra       {minimi['fibra_g']:8.1f} - {massimi['fibra_g']:.1f} g")

        if "kcal_target" in target:
            kt = target["kcal_target"]
            s_min = (minimi["kcal_100g"] - kt) / kt * 100
            s_max = (massimi["kcal_100g"] - kt) / kt * 100
            print(f"    kcal vs target {formatta_num(kt)}: "
                  f"{s_min:+.2f}% (min) / {s_max:+.2f}% (max)")
            controlla_limite_giorno(rilievi, 2, giorno, [s_min, s_max])
            fuori = []
            if not entro_tolleranza(s_min):
                fuori.append(f"scenario minimo {s_min:+.2f}%")
            if not entro_tolleranza(s_max):
                fuori.append(f"scenario massimo {s_max:+.2f}%")
            if fuori:
                rilievi.segnala(2, "SCENARIO_KCAL_FUORI_TOLLERANZA", f"giorno {giorno}: kcal fuori tolleranza "
                                  f"in uno scenario di scelta - "
                                  f"{'; '.join(fuori)}. Non bloccante: il "
                                  f"giudizio si da' sulla media settimanale "
                                  f"(VERIFICA SETTIMANALE).")

        for nome, kc, chiave in [("Proteine", 4, "proteine_pct_target"),
                                 ("Carboidrati", 4, "carboidrati_pct_target"),
                                 ("Grassi", 9, "grassi_pct_target")]:
            if chiave not in target:
                continue
            campo = {"Proteine": "proteine_g", "Carboidrati": "carboidrati_g",
                     "Grassi": "grassi_g"}[nome]
            # la % dipende sia dal nutriente sia dalle kcal: si valutano i due
            # estremi realmente calcolabili come limiti, non una combinazione
            estremi = []
            for tot in (minimi, massimi):
                if tot["kcal_100g"]:
                    estremi.append(tot[campo] * kc / tot["kcal_100g"] * 100)
            if not estremi:
                continue
            lo, hi = min(estremi), max(estremi)
            s_lo, s_hi = lo - target[chiave], hi - target[chiave]
            print(f"    {nome} {lo:.1f}% - {hi:.1f}% vs target "
                  f"{formatta_num(target[chiave])}% "
                  f"({s_lo:+.2f} / {s_hi:+.2f} punti)")
            if not entro_tolleranza(s_lo) or not entro_tolleranza(s_hi):
                rilievi.segnala(2, "SCENARIO_MACRO_FUORI_TOLLERANZA", f"giorno {giorno}: {nome.lower()} esce di "
                                   f"tolleranza a un estremo degli scenari "
                                   f"({s_lo:+.2f} / {s_hi:+.2f} punti). "
                                   f"Gli estremi sono limiti di garanzia, non "
                                   f"una giornata componibile: verificare sul "
                                   f"caso reale prima di correggere.")

        print(f"\n    micronutrienti (min - max vs LARN):")
        for nutriente, chiave in MICRONUTRIENTI_LARN.items():
            if chiave not in target or not target[chiave]:
                continue
            larn = target[chiave]
            vmin, vmax = minimi[nutriente], massimi[nutriente]
            pmin, pmax = vmin / larn * 100, vmax / larn * 100
            if pmax < 80:
                flag = "  (sotto 80% anche nel best case del giorno)"
            elif pmin < 80:
                flag = "  (dipende dalla scelta del paziente)"
            else:
                flag = ""
            print(f"      {nutriente:<18} {vmin:8.1f} - {vmax:8.1f}  "
                  f"({pmin:.0f}% - {pmax:.0f}% LARN){flag}")

        print("\n    NOTA: min e max sono calcolati per ogni nutriente")
        print("    separatamente. Sono limiti garantiti, NON una giornata")
        print("    realmente componibile. I micronutrienti qui sopra sono")
        print("    informativi: il giudizio sull'adeguatezza si da' sulla")
        print("    media settimanale del PASSO 3, non sul singolo giorno.")

    return intervalli


# --------------------------------------------------------------------------
# PASSO 2 (coda) - VERIFICA SETTIMANALE di kcal e macro
# --------------------------------------------------------------------------
# Decisione clinica del 18/09/2026 (Dott. Taglialatela): kcal e macro si
# giudicano sulla MEDIA SETTIMANALE, come i micronutrienti (principio 8).
# Il singolo giorno fuori tolleranza e' una segnalazione, non un blocco:
# forzare ogni giorno nel range produce pasti che il paziente non mangia.
# Bloccante resta solo la media settimanale fuori tolleranza.
# Giorni senza scelte: min = max = totale del PASSO 1.
# Giorni con scelte: estremi del PASSO 2 (limiti di garanzia per nutriente).

# Limite di sicurezza giornaliero sulle kcal (decisione clinica 18/09/2026):
# oltre questo scarto il singolo giorno BLOCCA anche se la settimana compensa.
LIMITE_SICUREZZA_GIORNO_PCT = 10.0


def controlla_limite_giorno(rilievi, passo, giorno, scarti):
    fuori = [s for s in scarti if abs(s) > LIMITE_SICUREZZA_GIORNO_PCT]
    if fuori:
        rilievi.blocca(passo, "GIORNO_KCAL_OLTRE_LIMITE_SICUREZZA",
                       f"giorno {giorno}: kcal oltre il limite di sicurezza "
                       f"giornaliero di +/-{LIMITE_SICUREZZA_GIORNO_PCT:.0f}% "
                       f"({', '.join(f'{s:+.2f}%' for s in fuori)})")


def verifica_settimanale(rilievi, dati_giorni, intervalli, target):
    print("\n  --- VERIFICA SETTIMANALE (media dei giorni del piano) ---")
    giorni = sorted(dati_giorni)
    if not giorni:
        return
    minimi, massimi = [], []
    for g in giorni:
        if g in intervalli:
            mn, mx = intervalli[g]
        else:
            mn = mx = dati_giorni[g]["totale"]
        minimi.append(mn)
        massimi.append(mx)
    n = len(giorni)
    somma = lambda lista, campo: sum(t[campo] for t in lista)
    print(f"    giorni considerati: {n}")
    if "kcal_target" in target:
        kt = target["kcal_target"]
        k_min = somma(minimi, "kcal_100g") / n
        k_max = somma(massimi, "kcal_100g") / n
        s_min = (k_min - kt) / kt * 100
        s_max = (k_max - kt) / kt * 100
        ok = entro_tolleranza(s_min) and entro_tolleranza(s_max)
        print(f"    kcal media {k_min:.1f} - {k_max:.1f} vs target "
              f"{formatta_num(kt)}: {s_min:+.2f}% / {s_max:+.2f}% -> "
              f"{'OK' if ok else 'FUORI TOLLERANZA'}")
        if not ok:
            rilievi.blocca(2, "SETTIMANA_KCAL_FUORI_TOLLERANZA",
                           f"media settimanale kcal fuori tolleranza "
                           f"({s_min:+.2f}% / {s_max:+.2f}%, limite "
                           f"+/-{TOLLERANZA_PCT}%)")
    for nome, kc, chiave, campo in [
            ("Proteine", 4, "proteine_pct_target", "proteine_g"),
            ("Carboidrati", 4, "carboidrati_pct_target", "carboidrati_g"),
            ("Grassi", 9, "grassi_pct_target", "grassi_g")]:
        if chiave not in target:
            continue
        estremi = []
        for lista in (minimi, massimi):
            kcal_tot = somma(lista, "kcal_100g")
            if kcal_tot:
                estremi.append(somma(lista, campo) * kc / kcal_tot * 100)
        if not estremi:
            continue
        lo, hi = min(estremi), max(estremi)
        s_lo, s_hi = lo - target[chiave], hi - target[chiave]
        ok = entro_tolleranza(s_lo) and entro_tolleranza(s_hi)
        print(f"    {nome} media {lo:.1f}% - {hi:.1f}% vs target "
              f"{formatta_num(target[chiave])}% ({s_lo:+.2f} / {s_hi:+.2f} "
              f"punti) -> {'OK' if ok else 'FUORI TOLLERANZA'}")
        # Gli estremi % dei macro NON sono una settimana componibile (min e
        # max sono calcolati per nutriente): si blocca solo se l'INTERO
        # intervallo garantito sta fuori tolleranza dallo stesso lato;
        # se esce un solo estremo e' una segnalazione, come nel PASSO 2.
        tutto_fuori = ((not entro_tolleranza(s_lo)) and
                       (not entro_tolleranza(s_hi)) and
                       ((s_lo > 0) == (s_hi > 0)))
        if tutto_fuori:
            rilievi.blocca(2, "SETTIMANA_MACRO_FUORI_TOLLERANZA",
                           f"media settimanale {nome.lower()} fuori "
                           f"tolleranza su tutto l'intervallo "
                           f"({s_lo:+.2f} / {s_hi:+.2f} punti)")
        elif not ok:
            rilievi.segnala(2, "SETTIMANA_MACRO_ESTREMO_FUORI",
                            f"media settimanale {nome.lower()}: un estremo "
                            f"esce di tolleranza ({s_lo:+.2f} / {s_hi:+.2f} "
                            f"punti). Limite di garanzia, non settimana "
                            f"componibile: verificare sul caso reale.")


# --------------------------------------------------------------------------
# PASSO 3 - micronutrienti per giorno e media settimanale
# --------------------------------------------------------------------------

def passo_3_micronutrienti(rilievi, dati_giorni, intervalli, target,
                           sottostime, db):
    titolo(3, "MICRONUTRIENTI - PER GIORNO E MEDIA SETTIMANALE")

    micro_presenti = [(n, c) for n, c in MICRONUTRIENTI_LARN.items()
                      if c in target and target[c]]
    if not micro_presenti:
        print("\n  Nessun riferimento LARN nei target: confronto non eseguibile.")
        rilievi.segnala(3, "LARN_ASSENTI", "target privo di riferimenti LARN: i micronutrienti "
                           "non sono confrontati con alcuna soglia")
        return

    giorni = sorted(dati_giorni)
    accumulo = {n: [] for n, _ in micro_presenti}
    giorni_con_presenza = {n: 0 for n, _ in micro_presenti}

    for giorno in giorni:
        print(f"\n  --- GIORNO {giorno} ---")
        if giorno in intervalli:
            minimi, massimi = intervalli[giorno]
            print("    (giorno a scelta multipla: valori riportati come "
                  "min - max, gia' calcolati al PASSO 2)")
            for nutriente, chiave in micro_presenti:
                larn = target[chiave]
                vmin, vmax = minimi[nutriente], massimi[nutriente]
                accumulo[nutriente].append((vmin, vmax))
                if vmax > 0:
                    giorni_con_presenza[nutriente] += 1
                flag = ""
                if nutriente in sottostime:
                    flag += "  ⛔ TOTALE SOTTOSTIMATO"
                print(f"    {nutriente:<18} {vmin:8.1f} - {vmax:8.1f}  "
                      f"({vmin / larn * 100:.0f}% - {vmax / larn * 100:.0f}% "
                      f"LARN){flag}")
        else:
            tot = dati_giorni[giorno]["totale"]
            for nutriente, chiave in micro_presenti:
                larn = target[chiave]
                v = tot[nutriente]
                accumulo[nutriente].append((v, v))
                if v > 0:
                    giorni_con_presenza[nutriente] += 1
                pct = v / larn * 100
                flag = ""
                if nutriente in sottostime:
                    flag += "  ⛔ TOTALE SOTTOSTIMATO"
                print(f"    {nutriente:<18} {v:8.1f}  ({pct:.0f}% LARN){flag}")

    print(f"\n  --- MEDIA SETTIMANALE su {len(giorni)} giorni ---")
    print("    E' QUESTA la lettura su cui si decide. I LARN sono riferimenti")
    print("    per l'assunzione ABITUALE, non soglie giornaliere: tutti i")
    print("    micronutrienti tracciati hanno riserve corporee che tamponano")
    print("    su finestre molto piu' lunghe di ventiquattr'ore (B12 anni,")
    print("    folati e ferro mesi, vitamina D settimane). I valori per giorno")
    print("    sopra servono a vedere la DISTRIBUZIONE, non a essere corretti")
    print("    uno per uno: inseguire il target ogni giorno produce")
    print("    accostamenti di alimenti che il paziente non mangia, e un piano")
    print("    non seguito vale meno di un piano buono che viene seguito.")
    for nutriente, chiave in micro_presenti:
        larn = target[chiave]
        valori = accumulo[nutriente]
        media_min = sum(v[0] for v in valori) / len(valori)
        media_max = sum(v[1] for v in valori) / len(valori)
        p_min, p_max = media_min / larn * 100, media_max / larn * 100
        flag = ""
        if p_max < 80:
            flag += "  ⚠️ SOTTO 80% LARN anche in media"
        if nutriente in sottostime:
            flag += "  ⛔ SOTTOSTIMATO"
        if abs(media_min - media_max) < 0.001:
            print(f"    {nutriente:<18} {media_min:8.1f}  ({p_min:.0f}% LARN){flag}")
        else:
            print(f"    {nutriente:<18} {media_min:8.1f} - {media_max:8.1f}  "
                  f"({p_min:.0f}% - {p_max:.0f}% LARN){flag}")

        if p_max < 80:
            if nutriente in sottostime:
                rilievi.segnala(3, "MEDIA_SOTTO_LARN_CON_GAP", f"{nutriente}: media settimanale sotto "
                                   f"l'80% LARN MA il totale e' marcato "
                                   f"sottostimato - verificare il gap prima "
                                   f"di qualsiasi intervento clinico")
            else:
                rilievi.segnala(3, "MEDIA_SOTTO_LARN", f"{nutriente}: media settimanale sotto "
                                   f"l'80% LARN ({p_max:.0f}%)")

        # La concentrazione resta un rilievo anche quando la media e' adeguata:
        # e' l'unico caso in cui la distribuzione conta davvero. Per il calcio
        # l'assorbimento satura intorno ai 500 mg per singola assunzione,
        # quindi una media raggiunta concentrando tutto in pochi giorni non e'
        # equivalente alla stessa media distribuita.
        if len(giorni) >= 6 and giorni_con_presenza[nutriente] < 3:
            rilievi.segnala(3, "DISTRIBUZIONE_CONCENTRATA", f"{nutriente}: presente in soli "
                               f"{giorni_con_presenza[nutriente]} giorni su "
                               f"{len(giorni)} - la media puo' essere adeguata "
                               f"ma la distribuzione no")


# --------------------------------------------------------------------------
# PASSO 4 - coerenza dati + gap dichiarati
# --------------------------------------------------------------------------

def passo_4_coerenza(rilievi, db, target, piano, gap, sottostime,
                     righe_estese=None):
    titolo(4, "COERENZA DEI DATI E GAP DICHIARATI")

    anomalie = coerenza.check_atwater(db)
    print(f"\n  A) Cross-check Atwater (allarme se > "
          f"{coerenza.SOGLIA_ATWATER_PCT}% E > "
          f"{coerenza.SOGLIA_ATWATER_KCAL_ASSOLUTA} kcal/100g):")
    if not anomalie:
        print("     nessuna anomalia sul database.")
    else:
        for a in anomalie:
            scarto = (f"{a['scarto_pct']:+.1f}% / {a['scarto_abs']:.2f} kcal"
                      if a["scarto_pct"] is not None else "kcal a zero")
            print(f"     ⚠️ {a['food_id']} - {a['nome']}: {scarto}")
        print("     Le kcal restano quelle della fonte: questo controllo dice")
        print("     dove verificare la trascrizione, non cosa correggere.")
        rilievi.segnala(4, "ATWATER_SEGNALATO", f"{len(anomalie)} alimento/i segnalato/i dal "
                           f"cross-check Atwater (falsi positivi noti e attesi: "
                           f"aglio, carciofi, semi di lino - M1; ogni altro "
                           f"nome va verificato)")

    problemi = coerenza.check_target(target)
    print(f"\n  B) Coerenza interna dei target:")
    if not problemi:
        print("     target coerenti.")
    for p in problemi:
        print(f"     ⚠️ {p}")
        rilievi.blocca(4, "TARGET_INCOERENTI", f"target incoerenti: {p}")

    sospetti = coerenza.check_righe_sospette(db, gap)
    print(f"\n  C) Righe con tutti i micronutrienti a zero:")
    if not sospetti:
        print("     nessuna riga sospetta.")
    for s in sospetti:
        print(f"     ⚠️ {s['food_id']} - {s['nome']}: probabile scheda incompleta")
        rilievi.segnala(4, "MICRO_TUTTI_ZERO", f"{s['nome']}: tutti i micronutrienti a zero, "
                           f"verificare la fonte")

    print(f"\n  D) Gap dichiarati sugli alimenti effettivamente usati nel piano:")
    if not sottostime:
        print("     nessun gap: i totali micronutrienti non sono sottostimati.")
    else:
        print("     ⛔ i totali seguenti sono SOTTOSTIMATI. Un valore sotto")
        print("        soglia qui NON e' una carenza accertata.")
        for nutriente in sorted(sottostime):
            print(f"        {nutriente}:")
            for fid, motivo in sottostime[nutriente]:
                nome = db[fid]["nome"] if fid in db else fid
                print(f"          - {nome}: {motivo}")

    print(f"\n  E) Formati confezione (regola anti-spreco, solo segnalazione):")
    try:
        fm = mod_formati.carica_formati()
    except Exception as e:
        print(f"     formati_confezione.csv non leggibile: {e}")
        rilievi.blocca(4, "FORMATI_ILLEGGIBILI", f"formati_confezione.csv non leggibile: {e}")
        fm = {}
    viol = mod_formati.controlla_piano(piano, fm)
    if not viol:
        print("     tutte le quantita' confezionate rispettano i formati.")
    for v in viol:
        print(f"     ⚠️ {v['nome']} {v['grammi']:g} g ({', '.join(v['dove'][:4])}"
              f"{'...' if len(v['dove']) > 4 else ''}): formati ammessi {v['ammesse']}")
        rilievi.segnala(4, "FORMATO_CONFEZIONE_NON_RISPETTATO",
                        f"{v['nome']} {v['grammi']:g} g non e' una confezione intera o un multiplo "
                        f"(ammessi: {v['ammesse']}) - rischio di spreco")

    # F) accoppiamenti vietati nello stesso pasto - decisione del 21/10/2026:
    # si segnala, non blocca. Le alternative di uno stesso gruppo_scelta si
    # valutano scenario per scenario: due opzioni alternative non si mangiano
    # insieme. Senza righe_estese non si possono separare gli scenari.
    print(f"\n  F) Accoppiamenti vietati nello stesso pasto (solo segnalazione):")
    if righe_estese is None:
        print("     non eseguito: servono le righe con gruppo_scelta/opzione.")
        rilievi.blocca(4, "ACCOPPIAMENTI_NON_VERIFICATI",
                       "controllo accoppiamenti non eseguito (righe estese assenti)")
        return
    try:
        ruoli = mod_accoppiamenti.carica_ruoli()
        regole = mod_accoppiamenti.carica_regole()
    except Exception as e:
        print(f"     file degli accoppiamenti non leggibili: {e}")
        rilievi.blocca(4, "ACCOPPIAMENTI_ILLEGGIBILI", f"file accoppiamenti non leggibili: {e}")
        return
    viol = mod_accoppiamenti.controlla_piano(righe_estese, ruoli, regole)
    if not viol:
        print("     nessun accoppiamento vietato.")
    for v in viol:
        a = " + ".join(db[x]["nome"] if x in db else x for x in v["alimenti_a"])
        b = " + ".join(db[x]["nome"] if x in db else x for x in v["alimenti_b"])
        sc = f" [{v['scenario']}]" if v["scenario"] else ""
        print(f"     ⚠️ {v['regola']} {v['pasto']}{sc}, giorni {','.join(v['giorni'])}: "
              f"{a} / {b}")
        rilievi.segnala(4, "ACCOPPIAMENTO_VIETATO",
                        f"{v['motivo']} - {v['pasto']}{sc}, giorni "
                        f"{','.join(v['giorni'])}: {a} / {b}")


# --------------------------------------------------------------------------
# PASSO 5 - interazioni farmaco-alimento
# --------------------------------------------------------------------------

GRAVITA_AMMESSE = ("alta", "media", "bassa")


def passo_5_interazioni(rilievi, piano, db, farmaci_path, interazioni_path,
                        orari_path):
    titolo(5, "INTERAZIONI FARMACO-ALIMENTO")

    forniti = [p for p in (farmaci_path, interazioni_path, orari_path) if p]
    if not forniti:
        print("\n  Nessun file di terapia fornito.")
        print("  ATTENZIONE: l'assenza del file NON e' l'assenza di terapia.")
        print("  Se il paziente assume farmaci, questo passo va rieseguito")
        print("  con --farmaci, --interazioni e --orari.")
        rilievi.segnala(5, "TERAPIA_NON_DICHIARATA", "verifica interazioni non eseguita: nessun file di "
                           "terapia fornito. Confermare che il paziente non "
                           "sia in terapia farmacologica.")
        return

    mancanti = [nome for nome, p in [("--farmaci", farmaci_path),
                                     ("--interazioni", interazioni_path),
                                     ("--orari", orari_path)] if not p]
    if mancanti:
        print(f"\n  File di terapia incompleti: mancano {', '.join(mancanti)}.")
        rilievi.blocca(5, "TERAPIA_INCOMPLETA", f"verifica interazioni impossibile: mancano "
                          f"{', '.join(mancanti)}. Con una terapia dichiarata "
                          f"in parte, il silenzio del motore non e' una "
                          f"rassicurazione.")
        return

    farmaci = mod_interazioni.carica_farmaci(farmaci_path)
    tabella = mod_interazioni.carica_interazioni(interazioni_path)
    orari = mod_interazioni.carica_orari(orari_path)

    # una gravita' scritta male non si declassa in silenzio: prima del
    # 21/10/2026 tutto cio' che non era esattamente "alta" diventava "media",
    # e un "Alta" maiuscolo perdeva il blocco
    ignote = sorted({(i["principio_attivo"], i["target"], i["gravita"])
                     for i in tabella if i["gravita"] not in GRAVITA_AMMESSE})
    for principio, target_i, grav in ignote:
        rilievi.blocca(5, "INTERAZIONE_GRAVITA_NON_RICONOSCIUTA",
                       f"tabella interazioni: gravita' '{grav}' non riconosciuta per "
                       f"{principio} / {target_i} (ammesse: alta, media, bassa)")
    # stessa famiglia: un tipo o un nutriente scritto male faceva sparire
    # l'interazione senza alcun avviso
    for i in tabella:
        etichetta = f"{i['principio_attivo']} / {i['tipo_target']} / {i['target']}"
        if i["tipo_target"] not in ("nutriente", "food_id"):
            rilievi.blocca(5, "INTERAZIONE_TIPO_NON_RICONOSCIUTO",
                           f"tabella interazioni: tipo_target non riconosciuto in "
                           f"{etichetta} (ammessi: nutriente, food_id)")
        elif i["tipo_target"] == "nutriente" and i["target"] not in NUTRIENTI_PER_100G:
            rilievi.blocca(5, "INTERAZIONE_NUTRIENTE_NON_RICONOSCIUTO",
                           f"tabella interazioni: nutriente non riconosciuto in "
                           f"{etichetta} (deve essere una colonna di alimenti.csv, "
                           f"es. calcio_mg)")
        elif i["tipo_target"] == "food_id" and i["target"] not in db:
            rilievi.segnala(5, "INTERAZIONE_FOOD_ID_ASSENTE",
                            f"tabella interazioni: {etichetta}: food_id assente dal "
                            f"database, l'interazione non puo' scattare")

    allerte, coperture_mancanti = mod_interazioni.verifica_interazioni(
        piano, db, farmaci, tabella, orari)

    if coperture_mancanti:
        print("\n  ⚠️ Principi attivi in terapia SENZA righe in tabella:")
        for f in coperture_mancanti:
            print(f"     - {f['principio_attivo']} ({f['nome_commerciale']})")
        print("     L'assenza di allerta non e' assenza di rischio: verifica")
        print("     clinica manuale a carico del nutrizionista.")
        rilievi.segnala(5, "PRINCIPIO_ATTIVO_NON_COPERTO", f"{len(coperture_mancanti)} principio/i attivo/i "
                           f"non coperto/i dalla tabella interazioni: "
                           f"{', '.join(f['principio_attivo'] for f in coperture_mancanti)}")

    orari_mancanti = [a for a in allerte if a["tipo"] == "ORARIO_MANCANTE"]
    for m in orari_mancanti:
        print(f"\n  ⚠️ Giorno {m['giorno']} / {m['pasto']}: {m['messaggio']}")
        rilievi.blocca(5, "ORARIO_PASTO_MANCANTE", f"giorno {m['giorno']}, {m['pasto']}: orario del "
                          f"pasto non definito, separazioni temporali non "
                          f"verificabili")

    violazioni = [a for a in allerte if a["tipo"] == "INTERAZIONE"]
    if not violazioni:
        print("\n  Nessuna violazione di separazione temporale sulle "
              "interazioni presenti in tabella.")
    else:
        ordine = {"alta": 0, "media": 1, "bassa": 2}
        violazioni.sort(key=lambda a: (a["giorno"], ordine.get(a["gravita"], 9)))
        for a in violazioni:
            print(f"\n  ⚠️ GIORNO {a['giorno']} - {a['pasto'].upper()} "
                  f"(ore {a['orario_pasto']}) vs {a['farmaco']} "
                  f"(ore {a['orario_farmaco']}) - gravita' {a['gravita']}")
            print(f"     {a['meccanismo']}")
            print(f"     separazione richiesta {a['separazione_richiesta']}h, "
                  f"distanza reale {a['distanza_reale']:.1f}h - {a['dettaglio']}")
            testo = (f"giorno {a['giorno']}, {a['pasto']}: {a['principio_attivo']} "
                     f"a {a['distanza_reale']:.1f}h invece di "
                     f"{a['separazione_richiesta']}h ({a['gravita']})")
            if a["gravita"] == "alta":
                rilievi.blocca(5, "INTERAZIONE_GRAVITA_ALTA", testo)
            elif a["gravita"] == "media":
                rilievi.segnala(5, "INTERAZIONE_GRAVITA_MEDIA", testo)
            elif a["gravita"] == "bassa":
                rilievi.segnala(5, "INTERAZIONE_GRAVITA_BASSA", testo)
            # gravita' non riconosciuta: gia' bloccata sopra, riga per riga


# --------------------------------------------------------------------------
# PASSO 6 - un solo livello colazione/spuntino per tutto il piano
# --------------------------------------------------------------------------

def firma_pasto(righe_giorno, pasto):
    """Firma strutturale di un pasto in un giorno.

    Include food_id, grammatura, gruppo di scelta e opzione: due giorni hanno
    la stessa firma solo se offrono ESATTAMENTE le stesse alternative con le
    stesse grammature. Ordinata, quindi indipendente dall'ordine delle righe
    nel CSV.
    """
    righe = [r for r in righe_giorno if r["pasto"] == pasto]
    if not righe:
        return None
    return tuple(sorted(
        (r["gruppo_scelta"], r["opzione"], r["food_id"], round(r["grammi"], 3))
        for r in righe))


def descrivi_firma(firma, db):
    if firma is None:
        return "assente"
    opzioni = defaultdict(list)
    for gruppo, opzione, fid, grammi in firma:
        etichetta = opzione or "fisso"
        nome = db[fid]["nome"] if fid in db else fid
        opzioni[etichetta].append(f"{nome} {formatta_num(grammi)}g")
    return " | ".join(f"[{k}] {', '.join(v)}" for k, v in sorted(opzioni.items()))


def passo_6_livello_unico(rilievi, righe_estese, db, deroga):
    titolo(6, "LIVELLO UNICO DI COLAZIONE E SPUNTINO SU TUTTO IL PIANO")
    print("\n  La scelta tra livello standard e livello rinforzato e' UNA SOLA")
    print("  DECISIONE PER L'INTERO PIANO, mai giorno per giorno. Le 4")
    print("  colazioni e i 2 spuntini sono gli STESSI per tutti i giorni")
    print("  strutturati: il paziente sceglie ogni giorno tra le stesse")
    print("  alternative, non gli si assegna una colazione per calendario.")
    print("\n  Verifica strutturale: la composizione di colazione e spuntino")
    print("  deve essere identica su tutti i giorni strutturati del piano.")

    per_giorno = defaultdict(list)
    for r in righe_estese:
        per_giorno[r["giorno"]].append(r)

    if deroga:
        print(f"\n  DEROGA DICHIARATA: {deroga}")
        print("  I rilievi di questo passo restano visibili ma non bloccano.")

    for pasto in pasti_strutturati(righe_estese):
        firme = {g: firma_pasto(righe, pasto) for g, righe in per_giorno.items()}
        gruppi = defaultdict(list)
        for giorno, f in firme.items():
            gruppi[f].append(giorno)

        presenti = {f: g for f, g in gruppi.items() if f is not None}
        assenti = gruppi.get(None, [])

        print(f"\n  --- {pasto.upper()} ---")

        if not presenti:
            print(f"    Nessun giorno del piano definisce un {pasto}: "
                  f"struttura uniforme (assenza su tutti i giorni).")
            rilievi.segnala(6, "PASTO_ASSENTE_SU_TUTTO_IL_PIANO", f"{pasto} assente su tutto il piano: uniforme, "
                               f"ma va confermato che sia una deroga voluta "
                               f"(es. spuntino dichiarato come saltato)")
            continue

        if len(presenti) == 1 and not assenti:
            firma = next(iter(presenti))
            giorni = sorted(presenti[firma])
            n_opzioni = len({o for _, o, _, _ in firma if o}) or 1
            print(f"    Un solo livello su tutti i {len(giorni)} giorni "
                  f"({n_opzioni} alternativa/e).")
            print(f"    {descrivi_firma(firma, db)}")
            continue

        # da qui in poi: struttura NON uniforme
        if assenti:
            print(f"    Giorni SENZA {pasto}: {', '.join(sorted(assenti))}")
        for i, (firma, giorni) in enumerate(sorted(presenti.items(),
                                                   key=lambda kv: sorted(kv[1])), 1):
            print(f"    Struttura {i} - giorni {', '.join(sorted(giorni))}:")
            print(f"      {descrivi_firma(firma, db)}")

        parti = []
        if len(presenti) > 1:
            parti.append(f"{len(presenti)} strutture diverse su giorni diversi")
        if assenti:
            parti.append(f"assente su {len(assenti)} giorno/i "
                         f"({', '.join(sorted(assenti))}) e presente sugli altri")
        messaggio = (f"{pasto} non uniforme sul piano: " + "; ".join(parti)
                     + ". La decisione standard-vs-rinforzata e' a livello di "
                       "intero piano, non di singolo giorno. Se l'anomalia e' "
                       "una deroga voluta (giorno libero, spuntino saltato), "
                       "dichiararla con --deroga-struttura.")
        print(f"\n    ⛔ {messaggio}")
        if deroga:
            rilievi.segnala(6, "STRUTTURA_NON_UNIFORME_IN_DEROGA", messaggio + f" [deroga dichiarata: {deroga}]")
        else:
            rilievi.blocca(6, "STRUTTURA_NON_UNIFORME", messaggio)

    _identifica_livelli(rilievi, per_giorno, db, deroga)


def firme_alternative(righe_giorno, pasto):
    """Insieme delle alternative offerte da un pasto, ciascuna come insieme
    di (food_id, grammi). Confrontabile con il catalogo colazioni_spuntini.csv.

    Un pasto senza gruppo_scelta offre una sola alternativa: tutti i suoi
    ingredienti insieme.
    """
    righe = [r for r in righe_giorno if r["pasto"] == pasto]
    if not righe:
        return set()
    per_opzione = defaultdict(list)
    for r in righe:
        per_opzione[(r["gruppo_scelta"], r["opzione"])].append(
            (r["food_id"], round(r["grammi"], 3)))
    return {frozenset(v) for v in per_opzione.values()}


def _identifica_livelli(rilievi, per_giorno, db, deroga):
    """Riconosce PER NOME il livello di colazione e spuntino, e verifica che
    sia lo stesso per i due pasti.

    Il controllo di uniformita' sopra vede solo se i giorni differiscono tra
    loro. Non vede una colazione del livello standard abbinata a uno spuntino
    del livello rinforzato: ogni giorno e' identico all'altro, quindi uniforme,
    ma il piano usa due livelli insieme. E' il caso che questo controllo
    aggiunge.
    """
    print("\n  --- RICONOSCIMENTO DEL LIVELLO ---")

    catalogo = struttura_pasti.carica_catalogo()
    if not catalogo:
        print("    Catalogo colazioni_spuntini.csv non trovato: il livello puo'")
        print("    essere verificato come unico, ma non identificato per nome.")
        rilievi.segnala(6, "CATALOGO_ASSENTE",
                        "colazioni_spuntini.csv non disponibile: il livello "
                        "(standard vs rinforzata_calcio) non e' stato "
                        "identificato, solo verificato come uniforme")
        return

    mancanti = struttura_pasti.food_id_mancanti(catalogo, db)
    if mancanti:
        elenco = ", ".join(f"{a}:{f}" for a, f in mancanti)
        print(f"    ⛔ Catalogo disallineato da alimenti.csv: {elenco}")
        rilievi.blocca(6, "CATALOGO_DISALLINEATO",
                       f"colazioni_spuntini.csv referenzia food_id assenti dal "
                       f"database: {elenco}")
        return

    esiti = {}
    tutte = [r for righe in per_giorno.values() for r in righe]
    for pasto in pasti_strutturati(tutte):
        firme = set()
        for righe in per_giorno.values():
            firme |= firme_alternative(righe, pasto)
        if not firme:
            print(f"    {pasto}: assente dal piano, nulla da identificare.")
            continue

        livello, esito, dettaglio = struttura_pasti.identifica_livello(
            firme, catalogo, pasto)
        esiti[pasto] = (livello, esito)

        if esito == "esatto":
            print(f"    {pasto}: livello {livello} - {dettaglio}")
        elif esito == "parziale":
            print(f"    {pasto}: livello {livello}, INCOMPLETO - {dettaglio}")
            rilievi.segnala(6, "LIVELLO_PARZIALE",
                            f"{pasto}: il piano offre solo parte delle "
                            f"alternative del livello {livello} - {dettaglio}. "
                            f"Il paziente ha meno scelta di quanto il "
                            f"protocollo preveda: confermare se e' voluto.")
        elif esito == "misto":
            print(f"    ⛔ {pasto}: alternative di livelli diversi - {dettaglio}")
            rilievi.blocca(6, "LIVELLO_MISTO",
                           f"{pasto}: le alternative offerte non appartengono "
                           f"tutte allo stesso livello - {dettaglio}")
        else:
            print(f"    {pasto}: fuori catalogo - {dettaglio}")
            rilievi.segnala(6, "LIVELLO_FUORI_CATALOGO",
                            f"{pasto}: alternative non presenti in "
                            f"colazioni_spuntini.csv ({dettaglio}). Non e' un "
                            f"errore - il piano puo' usare alternative "
                            f"costruite su misura - ma il livello non e' "
                            f"verificabile contro il protocollo.")

    livelli = {p: liv for p, (liv, _) in esiti.items() if liv}
    if len(set(livelli.values())) > 1:
        descrizione = ", ".join(f"{p} {liv}" for p, liv in sorted(livelli.items()))
        print(f"\n    ⛔ Colazione e spuntino appartengono a livelli diversi: "
              f"{descrizione}")
        messaggio = (f"il piano abbina livelli diversi tra i pasti "
                     f"({descrizione}). La scelta standard-vs-rinforzata vale "
                     f"per l'intero protocollo colazione+spuntino, non per un "
                     f"pasto alla volta: e' un'incoerenza che il controllo di "
                     f"uniformita' tra giorni non puo' vedere, perche' i "
                     f"giorni sono tutti uguali tra loro.")
        if deroga:
            rilievi.segnala(6, "LIVELLO_INCOERENTE_IN_DEROGA",
                            messaggio + f" [deroga dichiarata: {deroga}]")
        else:
            rilievi.blocca(6, "LIVELLO_INCOERENTE_TRA_PASTI", messaggio)
    elif len(livelli) == 2:
        livello = next(iter(set(livelli.values())))
        print(f"\n    Colazione e spuntino sono entrambi del livello {livello}.")
    elif len(livelli) > 2:
        livello = next(iter(set(livelli.values())))
        print(f"\n    Colazione, spuntino e secondo spuntino sono tutti del "
              f"livello {livello}.")


# --------------------------------------------------------------------------
# Verdetto finale
# --------------------------------------------------------------------------

def verdetto(rilievi):
    print(f"\n{'=' * 68}")
    print("VERDETTO")
    print("=" * 68)

    if rilievi.attenzioni:
        print(f"\n  DA DICHIARARE AL NUTRIZIONISTA ({len(rilievi.attenzioni)}):")
        for passo, codice, m in rilievi.attenzioni:
            print(f"    [PASSO {passo} · {codice}] {m}")

    if rilievi.bloccanti:
        print(f"\n  ⛔ RILIEVI BLOCCANTI ({len(rilievi.bloccanti)}):")
        for passo, codice, m in rilievi.bloccanti:
            print(f"    [PASSO {passo} · {codice}] {m}")
        print("\n  PIANO NON PRESENTABILE PER L'APPROVAZIONE.")
        print("  Risolvi i rilievi bloccanti e riesegui la pipeline.")
        return 1

    print("\n  Nessun rilievo bloccante.")
    print("  Il report e' utilizzabile per la tabella di approvazione")
    print("  (PASSO 6 del workflow piano alimentare).")
    print("\n  Resta fermo il gate: il motore propone e calcola,")
    print("  il nutrizionista decide. Questa non e' una validazione clinica.")
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Orchestratore del motore di calcolo - FASE 3")
    ap.add_argument("--piano", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--gap", default=os.path.join(BASE, "gap.csv"))
    ap.add_argument("--farmaci")
    ap.add_argument("--interazioni")
    ap.add_argument("--orari")
    ap.add_argument("--deroga-struttura", dest="deroga", default=None,
                    help="motivo clinico che autorizza una struttura pasti "
                         "non uniforme (PASSO 6): declassa il blocco ad "
                         "attenzione, ma il rilievo resta nel report")
    ap.add_argument("--salta-collaudo", action="store_true")
    ap.add_argument("--eccezione-etichetta", dest="eccezione_etichetta", default=None,
                    help="file con le sole voci da etichetta (colonne di alimenti.csv), "
                         "SOLO su richiesta del nutrizionista; non entrano nel database")
    args = ap.parse_args()

    print("=" * 68)
    print("PIPELINE DI VALUTAZIONE DEL PIANO - Studio Taglialatela")
    print("=" * 68)
    print(f"  piano:    {args.piano}")
    print(f"  target:   {args.target}")
    print(f"  alimenti: database ufficiale del motore"
          + (f" + eccezione etichetta {args.eccezione_etichetta}"
             if args.eccezione_etichetta else ""))

    rilievi = Rilievi()

    passo_0_collaudo(rilievi, args.salta_collaudo)
    if rilievi.bloccanti:
        return verdetto(rilievi)

    db, eccezioni, fermo = carica_database(rilievi, args.eccezione_etichetta)
    if fermo:
        return verdetto(rilievi)
    piano = carica_piano(args.piano)
    righe_estese = carica_piano_esteso(args.piano)
    target = carica_target(args.target)
    gap = carica_gap(args.gap)

    if controlla_food_id(rilievi, piano, db, gap, eccezioni):
        return verdetto(rilievi)

    if controlla_pasti_ammessi(rilievi, piano):
        return verdetto(rilievi)

    sottostime = nutrienti_sottostimati(piano, gap)
    giorni_con_scelte = {r["giorno"] for r in righe_estese if r["gruppo_scelta"]}

    dati_giorni = passo_1_calcolo(rilievi, piano, db, target, giorni_con_scelte)
    intervalli = passo_2_scenari(rilievi, righe_estese, db, target)
    verifica_settimanale(rilievi, dati_giorni, intervalli, target)
    passo_3_micronutrienti(rilievi, dati_giorni, intervalli, target,
                           sottostime, db)
    passo_4_coerenza(rilievi, db, target, piano, gap, sottostime,
                     righe_estese)
    passo_5_interazioni(rilievi, piano, db, args.farmaci, args.interazioni,
                        args.orari)
    passo_6_livello_unico(rilievi, righe_estese, db, args.deroga)

    return verdetto(rilievi)


if __name__ == "__main__":
    sys.exit(main())
