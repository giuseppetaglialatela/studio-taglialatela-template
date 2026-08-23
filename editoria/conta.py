#!/usr/bin/env python3
# Conteggio parole di corpo: esclude marcatori [Fxxx], titoli, formattazione MD.
import re, sys

def conta(testo):
    righe = []
    for r in testo.split("\n"):
        s = r.strip()
        if s.startswith("#"):      # titoli
            continue
        if s.startswith("---"):    # linee separatrici
            continue
        righe.append(r)
    t = "\n".join(righe)
    t = re.sub(r"\[F\d+\]", " ", t)          # marcatori
    t = re.sub(r"[*_`>]", " ", t)            # formattazione
    parole = [p for p in t.split() if re.search(r"[0-9A-Za-zÀ-ÿ]", p)]
    return len(parole)

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"{conta(open(p, encoding='utf-8').read()):>6}  {p}")
