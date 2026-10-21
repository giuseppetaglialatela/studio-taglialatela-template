#!/usr/bin/env python3
"""
Libreria dei blocchi pasto - Studio Nutrizionale Taglialatela

COSA E'
moduli_pasto.csv raccoglie blocchi di pranzo e cena riutilizzabili, estratti da
piani reali gia' consegnati. Sono una BASE DI PARTENZA da scalare, non un
sostituto del calcolo caso per caso: ogni blocco va ricalcolato col motore
dopo l'adattamento alle grammature del paziente.

PERCHE' IL FILE NON CONTIENE PIU' I VALORI NUTRIZIONALI
La prima versione portava kcal, macro, fibra, calcio e vitamina D precalcolati
accanto agli ingredienti. Il 29/07/2026 il ricalcolo ha trovato 165 valori su
168 corretti e tre sbagliati: la vitamina D di M18, M20 e M22 era dichiarata a
zero mentre il ricalcolo dava 0.13, 0.01 e 0.15 ug.

Quei tre valori NON erano errori di trascrizione: erano corretti il 27/07,
quando il file e' stato scritto, e sono diventati falsi il 28/07, quando la
vitamina D di gambero e polpo e' stata recuperata da USDA. La fonte e'
migliorata sotto il derivato, e nessuna rilettura del file lo avrebbe mai
rivelato - bisognava ricalcolare.

E' una via di divergenza diversa da quella del catalogo colazioni (dove S1 era
sbagliato dalla nascita) e piu' insidiosa, perche' non richiede alcun errore
umano per prodursi: basta che il database migliori.

Il file dichiara quindi solo gli ingredienti. I valori si ricalcolano sempre da
alimenti.csv, che e' la fonte.

SCHEMA - file affiancato, non fa parte dello schema congelato
moduli_pasto.csv
  modulo_id, nome, categoria, tag, ingredienti_food_id_grammi
  categoria: pranzo | cena
  tag: elenco separato da virgole (halal_ok, mensa_ok, vegetariano, legumi,
       pesce, carne, pratico). vitD, calcio e leggero NON si scrivono: si
       calcolano dai valori (vedi TAG_CALCOLATI); scritti a mano fanno fallire
       il collaudo
  ingredienti: "food_id:grammi;food_id:grammi;..."

USO
  python3 moduli_pasto.py                        tutta la libreria
  python3 moduli_pasto.py --categoria cena       solo le cene
  python3 moduli_pasto.py --tag pesce vitD       blocchi con TUTTI i tag
  python3 moduli_pasto.py --scala M07 1.15       grammature riscalate del 15%

COLAZIONI E SPUNTINI (21/10/2026)
moduli_colazione.csv ha lo stesso schema, con categoria colazione | spuntino e
tra i tag dolce | salata. E' una LIBRERIA di accoppiamenti, distinta dal
catalogo colazioni_spuntini.csv, che serve al motore per riconoscere il livello
standard/rinforzato e non va riempito di alternative.

AMPLIAMENTO - decisione del 21/10/2026
La libreria e' la raccolta degli ACCOPPIAMENTI VALIDI, estratta da tutti i
piani gia' fatti, per non ricomporre ogni volta pasti mal accoppiati. Il tetto
di 20-30 blocchi e' superato per decisione del nutrizionista: la consultazione
resta rapida coi filtri --categoria e --tag.
Un blocco nuovo entra solo se il suo NUCLEO non c'e' gia': il nucleo sono gli
alimenti portanti (proteine, cereali, patate, latticini, legumi, frutta secca,
dolci); verdura, frutta e condimenti si scambiano e non contano.
Nessun blocco puo' contenere un accoppiamento vietato
(accoppiamenti_vietati.csv): lo verifica il collaudo, controllo 8.
"""

import argparse
import csv
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
MODULI_DEFAULT = os.path.join(BASE, "moduli_pasto.csv")
COLAZIONI_DEFAULT = os.path.join(BASE, "moduli_colazione.csv")
CATEGORIE = ("colazione", "spuntino", "pranzo", "cena")

# Tag CALCOLATI (decisione del nutrizionista, 21/10/2026): non si scrivono nel
# file ma si ricavano a ogni esecuzione dai valori ricalcolati, come i
# nutrienti (principio 2). Scritti a mano erano incoerenti: un tonno con 24,5 ug
# di vitamina D senza tag vitD, uno sgombro con 3,2 ug con il tag.
# Valgono per pranzo e cena: le soglie sono state scelte su quei blocchi.
TAG_CALCOLATI = {
    "vitD": ("vitamina_d_ug", ">=", 5.0),     # un terzo del LARN adulto (15 ug)
    "calcio": ("calcio_mg", ">=", 300.0),     # circa un terzo del LARN (950 mg)
    "leggero": ("kcal_100g", "<=", 450.0),    # il quarto piu' leggero della libreria
}
CATEGORIE_TAG_CALCOLATI = ("pranzo", "cena")


def tag_calcolati(modulo, totali):
    """Tag ricavati dai valori del blocco (vedi TAG_CALCOLATI)."""
    if modulo["categoria"] not in CATEGORIE_TAG_CALCOLATI:
        return []
    fuori = []
    for tag, (nutriente, verso, soglia) in TAG_CALCOLATI.items():
        valore = totali[nutriente]
        if (valore >= soglia) if verso == ">=" else (valore <= soglia):
            fuori.append(tag)
    return fuori


def tag_calcolati_scritti(moduli):
    """Blocchi che riportano a mano un tag calcolato: e' un errore, perche'
    il tag scritto puo' divergere dai valori. Restituisce [(modulo_id, tag)]."""
    return [(m["modulo_id"], t) for m in moduli for t in m["tag"]
            if t in TAG_CALCOLATI]


def carica_moduli(path=None):
    """Senza path: libreria completa (pranzo/cena + colazioni/spuntini)."""
    if path is None:
        return (carica_moduli(MODULI_DEFAULT) + carica_moduli(COLAZIONI_DEFAULT))
    if not os.path.isfile(path):
        return []
    voci = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            voci.append({
                "modulo_id": row["modulo_id"].strip(),
                "nome": row["nome"].strip(),
                "categoria": row["categoria"].strip(),
                "tag": [t.strip() for t in row["tag"].split(",") if t.strip()],
                "ingredienti": _parse(row["ingredienti_food_id_grammi"]),
            })
    return voci


def _parse(testo):
    fuori = []
    for pezzo in testo.split(";"):
        pezzo = pezzo.strip()
        if not pezzo:
            continue
        fid, _, grammi = pezzo.partition(":")
        fuori.append((fid.strip(), float(grammi)))
    return fuori


def valori(db, ingredienti, fattore=1.0):
    """Ricalcola i nutrienti del blocco da alimenti.csv, con scala opzionale."""
    from calcolatore import calcola_riga, somma_nutrienti
    return somma_nutrienti([calcola_riga(db[fid], g * fattore)
                            for fid, g in ingredienti])


def gap_del_blocco(ingredienti, gap):
    """Nutrienti del blocco il cui totale e' SOTTOSTIMATO perche' pesca da
    voci con dati dichiarati mancanti in gap.csv.

    Senza questo, un blocco che riporta vitamina D 0.00 per un'orata (dato che
    CREA non pubblica) sembrerebbe privo di vitamina D invece che non misurato,
    e verrebbe scartato per la ragione sbagliata.
    """
    trovati = {}
    for fid, _ in ingredienti:
        for nutriente in gap.get(fid, {}):
            trovati.setdefault(nutriente, []).append(fid)
    return trovati


def food_id_mancanti(moduli, db):
    """food_id della libreria assenti dal database: e' un file affiancato e
    puo' disallinearsi da alimenti.csv senza che nulla lo veda."""
    return [(m["modulo_id"], fid) for m in moduli
            for fid, _ in m["ingredienti"] if fid not in db]


def _intestazione():
    print(f"  {'ID':<5} {'kcal':>6} {'P':>6} {'C':>6} {'G':>6} {'Fib':>5} "
          f"{'Ca':>6} {'vitD':>6}  nome")


def _riga(m, t, gap_voci=None):
    marca = ""
    if gap_voci:
        brevi = {"vitamina_d_ug": "vitD", "vitamina_b12_ug": "B12",
                 "folati_ug": "folati", "zinco_mg": "zinco"}
        marca = "  ⛔ sottostimati: " + ", ".join(
            brevi.get(n, n) for n in sorted(gap_voci))
    print(f"  {m['modulo_id']:<5} {t['kcal_100g']:>6.0f} {t['proteine_g']:>6.1f} "
          f"{t['carboidrati_g']:>6.1f} {t['grassi_g']:>6.1f} {t['fibra_g']:>5.1f} "
          f"{t['calcio_mg']:>6.0f} {t['vitamina_d_ug']:>6.2f}  {m['nome']}{marca}")


def main():
    from calcolatore import carica_alimenti, carica_gap

    ap = argparse.ArgumentParser(description="Libreria blocchi pasto")
    ap.add_argument("--categoria", choices=CATEGORIE)
    ap.add_argument("--tag", nargs="+", default=[],
                    help="mostra solo i blocchi che hanno TUTTI i tag indicati")
    ap.add_argument("--scala", nargs=2, metavar=("MODULO_ID", "FATTORE"),
                    help="stampa le grammature riscalate di un blocco")
    ap.add_argument("--alimenti", default=os.path.join(BASE, "alimenti.csv"))
    args = ap.parse_args()

    moduli = carica_moduli()
    if not moduli:
        print("moduli_pasto.csv non trovato o vuoto.")
        return 1
    db = carica_alimenti(args.alimenti)
    gap = carica_gap(os.path.join(BASE, "gap.csv"))

    scritti = tag_calcolati_scritti(moduli)
    if scritti:
        print("ERRORE: tag calcolati scritti a mano nella libreria "
              "(si ricavano dai valori, non si scrivono):")
        for mid, tag in scritti:
            print(f"  {mid}: {tag}")
        return 1

    mancanti = food_id_mancanti(moduli, db)
    if mancanti:
        print("ERRORE: food_id della libreria assenti da alimenti.csv:")
        for mid, fid in mancanti:
            print(f"  {mid}: {fid}")
        return 1

    if args.scala:
        mid, fattore = args.scala[0], float(args.scala[1])
        trovato = next((m for m in moduli if m["modulo_id"] == mid), None)
        if trovato is None:
            print(f"Modulo '{mid}' non trovato.")
            return 1
        print(f"\n{trovato['modulo_id']} - {trovato['nome']}  "
              f"(scala x{fattore})\n")
        for fid, g in trovato["ingredienti"]:
            print(f"  {db[fid]['nome']:<38} {g:>6.0f} g -> {g * fattore:>6.0f} g")
        print()
        _intestazione()
        _riga(trovato, valori(db, trovato["ingredienti"], fattore),
              gap_del_blocco(trovato["ingredienti"], gap))
        print("\n  Il blocco riscalato va comunque verificato nel piano "
              "completo:\n  questi numeri sono il punto di partenza, non "
              "l'approvazione.\n")
        return 0

    totali = {m["modulo_id"]: valori(db, m["ingredienti"]) for m in moduli}
    for m in moduli:
        m["tag"] = m["tag"] + tag_calcolati(m, totali[m["modulo_id"]])

    selezione = [m for m in moduli
                 if (not args.categoria or m["categoria"] == args.categoria)
                 and all(t in m["tag"] for t in args.tag)]

    print("=" * 78)
    print("LIBRERIA BLOCCHI PASTO - valori ricalcolati da alimenti.csv")
    print("=" * 78)
    print("I valori NON sono memorizzati: sono ricalcolati a ogni esecuzione.")
    print("Tag calcolati (pranzo e cena): vitD >= 5 ug, calcio >= 300 mg, "
          "leggero <= 450 kcal.")
    print("Il file dichiara solo gli ingredienti.\n")
    if args.categoria or args.tag:
        filtri = []
        if args.categoria:
            filtri.append(args.categoria)
        if args.tag:
            filtri.append("tag: " + ", ".join(args.tag))
        print(f"Filtro: {' | '.join(filtri)} -> {len(selezione)} blocchi su "
              f"{len(moduli)}\n")

    if not selezione:
        print("Nessun blocco corrisponde ai filtri.")
        tutti = sorted({t for m in moduli for t in m["tag"]})
        print(f"Tag disponibili: {', '.join(tutti)}")
        return 0

    for categoria in CATEGORIE:
        blocchi = [m for m in selezione if m["categoria"] == categoria]
        if not blocchi:
            continue
        print(f"--- {categoria.upper()} ---")
        _intestazione()
        for m in blocchi:
            _riga(m, totali[m["modulo_id"]],
                  gap_del_blocco(m["ingredienti"], gap))
            print(f"        tag: {', '.join(m['tag'])}")
        print()

    print("Sono una BASE DI PARTENZA da scalare, non un sostituto del calcolo")
    print("caso per caso: ogni blocco va ricalcolato nel piano del paziente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
