# Tabella degli alimenti

Generata da `tabella_alimenti.py --genera-pagina` dai CSV del motore: non si modifica a mano. Valori per 100 g di parte edibile. «n.d.» = dato mancante, dichiarato in `gap.csv`: non è uno zero.

**161 alimenti**, 18 valori mancanti su 8 alimenti.

## Valori mancanti

| Alimento | Nutriente | Motivo |
|---|---|---|
| Tacchino fesa cotta al forno (proxy fesa affettata) | epa_g | EPA/DHA non riportati dalla scheda BDA 8698_2: dato mancante, alimento di origine animale |
| Tacchino petto senza pelle | epa_g | EPA/DHA non riportati dalla scheda BDA 8697_2: dato mancante, alimento di origine animale |
| Trippa di bovini | folati_ug | folati presenti in quasi ogni alimento: dato non pubblicato dalla fonte |
| Trippa di bovini | vitamina_b12_ug | alimento di origine animale: zero implausibile, dato non pubblicato dalla fonte |
| Trippa di bovini | vitamina_d_ug | alimento di origine animale: zero implausibile, dato non pubblicato dalla fonte |
| Trippa di bovini | zinco_mg | minerale mai biologicamente assente in un alimento intero: dato non pubblicato dalla fonte |
| Latte parzialmente scremato | vitamina_b12_ug | alimento di origine animale: zero implausibile, dato non pubblicato dalla fonte |
| Latte parzialmente scremato | vitamina_d_ug | alimento di origine animale: zero implausibile, dato non pubblicato dalla fonte |
| Mozzarella di bufala | dha_g | EPA/DHA non riportati dalla scheda BDA 11796_2: dato mancante, alimento di origine animale |
| Mozzarella di bufala | epa_g | EPA/DHA non riportati dalla scheda BDA 11796_2: dato mancante, alimento di origine animale |
| Orata d'allevamento filetti | vitamina_d_ug | alimento di origine animale: zero implausibile, dato non pubblicato dalla fonte |
| Salmone affumicato | vitamina_d_ug | BDA-IEO dichiara traccia (0.005) su un pesce grasso; USDA riporta 17.1 ug ma con derivazione BFSN da altra forma dell alimento, dataPoints 0: valore probabilmente sottostimato, non usare come fonte portante |
| Sardine fresche | colesterolo_mg | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |
| Sardine fresche | dha_g | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |
| Sardine fresche | epa_g | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |
| Sardine fresche | monoinsaturi_g | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |
| Sardine fresche | polinsaturi_g | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |
| Sardine fresche | saturi_g | acidi grassi e colesterolo da INSA 882 (deroga INSA estesa agli acidi grassi, decisione del nutrizionista 31/10/2026): tabella non ancora acquisita |

## Altro

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Cioccolato fondente | 531 | 6,6 | 49,7 | 33,6 | 8 |
| Crema di nocciole e cacao | 537 | 6,9 | 58,1 | 32,4 | 3 |
| Miele | 304 | 0,6 | 80,3 | 0 | 0 |
| Olive verdi | 148 | 0,8 | 1 | 15 | 3 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cioccolato fondente | 51 | 5 | 0 | 12 | 0 | 1,3 | 89 | 0 |
| Crema di nocciole e cacao | 143 | 3,6 | 0,005 | 14 | 0,05 | 1 | 65 | 0 |
| Miele | 5 | 0,5 | 0 | 2 | 0 | 0,8 | 3 | 1 |
| Olive verdi | 64 | 1,6 | 0 | 0,5 | 0 | 0,4 | 11 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Cioccolato fondente | 20,59 | 11,08 | 1,41 | 0 | 0 | 0 |
| Crema di nocciole e cacao | 9,17 | 16,51 | 5,3 | 0 | 0 | 2 |
| Miele | 0 | 0 | 0 | 0 | 0 | 0 |
| Olive verdi | 2,1 | 10,47 | 1,68 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Cioccolato fondente | 203020 | CREA+BDA-IEO | 203020 | 2026-08-08 | BDA-IEO 2005_2 |
| Crema di nocciole e cacao | 203500 | CREA+BDA-IEO | 203500+2008_2 | 2026-10-21 | BDA-IEO 2008_2 |
| Miele | 210010 | CREA+BDA-IEO(proxy zinco/folati) | 210010 | 2026-07-26 | BDA-IEO 2017_2 |
| Olive verdi | 008820 | CREA+BDA-IEO(proxy zinco/folati)+USDA | 008820 | 2026-10-01 | BDA-IEO 590_1 |

## Carne

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Bovino adulto o vitellone filetto crudo | 127 | 20,5 | 0 | 5 | 0 |
| Bovino magro vitellone senza grasso visibile | 108 | 21,58 | 0 | 2,38 | 0 |
| Bresaola | 151 | 32 | 0 | 2,6 | 0 |
| Macinato di manzo magro (proxy: bovino adulto o vitellone tagli anteriori crudo) | 145 | 20,5 | 0 | 7 | 0 |
| Maiale lombo crudo | 146 | 20,7 | 0 | 7 | 0 |
| Pollo fuso (coscia) senza pelle crudo | 107 | 18,5 | 0 | 3,7 | 0 |
| Pollo petto crudo | 100 | 23,3 | 0 | 0,8 | 0 |
| Prosciutto cotto senza grasso visibile | 132 | 22,2 | 1 | 4,4 | 0 |
| Prosciutto crudo senza grasso visibile | 159 | 29,3 | 0 | 4,6 | 0 |
| Tacchino fesa cotta al forno (proxy fesa affettata) | 131 | 29,6 | 0 | 1,4 | 0 |
| Tacchino petto senza pelle | 107 | 24 | 0 | 1,2 | 0 |
| Trippa di bovini | 108 | 15,8 | 0 | 5 | 0 |
| Vitello filetto crudo | 107 | 20,7 | 0 | 2,7 | 0 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Bovino adulto o vitellone filetto crudo | 4 | 1,9 | 0,5 | 10 | 2 | 2,8 | 20 | 0 |
| Bovino magro vitellone senza grasso visibile | 4,4 | 1,56 | 0,5 | 27,6 | 2 | 3,76 | 17,4 | 0 |
| Bresaola | 7 | 2,4 | 0,5 | 19 | 2 | 3,9 | 34 | 0 |
| Macinato di manzo magro (proxy: bovino adulto o vitellone tagli anteriori crudo) | 10 | 1,3 | 0,56 | 19,4 | 2 | 4,5 | 17 | 0 |
| Maiale lombo crudo | 7 | 1,3 | 0,5 | 3 | 1 | 1,8 | 22 | 0 |
| Pollo fuso (coscia) senza pelle crudo | 13 | 1 | 0,1 | 9 | 1 | 1,9 | 23 | 0 |
| Pollo petto crudo | 4 | 0,4 | 0,2 | 14 | 0,05 | 0,7 | 32 | 0 |
| Prosciutto cotto senza grasso visibile | 7 | 0,9 | 0,8 | 19 | 1 | 2,6 | 16 | 0 |
| Prosciutto crudo senza grasso visibile | 16 | 1,3 | 0,6 | 4 | 0,05 | 2,2 | 23 | 0 |
| Tacchino fesa cotta al forno (proxy fesa affettata) | 11 | 1,5 | 0,4 | 7 | 1 | 1,3 | 39 | 0 |
| Tacchino petto senza pelle | 6 | 0,8 | 0,3 | 17 | 2 | 1,1 | 32 | 0 |
| Trippa di bovini | 8 | 4 | n.d. | n.d. | n.d. | n.d. | 13 | 3 |
| Vitello filetto crudo | 14 | 2,3 | 1,2 | 23 | 2 | 2,8 | 25 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Bovino adulto o vitellone filetto crudo | 1,67 | 1,63 | 0,99 | 0,11 | 0,05 | 60 |
| Bovino magro vitellone senza grasso visibile | 0,786 | 0,776 | 0,486 | 0,048 | 0,028 | 61,2 |
| Bresaola | 0,75 | 1,08 | 0,39 | 0,1 | 0,01 | 67 |
| Macinato di manzo magro (proxy: bovino adulto o vitellone tagli anteriori crudo) | 2,3026 | 2,275 | 1,4338 | 0,1382 | 0,0768 | 61,8 |
| Maiale lombo crudo | 2,23 | 2,38 | 1,82 | 0 | 0 | 61 |
| Pollo fuso (coscia) senza pelle crudo | 1,08 | 1,06 | 0,98 | 0,02 | 0,05 | 88 |
| Pollo petto crudo | 0,25 | 0,19 | 0,23 | 0 | 0 | 60 |
| Prosciutto cotto senza grasso visibile | 1,527 | 1,811 | 0,733 | 0,012 | 0 | 62 |
| Prosciutto crudo senza grasso visibile | 1,51 | 2,05 | 0,57 | 0 | 0 | 66 |
| Tacchino fesa cotta al forno (proxy fesa affettata) | 0,43 | 0,37 | 0,38 | n.d. | 0,04 | 62 |
| Tacchino petto senza pelle | 0,38 | 0,31 | 0,34 | n.d. | 0,03 | 50 |
| Trippa di bovini | 1,749 | 2,077 | 0,244 | 0 | 0 | 95 |
| Vitello filetto crudo | 1,0437 | 1,2597 | 0,1797 | 0,0009 | 0 | 55 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Bovino adulto o vitellone filetto crudo | 101170 | CREA+BDA-IEO(proxy scottona) | 101170+8655 | 2026-10-01 | BDA-IEO 8655_2 |
| Bovino magro vitellone senza grasso visibile | 8520 | BDA-IEO | 8520 | 2026-07-26 | BDA-IEO 8520_2 |
| Bresaola | 100061 | BDA-IEO | 100061 | 2026-07-26 | BDA-IEO 100061_2 |
| Macinato di manzo magro (proxy: bovino adulto o vitellone tagli anteriori crudo) | 101120 | CREA(proxy macinato)+BDA-IEO(proxy semigrassa) | 101120+8522 | 2026-10-23 | BDA-IEO 8522_2 |
| Maiale lombo crudo | 105210 | CREA+BDA-IEO+USDA | 105210 | 2026-07-28 | BDA-IEO 8670_2 |
| Pollo fuso (coscia) senza pelle crudo | 106410 | CREA+BDA-IEO | 106410+8686 | 2026-10-01 | BDA-IEO 8686_2 |
| Pollo petto crudo | 106500 | CREA+BDA-IEO | 106500 | 2026-07-26 | BDA-IEO 8689_2 |
| Prosciutto cotto senza grasso visibile | 9007 | BDA-IEO | 9007 | 2026-07-26 | BDA-IEO 9007_2 |
| Prosciutto crudo senza grasso visibile | 8711 | BDA-IEO | 8711 | 2026-07-26 | BDA-IEO 8711_2 |
| Tacchino fesa cotta al forno (proxy fesa affettata) | 106856 | CREA+BDA-IEO(proxy fesa affettata) | 106856+8698_2 | 2026-10-17 | BDA-IEO 8698_2 |
| Tacchino petto senza pelle | 8697 | BDA-IEO | 8697 | 2026-07-26 | BDA-IEO 8697_2 |
| Trippa di bovini | 115800 | CREA+USDA | 115800 | 2026-07-28 | BDA-IEO 1209_2 |
| Vitello filetto crudo | 101520 | CREA+BDA-IEO(proxy)+USDA | 101520 | 2026-07-28 | USDA USDA173826 |

## Cereali

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Avena cruda | 360 | 16,9 | 55,7 | 6,9 | 10,6 |
| Biscotti integrali | 441 | 8,2 | 62,2 | 17,5 | 8,5 |
| Cereali integrali in formelle (tipo Weetabix) | 351 | 10,5 | 72,7 | 1,9 | 9,7 |
| Corn flakes | 367 | 6,6 | 87,4 | 0,8 | 2,8 |
| Couscous secco | 361 | 13,7 | 76,5 | 1,1 | 4,5 |
| Farina d'avena | 378 | 12,6 | 66,3 | 7,1 | 7,6 |
| Farro crudo | 353 | 14,6 | 69,3 | 2,4 | 6,5 |
| Fette biscottate | 387 | 11,3 | 75 | 6 | 3,5 |
| Gallette di riso | 368 | 7,4 | 79,3 | 3,4 | 5 |
| Orzo perlato crudo | 346 | 9,4 | 73,7 | 1,5 | 9,2 |
| Pane comune | 269 | 8,4 | 59,8 | 0,4 | 3,8 |
| Pane di segale | 228 | 8,3 | 45,4 | 1,7 | 4,6 |
| Pane integrale | 224 | 8,5 | 44,1 | 1,3 | 6,5 |
| Pangrattato | 357 | 10,1 | 77,8 | 2,1 | 3,2 |
| Pasta di semola cruda | 341 | 13,5 | 72,7 | 1,2 | 1,7 |
| Pasta di semola integrale cruda | 330 | 13,3 | 64,8 | 2,2 | 7,1 |
| Piadina | 315 | 7,2 | 49,9 | 10,5 | 2,2 |
| Pop corn | 408 | 12 | 77,9 | 4,2 | 15,1 |
| Quinoa cruda | 376 | 15,4 | 57,8 | 8,1 | 12,2 |
| Riso basmati crudo | 367 | 9 | 82,9 | 1,9 | 1,3 |
| Riso bianco crudo | 334 | 6,7 | 80,4 | 0,4 | 1 |
| Riso integrale crudo | 341 | 7,5 | 77,4 | 1,9 | 1,9 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Avena cruda | 54 | 4,7 | 0 | 56 | 0 | 4 | 177 | 0 |
| Biscotti integrali | 26 | 1,9 | 0,06 | 14 | 0,1 | 1,13 | 68 | 0 |
| Cereali integrali in formelle (tipo Weetabix) | 30 | 12 | 0 | 170 | 0 | 1,7 | 83 | 0 |
| Corn flakes | 74 | 2,8 | 0 | 7 | 0 | 0,28 | 14 | 0 |
| Couscous secco | 24 | 1,9 | 0 | 28 | 0 | 1,4 | 52 | 0 |
| Farina d'avena | 80 | 4,2 | 0 | 32 | 0 | 2,3 | 114 | 0 |
| Farro crudo | 35 | 1,9 | 0 | 31 | 0 | 2,6 | 112 | 0 |
| Fette biscottate | 55 | 3,8 | 0 | 45 | 0 | 0,7 | 29 | 0 |
| Gallette di riso | 14 | 1,1 | 0 | 17 | 0 | 1,6 | 112 | 0 |
| Orzo perlato crudo | 21 | 1,1 | 0 | 20 | 0 | 1,15 | 46 | 0 |
| Pane comune | 15 | 1 | 0 | 29 | 0 | 0,37 | 15 | 0 |
| Pane di segale | 80 | 2,5 | 0 | 110 | 0 | 1,14 | 40 | 0 |
| Pane integrale | 25 | 2,5 | 0 | 40 | 0 | 1,6 | 66 | 0 |
| Pangrattato | 110 | 2,1 | 0 | 39 | 0 | 0,5 | 20 | 0 |
| Pasta di semola cruda | 22 | 1,4 | 0 | 19 | 0 | 1,15 | 51 | 0 |
| Pasta di semola integrale cruda | 39 | 2,7 | 0 | 29 | 0 | 2 | 100 | 0 |
| Piadina | 12 | 0,6 | 0 | 7 | 0 | 0,05 | 82 | 0 |
| Pop corn | 10 | 2,7 | 0 | 31 | 0 | 3,44 | 144 | 0 |
| Quinoa cruda | 46 | 3,6 | 0 | 20 | 0 | 2,74 | 189 | 0 |
| Riso basmati crudo | 5 | 0,8 | 0 | 12 | 0 | 1,48 | 32 | 0 |
| Riso bianco crudo | 24 | 0,8 | 0 | 13 | 0 | 1,3 | 20 | 0 |
| Riso integrale crudo | 32 | 1,6 | 0 | 22 | 0 | 1,8 | 116 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Avena cruda | 1,42 | 2,46 | 3 | 0 | 0 | 0 |
| Biscotti integrali | 3,32 | 5,4 | 7,69 | 0 | 0 | 15 |
| Cereali integrali in formelle (tipo Weetabix) | 0,32 | 0,23 | 0,78 | 0 | 0 | 0 |
| Corn flakes | 0,09 | 0,2 | 0,42 | 0 | 0 | 0 |
| Couscous secco | 0,22 | 0,11 | 0,44 | 0 | 0 | 0 |
| Farina d'avena | 1,46 | 2,53 | 3,09 | 0 | 0 | 0 |
| Farro crudo | 0,41 | 0,45 | 1,26 | 0 | 0 | 0 |
| Fette biscottate | 0,83 | 1,47 | 2,4 | 0 | 0 | 0 |
| Gallette di riso | 0,69 | 1,25 | 1,2 | 0 | 0 | 0 |
| Orzo perlato crudo | 0,36 | 0,19 | 0,85 | 0 | 0 | 0 |
| Pane comune | 0,04 | 0,04 | 0,15 | 0 | 0 | 0 |
| Pane di segale | 0,32 | 0,68 | 0,41 | 0 | 0 | 0 |
| Pane integrale | 0,27 | 0,26 | 0,51 | 0 | 0 | 0 |
| Pangrattato | 0,25 | 0,21 | 0,8 | 0 | 0 | 0 |
| Pasta di semola cruda | 0,19 | 0,14 | 0,61 | 0 | 0 | 0 |
| Pasta di semola integrale cruda | 0,32 | 0,27 | 0,85 | 0 | 0 | 0 |
| Piadina | 3,2 | 5,73 | 1,25 | 0 | 0 | 7 |
| Pop corn | 0,59 | 0,88 | 2,14 | 0 | 0 | 0 |
| Quinoa cruda | 0,93 | 2,14 | 4,37 | 0 | 0,07 | 0 |
| Riso basmati crudo | 0,13 | 0,16 | 0,23 | 0 | 0 | 0 |
| Riso bianco crudo | 0,1 | 0,13 | 0,18 | 0 | 0 | 0 |
| Riso integrale crudo | 0,35 | 0,63 | 0,59 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Avena cruda | 600009 | BDA-IEO | 600009 | 2026-07-26 | BDA-IEO 600009_2 |
| Biscotti integrali | 701307 | BDA-IEO | 701307 | 2026-07-26 | BDA-IEO 701307_2 |
| Cereali integrali in formelle (tipo Weetabix) | 999057 | BDA-IEO | 999057_2 | 2026-11-03 | BDA-IEO 999057_2 |
| Corn flakes | 3020 | CREA+BDA-IEO | 003020 | 2026-07-28 | BDA-IEO 19_2 |
| Couscous secco | 888013 | BDA-IEO | 888013 | 2026-07-26 | BDA-IEO 888013_2 |
| Farina d'avena | 000200 | CREA+BDA-IEO | 000200+9 | 2026-10-01 | BDA-IEO 9_2 |
| Farro crudo | 8603 | BDA-IEO | 8603 | 2026-07-26 | BDA-IEO 8603_2 |
| Fette biscottate | 001500 | CREA+BDA-IEO | 001500+73 | 2026-10-01 | BDA-IEO 73_2 |
| Gallette di riso | 8077 | BDA-IEO | 8077 | 2026-07-26 | BDA-IEO 8077_2 |
| Orzo perlato crudo | 000090 | CREA+BDA-IEO | 000090+4_2 | 2026-10-17 | BDA-IEO 4_2 |
| Pane comune | 100154_2 | BDA-IEO | 100154_2 | 2026-07-26 | BDA-IEO 100154_2 |
| Pane di segale | 30097 | BDA-IEO | 30097 | 2026-07-26 | BDA-IEO 30097_2 |
| Pane integrale | 000550 | CREA+BDA-IEO | 000550 | 2026-07-26 | BDA-IEO 33_2 |
| Pangrattato | 000570 | CREA+BDA-IEO | 000570+35_2 | 2026-10-21 | BDA-IEO 35_2 |
| Pasta di semola cruda | 000800 | CREA+BDA-IEO | 000800 | 2026-07-26 | BDA-IEO 50_2 |
| Pasta di semola integrale cruda | 60091 | BDA-IEO | 60091 | 2026-07-26 | BDA-IEO 60091_2 |
| Piadina | 9090 | BDA-IEO | 9090_2 | 2026-11-03 | BDA-IEO 9090_2 |
| Pop corn | 3009 | BDA-IEO | 3009 | 2026-07-26 | BDA-IEO 3009_2 |
| Quinoa cruda | 889001 | BDA-IEO | 889001 | 2026-07-26 | BDA-IEO 889001_2 |
| Riso basmati crudo | 000130 | CREA+BDA-IEO(proxy folati) | 000130 | 2026-07-27 | BDA-IEO 8075_2 |
| Riso bianco crudo | 000100 | CREA+BDA-IEO(proxy zinco/magnesio/folati) | 000100 | 2026-10-01 | BDA-IEO 5_2 |
| Riso integrale crudo | 500010 | BDA-IEO | 500010 | 2026-07-26 | BDA-IEO 500010_2 |

## Condimenti

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Capperi sott'aceto | 22 | 2,6 | 2,1 | 0,1 | 1,5 |
| Olio di oliva extravergine | 899 | 0 | 0 | 99,9 | 0 |
| Olive nere | 240 | 1,6 | 0,8 | 25,1 | 2,4 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Capperi sott'aceto | 19 | 0,9 | 0 | 38 | 0 | 0,2 | 33 | 17 |
| Olio di oliva extravergine | 0 | 0,2 | 0 | 0,5 | 0 | 0,005 | 0,5 | 0 |
| Olive nere | 62 | 1,6 | 0 | 0,5 | 0 | 0,5 | 4 | 20 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Capperi sott'aceto | 0,01 | 0,01 | 0,01 | 0 | 0 | 0 |
| Olio di oliva extravergine | 14,46 | 72,95 | 7,52 | 0 | 0 | 0 |
| Olive nere | 3,51 | 17,52 | 2,81 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Capperi sott'aceto | 777010 | BDA-IEO+USDA | 777010 | 2026-07-28 | BDA-IEO 777010_1 |
| Olio di oliva extravergine | 702901 | BDA-IEO | 702901 | 2026-07-26 | BDA-IEO 702901_2 |
| Olive nere | 592 | BDA-IEO+USDA(proxy) | 592 | 2026-07-28 | BDA-IEO 592_1 |

## Frutta

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Albicocche | 31 | 0,4 | 6,8 | 0,1 | 1,5 |
| Anguria cocomero fresco | 16 | 0,4 | 3,7 | 0 | 0,2 |
| Arance | 37 | 0,7 | 7,8 | 0,2 | 1,6 |
| Avocado | 238 | 4,4 | 1,8 | 23 | 3,3 |
| Banana | 69 | 1,2 | 15,4 | 0,3 | 1,8 |
| Ciliege | 40 | 0,8 | 9 | 0,1 | 1,3 |
| Fichi freschi | 51 | 0,9 | 11,2 | 0,2 | 2 |
| Fragole | 30 | 0,9 | 5,3 | 0,4 | 1,6 |
| Kiwi | 48 | 1,2 | 9 | 0,6 | 2,2 |
| Limone | 16 | 0,6 | 2,5 | 0 | 1,9 |
| Mandarini | 76 | 0,9 | 17,6 | 0,3 | 1,7 |
| Mele con buccia | 44 | 0,2 | 10 | 0 | 2,6 |
| Melone | 34 | 0,8 | 7,4 | 0,2 | 0,7 |
| Mirtillo nero | 31 | 0,9 | 5,1 | 0,2 | 3,1 |
| Pere fresche senza buccia | 43 | 0,3 | 8,8 | 0,1 | 3,8 |
| Pesche fresche con buccia | 28 | 0,7 | 5,8 | 0 | 1,9 |
| Prugne | 45 | 0,5 | 10,5 | 0,1 | 1,5 |
| Uva | 64 | 0,5 | 15,6 | 0,1 | 1,5 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Albicocche | 16 | 0,5 | 0 | 5 | 0 | 0,1 | 11 | 13 |
| Anguria cocomero fresco | 7 | 0,2 | 0 | 2 | 0 | 0,1 | 11,4 | 8 |
| Arance | 49 | 0,2 | 0 | 31 | 0 | 0,2 | 10 | 50 |
| Avocado | 13 | 0,6 | 0 | 11 | 0 | 0,4 | 25 | 18 |
| Banana | 7 | 0,8 | 0 | 14 | 0 | 0,2 | 34 | 16 |
| Ciliege | 30 | 0,6 | 0 | 5 | 0 | 0,1 | 10 | 11 |
| Fichi freschi | 43 | 0,5 | 0 | 6 | 0 | 0,2 | 15 | 7 |
| Fragole | 35 | 0,8 | 0 | 20 | 0 | 0,1 | 10 | 54 |
| Kiwi | 25 | 0,5 | 0 | 25 | 0 | 0,1 | 12 | 85 |
| Limone | 14 | 0,1 | 0 | 11 | 0 | 0,1 | 12 | 50 |
| Mandarini | 32 | 0,3 | 0 | 18 | 0 | 0,1 | 10 | 42 |
| Mele con buccia | 4 | 0,1 | 0 | 1 | 0 | 0,1 | 5 | 6 |
| Melone | 19 | 0,3 | 0 | 5 | 0 | 0,3 | 11 | 32 |
| Mirtillo nero | 41 | 0,7 | 0 | 6 | 0 | 0,2 | 5 | 15 |
| Pere fresche senza buccia | 11 | 0,3 | 0 | 5 | 0 | 0,05 | 7 | 4 |
| Pesche fresche con buccia | 8 | 0,4 | 0 | 7 | 0 | 0,35 | 8 | 0 |
| Prugne | 13 | 0,2 | 0 | 3 | 0 | 0,12 | 6 | 5 |
| Uva | 27 | 0,4 | 0 | 2 | 0 | 0,12 | 7 | 6 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Albicocche | 0,007 | 0,044 | 0,02 | 0 | 0 | 0 |
| Anguria cocomero fresco | 0 | 0 | 0 | 0 | 0 | 0 |
| Arance | 0,025 | 0,038 | 0,042 | 0 | 0 | 0 |
| Avocado | 2,48 | 18,33 | 1,45 | 0 | 0 | 0 |
| Banana | 0,11 | 0,04 | 0,09 | 0 | 0 | 0 |
| Ciliege | 0,019 | 0,024 | 0,026 | 0 | 0 | 0 |
| Fichi freschi | 0,04 | 0,044 | 0,096 | 0 | 0 | 0 |
| Fragole | 0,02 | 0,057 | 0,207 | 0 | 0 | 0 |
| Kiwi | 0,033 | 0,054 | 0,331 | 0 | 0 | 0 |
| Limone | 0 | 0 | 0 | 0 | 0 | 0 |
| Mandarini | 0,038 | 0,058 | 0,063 | 0 | 0 | 0 |
| Mele con buccia | 0 | 0 | 0 | 0 | 0 | 0 |
| Melone | 0,054 | 0,003 | 0,085 | 0 | 0 | 0 |
| Mirtillo nero | 0,017 | 0,028 | 0,088 | 0 | 0 | 0 |
| Pere fresche senza buccia | 0 | 0 | 0 | 0 | 0 | 0 |
| Pesche fresche con buccia | 0 | 0 | 0 | 0 | 0 | 0 |
| Prugne | 0,006 | 0,048 | 0,016 | 0 | 0 | 0 |
| Uva | 0,034 | 0,004 | 0,03 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Albicocche | 401 | BDA-IEO | 401 | 2026-07-26 | BDA-IEO 401_2 |
| Anguria cocomero fresco | 7040 | CREA+BDA-IEO+USDA | 007040 | 2026-07-28 | BDA-IEO 408_2 |
| Arance | 008000 | CREA+BDA-IEO(proxy zinco/magnesio/folati) | 008000 | 2026-10-01 | BDA-IEO 404_2 |
| Avocado | 999692 | BDA-IEO | 999692 | 2026-07-26 | BDA-IEO 999692_2 |
| Banana | 406 | BDA-IEO | 406 | 2026-07-26 | BDA-IEO 406_2 |
| Ciliege | 407 | BDA-IEO | 407 | 2026-07-26 | BDA-IEO 407_2 |
| Fichi freschi | 409 | BDA-IEO | 409 | 2026-07-26 | BDA-IEO 409_2 |
| Fragole | 411 | BDA-IEO | 411 | 2026-07-26 | BDA-IEO 411_2 |
| Kiwi | 429 | BDA-IEO | 429 | 2026-07-26 | BDA-IEO 429_2 |
| Limone | 008030 | CREA+BDA-IEO(proxy zinco/magnesio/folati) | 008030 | 2026-07-26 | BDA-IEO 413_2 |
| Mandarini | 008060 | CREA+BDA-IEO(proxy zinco/magnesio/folati) | 008060 | 2026-10-01 | BDA-IEO 417_2 |
| Mele con buccia | 8807 | BDA-IEO | 8807 | 2026-07-26 | BDA-IEO 8807_2 |
| Melone | 421 | BDA-IEO | 421 | 2026-07-26 | BDA-IEO 421_2 |
| Mirtillo nero | 500021 | BDA-IEO | 500021 | 2026-07-26 | BDA-IEO 500021_2 |
| Pere fresche senza buccia | 7260 | CREA | 007260 | 2026-07-26 | decisione nutrizionista  |
| Pesche fresche con buccia | 7290 | CREA+BDA-IEO+USDA | 007290 | 2026-07-28 | decisione nutrizionista  |
| Prugne | 427 | BDA-IEO | 427 | 2026-07-26 | BDA-IEO 427_2 |
| Uva | 428 | BDA-IEO | 428 | 2026-07-26 | BDA-IEO 428_2 |

## Frutta secca

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Anacardi | 604 | 15 | 33 | 46 | 3 |
| Burro d'arachidi | 625 | 24,9 | 8 | 53,7 | 6 |
| Mandorle dolci secche | 628 | 22 | 4,6 | 55,3 | 12,7 |
| Nocciole secche | 671 | 13,8 | 6,1 | 64,1 | 8,1 |
| Noci secche | 702 | 14,3 | 5,1 | 68,1 | 6,2 |
| Pistacchi secchi | 629 | 18,1 | 8,1 | 56,1 | 10,6 |
| Semi di lino secchi | 447 | 24,5 | 0 | 31 | 34,8 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Anacardi | 45 | 6 | 0 | 68 | 0 | 6 | 260 | 0 |
| Burro d'arachidi | 47 | 2,5 | 0 | 53 | 0 | 3,5 | 180 | 0 |
| Mandorle dolci secche | 240 | 3 | 0 | 48 | 0 | 2,5 | 264 | 0 |
| Nocciole secche | 150 | 3,3 | 0 | 72 | 0 | 2 | 160 | 4 |
| Noci secche | 61 | 2,4 | 0 | 66 | 0 | 5 | 121 | 1 |
| Pistacchi secchi | 131 | 7,3 | 0 | 51 | 0 | 2,37 | 158 | 2 |
| Semi di lino secchi | 198 | 8,2 | 0 | 60 | 0 | 7,8 | 392 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Anacardi | 8,165 | 24,964 | 8,23 | 0 | 0 | 0 |
| Burro d'arachidi | 10,62 | 27,21 | 13,45 | 0 | 0 | 0 |
| Mandorle dolci secche | 4,59 | 39,44 | 10,85 | 0 | 0 | 0 |
| Nocciole secche | 4,16 | 38,6 | 5,2 | 0 | 0 | 0 |
| Noci secche | 5,57 | 9,54 | 40,66 | 0 | 0 | 0 |
| Pistacchi secchi | 5,61 | 36,47 | 10,66 | 0 | 0 | 0 |
| Semi di lino secchi | 3 | 5,3 | 21,2 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Anacardi | 008610 | CREA+BDA-IEO | 008610+8802_2 | 2026-10-02 | BDA-IEO 8802_2 |
| Burro d'arachidi | 009010 | CREA+BDA-IEO(magnesio da BDA) | 009010+606010 | 2026-10-01 | BDA-IEO 606010_2 |
| Mandorle dolci secche | 008540 | CREA+BDA-IEO | 008540 | 2026-07-26 | BDA-IEO 8808_2 |
| Nocciole secche | 511 | BDA-IEO | 511 | 2026-07-26 | BDA-IEO 511_2 |
| Noci secche | 510 | BDA-IEO | 510 | 2026-07-26 | BDA-IEO 510_2 |
| Pistacchi secchi | 700607 | BDA-IEO | 700607 | 2026-07-26 | BDA-IEO 700607_2 |
| Semi di lino secchi | 9600_1 | BDA-IEO+USDA | 9600_1+169414 | 2026-10-21 | BDA-IEO 9600_1 |

## Latticini

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Feta | 250 | 15,6 | 1,5 | 20,2 | 0 |
| Fiocchi di latte magro | 115 | 9,7 | 3,2 | 7,1 | 0 |
| Formaggio cremoso spalmabile light | 179 | 9,2 | 3,1 | 14,5 | 0 |
| Formaggio spalmabile tipo philadelphia | 313 | 8,6 | 0 | 31 | 0 |
| Latte di vacca pastorizzato scremato | 36 | 3,6 | 5,3 | 0,2 | 0 |
| Latte parzialmente scremato | 46 | 3,5 | 5 | 1,5 | 0 |
| Mozzarella di bufala | 288 | 16,7 | 0,4 | 24,4 | 0 |
| Mozzarella di vacca | 253 | 18,7 | 0,7 | 19,5 | 0 |
| Parmigiano | 387 | 33,5 | 0 | 28,1 | 0 |
| Pecorino | 392 | 25,8 | 0,2 | 32 | 0 |
| Ricotta di pecora | 157 | 9,5 | 4,2 | 11,5 | 0 |
| Ricotta di vacca | 146 | 8,8 | 3,5 | 10,9 | 0 |
| Robiola | 338 | 20 | 2,3 | 27,7 | 0 |
| Yogurt di latte intero | 66 | 3,8 | 4,3 | 3,9 | 0 |
| Yogurt di latte parzialmente scremato | 43 | 3,4 | 3,8 | 1,7 | 0 |
| Yogurt di latte scremato | 36 | 3,3 | 4 | 0,9 | 0 |
| Yogurt greco | 115 | 6,4 | 2 | 9,1 | 0 |
| Yogurt greco 0% lipidi | 51 | 9 | 4 | 0 | 0 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Feta | 360 | 0,2 | 0,5 | 23 | 1,1 | 0,9 | 20 | 0 |
| Fiocchi di latte magro | 73 | 0,1 | 0,05 | 27 | 0,7 | 0,6 | 9 | 0 |
| Formaggio cremoso spalmabile light | 110 | 0,1 | 0,11 | 13 | 0,3 | 0,7 | 9 | 0,5 |
| Formaggio spalmabile tipo philadelphia | 110 | 0,1 | 0,17 | 13 | 0,3 | 0,7 | 9 | 0 |
| Latte di vacca pastorizzato scremato | 125 | 0,1 | 0,005 | 5 | 0,4 | 0,59 | 11 | 1 |
| Latte parzialmente scremato | 120 | 0,1 | n.d. | 8 | n.d. | 0,37 | 11 | 1 |
| Mozzarella di bufala | 210 | 0,2 | 0,16 | 19 | 2,1 | 2,6 | 10 | 0 |
| Mozzarella di vacca | 160 | 0,4 | 0,12 | 16 | 1,7 | 2,6 | 10 | 0 |
| Parmigiano | 1159 | 0,7 | 0,5 | 5 | 4,2 | 4 | 43 | 0 |
| Pecorino | 607 | 0,6 | 0,5 | 7 | 1,1 | 3,4 | 40 | 0 |
| Ricotta di pecora | 166 | 0,3 | 0,18 | 12 | 0,3 | 0,2 | 15 | 0 |
| Ricotta di vacca | 295 | 0,4 | 0,03 | 12 | 0,3 | 0,5 | 17 | 0 |
| Robiola | 704 | 0,7 | 0,17 | 19 | 0,6 | 4,1 | 20 | 0 |
| Yogurt di latte intero | 125 | 0,1 | 0,04 | 18 | 0,2 | 0,41 | 12 | 1 |
| Yogurt di latte parzialmente scremato | 120 | 0,1 | 0,01 | 17 | 0,2 | 0,6 | 19 | 1 |
| Yogurt di latte scremato | 120 | 0,1 | 0,01 | 14 | 0,2 | 0,6 | 18 | 1 |
| Yogurt greco | 150 | 0,3 | 0,05 | 6 | 0,2 | 0,5 | 12 | 0 |
| Yogurt greco 0% lipidi | 111 | 0,07 | 0 | 7 | 0,7 | 0,53 | 10,7 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Feta | 14,187 | 4,388 | 0,561 | 0 | 0 | 70 |
| Fiocchi di latte magro | 4,242 | 2,254 | 0,195 | 0 | 0 | 24 |
| Formaggio cremoso spalmabile light | 8,499 | 4,431 | 0,483 | 0 | 0 | 42 |
| Formaggio spalmabile tipo philadelphia | 18,519 | 9,869 | 0,839 | 0 | 0 | 90 |
| Latte di vacca pastorizzato scremato | 0,14 | 0,05 | 0,01 | 0 | 0 | 2 |
| Latte parzialmente scremato | 0,89 | 0,47 | 0,08 | 0 | 0 | 7 |
| Mozzarella di bufala | 14,3 | 7,46 | 0,81 | n.d. | n.d. | 56 |
| Mozzarella di vacca | 11,429 | 5,958 | 0,65 | 0 | 0 | 46 |
| Parmigiano | 18,54 | 8,81 | 0,79 | 0 | 0 | 91 |
| Pecorino | 17,344 | 7,943 | 0,601 | 0 | 0 | 104 |
| Ricotta di pecora | 7,36 | 2,5 | 0,68 | 0 | 0 | 56 |
| Ricotta di vacca | 6,82 | 2,76 | 0,39 | 0 | 0 | 50 |
| Robiola | 16,235 | 8,464 | 0,923 | 0 | 0 | 90 |
| Yogurt di latte intero | 2,07 | 0,84 | 0,13 | 0 | 0 | 11 |
| Yogurt di latte parzialmente scremato | 0,95 | 0,38 | 0,05 | 0 | 0 | 8 |
| Yogurt di latte scremato | 0,503 | 0,201 | 0,026 | 0 | 0 | 2 |
| Yogurt greco | 4,83 | 1,96 | 0,303 | 0 | 0 | 15 |
| Yogurt greco 0% lipidi | 0 | 0 | 0 | 0 | 0 | 5 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Feta | 805080 | BDA-IEO | 805080 | 2026-07-26 | BDA-IEO 805080_2 |
| Fiocchi di latte magro | 100015 | BDA-IEO | 100015 | 2026-07-26 | BDA-IEO 100015_2 |
| Formaggio cremoso spalmabile light | 170510 | CREA+BDA-IEO | 170510+8054_2 | 2026-10-02 | BDA-IEO 8054_2 |
| Formaggio spalmabile tipo philadelphia | 21792 | BDA-IEO | 21792 | 2026-07-26 | BDA-IEO 21792_2 |
| Latte di vacca pastorizzato scremato | 135030 | CREA+BDA-IEO | 135030+1604 | 2026-10-01 | BDA-IEO 1604_2 |
| Latte parzialmente scremato | 135020 | BDA-IEO | 135020 | 2026-07-26 | BDA-IEO 1603_2 |
| Mozzarella di bufala | 11796 | BDA-IEO | 11796 | 2026-07-26 | BDA-IEO 11796_2+1718_2 |
| Mozzarella di vacca | 1718 | BDA-IEO | 1718 | 2026-07-26 | BDA-IEO 1718_2 |
| Parmigiano | 1726 | BDA-IEO | 1726 | 2026-07-26 | BDA-IEO 1726_2 |
| Pecorino | 1721 | BDA-IEO | 1721 | 2026-07-26 | BDA-IEO 1721_2 |
| Ricotta di pecora | 166810 | CREA | 166810 | 2026-07-26 | BDA-IEO 1723_2 |
| Ricotta di vacca | 11793 | BDA-IEO | 11793 | 2026-07-26 | BDA-IEO 11793_2 |
| Robiola | 100030 | BDA-IEO | 100030 | 2026-07-26 | BDA-IEO 100030_2 |
| Yogurt di latte intero | 150010 | CREA | 150010 | 2026-07-26 | BDA-IEO 1630_2 |
| Yogurt di latte parzialmente scremato | 1631 | BDA-IEO | 1631 | 2026-07-26 | BDA-IEO 1631_2 |
| Yogurt di latte scremato | 152000 | CREA+BDA-IEO | 152000 | 2026-09-18 | BDA-IEO 1632_2 |
| Yogurt greco | 8053 | BDA-IEO | 8053 | 2026-07-26 | BDA-IEO 8053_2 |
| Yogurt greco 0% lipidi | 150030 | CREA+USDA(debole folati/vitamina C) | 150030+330137+170894 | 2026-10-01 | decisione nutrizionista+USDA USDA170894 |

## Legumi

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Ceci in scatola scolati | 111 | 6,7 | 13,9 | 2,3 | 5,7 |
| Ceci secchi cotti bolliti | 132 | 7 | 18,9 | 2,4 | 5,8 |
| Fagioli borlotti secchi cotti bolliti | 106 | 6,9 | 16,4 | 0,4 | 6,9 |
| Fagioli cannellini in scatola scolati | 86 | 6 | 12,5 | 0,6 | 4,8 |
| Fave secche cotte bollite | 146 | 11 | 22,4 | 1,3 | 3 |
| Lenticchie secche cotte bollite | 109 | 6,9 | 16,3 | 0,4 | 8,3 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ceci in scatola scolati | 43 | 1,8 | 0 | 42 | 0 | 1,03 | 24 | 0,5 |
| Ceci secchi cotti bolliti | 58 | 2,2 | 0 | 45 | 0 | 1,7 | 37 | 0,1 |
| Fagioli borlotti secchi cotti bolliti | 46 | 2,3 | 0 | 32 | 0 | 1,2 | 50 | 0 |
| Fagioli cannellini in scatola scolati | 39 | 2 | 0 | 8 | 0 | 0,68 | 29,3 | 0 |
| Fave secche cotte bollite | 90 | 5 | 0 | 145 | 0 | 4,6 | 43 | 0 |
| Lenticchie secche cotte bollite | 29 | 3 | 0 | 110 | 0 | 1,1 | 28 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Ceci in scatola scolati | 0,2957 | 0,6407 | 1,265 | 0 | 0 | 0 |
| Ceci secchi cotti bolliti | 0,3086 | 0,6661 | 1,3176 | 0 | 0 | 0 |
| Fagioli borlotti secchi cotti bolliti | 0,08 | 0,0304 | 0,192 | 0 | 0 | 0 |
| Fagioli cannellini in scatola scolati | 0,12 | 0,048 | 0,288 | 0 | 0 | 0 |
| Fave secche cotte bollite | 0,2167 | 0,26 | 0,546 | 0 | 0 | 0 |
| Lenticchie secche cotte bollite | 0,0544 | 0,0672 | 0,1872 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Ceci in scatola scolati | 004010 | CREA+BDA-IEO | 004010 | 2026-09-17 | BDA-IEO 700082_1 |
| Ceci secchi cotti bolliti | 4005 | CREA | 004005 | 2026-07-26 | BDA-IEO 201_1 |
| Fagioli borlotti secchi cotti bolliti | 004125 | CREA+USDA | 004125 | 2026-07-28 | BDA-IEO 202_1 |
| Fagioli cannellini in scatola scolati | 004210 | CREA+BDA-IEO(proxy)+USDA | 004210 | 2026-07-26 | BDA-IEO 100139_1 |
| Fave secche cotte bollite | 004425 | CREA+BDA-IEO(proxy minerali)+USDA | 004425+203_1 | 2026-07-28 | BDA-IEO 203_1 |
| Lenticchie secche cotte bollite | 4505 | CREA+BDA-IEO(proxy folati) | 004505 | 2026-07-26 | BDA-IEO 204_1 |

## Molluschi

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Calamaro fresco | 68 | 12,6 | 0,6 | 1,7 | 0 |
| Cozza/mitilo fresca | 84 | 11,7 | 3,4 | 2,7 | 0 |
| Seppia fresca | 72 | 14 | 0,7 | 1,5 | 0 |
| Vongola fresca | 72 | 10,2 | 2,2 | 2,5 | 0 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Calamaro fresco | 144 | 0,2 | 0,005 | 13 | 3 | 3,1 | 22 | 0,5 |
| Cozza/mitilo fresca | 88 | 5,8 | 0,005 | 37 | 19 | 2,2 | 44 | 0,5 |
| Seppia fresca | 27 | 0,8 | 0,005 | 13 | 2 | 4,2 | 32 | 0,5 |
| Vongola fresca | 46 | 14 | 4 | 16 | 49 | 1,4 | 9 | 13 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Calamaro fresco | 0,85 | 0,45 | 0,4 | 0,31 | 0,09 | 64 |
| Cozza/mitilo fresca | 0,52 | 0,63 | 0,58 | 0,27 | 0,11 | 121 |
| Seppia fresca | 0,429 | 0,214 | 0,429 | 0,214 | 0,214 | 64 |
| Vongola fresca | 0,242 | 0,206 | 0,722 | 0,18 | 0,18 | 50 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Calamaro fresco | 1304 | BDA-IEO | 1304 | 2026-07-27 | BDA-IEO 1304_2 |
| Cozza/mitilo fresca | 1307 | BDA-IEO | 1307 | 2026-07-27 | BDA-IEO 1307_2 |
| Seppia fresca | 1320 | BDA-IEO | 1320 | 2026-07-27 | BDA-IEO 1320_2 |
| Vongola fresca | 1328 | BDA-IEO | 1328 | 2026-07-27 | BDA-IEO 1328_2 |

## Pesce

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Alici/acciughe fresche | 96 | 16,8 | 1,5 | 2,6 | 0 |
| Branzino spigola | 82 | 16,5 | 0,6 | 1,5 | 0 |
| Cozza mitilo | 84 | 11,7 | 3,4 | 2,7 | 0 |
| Gambero | 71 | 13,6 | 2,9 | 0,6 | 0 |
| Merluzzo | 71 | 17 | 0 | 0,3 | 0 |
| Orata d'allevamento filetti | 159 | 19,7 | 1,2 | 8,4 | 0 |
| Pesce spada | 109 | 16,9 | 1 | 4,2 | 0 |
| Polpo | 57 | 10,6 | 1,4 | 1 | 0 |
| Salmone | 185 | 18,4 | 1 | 12 | 0 |
| Salmone affumicato | 147 | 25,4 | 1,2 | 4,5 | 0 |
| Salmone in salamoia (in scatola) | 192 | 21,1 | 1 | 11,5 | 0 |
| Sardine fresche | 225 | 20,3 | 1,5 | 15,4 | 0 |
| Scorfano | 82 | 19 | 0,6 | 0,4 | 0 |
| Sgombro | 170 | 17 | 0,5 | 11,1 | 0 |
| Sogliola fresca | 86 | 16,9 | 0,8 | 1,7 | 0 |
| Tonno | 159 | 21,5 | 0,1 | 8,1 | 0 |
| Tonno in scatola al naturale sgocciolato | 103 | 25,1 | 0 | 0,3 | 0 |
| Vongole in scatola al naturale | 140 | 25,6 | 5,1 | 2 | 0 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Alici/acciughe fresche | 148 | 2,8 | 11 | 9 | 0,62 | 4,2 | 22 | 0 |
| Branzino spigola | 20 | 4,1 | 5,6 | 9 | 0,6 | 2,1 | 29 | 0 |
| Cozza mitilo | 88 | 5,8 | 0,005 | 37 | 19 | 2,2 | 44 | 0 |
| Gambero | 110 | 1,8 | 0,1 | 14 | 3 | 1,9 | 39 | 2 |
| Merluzzo | 25 | 0,7 | 0,005 | 12 | 1 | 2 | 20 | 0,5 |
| Orata d'allevamento filetti | 30 | 0,6 | n.d. | 5 | 2 | 0,5 | 24 | 0 |
| Pesce spada | 4 | 0,4 | 11 | 2 | 2 | 0,4 | 27 | 1 |
| Polpo | 144 | 1,5 | 0,005 | 16 | 20 | 5,1 | 39 | 0 |
| Salmone | 27 | 0,7 | 8 | 16 | 4 | 0,6 | 27 | 0 |
| Salmone affumicato | 19 | 0,6 | n.d. | 2 | 3 | 0,4 | 32 | 0,5 |
| Salmone in salamoia (in scatola) | 66 | 0,8 | 17 | 14 | 4 | 0,8 | 25 | 0 |
| Sardine fresche | 72 | 1 | 21 | 15 | 10 | 1,6 | 31 | 0 |
| Scorfano | 61 | 5,5 | 0,005 | 9 | 0,6 | 1,8 | 21 | 0 |
| Sgombro | 38 | 1,2 | 2,9 | 1 | 7 | 2 | 21 | 0 |
| Sogliola fresca | 12 | 0,8 | 0,005 | 5 | 2 | 1,5 | 0,2 | 0 |
| Tonno | 38 | 1,3 | 16,3 | 20 | 5 | 0,5 | 26 | 0 |
| Tonno in scatola al naturale sgocciolato | 8 | 1 | 2 | 4 | 4 | 0,7 | 27 | 0 |
| Vongole in scatola al naturale | 92 | 28 | 4 | 29 | 99 | 2,7 | 18 | 22 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Alici/acciughe fresche | 1,3 | 0,4 | 0,85 | 0,27 | 0,52 | 61 |
| Branzino spigola | 0,35 | 0,3 | 0,4 | 0,09 | 0,2 | 48 |
| Cozza mitilo | 0,52 | 0,63 | 0,58 | 0,27 | 0,11 | 121 |
| Gambero | 0,09 | 0,128 | 0,193 | 0,09 | 0,065 | 150 |
| Merluzzo | 0,06 | 0,07 | 0,12 | 0,03 | 0,08 | 50 |
| Orata d'allevamento filetti | 1,94 | 2,78 | 2,21 | 0,46 | 0,95 | 68 |
| Pesce spada | 1,149 | 1,623 | 0,964 | 0,115 | 0,555 | 70 |
| Polpo | 0,42 | 0,2 | 0,4 | 0,18 | 0,22 | 72 |
| Salmone | 2,97 | 4,6 | 3,05 | 0,89 | 1,19 | 35 |
| Salmone affumicato | 0,777 | 1,8 | 1,268 | 0,205 | 0,532 | 35 |
| Salmone in salamoia (in scatola) | 2,265 | 4,182 | 3,311 | 0,871 | 1,394 | 35 |
| Sardine fresche | n.d. | n.d. | n.d. | n.d. | n.d. | n.d. |
| Scorfano | 0,09 | 0,078 | 0,125 | 0,011 | 0,086 | 67 |
| Sgombro | 2,61 | 4,13 | 2,46 | 0,73 | 1,26 | 95 |
| Sogliola fresca | 0,219 | 0,328 | 0,959 | 0,267 | 0,389 | 25 |
| Tonno | 3,35 | 1,51 | 3,2 | 0,8 | 2,15 | 70 |
| Tonno in scatola al naturale sgocciolato | 0,1 | 0,05 | 0,1 | 0 | 0,05 | 63 |
| Vongole in scatola al naturale | 0,19 | 0,17 | 0,55 | 0,14 | 0,15 | 67 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Alici/acciughe fresche | 1300 | BDA-IEO | 1300 | 2026-07-27 | BDA-IEO 1300_2 |
| Branzino spigola | 123200 | CREA+BDA-IEO+USDA | 123200 | 2026-07-28 | BDA-IEO 1323_2 |
| Cozza mitilo | 127120 | CREA+BDA-IEO | 127120 | 2026-07-28 | BDA-IEO 1307_2 |
| Gambero | 1309 | BDA-IEO+USDA | 1309 | 2026-07-28 | BDA-IEO 1309_2 |
| Merluzzo | 1313 | BDA-IEO | 1313 | 2026-07-26 | BDA-IEO 1313_2 |
| Orata d'allevamento filetti | 8734 | BDA-IEO | 8734 | 2026-07-26 | BDA-IEO 8734_2 |
| Pesce spada | 100110_2 | BDA-IEO(deroga-energia-macro) | 100110_2 | 2026-08-08 | BDA-IEO 100110_2 |
| Polpo | 127150 | CREA+BDA-IEO | 127150 | 2026-07-28 | BDA-IEO 1316_2 |
| Salmone | 700405 | BDA-IEO | 700405 | 2026-07-26 | BDA-IEO 700405_2 |
| Salmone affumicato | 122410 | CREA+BDA-IEO | 122410+700407 | 2026-08-07 | BDA-IEO 700407_2 |
| Salmone in salamoia (in scatola) | 1510 | BDA-IEO | 1510 | 2026-07-26 | BDA-IEO 1510_2 |
| Sardine fresche | 122800 | CREA+INSA(micronutrienti) | 122800+INSA882 | 2026-10-01 |   |
| Scorfano | 122900 | CREA+BDA-IEO | 122900 | 2026-09-15 | BDA-IEO 8739_2 |
| Sgombro | 1321 | BDA-IEO | 1321 | 2026-07-26 | BDA-IEO 1321_2 |
| Sogliola fresca | 1322 | BDA-IEO | 1322 | 2026-07-27 | BDA-IEO 1322_2 |
| Tonno | 1325 | BDA-IEO | 1325 | 2026-07-26 | BDA-IEO 1325_2 |
| Tonno in scatola al naturale sgocciolato | 1515 | BDA-IEO | 1515 | 2026-07-26 | BDA-IEO 1515_2 |
| Vongole in scatola al naturale | 700832 | BDA-IEO | 700832 | 2026-07-26 | BDA-IEO 700832_2 |

## Uova

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Albume di uovo di gallina | 43 | 10,7 | 0,05 | 0,05 | 0 |
| Tuorlo di uovo di gallina | 325 | 15,8 | 0,05 | 29,1 | 0 |
| Uovo di gallina intero | 128 | 12,4 | 0 | 8,7 | 0 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Albume di uovo di gallina | 7 | 0,1 | 0 | 8 | 0,1 | 0,26 | 12 | 0 |
| Tuorlo di uovo di gallina | 116 | 4,9 | 4,94 | 130 | 6,9 | 2,14 | 14 | 0 |
| Uovo di gallina intero | 48 | 1,5 | 1,75 | 50 | 2,5 | 1,2 | 13 | 0 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Albume di uovo di gallina | 0 | 0 | 0 | 0 | 0 | 0 |
| Tuorlo di uovo di gallina | 9,82 | 8,29 | 4,63 | 0 | 0 | 1337 |
| Uovo di gallina intero | 3,17 | 2,58 | 1,26 | 0 | 0 | 371 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Albume di uovo di gallina | 182010 | CREA+BDA-IEO | 182010 | 2026-09-18 | BDA-IEO 1801_2 |
| Tuorlo di uovo di gallina | 183010 | CREA+BDA-IEO | 183010+1802_2 | 2026-10-02 | BDA-IEO 1802_2 |
| Uovo di gallina intero | 1800 | BDA-IEO | 1800 | 2026-07-26 | BDA-IEO 1800_2 |

## Verdura

### Energia e macronutrienti

| Alimento | kcal | Prot g | Carb g | Grassi g | Fibra g |
|---|---:|---:|---:|---:|---:|
| Aglio | 53 | 8,4 | 1 | 0,8 | 4,3 |
| Asparagi | 33 | 3,6 | 3,3 | 0,2 | 2,1 |
| Barbabietole rosse crude | 25 | 1,1 | 4 | 0 | 2,6 |
| Basilico fresco | 42 | 3,1 | 5,2 | 0,8 | 1,6 |
| Bietola cruda | 15 | 1,3 | 1,8 | 0,1 | 1,2 |
| Broccolo a testa | 33 | 3 | 3,1 | 0,4 | 3,1 |
| Carciofi | 33 | 2,7 | 2,5 | 0,2 | 5,5 |
| Cardi crudi | 13 | 0,6 | 1,7 | 0,1 | 1,5 |
| Carote | 39 | 1,1 | 7,6 | 0 | 3,1 |
| Cavolfiore | 30 | 3,2 | 2,7 | 0,2 | 2,4 |
| Cavoli di Bruxelles crudi | 47 | 4,2 | 4,2 | 0,5 | 5 |
| Cavolo broccolo verde ramoso crudo | 30 | 3,4 | 2 | 0,3 | 3 |
| Cavolo cappuccio rosso crudo | 22 | 1,9 | 2,7 | 0,2 | 1 |
| Cavolo cappuccio verde crudo | 24 | 2,1 | 2,5 | 0,1 | 2,6 |
| Cetrioli | 15 | 0,7 | 1,8 | 0,5 | 0,6 |
| Cicoria catalogna | 30 | 1,8 | 3,2 | 0,5 | 3,1 |
| Cicoria da taglio cruda | 14 | 1,2 | 1,7 | 0,1 | 1,2 |
| Cicoria di campo cruda | 17 | 1,4 | 0,7 | 0,2 | 3,6 |
| Cime di rapa (broccoletti di rapa) crude | 28 | 2,9 | 2 | 0,3 | 2,9 |
| Cipolla | 28 | 1 | 5,7 | 0,1 | 1 |
| Cipolline | 41 | 1,3 | 8,5 | 0,1 | 1,7 |
| Fagiolini | 24 | 2,1 | 2,4 | 0,1 | 2,9 |
| Finocchio | 13 | 1,2 | 1 | 0 | 2,2 |
| Funghi prataioli coltivati | 23 | 2,3 | 1,9 | 0,4 | 1,7 |
| Indivia | 20 | 0,9 | 2,7 | 0,3 | 1,6 |
| Indivia belga (cicoria witloof) cruda | 20 | 0,7 | 3,2 | 0,3 | 1,1 |
| Lattuga | 22 | 1,8 | 2,2 | 0,4 | 1,5 |
| Mais dolce in scatola sgocciolato | 105 | 3,4 | 20,5 | 1,3 | 1,4 |
| Melanzane | 20 | 1,1 | 2,6 | 0,1 | 2,6 |
| Patate | 80 | 2,1 | 18 | 0,1 | 1,6 |
| Patate dolci | 92 | 1,2 | 21,3 | 0,3 | 2,3 |
| Peperoni dolci | 26 | 0,9 | 4,2 | 0,3 | 1,9 |
| Piselli | 87 | 7 | 12,4 | 0,2 | 5,2 |
| Pomodori da insalata | 19 | 1,2 | 2,8 | 0,2 | 1,1 |
| Pomodori pelati in scatola | 22 | 1,2 | 3 | 0,5 | 0,9 |
| Porri | 35 | 2,1 | 5,2 | 0,1 | 2,9 |
| Radicchio rosso | 18 | 1,4 | 1,6 | 0,1 | 3 |
| Rucola | 28 | 2,6 | 2,1 | 0,7 | 1,6 |
| Scarola | 19 | 1,1 | 2,3 | 0,3 | 1,8 |
| Sedano | 23 | 2,3 | 2,4 | 0,2 | 1,6 |
| Sedano rapa crudo | 29 | 1,9 | 3,8 | 0,1 | 3,1 |
| Spinaci | 35 | 3,4 | 3 | 0,7 | 1,9 |
| Valerianella (songino) | 28 | 2 | 3,6 | 0,4 | 1,5 |
| Zucca gialla | 19 | 1,1 | 3,5 | 0,1 | 0,5 |
| Zucchine | 14 | 1,3 | 1,4 | 0,1 | 1,3 |

### Micronutrienti

| Alimento | Ca mg | Fe mg | Vit D µg | Folati µg | B12 µg | Zn mg | Mg mg | Vit C mg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Aglio | 15 | 1,2 | 0 | 3 | 0 | 0,59 | 17 | 9 |
| Asparagi | 25 | 1,2 | 0 | 175 | 0 | 0,3 | 13,8 | 18 |
| Barbabietole rosse crude | 20 | 0,4 | 0 | 101 | 0 | 0,4 | 21 | 7 |
| Basilico fresco | 250 | 5,5 | 0 | 55 | 0 | 0,7 | 64 | 26 |
| Bietola cruda | 67 | 1 | 0 | 85 | 0 | 0,78 | 38 | 24 |
| Broccolo a testa | 28 | 0,8 | 0 | 132 | 0 | 0,6 | 21 | 54 |
| Carciofi | 86 | 1 | 0 | 68 | 0 | 0,8 | 60 | 12 |
| Cardi crudi | 96 | 0,2 | 0 | 28 | 0 | 0,17 | 42 | 4 |
| Carote | 44 | 0,7 | 0 | 10 | 0 | 0,4 | 12,4 | 4 |
| Cavolfiore | 44 | 0,8 | 0 | 71 | 0 | 0,7 | 28 | 59 |
| Cavoli di Bruxelles crudi | 51 | 1,1 | 0 | 100 | 0 | 0,5 | 25 | 81 |
| Cavolo broccolo verde ramoso crudo | 72 | 1,2 | 0 | 90 | 0 | 0,6 | 29 | 77 |
| Cavolo cappuccio rosso crudo | 60 | 1 | 0 | 32 | 0 | 0,3 | 13,3 | 52 |
| Cavolo cappuccio verde crudo | 60 | 1,1 | 0 | 59 | 0 | 0,23 | 13,9 | 47 |
| Cetrioli | 16 | 0,3 | 0 | 9 | 0 | 0,09 | 10,1 | 11 |
| Cicoria catalogna | 74 | 0,7 | 0 | 110 | 0 | 0,3 | 30 | 17 |
| Cicoria da taglio cruda | 150 | 1,5 | 0 | 110 | 0 | 0,2 | 30 | 8 |
| Cicoria di campo cruda | 74 | 0,7 | 0 | 110 | 0 | 0,2 | 30 | 17 |
| Cime di rapa (broccoletti di rapa) crude | 97 | 1,5 | 0 | 170 | 0 | 0,2 | 22 | 110 |
| Cipolla | 25 | 0,4 | 0 | 20 | 0 | 0,3 | 10 | 5 |
| Cipolline | 51 | 0,4 | 0 | 17 | 0 | 0,2 | 10 | 6 |
| Fagiolini | 35 | 0,9 | 0 | 80 | 0 | 0,2 | 28,2 | 16 |
| Finocchio | 45 | 0,4 | 0 | 49 | 0 | 0,1 | 15 | 12 |
| Funghi prataioli coltivati | 10 | 1,2 | 0 | 44 | 0 | 0,4 | 9 | 4 |
| Indivia | 93 | 1,7 | 0 | 156 | 0 | 0,4 | 15 | 35 |
| Indivia belga (cicoria witloof) cruda | 18 | 0,3 | 0 | 14 | 0 | 0,2 | 10 | 3 |
| Lattuga | 45 | 0,8 | 0 | 64 | 0 | 0,2 | 11 | 6 |
| Mais dolce in scatola sgocciolato | 4 | 0,5 | 0 | 45 | 0 | 0,45 | 16 | 7 |
| Melanzane | 14 | 0,3 | 0 | 18 | 0 | 0,2 | 13,5 | 11 |
| Patate | 10 | 0,6 | 0 | 35 | 0 | 0,27 | 23 | 15 |
| Patate dolci | 24 | 0,7 | 0 | 17 | 0 | 0,3 | 19,1 | 23 |
| Peperoni dolci | 17 | 0,7 | 0 | 24 | 0 | 0,2 | 12 | 151 |
| Piselli | 47 | 1,8 | 0 | 62 | 0 | 0,7 | 33 | 28 |
| Pomodori da insalata | 11 | 0,4 | 0 | 14 | 0 | 0,2 | 11 | 21 |
| Pomodori pelati in scatola | 9 | 0,2 | 0 | 10 | 0 | 0,27 | 18,6 | 18 |
| Porri | 54 | 0,8 | 0 | 74 | 0 | 0,2 | 15,7 | 9 |
| Radicchio rosso | 36 | 0,3 | 0 | 13 | 0 | 0,2 | 13 | 10 |
| Rucola | 160 | 1,5 | 0 | 97 | 0 | 0,4 | 47 | 15 |
| Scarola | 37 | 1,3 | 0 | 156 | 0 | 0,14 | 9 | 11 |
| Sedano | 31 | 0,5 | 0 | 38 | 0 | 0,1 | 10,9 | 32 |
| Sedano rapa crudo | 52 | 0,5 | 0 | 51 | 0 | 0,3 | 20 | 6 |
| Spinaci | 78 | 2,9 | 0 | 150 | 0 | 1,43 | 79 | 54 |
| Valerianella (songino) | 38 | 2,2 | 0 | 14 | 0 | 0,6 | 13 | 38 |
| Zucca gialla | 20 | 0,9 | 0 | 10 | 0 | 0,2 | 15 | 9 |
| Zucchine | 21 | 0,5 | 0 | 52 | 0 | 0,2 | 15,3 | 11 |

### Lipidi

| Alimento | Saturi g | Mono g | Poli g | EPA g | DHA g | Col mg |
|---|---:|---:|---:|---:|---:|---:|
| Aglio | 0,1467 | 0,0133 | 0,4 | 0 | 0 | 0 |
| Asparagi | 0,05 | 0,01 | 0,09 | 0 | 0 | 0 |
| Barbabietole rosse crude | 0 | 0 | 0 | 0 | 0 | 0 |
| Basilico fresco | 0,05 | 0,12 | 0,51 | 0 | 0 | 0 |
| Bietola cruda | 0,02 | 0,02 | 0,04 | 0 | 0 | 0 |
| Broccolo a testa | 0,06 | 0,03 | 0,19 | 0 | 0 | 0 |
| Carciofi | 0,05 | 0,01 | 0,08 | 0 | 0 | 0 |
| Cardi crudi | 0,01 | 0,02 | 0,04 | 0 | 0 | 0 |
| Carote | 0 | 0 | 0 | 0 | 0 | 0 |
| Cavolfiore | 0,03 | 0,01 | 0,08 | 0 | 0 | 0 |
| Cavoli di Bruxelles crudi | 0,1 | 0,04 | 0,26 | 0 | 0 | 0 |
| Cavolo broccolo verde ramoso crudo | 0,05 | 0,02 | 0,14 | 0 | 0 | 0 |
| Cavolo cappuccio rosso crudo | 0,03 | 0,01 | 0,1 | 0 | 0 | 0 |
| Cavolo cappuccio verde crudo | 0,01 | 0,01 | 0,05 | 0 | 0 | 0 |
| Cetrioli | 0,17 | 0,01 | 0,23 | 0 | 0 | 0 |
| Cicoria catalogna | 0,12 | 0,01 | 0,22 | 0 | 0 | 0 |
| Cicoria da taglio cruda | 0,02 | 0 | 0,04 | 0 | 0 | 0 |
| Cicoria di campo cruda | 0,05 | 0 | 0,09 | 0 | 0 | 0 |
| Cime di rapa (broccoletti di rapa) crude | 0,07 | 0,02 | 0,12 | 0 | 0 | 0 |
| Cipolla | 0,02 | 0,01 | 0,03 | 0 | 0 | 0 |
| Cipolline | 0,02 | 0,01 | 0,04 | 0 | 0 | 0 |
| Fagiolini | 0,02 | 0 | 0,06 | 0 | 0 | 0 |
| Finocchio | 0 | 0 | 0 | 0 | 0 | 0 |
| Funghi prataioli coltivati | 0,1 | 0,01 | 0,22 | 0 | 0 | 0 |
| Indivia | 0,07 | 0,01 | 0,13 | 0 | 0 | 0 |
| Indivia belga (cicoria witloof) cruda | 0,07 | 0,01 | 0,13 | 0 | 0 | 0 |
| Lattuga | 0,05 | 0,01 | 0,21 | 0 | 0 | 0 |
| Mais dolce in scatola sgocciolato | 0,2 | 0,3 | 0,57 | 0 | 0 | 0 |
| Melanzane | 0,02 | 0,01 | 0,04 | 0 | 0 | 0 |
| Patate | 0,03 | 0,01 | 0,01 | 0 | 0 | 0 |
| Patate dolci | 0,06 | 0,01 | 0,132 | 0 | 0 | 0 |
| Peperoni dolci | 0,05 | 0,02 | 0,16 | 0 | 0 | 0 |
| Piselli | 0,08 | 0,06 | 0,02 | 0 | 0 | 0 |
| Pomodori da insalata | 0,03 | 0,03 | 0,08 | 0 | 0 | 0 |
| Pomodori pelati in scatola | 0,07 | 0,08 | 0,21 | 0 | 0 | 0 |
| Porri | 0,01 | 0 | 0,05 | 0 | 0 | 0 |
| Radicchio rosso | 0,02 | 0 | 0,05 | 0 | 0 | 0 |
| Rucola | 0,09 | 0,05 | 0,32 | 0 | 0 | 0 |
| Scarola | 0,075 | 0 | 0,135 | 0 | 0 | 0 |
| Sedano | 0,05 | 0,04 | 0,1 | 0 | 0 | 0 |
| Sedano rapa crudo | 0,03 | 0,02 | 0,05 | 0 | 0 | 0 |
| Spinaci | 0,07 | 0,05 | 0,42 | 0 | 0 | 0 |
| Valerianella (songino) | 0,05 | 0,01 | 0,21 | 0 | 0 | 0 |
| Zucca gialla | 0,05 | 0,01 | 0,01 | 0 | 0 | 0 |
| Zucchine | 0,02 | 0,01 | 0,04 | 0 | 0 | 0 |

### Fonti

| Alimento | food_id | Fonte | Codice | Verifica | Fonte lipidi |
|---|---|---|---|---|---|
| Aglio | 005000 | CREA+BDA-IEO(proxy folati) | 005000 | 2026-07-26 | BDA-IEO 301_1 |
| Asparagi | 304 | BDA-IEO+USDA | 304 | 2026-07-28 | BDA-IEO 304_1 |
| Barbabietole rosse crude | 005060 | CREA+BDA-IEO(proxy zinco/folati)+USDA | 005060 | 2026-10-01 | BDA-IEO 306_1 |
| Basilico fresco | 006800 | CREA+BDA-IEO+USDA | 006800+8001_1+172232 | 2026-10-28 | BDA-IEO 8001_1 |
| Bietola cruda | 5080 | CREA | 005080 | 2026-07-26 | BDA-IEO 307_1 |
| Broccolo a testa | 309 | BDA-IEO+USDA | 309 | 2026-07-28 | BDA-IEO 309_1 |
| Carciofi | 005120 | CREA+BDA-IEO(proxy zinco/folati)+USDA | 005120 | 2026-10-01 | BDA-IEO 310_1 |
| Cardi crudi | 005140 | CREA+BDA-IEO+USDA | 005140+311_1+169981 | 2026-10-28 | BDA-IEO 311_1 |
| Carote | 312 | BDA-IEO+USDA | 312 | 2026-07-28 | BDA-IEO 312_1 |
| Cavolfiore | 005160 | CREA | 005160 | 2026-07-26 | BDA-IEO 313_1 |
| Cavoli di Bruxelles crudi | 005170 | CREA+BDA-IEO+USDA | 005170+315_1+2685575 | 2026-10-28 | BDA-IEO 315_1 |
| Cavolo broccolo verde ramoso crudo | 005180 | CREA+BDA-IEO | 005180+314_1 | 2026-10-28 | BDA-IEO 314_1 |
| Cavolo cappuccio rosso crudo | 005190 | CREA+BDA-IEO+USDA | 005190+317_1+2346408 | 2026-10-28 | BDA-IEO 317_1 |
| Cavolo cappuccio verde crudo | 005200 | CREA+BDA-IEO+USDA | 005200+316_1+2346407 | 2026-10-28 | BDA-IEO 316_1 |
| Cetrioli | 318 | BDA-IEO+USDA | 318 | 2026-07-28 | BDA-IEO 318_1 |
| Cicoria catalogna | 100171_1 | BDA-IEO+USDA(proxy magnesio) | 100171_1+169992 | 2026-10-28 | BDA-IEO 100171_1 |
| Cicoria da taglio cruda | 005230 | CREA+BDA-IEO+USDA(proxy folati/magnesio) | 005230+320_1+169992 | 2026-10-28 | BDA-IEO 320_1 |
| Cicoria di campo cruda | 005240 | CREA+BDA-IEO+USDA(proxy folati/magnesio) | 005240+319_1+169992 | 2026-10-28 | BDA-IEO 319_1 |
| Cime di rapa (broccoletti di rapa) crude | 005090 | CREA+BDA-IEO+USDA | 005090+308_1+170381 | 2026-10-28 | BDA-IEO 308_1 |
| Cipolla | 005300 | CREA+BDA-IEO(proxy zinco)+USDA | 005300 | 2026-07-28 | BDA-IEO 322_1 |
| Cipolline | 323 | BDA-IEO+USDA(proxy) | 323 | 2026-07-28 | BDA-IEO 323_1 |
| Fagiolini | 101 | BDA-IEO+USDA | 101 | 2026-07-28 | BDA-IEO 101_1 |
| Finocchio | 324 | BDA-IEO+USDA | 324 | 2026-07-28 | BDA-IEO 324_1 |
| Funghi prataioli coltivati | 329 | BDA-IEO+USDA | 329 | 2026-07-28 | BDA-IEO 329_1 |
| Indivia | 005400 | CREA+BDA-IEO+USDA | 005400+330_1+168412 | 2026-10-28 | BDA-IEO 330_1 |
| Indivia belga (cicoria witloof) cruda | 005250 | CREA+BDA-IEO+USDA | 005250+321_1+170404 | 2026-10-28 | BDA-IEO 321_1 |
| Lattuga | 331 | BDA-IEO+USDA(proxy) | 331 | 2026-07-28 | BDA-IEO 331_1 |
| Mais dolce in scatola sgocciolato | 000070 | CREA+BDA-IEO | 000070+9039 | 2026-10-01 | BDA-IEO 9039_2 |
| Melanzane | 334 | BDA-IEO+USDA | 334 | 2026-07-28 | BDA-IEO 334_1 |
| Patate | 381 | BDA-IEO+USDA | 381 | 2026-07-28 | BDA-IEO 381_1 |
| Patate dolci | 50399 | BDA-IEO+USDA | 50399 | 2026-07-28 | BDA-IEO 50399_1 |
| Peperoni dolci | 336 | BDA-IEO+USDA(proxy) | 336 | 2026-07-28 | BDA-IEO 336_1 |
| Piselli | 103 | BDA-IEO+USDA | 103 | 2026-07-28 | BDA-IEO 103_1 |
| Pomodori da insalata | 391 | BDA-IEO+USDA | 391 | 2026-07-28 | BDA-IEO 391_1 |
| Pomodori pelati in scatola | 392 | BDA-IEO+USDA(proxy) | 392 | 2026-07-28 | BDA-IEO 392_1 |
| Porri | 005650 | CREA+BDA-IEO(proxy zinco/folati)+USDA | 005650 | 2026-10-01 | BDA-IEO 337_1 |
| Radicchio rosso | 339 | BDA-IEO+USDA | 339 | 2026-07-28 | BDA-IEO 339_1 |
| Rucola | 700169 | BDA-IEO+USDA | 700169 | 2026-07-28 | BDA-IEO 700169_1 |
| Scarola | 005465 | CREA+BDA-IEO | 005465+100181_1 | 2026-10-28 | BDA-IEO 100181_1 |
| Sedano | 343 | BDA-IEO+USDA | 343 | 2026-07-28 | BDA-IEO 343_1 |
| Sedano rapa crudo | 005690 | CREA+BDA-IEO+USDA | 005690+344_1+170400 | 2026-10-28 | BDA-IEO 344_1 |
| Spinaci | 345 | BDA-IEO+USDA | 345 | 2026-07-28 | BDA-IEO 345_1 |
| Valerianella (songino) | 19072_1 | BDA-IEO+USDA | 19072_1+169219 | 2026-10-28 | BDA-IEO 19072_1 |
| Zucca gialla | 347 | BDA-IEO+USDA(proxy) | 347 | 2026-07-28 | BDA-IEO 347_1 |
| Zucchine | 349 | BDA-IEO+USDA | 349 | 2026-07-28 | BDA-IEO 349_1 |
