#!/usr/bin/env python3
"""
Modulo stima TDEE - Studio Nutrizionale Taglialatela

Calcola una PROPOSTA di TDEE e di target.csv di partenza dai dati del
fascicolo paziente. Il valore resta sempre da confermare dal nutrizionista:
questo modulo non decide il piano, propone un punto di partenza.

Formula: Mifflin-St Jeor (la piu' validata su popolazione generale).
    Uomo:  BMR = 10*peso_kg + 6.25*altezza_cm - 5*eta_anni + 5
    Donna: BMR = 10*peso_kg + 6.25*altezza_cm - 5*eta_anni - 161

Fattori di attivita' (PAL) standard:
    sedentario        1.20
    leggero           1.375
    moderato          1.55
    intenso           1.725
    molto_intenso     1.90
"""

from larn import riferimenti as riferimenti_larn

PAL = {
    "sedentario": 1.20,
    "leggero": 1.375,
    "moderato": 1.55,
    "intenso": 1.725,
    "molto_intenso": 1.90,
}


def calcola_bmr(peso_kg, altezza_cm, eta_anni, sesso):
    base = 10 * peso_kg + 6.25 * altezza_cm - 5 * eta_anni
    if sesso.upper() == "M":
        return base + 5
    elif sesso.upper() == "F":
        return base - 161
    else:
        raise ValueError("sesso deve essere 'M' o 'F'")


def proponi_tdee(peso_kg, altezza_cm, eta_anni, sesso, livello_attivita):
    if livello_attivita not in PAL:
        raise ValueError(f"livello_attivita deve essere uno tra: {list(PAL)}")
    bmr = calcola_bmr(peso_kg, altezza_cm, eta_anni, sesso)
    tdee = bmr * PAL[livello_attivita]
    return {
        "bmr_kcal": round(bmr, 1),
        "fattore_attivita": PAL[livello_attivita],
        "tdee_stimato_kcal": round(tdee, 1),
        "formula": "Mifflin-St Jeor",
        "nota": "Valore di partenza da confermare dal nutrizionista in base a "
                "obiettivo (mantenimento/deficit/surplus) e quadro clinico. "
                "Non sostituisce la valutazione clinica.",
    }


def proponi_target_csv(tdee_kcal, tipo_piano, proteine_pct, carboidrati_pct,
                       grassi_pct, fibra_g_target, sesso=None, eta_anni=None,
                       condizione="nessuna", larn=None):
    """
    tipo_piano: 'mantenimento' | 'deficit_lieve' (-15%) | 'deficit_moderato' (-25%)
                | 'surplus_lieve' (+10%)
    I LARN si leggono da larn.csv per sesso, eta' e condizione (nessuna |
    menopausa | gravidanza | allattamento). Non esistono valori di default:
    senza sesso ed eta' il modulo si ferma. Con larn={...} si possono forzare
    singoli valori (uso clinico motivato), ma restano sovrascritture esplicite.
    Restituisce le righe pronte per target.csv (il nutrizionista conferma
    prima di salvare).
    """
    fattori = {
        "mantenimento": 1.0,
        "deficit_lieve": 0.85,
        "deficit_moderato": 0.75,
        "surplus_lieve": 1.10,
    }
    if tipo_piano not in fattori:
        raise ValueError(f"tipo_piano deve essere uno tra: {list(fattori)}")
    kcal_piano = round(tdee_kcal * fattori[tipo_piano])

    valori_larn, nota_larn = riferimenti_larn(sesso, eta_anni, condizione)
    if larn:
        valori_larn = dict(valori_larn)
        valori_larn.update(larn)

    righe = {
        "kcal_target": kcal_piano,
        "proteine_pct_target": proteine_pct,
        "carboidrati_pct_target": carboidrati_pct,
        "grassi_pct_target": grassi_pct,
        "fibra_g_target": fibra_g_target,
        **valori_larn,
    }
    return righe


def autotest():
    # Verifica con il paziente fittizio P00 (36 anni, M, 180cm, 75kg, sedentario)
    r = proponi_tdee(75, 180, 36, "M", "sedentario")
    print("TDEE proposto:", r)
    assert abs(r["tdee_stimato_kcal"] - 2040) < 1, "Non coincide col TDEE gia' approvato per il paziente fittizio P00"
    t = proponi_target_csv(r["tdee_stimato_kcal"], "mantenimento", 22, 48, 30, 30,
                           sesso="M", eta_anni=36)
    print("Target proposto:", t)
    assert t["larn_vitamina_b12_ug"] == 4.0, "LARN non letti dalla tabella V revisione"
    try:
        proponi_target_csv(2000, "mantenimento", 22, 48, 30, 30)
    except ValueError:
        print("OK: senza sesso ed eta' il modulo si ferma invece di usare default.")
    else:
        raise AssertionError("avrebbe dovuto fermarsi senza sesso ed eta'")
    print("\nVerifica OK: coincide con il TDEE 2040 kcal gia' confermato manualmente per il paziente fittizio P00.")
    return 0


TIPI_PIANO = ("mantenimento", "deficit_lieve", "deficit_moderato", "surplus_lieve")


def main(argv=None):
    """Riga di comando (23/10/2026). Prima `--help` eseguiva la demo sul paziente
    fittizio: ora la demo e' --autotest e senza dati il modulo si ferma (nucleo,
    sezione 6: mai valori di default)."""
    import argparse, csv, sys
    ap = argparse.ArgumentParser(
        description="PROPOSTA di TDEE (Mifflin-St Jeor + PAL) e, con --piano, di target.csv. "
                    "Sempre da confermare dal nutrizionista.")
    ap.add_argument("--autotest", action="store_true",
                    help="verifica sul paziente fittizio (2040 kcal); nessun altro argomento")
    ap.add_argument("--peso", type=float, help="kg")
    ap.add_argument("--altezza", type=float, help="cm")
    ap.add_argument("--eta", type=int, help="anni")
    ap.add_argument("--sesso", type=str.upper, choices=("M", "F"))
    ap.add_argument("--attivita", choices=tuple(PAL),
                    help="chiave del Form A (livello_attivita_dichiarato)")
    ap.add_argument("--piano", choices=TIPI_PIANO, help="con --piano propone anche target.csv")
    ap.add_argument("--proteine", type=float, help="%% kcal")
    ap.add_argument("--carboidrati", type=float, help="%% kcal")
    ap.add_argument("--grassi", type=float, help="%% kcal")
    ap.add_argument("--fibra", type=float, help="g/die")
    ap.add_argument("--condizione",
                    help="solo con --piano: nessuna (predefinita) | menopausa | gravidanza | "
                         "allattamento (larn.csv)")
    ap.add_argument("--tdee-confermato", dest="tdee_confermato", type=float,
                    help="kcal: target calcolato sul TDEE gia' confermato invece che sulla stima")
    ap.add_argument("--out", help="scrive la proposta di target.csv in questo file")
    a = ap.parse_args(argv)

    if a.autotest:
        altri = [k for k, v in vars(a).items() if k != "autotest" and v is not None]
        if altri:
            ap.error("--autotest non si combina con i dati di un paziente")
        return autotest()
    mancanti = [f"--{n}" for n in ("peso", "altezza", "eta", "sesso", "attivita")
                if getattr(a, n) is None]
    if mancanti:
        ap.error("dati mancanti: " + ", ".join(mancanti)
                 + " (si chiedono, mai valori di default; la demo e' --autotest)")
    # plausibilita', come i limiti del Form A; Mifflin-St Jeor e' validata sugli adulti
    for nome, v, lo, hi in (("peso", a.peso, 30, 300), ("altezza", a.altezza, 120, 220),
                            ("eta", a.eta, 18, 100)):
        if not lo <= v <= hi:
            ap.error(f"--{nome} {v:g} fuori dal campo ammesso ({lo}-{hi})")
    if a.tdee_confermato is not None and not 800 <= a.tdee_confermato <= 6000:
        ap.error(f"--tdee-confermato {a.tdee_confermato:g} fuori dal campo ammesso (800-6000)")
    if a.out and not a.piano:
        ap.error("--out richiede --piano")
    if a.condizione is not None and not a.piano:
        ap.error("--condizione serve solo con --piano (sceglie i LARN del target)")
    condizione = a.condizione or "nessuna"
    if a.piano:
        try:                     # LARN controllati PRIMA di stampare qualunque risultato
            riferimenti_larn(a.sesso, a.eta, condizione)
        except ValueError as e:
            ap.error(str(e))
    if a.out:
        import os
        if os.path.exists(a.out):
            ap.error(f"{a.out} esiste gia': scegliere un altro nome (non si sovrascrive)")
        if not os.path.isdir(os.path.dirname(os.path.abspath(a.out))):
            ap.error(f"cartella di {a.out} inesistente")
    macro = [a.proteine, a.carboidrati, a.grassi, a.fibra]
    if a.piano and None in macro:
        ap.error("con --piano servono --proteine, --carboidrati, --grassi e --fibra")
    if a.piano and abs(a.proteine + a.carboidrati + a.grassi - 100) > 0.5:
        ap.error(f"proteine + carboidrati + grassi = "
                 f"{a.proteine + a.carboidrati + a.grassi:g}%, non 100%")
    if not a.piano and any(v is not None for v in macro + [a.tdee_confermato]):
        ap.error("--proteine, --carboidrati, --grassi, --fibra e --tdee-confermato "
                 "servono solo con --piano")

    try:
        r = proponi_tdee(a.peso, a.altezza, a.eta, a.sesso, a.attivita)
    except ValueError as e:
        ap.error(str(e))
    print(f"BMR (Mifflin-St Jeor): {r['bmr_kcal']:g} kcal")
    print(f"Fattore di attivita' ({a.attivita}): {r['fattore_attivita']:g}")
    fuori_campo = not 800 <= r["tdee_stimato_kcal"] <= 6000
    if fuori_campo and a.piano and a.tdee_confermato is None:
        ap.error(f"TDEE stimato {r['tdee_stimato_kcal']:g} kcal fuori dal campo ammesso "
                 f"(800-6000): per un target serve --tdee-confermato")
    print(f"TDEE STIMATO: {r['tdee_stimato_kcal']:g} kcal - PROPOSTA da confermare")
    if fuori_campo:
        print("AVVISO: stima fuori dal campo 800-6000 kcal, da rivedere prima di usarla")
    if not a.piano:
        return 0
    base = a.tdee_confermato if a.tdee_confermato is not None else r["tdee_stimato_kcal"]
    try:
        t = proponi_target_csv(base, a.piano, a.proteine, a.carboidrati, a.grassi, a.fibra,
                               sesso=a.sesso, eta_anni=a.eta, condizione=condizione)
    except ValueError as e:
        ap.error(str(e))
    print(f"\nProposta di target.csv ({a.piano}, su TDEE "
          f"{'confermato' if a.tdee_confermato is not None else 'STIMATO'} {base:g} kcal):")
    print("parametro,valore")
    for k, v in t.items():
        print(f"{k},{v:g}" if isinstance(v, (int, float)) else f"{k},{v}")
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["parametro", "valore"])
            for k, v in t.items():
                w.writerow([k, f"{v:g}" if isinstance(v, (int, float)) else v])
        print(f"\nScritto {a.out}: e' una proposta, si usa solo dopo la conferma.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
