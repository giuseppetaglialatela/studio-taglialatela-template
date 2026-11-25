# Registro dei riferimenti clinici

Generato da `riferimenti.py --genera-pagina` da `riferimenti.csv`: non si modifica a mano (il collaudo controlla che coincida). Ogni valore con documento, posizione e frase originale. Si controllano solo i parametri dei profili scelti nel piano: il profilo «generale» (LARN) da solo non dà avvisi, è il termine di confronto, e un profilo lo sostituisce solo se più restrittivo (salvo le righe «sostituisce»). Avvisi, mai blocchi.

Impronta del registro: `35d6a7487ab0`

## generale — popolazione adulta sana (LARN): termine di confronto, da solo non da' avvisi

- `R001` **acidi grassi saturi** ≤ 10 % dell'energia
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 12, tab. 1; p. 5; evidenza: SDT, nessuna classe; popolazione: adulti sani; verificato: 2026-10-28
  - «viene suggerito un SDT <10% En per gli acidi grassi saturi (SFA)»
  - nota: confermato da OMS 2023 (saturi ≤ 10% dell'energia)
- `R002` **acidi grassi trans** (indicazione)
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 12, tab. 1; p. 5; evidenza: SDT, nessuna classe; popolazione: adulti sani; verificato: 2026-10-28
  - «limitazione assoluta degli AG trans» · «Gli AG trans di derivazione naturale dovrebbero comunque limitarsi a valori <1% En»
- `R003` **zuccheri totali** ≤ 15 % dell'energia
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 5; p. 12, tab. 1; evidenza: SDT «in via prudenziale»; popolazione: adulti sani; verificato: 2026-10-28
  - «un SDT per gli zuccheri totali (quelli naturalmente presenti negli alimenti più quelli aggiunti agli alimenti) <15% En, corrispondente all'apporto medio della popolazione italiana»
- `R004` **fibra totale** ≥ 25 g/die
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 4; p. 12, tab. 1; evidenza: SDT, GRADE moderata; popolazione: adulti sani, anche sotto 2000 kcal; verificato: 2026-10-28
  - «è indicato un SDT per la fibra alimentare non inferiore a 25 g/die»
- `R005` **EPA + DHA** ≥ 250 mg/die
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 6; evidenza: RI, adottato da FAO/WHO 2009 ed EFSA 2010; popolazione: adulti; verificato: 2026-10-28
  - «un RI pari a 0,5-2% dell'energia totale della dieta con la precisazione che almeno 250 mg/die vengano introdotti come EPA+DHA»
- `R006` **sodio** ≤ 2000 mg/die
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 7; p. 13, tab. 2; evidenza: SDT, nessuna classe; popolazione: 11-64 anni; verificato: 2026-10-28
  - «Per la popolazione adulta, l'SDT per il sodio è fissato a 2 g/die (87 mmol, corrispondenti a 5 g di sale)»
- `R007` **potassio** ≥ 4500 mg/die
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 1, p. 8-9; p. 13, tab. 2; evidenza: SDT, nessuna classe; popolazione: 11-64 anni; verificato: 2026-10-28
  - «viene indicato anche un SDT per il potassio, corrispondente a 4500 mg/die (circa 120 mmol/die)»
- `R008` **potassio: eccezioni al SDT** (indicazione)
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 9; evidenza: —; popolazione: diabete tipo 1, insufficienza renale cronica o terminale, scompenso grave, insufficienza surrenalica, farmaci risparmiatori di potassio; verificato: 2026-10-28
  - «In questi casi, è opportuna una prescrizione dietetica individualizzata con apporti di K ridotti rispetto a quanto indicato per gli individui sani»

## over65 — 65 anni e oltre (sostituisce i valori generali)

- `R010` **sodio** ≤ 1600 mg/die
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 7; p. 13, tab. 2; evidenza: SDT, nessuna classe; popolazione: 65 anni e oltre; verificato: 2026-10-28
  - «Per i soggetti di età ≥ 65 anni, si consiglia invece una riduzione dell'SDT a 1,6 g/die»
- `R011` **potassio** ≥ 3900 mg/die — **DA_VERIFICARE**
  - SINU, LARN V revisione (2024), Appendici A-D, App. D p. 13, tab. 2; evidenza: SDT; popolazione: 65 anni e oltre; verificato: —
  - nota: valore nella tabella delle estrazioni, frase originale non trascritta: da leggere sulla fonte prima dell'uso
- `R012` **proteine per kg di peso corporeo** ≥ 1 g/kg/die
  - ESPEN practical guideline geriatria (Volkert D et al.), Clin Nutr 2022;41:958-989, Raccomandazione 2 (R2), p. 960; commento alla raccomandazione 81, p. 983; evidenza: R2: grado B, consenso forte 100%; popolazione: 65 anni e oltre, anche in calo di peso; verificato: 2026-11-25
  - «Protein intake in older persons should be at least 1 g protein per kg BW and day. The amount should be individually adjusted with regard to nutritional status, physical activity level, disease status, and tolerance.» · in calo di peso: «assuring a protein intake of at least 1 g/kg BW/d and appropriate intake of micronutrients»
  - nota: Approvato dal nutrizionista il 25/11/2026 (minimo 1,0, nessun massimo). Peso di riferimento (decisione del 25/11/2026): con BMI >= 30 il peso aggiustato = peso a BMI 25 + 25% dell'eccesso (Barazzoni R et al., Clin Nutr 2026;61:106645, SOGLI, Statement 11 p. 5; Statement 14 p. 7: «>1 g protein/kg ABW/day» durante la gestione dell'obesità; nessun grado né metodo di consenso formale; gli autori: apporto ottimale nell'obesità «incompletely defined, especially during weight loss», p. 4); sotto 30 il peso attuale. ESPEN dice solo «BW». Concordante: PROT-AGE (Bauer J et al., JAMDA 2013;14:542-559, riquadro p. 554): «at least in the range of 1.0 to 1.2 g/kg BW/d»; 1,2-1,5 g/kg con malattia acuta o cronica; con eGFR < 30 non in dialisi le proteine vanno limitate (consenso Delphi-like, p. 543-544). Si verifica solo con peso_kg e altezza_cm nei metadati.
- `R013` **calo di peso nell'anziano: quando** (indicazione)
  - ESPEN practical guideline geriatria (Volkert D et al.), Clin Nutr 2022;41:958-989, Raccomandazioni 79-80, pp. 982-983; evidenza: R79 (R54): GPP, consenso forte 95%; R80 (R55): GPP, consenso forte 100%; popolazione: 65 anni e oltre in sovrappeso o con obesità; verificato: 2026-11-25
  - «In overweight older persons, weight-reducing diets shall be avoided in order to prevent loss of muscle mass and accompanying functional decline.» · «In obese older persons with weight-related health problems, weight-reducing diets shall only be considered after careful and individual weighing of benefits and risks.»
- `R014` **calo di peso nell'anziano: come (deficit, apporto minimo, velocità, esercizio)** (indicazione)
  - ESPEN practical guideline geriatria (Volkert D et al.), Clin Nutr 2022;41:958-989, Raccomandazioni 81-82 e commento, p. 983; evidenza: R81 (R56): GPP, consenso forte 95%; R82 (R57): grado A, consenso forte 100%; popolazione: 65 anni e oltre con obesità; verificato: 2026-11-25
  - «If weight reduction is considered in obese older persons, energy restriction shall be only moderate in order to achieve a slow weight reduction and preserve muscle mass.» · «a maximally moderate caloric restriction (~500 kcal/d less than estimated needs and maintaining a minimum intake of 1000–1200 kcal/d) targeting a weight loss of 0.25–1 kg/ week» · «If weight reduction is considered in obese older persons, dietary interventions shall be combined with physical exercise whenever possible in order to preserve muscle mass.»

## ipercolesterolemia — ipercolesterolemia / LDL elevato

- `R020` **acidi grassi saturi** ≤ 7 % dell'energia
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.2, p. 136; evidenza: nessuna classe; tab. 8: effetto ++ su LDL-C, livello A; popolazione: ipercolesterolemia; verificato: 2026-10-30
  - «its consumption should be <10% of the total caloric intake and should be further reduced (<7% of energy) in the presence of hypercholesterolaemia»
  - nota: 2025 Focused Update: dieta invariata (verificato il 30/10/2026)
- `R021` **colesterolo alimentare** ≤ 300 mg/die
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.2, p. 136; evidenza: nessuna classe; tab. 8: effetto +, livello B; popolazione: colesterolo plasmatico alto; verificato: 2026-10-30
  - «The cholesterol intake in the diet should be reduced (<300 mg/day), particularly in people with high plasma cholesterol levels»
  - nota: il LARN V non ha un SDT per il colesterolo
- `R022` **fibra totale** 25-40 g/die
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.3, p. 136; evidenza: nessuna classe; tab. 8: effetto ++, livello A; popolazione: controllo dei lipidi plasmatici; verificato: 2026-10-30
  - «a fat-modified diet that provides 25–40 g per day of total dietary fibre, including ≥7–13 g of soluble fibre, is well tolerated, effective, and recommended for plasma lipid control»
- `R023` **fibra solubile** ≥ 7 g/die
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.3, p. 136; evidenza: nessuna classe; tab. 8: effetto ++, livello A; popolazione: controllo dei lipidi plasmatici; verificato: 2026-10-30
  - «a fat-modified diet that provides 25–40 g per day of total dietary fibre, including ≥7–13 g of soluble fibre, is well tolerated, effective, and recommended for plasma lipid control»
- `R024` **carboidrati** 45-55 % dell'energia
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.3, p. 136; evidenza: nessuna classe; popolazione: dislipidemie; verificato: 2026-10-28
  - «Carbohydrate intake should range between 45–55% of total energy intake»
- `R025` **zuccheri aggiunti** ≤ 10 % dell'energia
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.3, p. 136; evidenza: nessuna classe; tab. 8 (mono- e disaccaridi su TG): ++, B; popolazione: dislipidemie; verificato: 2026-10-28
  - «Intake of added sugar should not exceed 10% of total energy (in addition to the amount present in natural foods such as fruits and dairy products); more restrictive advice concerning sugars may be useful for those needing to lose weight or with high plasma TG values, MetS, or DM»
- `R026` **acidi grassi trans** (indicazione)
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.2, p. 135; evidenza: tab. 8: ++, A; popolazione: dislipidemie; verificato: 2026-10-28
  - «Avoiding any consumption of trans fat is a key measure of the dietary prevention of CVD»
- `R027` **alcol** ≤ 10 g/die
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.4, p. 136; evidenza: nessuna classe; popolazione: chi beve già, con trigliceridi non elevati; verificato: 2026-10-28
  - «Moderate alcohol consumption [≤10 g/day (1 unit) for men and women] is acceptable for those who drink alcoholic beverages, if TG levels are not elevated»
- `R028` **grassi totali** (indicazione)
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, p. 136; evidenza: nessuna classe; popolazione: dislipidemie; verificato: 2026-10-28
  - «fat intakes >35–40% of calories are generally associated with increased intakes of both saturated fat and calories»

## ipertrigliceridemia — trigliceridi elevati

- `R030` **fruttosio** ≤ 10 % dell'energia
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.2, p. 135; evidenza: nessuna classe; popolazione: ipertrigliceridemia, obesità addominale; verificato: 2026-10-28
  - «Habitual consumption of significant amounts (>10% energy) of dietary fructose contributes to TG elevation»
- `R031` **zuccheri aggiunti** ≤ 10 % dell'energia
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.4.3, p. 136; evidenza: nessuna classe; tab. 8 (mono- e disaccaridi su TG): ++, B; popolazione: trigliceridi elevati: consiglio più restrittivo senza numero; verificato: 2026-10-28
  - «Intake of added sugar should not exceed 10% of total energy (in addition to the amount present in natural foods such as fruits and dairy products); more restrictive advice concerning sugars may be useful for those needing to lose weight or with high plasma TG values, MetS, or DM»
- `R032` **alcol** (indicazione)
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, tab. 8, p. 134; evidenza: tab. 8: effetto +++ sui TG, livello A; popolazione: ipertrigliceridemia; verificato: 2026-10-30
  - «Reduce alcohol intake»
- `R033` **pesce ed EPA+DHA: la dose da 2-3 g/die è farmacologica, non alimentare** (indicazione)
  - ESC/EAS 2019 dislipidemie, Eur Heart J 2020;41:111-188, §7.5.6, p. 137; evidenza: nessuna classe per la dieta; popolazione: ipertrigliceridemia; verificato: 2026-10-28
  - «consumption of fish (at least twice a week) … Pharmacological doses of long-chain n-3 fatty acids (2–3 g/day) reduce TG levels by about 30%»

## ipertensione — pressione elevata o ipertensione

- `R040` **sodio** ≤ 2000 mg/die
  - ESC 2024 ipertensione, Eur Heart J 2024;45:3912-4018, Recommendation Table 15, p. 3958; testo p. 3955; evidenza: I, A; popolazione: adulti con pressione elevata o ipertensione; verificato: 2026-10-28
  - «Restriction of sodium to approximately 2 g per day is recommended where possible in all adults with elevated BP and hypertension» · «This includes added salt and salt already contained in food»
- `R041` **alcol** ≤ 100 g/settimana
  - ESC 2024 ipertensione, Eur Heart J 2024;45:3912-4018, Recommendation Table 15, p. 3958; evidenza: I, B; popolazione: tutti; verificato: 2026-10-28
  - «recommended to drink less alcohol than the upper limit, which is about 100 g/week of pure alcohol … Preferably, it is recommended to avoid alcohol»
- `R042` **zuccheri liberi** ≤ 10 % dell'energia
  - ESC 2024 ipertensione, Eur Heart J 2024;45:3912-4018, Recommendation Table 15, p. 3958; evidenza: I, B; popolazione: tutti; verificato: 2026-10-28
  - «It is recommended to restrict free sugar consumption, in particular sugar-sweetened beverages, to a maximum of 10% of energy intake»
- `R043` **potassio** (indicazione)
  - ESC 2024 ipertensione, Eur Heart J 2024;45:3912-4018, Recommendation Table 15, p. 3958; evidenza: IIa, A; popolazione: ipertesi con sodio alto, senza malattia renale cronica moderata-avanzata; verificato: 2026-10-28
  - «an increase of potassium intake by 0.5–1.0 g/day … should be considered»
- `R044` **potassio: sorveglianza** (indicazione)
  - ESC 2024 ipertensione, Eur Heart J 2024;45:3912-4018, Recommendation Table 15, p. 3958 (ripresa a p. 3921); evidenza: IIa, C; popolazione: malattia renale cronica, diuretici risparmiatori di potassio, ACE-inibitori, sartani, spironolattone; verificato: 2026-10-28
  - «monitoring serum levels of potassium should be considered if dietary potassium is being increased»

## masld — steatosi epatica metabolica (MASLD)

- `R060` **calo di peso** (indicazione)
  - EASL-EASD-EASO 2024 MASLD (sintesi), Diabetologia 2024;67:2375-2392, p. 2384; evidenza: LoE 2, forte, consenso forte; popolazione: MASLD con sovrappeso; verificato: 2026-10-28
  - «should aim at a sustained reduction of ≥5% to reduce liver fat, 7–10% to improve liver inflammation and ≥10% to improve fibrosis»
- `R061` **qualità della dieta** (indicazione)
  - EASL-EASD-EASO 2024 MASLD (sintesi), Diabetologia 2024;67:2375-2392, p. 2384; evidenza: LoE 2, forte, consenso forte; popolazione: MASLD; verificato: 2026-10-28
  - «improving diet quality (similar to the Mediterranean dietary pattern), limiting the consumption of ultra-processed food (rich in sugars and saturated fat) and avoiding sugar-sweetened beverages should be recommended»
- `R062` **alcol** (indicazione)
  - EASL-EASD-EASO 2024 MASLD (sintesi), Diabetologia 2024;67:2375-2392, p. 2378; evidenza: LoE 3, forte; popolazione: MASLD; verificato: 2026-10-28
  - «should be discouraged from consuming alcohol» · «All alcohol consumption should be stopped completely and permanently in individuals with advanced fibrosis or cirrhosis»

## diabete_t2 — diabete tipo 2

- `R050` **fibra totale** ≥ 35 g/die
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 969; evidenza: certezza moderata; popolazione: diabete; verificato: 2026-10-28
  - «Dietary fibre intake should be at least 35 g per day (4 g per 1000 kJ)»
- `R051` **zuccheri liberi** ≤ 10 % dell'energia
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 969; evidenza: certezza moderata; popolazione: diabete; verificato: 2026-10-28
  - «Intakes of free or added sugars should be below 10% of total energy intake»
- `R052` **acidi grassi saturi** ≤ 10 % dell'energia
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 971; evidenza: certezza bassa; popolazione: diabete; verificato: 2026-10-28
  - «Saturated- and trans-fat intakes should comprise <10% and <1% of total energy, respectively»
- `R053` **acidi grassi trans** ≤ 1 % dell'energia
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 971; evidenza: certezza bassa; popolazione: diabete; verificato: 2026-10-28
  - «Saturated- and trans-fat intakes should comprise <10% and <1% of total energy, respectively»
- `R054` **proteine** 10-20 % dell'energia
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 972; evidenza: certezza bassa; popolazione: eGFR > 60; con dieta di calo di peso fino a 12 mesi ammesso 23-32%; verificato: 2026-10-28
  - «a protein intake of 10–20% total energy is recommended» · «a protein intake of 23–32% may be recommended in the short term (up to 12 months) in the context of a weight-loss diet»
  - nota: in un piano di calo di peso l'avviso oltre il 20% va letto con la seconda frase
- `R055` **alcol** (indicazione)
  - EASD DNSG 2023, Diabetologia 2023;66:965-985, p. 967; evidenza: commento, senza grado; popolazione: tutti; verificato: 2026-10-28
  - «we do not recommend alcohol consumption at any level»

## obesita — obesità

linea guida SIO/ISS 2026 (Eat Weight Disord 2026;31:9) letta per intero il 25/11/2026: nessun valore numerico sui nutrienti, solo indicazioni

- `R080` **intervento strutturato sullo stile di vita** (indicazione)
  - Linea guida SIO/ISS obesità (Barazzoni R et al.), Eat Weight Disord 2026;31:9, doi 10.1007/s40519-026-01813-z, PICO 5, p. 5; Tabella 1, p. 3; evidenza: forte a favore, qualità delle evidenze moderata; popolazione: adulti con BMI ≥ 25 (la linea guida si applica da BMI 27); verificato: 2026-11-25
  - «We recommend, in subjects with BMI≥25 kg/m2, structured lifestyle rather than non-structured lifestyle interventions in overweight and obesity management»
- `R081` **dieta chetogenica (discordanza nella fonte: la Tabella 1 a p. 3 dice «We do not recommend», il testo a p. 6 «We do not suggest»; il grado è condizionato in entrambi)** (indicazione)
  - Linea guida SIO/ISS obesità (Barazzoni R et al.), Eat Weight Disord 2026;31:9, doi 10.1007/s40519-026-01813-z, PICO 7, p. 6; Tabella 1, p. 3; evidenza: condizionata contro, qualità delle evidenze molto bassa; popolazione: adulti con BMI ≥ 25; verificato: 2026-11-25
  - «We do not suggest in subjects with BMI≥25 kg/m2 to routinely adopt a ketogenic diet versus balanced macronutrient diets (e.g., Mediterranean diet) for overweight and obesity treatment»
- `R082` **obiettivo di calo di peso (il quesito riguarda il calo con farmaci o chirurgia; esito: benessere psicologico)** (indicazione)
  - Linea guida SIO/ISS obesità (Barazzoni R et al.), Eat Weight Disord 2026;31:9, doi 10.1007/s40519-026-01813-z, PICO 13, p. 8; Tabella 1, p. 4; evidenza: forte a favore, qualità delle evidenze moderata; popolazione: adulti con BMI ≥ 30; verificato: 2026-11-25
  - «We recommend in subjects with BMI≥30 kg/m2 a weight loss of at least 5% to achieve (or maintain) a psychological well-being»

## sportivo_forza — allenamento di forza o ipertrofia

- `R070` **proteine per kg di peso corporeo** ≥ 1,6 g/kg/die
  - Morton RW et al., Br J Sports Med 2018;52:376-384, doi 10.1136/bjsports-2017-097608, Risultati, «Break point analysis», p. 6 di 10; Abstract, «Summary/conclusion», p. 1 di 10; evidenza: meta-analisi e meta-regressione di RCT (49 studi, 1.863 partecipanti); break point non significativo (p=0,079); popolazione: adulti sani in allenamento di forza di almeno 6 settimane; verificato: 2026-11-22
  - «break point=1.62 (1.03, 2.20) g/kg/day» · «With protein supplementation, protein intakes at amounts greater than ~1.6 g/kg/day do not further contribute RET-induced gains in FFM»
  - nota: Approvato dal nutrizionista il 22/11/2026 (minimo 1,6, nessun massimo). Limite superiore lasciato vuoto: 2,2 g/kg/die e' il limite superiore dell'intervallo di confidenza, non un tetto di sicurezza. Concordanti: ISSN 2017 (J Int Soc Sports Nutr 14:20, 1,4-2,0 g/kg/die); Nunes 2022 (J Cachexia Sarcopenia Muscle 13:795, forza maggiore da 1,6 g/kg/die). In deficit energetico la relazione resta lineare (Refalo 2025, Strength Cond J): 1,6 e' un minimo, non un tetto. Il motore non conosce il peso: si mostra, non si controlla
