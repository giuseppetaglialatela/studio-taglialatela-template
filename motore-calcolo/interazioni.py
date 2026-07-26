#!/usr/bin/env python3
"""
Modulo interazioni farmaco-alimento - Studio Nutrizionale Taglialatela

PRINCIPIO DI PROGETTAZIONE:
Questo modulo NON contiene conoscenza farmacologica propria. Si limita a
incrociare in modo deterministico:
  - farmaci_paziente.csv (terapia in corso, con orario di assunzione)
  - interazioni.csv      (tabella curata e validata dal nutrizionista)
  - orari_pasti.csv      (orario di ogni pasto del piano)
  - composizione del piano (dal calcolatore)

Se un'interazione non e' presente in interazioni.csv, il motore NON la
segnala e NON la inventa: resta a carico della verifica clinica manuale.
Il modulo segnala esplicitamente quali principi attivi in terapia non hanno
alcuna riga nella tabella, cosi' che l'assenza di allarme non venga scambiata
per assenza di rischio.

SCHEMI:
farmaci_paziente.csv: principio_attivo, nome_commerciale, orario_assunzione, note
interazioni.csv:      principio_attivo, tipo_target, target, meccanismo,
                      separazione_ore, gravita
                      tipo_target: "nutriente" | "food_id"
orari_pasti.csv:      giorno, pasto, orario   (formato HH:MM)
"""

import csv
from datetime import datetime


def _ora(hhmm):
    return datetime.strptime(hhmm.strip(), "%H:%M")


def _distanza_ore(ora_a, ora_b):
    """Distanza assoluta in ore tra due orari nella stessa giornata."""
    delta = abs((_ora(ora_a) - _ora(ora_b)).total_seconds()) / 3600.0
    return delta


def carica_farmaci(path):
    farmaci = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            farmaci.append({
                "principio_attivo": row["principio_attivo"].strip(),
                "nome_commerciale": row.get("nome_commerciale", "").strip(),
                "orario_assunzione": row["orario_assunzione"].strip(),
                "note": row.get("note", "").strip(),
            })
    return farmaci


def carica_interazioni(path):
    inter = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inter.append({
                "principio_attivo": row["principio_attivo"].strip(),
                "tipo_target": row["tipo_target"].strip(),
                "target": row["target"].strip(),
                "meccanismo": row["meccanismo"].strip(),
                "separazione_ore": float(row["separazione_ore"]),
                "gravita": row["gravita"].strip(),
            })
    return inter


def carica_orari(path):
    orari = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            orari[(row["giorno"].strip(), row["pasto"].strip())] = row["orario"].strip()
    return orari


def verifica_interazioni(piano_righe, db_alimenti, farmaci, interazioni, orari,
                         soglia_nutriente_rilevante=None):
    """
    Restituisce (allerte, coperture_mancanti).

    allerte: lista di dict con giorno, pasto, farmaco, meccanismo, gravita,
             distanza reale e separazione richiesta.
    coperture_mancanti: principi attivi in terapia senza righe in tabella.
    """
    if soglia_nutriente_rilevante is None:
        # sotto queste quantita' per pasto il contributo e' considerato
        # trascurabile ai fini dell'interazione (soglie prudenziali,
        # modificabili dal nutrizionista)
        soglia_nutriente_rilevante = {"calcio_mg": 50.0, "ferro_mg": 1.0}

    # raggruppa il piano per (giorno, pasto)
    per_pasto = {}
    for r in piano_righe:
        per_pasto.setdefault((r["giorno"], r["pasto"]), []).append(r)

    allerte = []
    for (giorno, pasto), righe in per_pasto.items():
        orario_pasto = orari.get((giorno, pasto))
        if orario_pasto is None:
            allerte.append({
                "tipo": "ORARIO_MANCANTE",
                "giorno": giorno, "pasto": pasto,
                "messaggio": "Orario del pasto non definito: impossibile "
                             "verificare le separazioni temporali.",
            })
            continue

        # calcola contenuto del pasto per nutriente e food_id presenti
        contenuto_nutrienti = {}
        food_ids = set()
        for r in righe:
            al = db_alimenti[r["food_id"]]
            food_ids.add(r["food_id"])
            fattore = r["grammi"] / 100.0
            for k, v in al.items():
                if k == "nome":
                    continue
                contenuto_nutrienti[k] = contenuto_nutrienti.get(k, 0.0) + v * fattore

        for farmaco in farmaci:
            distanza = _distanza_ore(orario_pasto, farmaco["orario_assunzione"])
            for inter in interazioni:
                if inter["principio_attivo"] != farmaco["principio_attivo"]:
                    continue
                if distanza >= inter["separazione_ore"]:
                    continue  # separazione gia' rispettata

                colpito = False
                dettaglio = ""
                if inter["tipo_target"] == "nutriente":
                    quantita = contenuto_nutrienti.get(inter["target"], 0.0)
                    soglia = soglia_nutriente_rilevante.get(inter["target"], 0.0)
                    if quantita > soglia:
                        colpito = True
                        dettaglio = f"{inter['target']} nel pasto: {quantita:.1f}"
                elif inter["tipo_target"] == "food_id":
                    if inter["target"] in food_ids:
                        colpito = True
                        dettaglio = f"alimento presente: {db_alimenti[inter['target']]['nome']}"

                if colpito:
                    allerte.append({
                        "tipo": "INTERAZIONE",
                        "giorno": giorno,
                        "pasto": pasto,
                        "orario_pasto": orario_pasto,
                        "farmaco": farmaco["nome_commerciale"] or farmaco["principio_attivo"],
                        "principio_attivo": farmaco["principio_attivo"],
                        "orario_farmaco": farmaco["orario_assunzione"],
                        "meccanismo": inter["meccanismo"],
                        "gravita": inter["gravita"],
                        "separazione_richiesta": inter["separazione_ore"],
                        "distanza_reale": distanza,
                        "dettaglio": dettaglio,
                    })

    # principi attivi senza copertura in tabella
    coperti = {i["principio_attivo"] for i in interazioni}
    coperture_mancanti = [
        f for f in farmaci if f["principio_attivo"] not in coperti
    ]

    return allerte, coperture_mancanti


def stampa_report_interazioni(allerte, coperture_mancanti):
    print(f"\n{'='*60}\nINTERAZIONI FARMACO-ALIMENTO\n{'='*60}")

    if coperture_mancanti:
        print("\n  ATTENZIONE - principi attivi senza righe in tabella interazioni.")
        print("  L'assenza di allerta NON significa assenza di rischio:")
        for f in coperture_mancanti:
            print(f"    - {f['principio_attivo']} "
                  f"({f['nome_commerciale']}) -> verifica clinica manuale")

    inter = [a for a in allerte if a["tipo"] == "INTERAZIONE"]
    mancanti = [a for a in allerte if a["tipo"] == "ORARIO_MANCANTE"]

    for m in mancanti:
        print(f"\n  ⚠️ Giorno {m['giorno']} / {m['pasto']}: {m['messaggio']}")

    if not inter:
        print("\n  Nessuna violazione di separazione temporale rilevata "
              "sulle interazioni presenti in tabella.")
    else:
        ordine_gravita = {"alta": 0, "media": 1, "bassa": 2}
        inter.sort(key=lambda a: (a["giorno"],
                                  ordine_gravita.get(a["gravita"], 9)))
        for a in inter:
            simbolo = "⚠️" if a["gravita"] in ("alta", "media") else "•"
            print(f"\n  {simbolo} GIORNO {a['giorno']} - {a['pasto'].upper()} "
                  f"(ore {a['orario_pasto']}) vs {a['farmaco']} "
                  f"(ore {a['orario_farmaco']})")
            print(f"     Gravita': {a['gravita']}")
            print(f"     Meccanismo: {a['meccanismo']}")
            print(f"     Separazione richiesta: {a['separazione_richiesta']}h | "
                  f"distanza reale: {a['distanza_reale']:.1f}h")
            print(f"     {a['dettaglio']}")
