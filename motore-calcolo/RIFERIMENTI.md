# Registro dei riferimenti clinici

Generato da `riferimenti.py --genera-pagina` da `riferimenti.csv`: non si modifica a mano (il collaudo controlla che coincida). Ogni valore con documento, posizione e frase originale. Si controllano solo i parametri dei profili scelti nel piano: il profilo «generale» (LARN) da solo non dà avvisi, è il termine di confronto, e un profilo lo sostituisce solo se più restrittivo (salvo le righe «sostituisce»). Avvisi, mai blocchi.

Impronta del registro: `7f5db1f99598`

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

linea guida SIO/ISS 2026 (Eat Weight Disord 2026;31:9) non ancora letta: nessun riferimento caricato

Nessuna riga.
