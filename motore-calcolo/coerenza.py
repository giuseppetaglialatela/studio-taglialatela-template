#!/usr/bin/env python3
"""
Modulo controlli di coerenza - Studio Nutrizionale Taglialatela

Serve a intercettare errori nei DATI prima che si propaghino nei piani.
E' la risposta al rischio "se sbaglio una riga del database, sbagliano tutte
le diete e non me ne accorgo piu'".

CONTROLLI IMPLEMENTATI:

  A) Cross-check Atwater sul database alimenti
     Le kcal dichiarate dalla fonte (CREA/BDA) NON vengono mai sostituite dal
     calcolo 4/4/9 - restano quelle della fonte, come da protocollo.
     Il calcolo 4/4/9 viene usato solo come CONTROLLO: se lo scarto supera la
     soglia attesa, e' quasi sempre un errore di battitura, non una differenza
     di metodo. CREA usa il metodo Southgate, con scarto fisiologico noto del
     4-8%: la soglia di allarme e' quindi fissata al 12% (margine sopra il
     massimo fisiologico atteso).

  B) Coerenza interna dei target
     Le percentuali di macronutrienti dichiarate devono sommare a 100 (+/-1).

  C) Righe sospette nel database
     Alimenti con tutti i micronutrienti a zero: quasi sempre indicano una
     scheda compilata a meta', non un alimento realmente privo di micro.

  D) Verifica strutturale somma pasti = totale giorno
     Ridondante per costruzione, ma tenuta come test di regressione: se un
     domani il codice cambia, questo controllo se ne accorge.
"""

SOGLIA_ATWATER_PCT = 12.0  # sopra il 4-8% fisiologico del metodo Southgate

MICRO = ["calcio_mg", "ferro_mg", "vitamina_d_ug", "folati_ug",
         "vitamina_b12_ug", "zinco_mg", "magnesio_mg", "vitamina_c_mg"]


def check_atwater(db_alimenti):
    """A) Confronta kcal dichiarate vs ricalcolo 4/4/9 come controllo qualita'."""
    anomalie = []
    for fid, al in db_alimenti.items():
        kcal_dichiarate = al["kcal_100g"]
        kcal_atwater = (al["proteine_g"] * 4 + al["carboidrati_g"] * 4
                        + al["grassi_g"] * 9)
        if kcal_dichiarate == 0:
            if kcal_atwater > 5:
                anomalie.append({
                    "food_id": fid, "nome": al["nome"],
                    "kcal_dichiarate": kcal_dichiarate,
                    "kcal_atwater": kcal_atwater,
                    "scarto_pct": None,
                    "nota": "kcal dichiarate a zero ma macronutrienti presenti",
                })
            continue
        scarto_pct = (kcal_atwater - kcal_dichiarate) / kcal_dichiarate * 100
        if abs(scarto_pct) > SOGLIA_ATWATER_PCT:
            anomalie.append({
                "food_id": fid, "nome": al["nome"],
                "kcal_dichiarate": kcal_dichiarate,
                "kcal_atwater": kcal_atwater,
                "scarto_pct": scarto_pct,
                "nota": "scarto oltre il margine fisiologico Southgate "
                        "(4-8%): probabile errore di trascrizione",
            })
    return anomalie


def check_target(target):
    """B) Le percentuali macro dichiarate devono sommare a 100."""
    problemi = []
    chiavi = ["proteine_pct_target", "carboidrati_pct_target", "grassi_pct_target"]
    presenti = [k for k in chiavi if k in target]
    if len(presenti) == 3:
        somma = sum(target[k] for k in chiavi)
        if abs(somma - 100.0) > 1.0:
            problemi.append(
                f"Le percentuali macro target sommano a {somma:.1f}% invece di 100%"
            )
    elif presenti:
        problemi.append(
            f"Target macro incompleti: definiti solo {', '.join(presenti)}"
        )
    if "kcal_target" in target and target["kcal_target"] <= 0:
        problemi.append("kcal_target non valido (<= 0)")
    return problemi


def check_righe_sospette(db_alimenti):
    """C) Alimenti con tutti i micronutrienti a zero = scheda incompleta."""
    sospetti = []
    for fid, al in db_alimenti.items():
        if all(al.get(m, 0.0) == 0.0 for m in MICRO):
            sospetti.append({"food_id": fid, "nome": al["nome"]})
    return sospetti


def check_somma_pasti(totali_per_pasto, totale_giorno, nutrienti):
    """D) Test di regressione: somma dei pasti == totale giorno."""
    discrepanze = []
    for n in nutrienti:
        somma = sum(tp[n] for tp in totali_per_pasto)
        atteso = totale_giorno[n]
        if abs(somma - atteso) > 0.001:
            discrepanze.append(
                f"{n}: somma pasti {somma:.4f} != totale giorno {atteso:.4f}"
            )
    return discrepanze


def stampa_report_coerenza(db_alimenti, target):
    print(f"\n{'='*60}\nCONTROLLI DI COERENZA E QUALITA' DATI\n{'='*60}")

    anomalie = check_atwater(db_alimenti)
    print(f"\n  A) Cross-check kcal dichiarate vs 4/4/9 "
          f"(soglia allarme {SOGLIA_ATWATER_PCT}%):")
    if not anomalie:
        print("     Nessuna anomalia: tutti gli alimenti entro il margine atteso.")
    else:
        for a in anomalie:
            print(f"     ⚠️ {a['food_id']} - {a['nome']}")
            print(f"        dichiarate: {a['kcal_dichiarate']:.0f} kcal | "
                  f"ricalcolo 4/4/9: {a['kcal_atwater']:.0f} kcal", end="")
            if a["scarto_pct"] is not None:
                print(f" | scarto: {a['scarto_pct']:+.1f}%")
            else:
                print()
            print(f"        {a['nota']}")
        print("\n     NOTA: le kcal restano quelle della fonte. Questo controllo")
        print("     segnala solo dove verificare la trascrizione.")

    problemi = check_target(target)
    print(f"\n  B) Coerenza interna dei target:")
    if not problemi:
        print("     Target coerenti.")
    else:
        for p in problemi:
            print(f"     ⚠️ {p}")

    sospetti = check_righe_sospette(db_alimenti)
    print(f"\n  C) Righe con tutti i micronutrienti a zero:")
    if not sospetti:
        print("     Nessuna riga sospetta.")
    else:
        for s in sospetti:
            print(f"     ⚠️ {s['food_id']} - {s['nome']}: "
                  f"probabile scheda incompleta, verificare la fonte")
