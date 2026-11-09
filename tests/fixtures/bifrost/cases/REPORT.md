# Bifrost: case catalogue

Every case in [`tests/cases.yaml`](../../../cases.yaml) run through the Bifrost core.
Stednavne match on the name before " (" because Bifrost has no subtype (#1).

- Source: recorded fixtures (2026-11-06, 2026-11-08), replayed through the current core
- Generated: 2026-11-09T12:31:02+00:00
- Cases: 69.
- Bifrost: 36 pass, 21 known gaps (xfail), 11 pass despite a known gap (xpass), 0 fail, 1 without expectation.

✅ pass · ⚠️ known gap · 🎉 passes despite a known gap · ❌ unexpected failure

| Case | Typed | Expected | Bifrost | Known gap |
|---|---|---|---|---|
| [adr-vangebovej-71](#adr-vangebovej-71) | `Vangebovej 71` | Vangebovej 71, Søllerød, 2840 Holte | ✅ rank 1 |  |
| [adr-vangebovej-71-alle-typer](#adr-vangebovej-71-alle-typer) | `Vangebovej 71` | Vangebovej 71, Søllerød, 2840 Holte | ✅ rank 1 |  |
| [adr-vangebovej-71-soelleroed](#adr-vangebovej-71-soelleroed) | `vangebovej 71 søllerød` | Vangebovej 71, Søllerød, 2840 Holte | ✅ rank 1 |  |
| [adr-raadhuspladsen-1](#adr-raadhuspladsen-1) | `rådhuspladsen 1` | Rådhuspladsen 1, 1550 København V (top 3) | ✅ rank 1 |  |
| [adr-raadhuspladsen-1-versaler](#adr-raadhuspladsen-1-versaler) | `RÅDHUSPLADSEN 1` | Rådhuspladsen 1, 1550 København V (top 3) | ✅ rank 1 |  |
| [adr-raadhuspl](#adr-raadhuspl) | `rådhuspl` | Rådhuspladsen 1, 1550 København V (top 3) | ⚠️ 'Rådhuspladsen 1, 1550 København V' not found | #3 |
| [adr-noerrebrog-1](#adr-noerrebrog-1) | `nørrebrog 1` | Nørrebrogade 1, 2200 København N (top 3) | ⚠️ 'Nørrebrogade 1, 2200 København N' not found | #3 |
| [adr-noerrebrog](#adr-noerrebrog) | `nørrebrog` | Nørrebrogade 1, 2200 København N (top 5) | ⚠️ 'Nørrebrogade 1, 2200 København N' not found | #3 |
| [adr-vangeb](#adr-vangeb) | `vangeb` | Vangeboled 1, Søllerød, 2840 Holte (top 5) | ⚠️ 'Vangeboled 1, Søllerød, 2840 Holte' not found | #3 |
| [adr-vangeb-77](#adr-vangeb-77) | `vangeb 77` | Vangebovej 77, Søllerød, 2840 Holte | ⚠️ 'Vangebovej 77, Søllerød, 2840 Holte' not found | #3 |
| [adr-77-vangeb](#adr-77-vangeb) | `77 vangeb` | Vangebovej 77, Søllerød, 2840 Holte | ⚠️ 'Vangebovej 77, Søllerød, 2840 Holte' not found | #3 |
| [adr-14-oesterlund](#adr-14-oesterlund) | `14 østerlund` | Østerlund 14, 9870 Sindal (top 2) | ⚠️ 'Østerlund 14, 9870 Sindal' not found | #33 |
| [adr-oesterlund-14](#adr-oesterlund-14) | `østerlund 14` | Østerlund 14, 9870 Sindal (top 2) | ✅ rank 2 |  |
| [adr-77-vangebovej](#adr-77-vangebovej) | `77 vangebovej` | Vangebovej 77, Søllerød, 2840 Holte | ✅ rank 1 |  |
| [adr-1-noerrebrogade](#adr-1-noerrebrogade) | `1 nørrebrogade` | Nørrebrogade 1, 2200 København N (top 5) | ⚠️ 'Nørrebrogade 1, 2200 København N' not found | #33 |
| [adr-noerrebrogade-vejnavn](#adr-noerrebrogade-vejnavn) | `Nørrebrogade` | Nørrebrogade 1, 2200 København N (top 10) → Bifrost: Nørrebrogade (2200 København N) (top 10) | ✅ rank 4 |  |
| [adr-vestergade-21-aarhus](#adr-vestergade-21-aarhus) | `vestergade 21 aarhus` | Vestergade 21, 8000 Aarhus C | ✅ rank 1 |  |
| [adr-vestergade-21-aar](#adr-vestergade-21-aar) | `vestergade 21 aar` | Vestergade 21, 8000 Aarhus C (top 3) | 🎉 rank 2 | #3 |
| [adr-skodsb](#adr-skodsb) | `skodsb` | Skodsborg Strandvej 1, 2942 Skodsborg (top 5) | ⚠️ 'Skodsborg Strandvej 1, 2942 Skodsborg' not found | #3 |
| [adr-skodsborgvej-41](#adr-skodsborgvej-41) | `skodsborgvej 41` | Skodsborgvej 41, 2830 Virum (top 3) | ✅ rank 1 |  |
| [adr-skodsborgvej-414](#adr-skodsborgvej-414) | `skodsborgvej 414` | Skodsborgvej 414, 2942 Skodsborg (top 3) | ✅ rank 1 |  |
| [adr-frederiksberggade-1a](#adr-frederiksberggade-1a) | `frederiksberggade 1a` | Frederiksberggade 1A, 1459 København K | ✅ rank 1 |  |
| [adr-noeddebogade-1-st-th](#adr-noeddebogade-1-st-th) | `nøddebogade 1 st th` | (no rows) → Bifrost: Nøddebogade 1, st. th, 2200 København N | ✅ rank 1 |  |
| [ste-skagen](#ste-skagen) | `skagen` | Skagen (By i Frederikshavn Kommune) (top 10) | ✅ rank 5 (name only, #1) | #1 |
| [ste-skag](#ste-skag) | `ste: skag` | Skagen (By i Frederikshavn Kommune) (top 10) | 🎉 rank 1 (name only, #1) | #3 |
| [ste-mols-bjerge](#ste-mols-bjerge) | `mols bjerge` | Mols Bjerge (Højdedrag i Knebel) (top 10) | ✅ rank 6 (name only, #1) | #1 |
| [ste-gudenaa](#ste-gudenaa) | `gudenå` | Gudenå (Vandløb i Vonge) (top 3) | ✅ rank 1 (name only, #1) | #1 |
| [ste-vendsyssel](#ste-vendsyssel) | `ste: vendsyssel` | Vendsyssel (Landsdel i Region Nordjylland) (top 3) | ✅ rank 1 (name only, #1) | #1 |
| [ste-skodsborg](#ste-skodsborg) | `ste: skodsborg` | Skodsborg (By i Rudersdal Kommune) (top 3) | ✅ rank 1 (name only, #1) | #1 |
| [ste-raadhuspladsen](#ste-raadhuspladsen) | `ste: rådhuspladsen` | Rådhuspladsen (Seværdighed i København V) (top 3) | ✅ rank 1 (name only, #1) | #1 |
| [ste-oeenslaeger](#ste-oeenslaeger) | `ste: øenslæger` | Oehlenschlägers Bøg (Løvtræ i Tranekær) (top 3) | ⚠️ 'Oehlenschlägers Bøg (Løvtræ i Tranekær)' not found | #34 |
| [ste-oeenslaeger-alle-typer](#ste-oeenslaeger-alle-typer) | `øenslæger` | Oehlenschlægersgade 1, 1663 København V (top 5) | ⚠️ 'Oehlenschlægersgade 1, 1663 København V' not found | #34 |
| [ste-tivoli](#ste-tivoli) | `tivoli` | Tivoli (Forlystelsespark i København V) (top 5) | ✅ rank 1 (name only, #1) | #1 |
| [ste-anholt](#ste-anholt) | `anholt` | Anholt (Ø i Kattegat) (top 5) | ✅ rank 1 (name only, #1) | #1 |
| [ste-roskilde-fjord](#ste-roskilde-fjord) | `roskilde fjord` | Roskilde Fjord (Fjord i Isefjord) | ✅ rank 1 (name only, #1) | #1 |
| [ste-gudenaa-kommunefilter-730](#ste-gudenaa-kommunefilter-730) | `ste: gudenå` | Gudenå (Vandløb i Vonge) (top 5) | ⚠️ 'Gudenå (Vandløb i Vonge)' not found | #35 |
| [ste-vor-frue-kommunefilter](#ste-vor-frue-kommunefilter) | `vor frue` | Vor Frue Kirke (Kirke i København K) (top 5) | 🎉 rank 1 (name only, #1) | #2 |
| [pos-8000](#pos-8000) | `8000` | 8000 Aarhus C (top 10) | ✅ rank 1 |  |
| [pos-80](#pos-80) | `pos: 80` | 8000 Aarhus C (top 3) | ⚠️ '8000 Aarhus C' not found | #3 |
| [pos-aarhus](#pos-aarhus) | `aarhus` | 8000 Aarhus C (top 3) | ✅ rank 1 |  |
| [pos-aar](#pos-aar) | `pos: aar` | 8000 Aarhus C (top 5) | 🎉 rank 5 | #3 |
| [pos-aabenraa-aa](#pos-aabenraa-aa) | `pos: åbenrå` | 6200 Aabenraa | ✅ rank 1 |  |
| [mat-5a](#mat-5a) | `5a` | 5a, Kirke Sonnerup By, Kirke Sonnerup (top 5) | ⚠️ '5a, Kirke Sonnerup By, Kirke Sonnerup' not found | #4 |
| [mat-1a-soenderby](#mat-1a-soenderby) | `1a sønderby` | 1a, Sønderby, Kegnæs (top 3) | ⚠️ '1a, Sønderby, Kegnæs' not found | #4 |
| [mat-162-vestervold](#mat-162-vestervold) | `162 vestervold` | 162, Vestervold Kvarter, København | 🎉 rank 1 | #4 |
| [mat-162-vesterv](#mat-162-vesterv) | `mat: 162 vesterv` | 162, Vestervold Kvarter, København | ⚠️ '162, Vestervold Kvarter, København' not found | #3 |
| [mat-bfe-6033528](#mat-bfe-6033528) | `6033528` | 162, Vestervold Kvarter, København | 🎉 rank 1 | #4 |
| [mat-3kg-soell](#mat-3kg-soell) | `mat: 3kg søll` | 3kg, Øverød By, Søllerød (top 2) | ⚠️ '3kg, Øverød By, Søllerød' not found | #4 |
| [mat-3kg-soelleroed](#mat-3kg-soelleroed) | `3kg søllerød` | 3kg, Søllerød By, Søllerød (top 2) | 🎉 rank 1 | #4 |
| [mat-3kg](#mat-3kg) | `mat: 3kg` | 3kg, Øverød By, Søllerød (top 40) | 🎉 rank 3 | #4 |
| [mat-1a-kommunefilter-615](#mat-1a-kommunefilter-615) | `1a` | 1a, Nim By, Nim (top 3) | ⚠️ '1a, Nim By, Nim' not found | #2 |
| [mat-1an-gentofte](#mat-1an-gentofte) | `mat: 1an gentofte` | (no rows) | ⚠️ expected no rows, got 40 | #4 |
| [kom-101](#kom-101) | `kom: 101` | Københavns Kommune | ✅ rank 1 |  |
| [kom-koeb](#kom-koeb) | `kom: køb` | Københavns Kommune | ⚠️ rank 2 > 1 | #3 |
| [kom-aarhus-alle-typer](#kom-aarhus-alle-typer) | `aarhus` | Aarhus Kommune (top 20) | ✅ rank 11 |  |
| [kom-aabenraa-aa](#kom-aabenraa-aa) | `kommune: åbenrå` | Aabenraa Kommune | ✅ rank 1 |  |
| [ops-aarhus](#ops-aarhus) | `ops: aarhus` | Aarhus Nordkredsen (top 3) | ✅ rank 2 |  |
| [ops-aar](#ops-aar) | `ops: aar` | Aarhus Nordkredsen (top 5) | 🎉 rank 2 | #3 |
| [pol-midt](#pol-midt) | `pol: midt` | Midt- og Vestjyllands Politikreds | ✅ rank 1 |  |
| [pol-koebenhavn](#pol-koebenhavn) | `københavn` | Københavns Politikreds | ✅ rank 1 |  |
| [reg-midt](#reg-midt) | `reg: midt` | Region Midtjylland | ✅ rank 1 |  |
| [reg-hovedstaden-alle-typer](#reg-hovedstaden-alle-typer) | `hovedstaden` | Region Hovedstaden (top 20) | ✅ rank 6 |  |
| [pfx-kom-aar](#pfx-kom-aar) | `kom: aar` | Aarhus Kommune (top 3) | 🎉 rank 1 | #3 |
| [pfx-adr-versaler-uden-mellemrum](#pfx-adr-versaler-uden-mellemrum) | `ADR:vangebovej 71` | Vangebovej 71, Søllerød, 2840 Holte | ✅ rank 1 |  |
| [pfx-ukendt-praefiks](#pfx-ukendt-praefiks) | `udg: 1an gentofte` | Husnumre - Der skete en fejl → Bifrost: none | ➖ no expectation |  |
| [pfx-kun-praefiks](#pfx-kun-praefiks) | `adr:` | (no rows) | ✅ no rows |  |
| [kf-vestergade-751](#kf-vestergade-751) | `vestergade` | Vestergade 1B, 8000 Aarhus C (top 3) | ⚠️ 'Vestergade 1B, 8000 Aarhus C' not found | #3 |
| [kf-vestergade-1-101](#kf-vestergade-1-101) | `vestergade 1` | Vestergade 1, 1456 København K | ✅ rank 1 |  |
| [kf-lyngby-230-173](#kf-lyngby-230-173) | `lyngby` | 2800 Kongens Lyngby (top 20) | 🎉 rank 11 | #2 |

## Cases

### adr-vangebovej-71

*Brugeren vil finde Vangebovej 71 og zoome til adressen*

- Typed: `Vangebovej 71`
- Expected: Vangebovej 71, Søllerød, 2840 Holte (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 314 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vangebovej 71, Søllerød, 2840 Holte** |
| 2 | adr: Vangebovej 31, Søllerød, 2840 Holte |
| 3 | adr: Vangebovej 41, Søllerød, 2840 Holte |
| 4 | adr: Vangebovej 51, Søllerød, 2840 Holte |
| 5 | adr: Vangebovej 61, Søllerød, 2840 Holte |
| 6 | adr: Vangebovej 73, Søllerød, 2840 Holte |
| 7 | adr: Vangebovej 75, Søllerød, 2840 Holte |
| 8 | adr: Vangebovej 77, Søllerød, 2840 Holte |
| 9 | adr: Vangebovej 79, Søllerød, 2840 Holte |
| 10 | adr: Vangebovej 81, Søllerød, 2840 Holte |
| | … 10 more |

### adr-vangebovej-71-alle-typer

*Brugeren har alle typer slået til og vil finde Vangebovej 71*

- Typed: `Vangebovej 71`
- Expected: Vangebovej 71, Søllerød, 2840 Holte (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 188 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vangebovej 71, Søllerød, 2840 Holte** |
| 2 | adr: Vangebovej 31, Søllerød, 2840 Holte |
| 3 | adr: Vangebovej 41, Søllerød, 2840 Holte |
| 4 | adr: Vangebovej 51, Søllerød, 2840 Holte |
| 5 | adr: Vangebovej 61, Søllerød, 2840 Holte |
| 6 | ste: Vangebovej (bygning, Rudersdal) |
| 7 | ste: Vangebo (bygning, Helsingør) |
| 8 | ste: Vange (bygning, Tønder) |
| 9 | ste: Vangen (bygning, Hedensted) |
| 10 | ste: Vangen (bygning, Vesthimmerlands) |
| | … 16 more |

### adr-vangebovej-71-soelleroed

*Brugeren skriver det supplerende bynavn med for at finde Vangebovej 71*

- Typed: `vangebovej 71 søllerød`
- Expected: Vangebovej 71, Søllerød, 2840 Holte (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 309 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vangebovej 71, Søllerød, 2840 Holte** |
| 2 | adr: Vangebovej 31, Søllerød, 2840 Holte |
| 3 | adr: Vangebovej 41, Søllerød, 2840 Holte |
| 4 | adr: Vangebovej 51, Søllerød, 2840 Holte |
| 5 | adr: Vangebovej 61, Søllerød, 2840 Holte |
| 6 | ste: Søllerød (bebyggelse, Rudersdal) |
| 7 | ste: Vangebovej (bygning, Rudersdal) |
| 8 | ste: Søllerød Sø (sø, Rudersdal) |
| 9 | ste: Søllerød Slot (bygning, Rudersdal) |
| 10 | ste: Skallerød Vang (naturareal, Hillerød) |
| | … 15 more |

### adr-raadhuspladsen-1

*Brugeren vil finde Københavns Rådhus på Rådhuspladsen 1*

- Typed: `rådhuspladsen 1`
- Expected: Rådhuspladsen 1, 1550 København V (top 3) (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 955 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Rådhuspladsen 1, 1550 København V** |
| 2 | adr: Rådhuspladsen 1, 3300 Frederiksværk |
| 3 | adr: Rådhuspladsen 1, 4200 Slagelse |
| 4 | adr: Rådhuspladsen 1, 4300 Holbæk |
| 5 | adr: Rådhuspladsen 1, Otterup, 5450 Otterup |
| 6 | ste: Rådhuspladsen (seværdighed, København) |
| 7 | ste: Rådhuspladsen (seværdighed, Gladsaxe) |
| 8 | ste: Rådhuspladsen (standsningssted, København) |
| 9 | ste: H.C. Andersen - Rådhuspladsen (seværdighed, København) |
| 10 | ste: Domhuspladsen (seværdighed, Høje-Taastrup) |
| | … 6 more |

### adr-raadhuspladsen-1-versaler

*Brugeren skriver adressen med store bogstaver*

- Typed: `RÅDHUSPLADSEN 1`
- Expected: Rådhuspladsen 1, 1550 København V (top 3) (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 191 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Rådhuspladsen 1, 1550 København V** |
| 2 | adr: Rådhuspladsen 1, 3300 Frederiksværk |
| 3 | adr: Rådhuspladsen 1, 4200 Slagelse |
| 4 | adr: Rådhuspladsen 1, 4300 Holbæk |
| 5 | adr: Rådhuspladsen 1, Otterup, 5450 Otterup |
| 6 | adr: Rådhuspladsen 1, 8000 Aarhus C |
| 7 | adr: Rådhuspladsen 1, 8362 Hørning |
| 8 | adr: Rådhuspladsen 1, 9300 Sæby |
| 9 | adr: Rådhuspladsen 1B, 1., 8000 Aarhus C |
| 10 | adr: Rådhuspladsen 1C, 8000 Aarhus C |
| | … 10 more |

### adr-raadhuspl

*Brugeren vil finde Rådhuspladsen 1 i København og har kun nået at skrive en del af vejnavnet*

- Typed: `rådhuspl`
- Expected: Rådhuspladsen 1, 1550 København V (top 3) (point)
- Bifrost: ⚠️ known gap — 'Rådhuspladsen 1, 1550 København V' not found
- Slowest search request: 490 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Rådhuspladsen |
| 2 | adr: Rådhuspladsen (4660 Store Heddinge) |
| 3 | adr: Rådhuspladsen (4300 Holbæk) |
| 4 | adr: Rådhuspladsen (5450 Otterup) |
| 5 | adr: Rådhuspladsen (3300 Frederiksværk) |
| 6 | ste: Rådhuspladsen (seværdighed, København) |
| 7 | ste: Rådhuspladsen (seværdighed, Gladsaxe) |
| 8 | ste: Rådhuspladsen (standsningssted, København) |
| 9 | ste: Rådhuset (bygning, København) |
| 10 | ste: Rådhusparken (naturareal, Horsens) |
| | … 12 more |

### adr-noerrebrog-1

*Brugeren vil finde Nørrebrogade 1 og forkorter vejnavnet*

- Typed: `nørrebrog 1`
- Expected: Nørrebrogade 1, 2200 København N (top 3) (point)
- Bifrost: ⚠️ known gap — 'Nørrebrogade 1, 2200 København N' not found
- Slowest search request: 575 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Nørrebro 1, 4653 Karise |
| 2 | adr: Nørrebro 1, 5900 Rudkøbing |
| 3 | adr: Nørrebro 1, 5985 Søby Ærø |
| 4 | adr: Nørrebro 1, 6400 Sønderborg |
| 5 | adr: Nørrebro 1, 7900 Nykøbing M |
| 6 | ste: Nørrebro (bebyggelse, København) |
| 7 | ste: Nørrebro (topografi, Holstebro) |
| 8 | ste: Nørrebro (topografi, Varde) |
| 9 | ste: Nørrebro (topografi, Ringkøbing-Skjern) |
| 10 | ste: Nørrebroen (bygning, Frederikshavn) |
| | … 12 more |

### adr-noerrebrog

*Brugeren vil finde Nørrebrogade og har kun skrevet 'nørrebrog'*

- Typed: `nørrebrog`
- Expected: Nørrebrogade 1, 2200 København N (top 5) (point)
- Bifrost: ⚠️ known gap — 'Nørrebrogade 1, 2200 København N' not found
- Slowest search request: 246 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Nørrebro (4653 Karise) |
| 2 | adr: Nørrebro (9700 Brønderslev) |
| 3 | adr: Nørrebro (9800 Hjørring) |
| 4 | adr: Nørrebro (6400 Sønderborg) |
| 5 | adr: Nørrebro (5900 Rudkøbing) |
| 6 | ste: Nørrebro (bebyggelse, København) |
| 7 | ste: Nørrebro (topografi, Holstebro) |
| 8 | ste: Nørrebro (topografi, Varde) |
| 9 | ste: Nørrebro (topografi, Ringkøbing-Skjern) |
| 10 | ste: Nørrebroen (bygning, Frederikshavn) |
| | … 19 more |

### adr-vangeb

*Brugeren vil finde en adresse på Vangebovej eller Vangeboled i Holte og har kun skrevet 'vangeb'*

- Typed: `vangeb`
- Expected: Vangeboled 1, Søllerød, 2840 Holte (top 5) (point)
- Bifrost: ⚠️ known gap — 'Vangeboled 1, Søllerød, 2840 Holte' not found
- Slowest search request: 275 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | ste: Vangebo (bygning, Helsingør) |
| 2 | ste: Vange (bygning, Tønder) |
| 3 | ste: Vangen (bygning, Hedensted) |
| 4 | ste: Vangen (bygning, Vesthimmerlands) |
| 5 | ste: Vangen (bygning, Hjørring) |
| 6 | adr: Vangen (6715 Esbjerg N) |
| 7 | adr: Vangen (9460 Brovst) |
| 8 | adr: Vangen (4281 Gørlev) |
| 9 | adr: Vangen (8270 Højbjerg) |
| 10 | adr: Vangen (8963 Auning) |
| | … 15 more |

### adr-vangeb-77

*Brugeren vil finde Vangebovej 77 og forkorter vejnavnet*

- Typed: `vangeb 77`
- Expected: Vangebovej 77, Søllerød, 2840 Holte (point)
- Bifrost: ⚠️ known gap — 'Vangebovej 77, Søllerød, 2840 Holte' not found
- Slowest search request: 199 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Vangen 77, 9400 Nørresundby |
| 2 | adr: Vangen 177, 1., 9400 Nørresundby |
| 3 | adr: Vangen 277, 9400 Nørresundby |
| 4 | adr: Vangen 377, 2., 9400 Nørresundby |
| 5 | adr: Vangen 7, Nexø, 3730 Nexø |
| 6 | ste: Vangebo (bygning, Helsingør) |
| 7 | ste: Vange (bygning, Tønder) |
| 8 | ste: Vangen (bygning, Hedensted) |
| 9 | ste: Vangen (bygning, Vesthimmerlands) |
| 10 | ste: Vangen (bygning, Hjørring) |
| | … 15 more |

### adr-77-vangeb

*Brugeren skriver husnummeret først og forkorter vejnavnet for at finde Vangebovej 77*

- Typed: `77 vangeb`
- Expected: Vangebovej 77, Søllerød, 2840 Holte (point)
- Bifrost: ⚠️ known gap — 'Vangebovej 77, Søllerød, 2840 Holte' not found
- Slowest search request: 858 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | ste: Vangebo (bygning, Helsingør) |
| 2 | ste: Vange (bygning, Tønder) |
| 3 | ste: Vangen (bygning, Hedensted) |
| 4 | ste: Vangen (bygning, Vesthimmerlands) |
| 5 | ste: Vangen (bygning, Hjørring) |
| 6 | pos: 7184 Vandel |
| 7 | pos: 2720 Vanløse |
| 8 | pos: 7442 Engesvang |
| 9 | pos: 4772 Langebæk |
| 10 | pos: 9430 Vadum |
| | … 10 more |

### adr-14-oesterlund

*Brugeren skriver husnummeret først for at finde Østerlund 14*

- Typed: `14 østerlund`
- Expected: Østerlund 14, 9870 Sindal (top 2) (point)
- Bifrost: ⚠️ known gap — 'Østerlund 14, 9870 Sindal' not found
- Slowest search request: 231 ms
- Known gap: #33

| # | Bifrost |
|---|---|
| 1 | ste: Østerlund (bygning, Lemvig) |
| 2 | ste: Østerlund (bygning, Vejle) |
| 3 | ste: Østerlund (bygning, Faaborg-Midtfyn) |
| 4 | ste: Østerlund (bygning, Herning) |
| 5 | ste: Østerlund (bygning, Viborg) |
| 6 | pos: 9750 Østervrå |
| 7 | pos: 3751 Østermarie |
| 8 | pos: 7990 Øster Assels |
| 9 | pos: 4894 Øster Ulslev |
| 10 | pos: 8752 Østbirk |
| | … 13 more |

### adr-oesterlund-14

*Brugeren vil finde Østerlund 14 og skriver husnummeret efter vejnavnet*

- Typed: `østerlund 14`
- Expected: Østerlund 14, 9870 Sindal (top 2) (point)
- Bifrost: ✅ pass — rank 2
- Geometry of the hit: Point
- Slowest search request: 284 ms

| # | Bifrost |
|---|---|
| 1 | adr: Østerlund 14, Gjellerup, 7400 Herning |
| 2 | adr: **Østerlund 14, 9870 Sindal** |
| 3 | adr: Østerlund 1, Trørød, 2950 Vedbæk |
| 4 | adr: Østerlund 4, Trørød, 2950 Vedbæk |
| 5 | adr: Østerlund 10, Trørød, 2950 Vedbæk |
| 6 | ste: Østerlund (bygning, Lemvig) |
| 7 | ste: Østerlund (bygning, Vejle) |
| 8 | ste: Østerlund (bygning, Faaborg-Midtfyn) |
| 9 | ste: Østerlund (bygning, Herning) |
| 10 | ste: Østerlund (bygning, Viborg) |
| | … 18 more |

### adr-77-vangebovej

*Brugeren skriver husnummeret først og hele vejnavnet for at finde Vangebovej 77*

- Typed: `77 vangebovej`
- Expected: Vangebovej 77, Søllerød, 2840 Holte (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 239 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vangebovej 77, Søllerød, 2840 Holte** |
| 2 | adr: Vangebovej 17, Søllerød, 2840 Holte |
| 3 | adr: Vangebovej 57, Søllerød, 2840 Holte |
| 4 | adr: Vangebovej 67, Søllerød, 2840 Holte |
| 5 | adr: Vangebovej 71, Søllerød, 2840 Holte |
| 6 | ste: Vangebovej (bygning, Rudersdal) |
| 7 | ste: Vangebo (bygning, Helsingør) |
| 8 | ste: Vange (bygning, Tønder) |
| 9 | ste: Vangen (bygning, Hedensted) |
| 10 | ste: Vangen (bygning, Vesthimmerlands) |
| | … 16 more |

### adr-1-noerrebrogade

*Brugeren skriver husnummeret først og hele vejnavnet for at finde Nørrebrogade 1*

- Typed: `1 nørrebrogade`
- Expected: Nørrebrogade 1, 2200 København N (top 5) (point)
- Bifrost: ⚠️ known gap — 'Nørrebrogade 1, 2200 København N' not found
- Slowest search request: 198 ms
- Known gap: #33

| # | Bifrost |
|---|---|
| 1 | ste: Nørrebro (bebyggelse, København) |
| 2 | ste: Nørrebro (topografi, Holstebro) |
| 3 | ste: Nørrebro (topografi, Varde) |
| 4 | ste: Nørrebro (topografi, Ringkøbing-Skjern) |
| 5 | ste: Nørregade (bebyggelse, Tønder) |
| 6 | pos: 4951 Nørreballe |
| 7 | pos: 8766 Nørre Snede |
| 8 | pos: 5580 Nørre Aaby |
| 9 | pos: 6830 Nørre Nebel |
| 10 | pos: 9400 Nørresundby |
| | … 6 more |

### adr-noerrebrogade-vejnavn

*Brugeren skriver kun vejnavnet Nørrebrogade og vil se vejen i København*

- Typed: `Nørrebrogade`
- Expected: Nørrebrogade 1, 2200 København N (top 10) → Bifrost: Nørrebrogade (2200 København N) (top 10) (point)
- Bifrost differs on purpose: Bifrosts /resolve giver veje, ikke husnumre, når der kun står et vejnavn. Pluginet viser vejene under Husnumre.
- Bifrost: ✅ pass — rank 4
- Geometry of the hit: MultiLineString
- Slowest search request: 244 ms

| # | Bifrost |
|---|---|
| 1 | adr: Nørrebrogade (8700 Horsens) |
| 2 | adr: Nørrebrogade (7000 Fredericia) |
| 3 | adr: Nørrebrogade (8900 Randers C, 8930 Randers NØ) |
| 4 | adr: **Nørrebrogade (2200 København N)** |
| 5 | adr: Nørrebrogade (7500 Holstebro) |
| 6 | adr: Nørrebrogade (8722 Hedensted) |
| 7 | adr: Nørrebrogade (4930 Maribo) |
| 8 | adr: Nørrebrogade (7100 Vejle) |
| 9 | adr: Nørrebrogade (8000 Aarhus C) |
| 10 | adr: Nørrebrogade (6700 Esbjerg) |
| | … 10 more |

### adr-vestergade-21-aarhus

*Brugeren vil finde Vestergade 21 i Aarhus og skriver byen med*

- Typed: `vestergade 21 aarhus`
- Expected: Vestergade 21, 8000 Aarhus C (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 290 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vestergade 21, 8000 Aarhus C** |
| 2 | adr: Vesterbrogade 21, 8000 Aarhus C |
| 3 | adr: Vestergade 21, 5560 Aarup |
| 4 | adr: Vestergade 11, 5560 Aarup |
| 5 | adr: Vestergade 20, 5560 Aarup |
| 6 | ste: Århus Vest (topografi, Aarhus) |
| 7 | ste: Aarhus Vest (topografi, Aarhus) |
| 8 | ste: Vestergade 44 (bygning, Ærø) |
| 9 | ste: Vestergårdhus (bygning, Holstebro) |
| 10 | ste: FGU Aarhus Vest (bygning, Aarhus) |
| | … 18 more |

### adr-vestergade-21-aar

*Brugeren vil finde Vestergade 21 i Aarhus og forkorter byen*

- Typed: `vestergade 21 aar`
- Expected: Vestergade 21, 8000 Aarhus C (top 3) (point)
- Bifrost: 🎉 passes despite known gap — rank 2
- Geometry of the hit: Point
- Slowest search request: 348 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Vestergade 21, 5560 Aarup |
| 2 | adr: **Vestergade 21, 8000 Aarhus C** |
| 3 | adr: Vestergade 11, 5560 Aarup |
| 4 | adr: Vestergade 20, 5560 Aarup |
| 5 | adr: Vestergade 22, 5560 Aarup |
| 6 | ste: Vestergade 44 (bygning, Ærø) |
| 7 | ste: Vestergårde (bebyggelse, Vesthimmerlands) |
| 8 | ste: Vestergårde (bebyggelse, Brønderslev) |
| 9 | ste: Vestergårde (bebyggelse, Skive) |
| 10 | ste: Vestergårde (bebyggelse, Randers) |
| | … 18 more |

### adr-skodsb

*Brugeren vil finde en adresse på Skodsborg Strandvej og har kun skrevet 'skodsb'*

- Typed: `skodsb`
- Expected: Skodsborg Strandvej 1, 2942 Skodsborg (top 5) (point)
- Bifrost: ⚠️ known gap — 'Skodsborg Strandvej 1, 2942 Skodsborg' not found
- Slowest search request: 1411 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Skodsbølvej (6310 Broager) |
| 2 | adr: Skodsbølvej (6880 Tarm) |
| 3 | adr: Skodsborgvej (2830 Virum, 2840 Holte, 2850 Nærum, 2942 Skodsborg) |
| 4 | adr: Skodsborgvej (9270 Klarup) |
| 5 | ste: Skodsbøl (bebyggelse, Ringkøbing-Skjern) |
| 6 | ste: Skodsbøl (bebyggelse, Sønderborg) |
| 7 | ste: Skodsborg (bebyggelse, Rudersdal) |
| 8 | ste: Skodsbjerg (bygning, Haderslev) |
| 9 | ste: Skodsbøl Skov (naturareal, Sønderborg) |
| 10 | pos: 2942 Skodsborg |
| | … 13 more |

### adr-skodsborgvej-41

*Brugeren vil finde Skodsborgvej 41*

- Typed: `skodsborgvej 41`
- Expected: Skodsborgvej 41, 2830 Virum (top 3) (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 201 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Skodsborgvej 41, 2830 Virum** |
| 2 | adr: Skodsborgvej 41, 9270 Klarup |
| 3 | adr: Skodsborgvej 341, 2850 Nærum |
| 4 | adr: Skodsborgvej 410, 2942 Skodsborg |
| 5 | adr: Skodsborgvej 412, 2942 Skodsborg |
| 6 | adr: Skodsborgvej 414, 2942 Skodsborg |
| 7 | adr: Skodsborgvej 416, 2942 Skodsborg |
| 8 | adr: Skodsborgvej 1, 2830 Virum |
| 9 | adr: Skodsborgvej 40, 2830 Virum |
| 10 | adr: Skodsborgvej 42, 2830 Virum |
| | … 10 more |

### adr-skodsborgvej-414

*Brugeren vil finde Skodsborgvej 414 og skriver hele adressen*

- Typed: `skodsborgvej 414`
- Expected: Skodsborgvej 414, 2942 Skodsborg (top 3) (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 208 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Skodsborgvej 414, 2942 Skodsborg** |
| 2 | adr: Skodsborgvej 14, 2830 Virum |
| 3 | adr: Skodsborgvej 41, 2830 Virum |
| 4 | adr: Skodsborgvej 44, 2830 Virum |
| 5 | adr: Skodsborgvej 314, 2850 Nærum |
| 6 | adr: Skodsborgvej 410, 2942 Skodsborg |
| 7 | adr: Skodsborgvej 412, 2942 Skodsborg |
| 8 | adr: Skodsborgvej 416, 2942 Skodsborg |
| 9 | adr: Skodsborgvej 14, 9270 Klarup |
| 10 | adr: Skodsborgvej 41, 9270 Klarup |
| | … 10 more |

### adr-frederiksberggade-1a

*Brugeren vil finde en adresse med husbogstav: Frederiksberggade 1A*

- Typed: `frederiksberggade 1a`
- Expected: Frederiksberggade 1A, 1459 København K (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 291 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Frederiksberggade 1A, 1459 København K** |
| 2 | adr: Frederiksberggade 11A, 1459 København K |
| 3 | adr: Frederiksberggade 12A, 1459 København K |
| 4 | adr: Frederiksberggade 17A, 1459 København K |
| 5 | adr: Frederiksberggade 51A, 7323 Give |
| 6 | adr: Frederiksberggade 13A, 8600 Silkeborg |
| 7 | adr: Frederiksberggade 15A, 8600 Silkeborg |
| 8 | adr: Frederiksberggade 11A, 8700 Horsens |
| 9 | adr: Frederiksberggade 3A, 1459 København K |
| 10 | adr: Frederiksberggade 25A, 1459 København K |
| | … 10 more |

### adr-noeddebogade-1-st-th

*Brugeren vil finde lejligheden Nøddebogade 1, st. th.*

- Typed: `nøddebogade 1 st th`
- Expected: (no rows) → Bifrost: Nøddebogade 1, st. th, 2200 København N
- Bifrost differs on purpose: Bifrost finder selve lejligheden (ny mulighed).
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 446 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Nøddebogade 1, st. th, 2200 København N** |
| 2 | adr: Nøddebogade 1, st. tv, 2200 København N |
| 3 | adr: Nøddebogade 11, st. th, 2200 København N |
| 4 | adr: Nøddebogade 17, st. th, 2200 København N |
| 5 | adr: Nøddebovej 1, st. th, 2640 Hedehusene |
| 6 | adr: Nøddebogade 1, 1. th, 2200 København N |
| 7 | adr: Nøddebogade 1, 3. th, 2200 København N |
| 8 | adr: Nøddebogade 1, 4. th, 2200 København N |
| 9 | adr: Nøddebogade 11, st. tv, 2200 København N |
| 10 | adr: Nøddebogade 13, st., 2200 København N |
| | … 10 more |

### ste-skagen

*Brugeren vil finde byen Skagen*

- Typed: `skagen`
- Expected: Skagen (By i Frederikshavn Kommune) (top 10) (polygon)
- Bifrost: ✅ pass — rank 5 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 1618 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | adr: Skagenvej (8250 Egå) |
| 2 | adr: Skagenvej (8940 Randers SV) |
| 3 | adr: Lille Skagen (9990 Skagen) |
| 4 | adr: Skagensvej (9700 Brønderslev) |
| 5 | ste: **Skagen (naturareal, Slagelse)** |
| 6 | ste: **Skagen (bygning, Brønderslev)** |
| 7 | ste: **Skagen (bebyggelse, Frederikshavn)** |
| 8 | ste: Skagen Fyr (navigationsanlæg, Frederikshavn) |
| 9 | ste: Skagen Skole (bygning, Frederikshavn) |
| 10 | pos: 9990 Skagen |
| | … 15 more |

### ste-skag

*Brugeren vil finde Skagen og har kun skrevet 'skag'*

- Typed: `ste: skag`
- Expected: Skagen (By i Frederikshavn Kommune) (top 10) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 229 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | ste: **Skagen (naturareal, Slagelse)** |
| 2 | ste: **Skagen (bygning, Brønderslev)** |
| 3 | ste: **Skagen (bebyggelse, Frederikshavn)** |
| 4 | ste: Skau (bygning, Holstebro) |
| 5 | ste: Skage Sø (sø, Slagelse) |
| 6 | ste: Skaghøj (fortidsminde, Favrskov) |
| 7 | ste: Skagholt (naturareal, Syddjurs) |
| 8 | ste: Skaghorn (sø, Assens) |
| 9 | ste: Skade (bebyggelse, Ikast-Brande) |
| 10 | ste: Skads (bebyggelse, Esbjerg) |
| | … 30 more |

### ste-mols-bjerge

*Brugeren vil finde naturområdet Mols Bjerge*

- Typed: `mols bjerge`
- Expected: Mols Bjerge (Højdedrag i Knebel) (top 10) (polygon)
- Bifrost: ✅ pass — rank 6 (name only, #1)
- Geometry of the hit: MultiPolygon
- Slowest search request: 880 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | adr: Mols Bjerge Vej (8400 Ebeltoft, 8420 Knebel) |
| 2 | adr: Pouls Bjerge (6857 Blåvand) |
| 3 | adr: Bjerget (7700 Thisted) |
| 4 | adr: Bjerget (9310 Vodskov) |
| 5 | adr: Bjerget (2970 Hørsholm) |
| 6 | ste: **Mols Bjerge (landskabsform, Syddjurs)** |
| 7 | ste: Bjerge (landskabsform, Thisted) |
| 8 | ste: Bjerge (bebyggelse, Kalundborg) |
| 9 | ste: Mols Bjerge Feriecenter (bygning, Syddjurs) |
| 10 | ste: Mols Bjerge Nationalpark (restriktionsareal, Syddjurs) |
| | … 15 more |

### ste-gudenaa

*Brugeren vil finde Gudenåen og se vandløbet på kortet*

- Typed: `gudenå`
- Expected: Gudenå (Vandløb i Vonge) (top 3) (line)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: MultiLineString
- Slowest search request: 245 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Gudenå (vandløb, Silkeborg)** |
| 2 | ste: Gudenå Øst (topografi, Randers) |
| 3 | ste: Gudenå Vest (topografi, Randers) |
| 4 | ste: Gudenå-Krukken (seværdighed, Randers) |
| 5 | ste: Gudenåbroen (vej, Randers) |
| 6 | ste: Gudenåhuset (bygning, Viborg) |
| 7 | ste: Gudenåmuseet (bygning, Horsens) |
| 8 | ste: Gudenåparken (naturareal, Randers) |
| 9 | ste: Gudenåskolen (bygning, Skanderborg) |
| 10 | ste: Gudensø (sø, Skanderborg) |
| | … 30 more |

### ste-vendsyssel

*Brugeren vil finde landsdelen Vendsyssel*

- Typed: `ste: vendsyssel`
- Expected: Vendsyssel (Landsdel i Region Nordjylland) (top 3) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 162 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Vendsyssel (topografi, Hjørring)** |
| 2 | ste: **Vendsyssel (topografi, Aalborg)** |
| 3 | ste: AOF Vendsyssel (bygning, Brønderslev) |
| 4 | ste: CKU Vendsyssel (bygning, Hjørring) |
| 5 | ste: FGU Vendsyssel (bygning, Hjørring) |
| 6 | ste: Vendsyssel-Thy (landskabsform, Aalborg) |
| 7 | ste: Hospice Vendsyssel (bygning, Frederikshavn) |
| 8 | ste: Vendsyssel Plantage (naturareal, Hjørring) |
| 9 | ste: SOSU Nord Vendsyssel (bygning, Hjørring) |
| 10 | ste: Vendsyssel Kunstmuseum (bygning, Hjørring) |
| | … 30 more |

### ste-skodsborg

*Brugeren vil finde byen Skodsborg*

- Typed: `ste: skodsborg`
- Expected: Skodsborg (By i Rudersdal Kommune) (top 3) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: MultiPolygon
- Slowest search request: 251 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Skodsborg (bebyggelse, Rudersdal)** |
| 2 | ste: Skodsborg Dam (sø, Rudersdal) |
| 3 | ste: Skodsborg Eng (naturareal, Rudersdal) |
| 4 | ste: Skodsborg Station (standsningssted, Rudersdal) |
| 5 | ste: Skodborg (bebyggelse, Lemvig) |
| 6 | ste: Skodborg (bebyggelse, Vejen) |
| 7 | ste: Skodsbøl (bebyggelse, Ringkøbing-Skjern) |
| 8 | ste: Skodsbøl (bebyggelse, Sønderborg) |
| 9 | ste: Skovsborg (bygning, Kalundborg) |
| 10 | ste: Skovsborg (bygning, Herning) |
| | … 30 more |

### ste-raadhuspladsen

*Brugeren vil finde pladsen Rådhuspladsen som stednavn*

- Typed: `ste: rådhuspladsen`
- Expected: Rådhuspladsen (Seværdighed i København V) (top 3) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 184 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Rådhuspladsen (seværdighed, København)** |
| 2 | ste: **Rådhuspladsen (seværdighed, Gladsaxe)** |
| 3 | ste: **Rådhuspladsen (standsningssted, København)** |
| 4 | ste: H.C. Andersen - Rådhuspladsen (seværdighed, København) |
| 5 | ste: Domhuspladsen (seværdighed, Høje-Taastrup) |
| 6 | ste: Rådhusparken (naturareal, Horsens) |
| 7 | ste: Rådhusparken (naturareal, Aarhus) |
| 8 | ste: Rådhusparken (naturareal, Roskilde) |
| 9 | ste: Frederiksberg Rådhusplads (seværdighed, Frederiksberg) |
| 10 | ste: Rådhushaven (naturareal, København) |
| | … 30 more |

### ste-oeenslaeger

*Brugeren vil finde stednavne med Oehlenschläger og staver det, som det udtales*

- Typed: `ste: øenslæger`
- Expected: Oehlenschlägers Bøg (Løvtræ i Tranekær) (top 3) (point)
- Bifrost: ⚠️ known gap — 'Oehlenschlägers Bøg (Løvtræ i Tranekær)' not found
- Slowest search request: 231 ms
- Known gap: #34

| # | Bifrost |
|---|---|
| 1 | ste: Øenslyst (bygning, Syddjurs) |
| 2 | ste: Øen (naturareal, Haderslev) |
| 3 | ste: Øen (bebyggelse, Faaborg-Midtfyn) |
| 4 | ste: Øen (bygning, Syddjurs) |
| 5 | ste: Øen (landskabsform, Syddjurs) |
| 6 | ste: Øen (bygning, København) |
| 7 | ste: Øen (seværdighed, Kalundborg) |
| 8 | ste: Øen (seværdighed, Allerød) |
| 9 | ste: Øen (landskabsform, Langeland) |
| 10 | ste: Øen (bebyggelse, Langeland) |
| | … 30 more |

### ste-oeenslaeger-alle-typer

*Brugeren har alle typer slået til og søger på 'øenslæger'*

- Typed: `øenslæger`
- Expected: Oehlenschlægersgade 1, 1663 København V (top 5) (point)
- Bifrost: ⚠️ known gap — 'Oehlenschlægersgade 1, 1663 København V' not found
- Slowest search request: 173 ms
- Known gap: #34

| # | Bifrost |
|---|---|
| 1 | adr: Øen (8560 Kolind) |
| 2 | adr: Øen (6880 Tarm) |
| 3 | adr: Øen (6710 Esbjerg V) |
| 4 | adr: Oehlenschlægersvej (8230 Åbyhøj) |
| 5 | adr: Oehlenschlægersvej (5230 Odense M) |
| 6 | ste: Øenslyst (bygning, Syddjurs) |
| 7 | ste: Øen (naturareal, Haderslev) |
| 8 | ste: Øen (bebyggelse, Faaborg-Midtfyn) |
| 9 | ste: Øen (bygning, Syddjurs) |
| 10 | ste: Øen (landskabsform, Syddjurs) |
| | … 14 more |

### ste-tivoli

*Brugeren vil finde forlystelsesparken Tivoli i København*

- Typed: `tivoli`
- Expected: Tivoli (Forlystelsespark i København V) (top 5) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 163 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Tivoli (naturareal, Silkeborg)** |
| 2 | ste: **Tivoli (seværdighed, København)** |
| 3 | ste: **Tivoli (bygning, Vordingborg)** |
| 4 | ste: **Tivoli (bebyggelse, Furesø)** |
| 5 | ste: **Tivoli (bebyggelse, Ærø)** |
| 6 | ste: Tivoli Hotel (bygning, København) |
| 7 | ste: Tivoli Søen (sø, København) |
| 8 | ste: Tivolisøen (sø, Ringsted) |
| 9 | ste: Tivoli Friheden (seværdighed, Aarhus) |
| 10 | ste: Tivolislottet (bygning, København) |
| | … 30 more |

### ste-anholt

*Brugeren vil finde øen Anholt*

- Typed: `anholt`
- Expected: Anholt (Ø i Kattegat) (top 5) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: MultiPolygon
- Slowest search request: 153 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Anholt (landskabsform, Norddjurs)** |
| 2 | ste: **Anholt (havnebassin)** |
| 3 | ste: **Anholt (bygning, Frederikshavn)** |
| 4 | ste: **Anholt (landskabsform, Ringkøbing-Skjern)** |
| 5 | ste: **Anholt (bygning, Ringkøbing-Skjern)** |
| 6 | ste: **Anholt (lufthavn, Norddjurs)** |
| 7 | ste: **Anholt (bebyggelse, Sønderborg)** |
| 8 | ste: **Anholt (bebyggelse, Norddjurs)** |
| 9 | ste: **Anholt (bebyggelse, Kolding)** |
| 10 | ste: Anholt Bro (topografi, Ringkøbing-Skjern) |
| | … 30 more |

### ste-roskilde-fjord

*Brugeren vil finde Roskilde Fjord*

- Typed: `roskilde fjord`
- Expected: Roskilde Fjord (Fjord i Isefjord) (polygon)
- Bifrost: ✅ pass — rank 1 (name only, #1)
- Geometry of the hit: Polygon
- Slowest search request: 238 ms
- Known gap: #1

| # | Bifrost |
|---|---|
| 1 | ste: **Roskilde Fjord (farvand)** |
| 2 | ste: Roskilde (bebyggelse, Roskilde) |
| 3 | ste: FGU Roskilde (bygning, Roskilde) |
| 4 | ste: Roskilde Fjord Vildtreservat (restriktionsareal) |
| 5 | ste: AU Roskilde (bygning, Roskilde) |
| 6 | ste: HTX Roskilde (bygning, Roskilde) |
| 7 | ste: Roskilde BMX (idrætsanlæg, Roskilde) |
| 8 | ste: Roskilde Kro (bygning, Albertslund) |
| 9 | ste: Roskilde Ring (naturareal, Roskilde) |
| 10 | ste: STU Roskilde (bygning, Roskilde) |
| | … 30 more |

### ste-gudenaa-kommunefilter-730

*Brugeren har kommunefilter på Randers og vil finde Gudenå, der løber gennem Randers*

- Typed: `ste: gudenå`
- Kommunefilter: 730
- Expected: Gudenå (Vandløb i Vonge) (top 5) (line)
- Bifrost: ⚠️ known gap — 'Gudenå (Vandløb i Vonge)' not found
- Hidden by the kommune filter: ste 94
- Slowest search request: 229 ms
- Known gap: #35

| # | Bifrost |
|---|---|
| 1 | ste: Gudenå Øst (topografi, Randers) |
| 2 | ste: Gudenå Vest (topografi, Randers) |
| 3 | ste: Gudenå-Krukken (seværdighed, Randers) |
| 4 | ste: Gudenåbroen (vej, Randers) |
| 5 | ste: Gudenåparken (naturareal, Randers) |
| 6 | ste: Pigen i Gudenåen (seværdighed, Randers) |

### ste-vor-frue-kommunefilter

*Brugeren har kommunefilter på København og Aalborg og vil finde Vor Frue*

- Typed: `vor frue`
- Kommunefilter: 101, 851
- Expected: Vor Frue Kirke (Kirke i København K) (top 5) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1 (name only, #1)
- Hidden by the kommune filter: ste 95
- Geometry of the hit: MultiPolygon
- Slowest search request: 224 ms
- Known gap: #2

| # | Bifrost |
|---|---|
| 1 | ste: **Vor Frue Kirke (bygning, København)** |
| 2 | ste: **Vor Frue Kirke (bygning, Aalborg)** |
| 3 | ste: Frue Plads (seværdighed, København) |
| 4 | ste: Vor Frelsers Kirke (bygning, Aalborg) |
| 5 | ste: Vor Frelsers Kirke (bygning, København) |

### pos-8000

*Brugeren vil finde postnummer 8000*

- Typed: `8000`
- Expected: 8000 Aarhus C (top 10) (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 134 ms

| # | Bifrost |
|---|---|
| 1 | pos: **8000 Aarhus C** |
| 2 | ste: 80 (topografi, Aabenraa) |
| 3 | ste: 80a (topografi) |
| 4 | ste: 8 (topografi, Aabenraa) |
| 5 | ste: Skate6000 (bygning, Kolding) |
| 6 | ste: 81 (topografi) |

### pos-80

*Brugeren vil finde postnummer 8000 og har kun skrevet '80'*

- Typed: `pos: 80`
- Expected: 8000 Aarhus C (top 3) (polygon)
- Bifrost: ⚠️ known gap — '8000 Aarhus C' not found
- Slowest search request: 199 ms
- Known gap: #3

*No rows.*

### pos-aarhus

*Brugeren vil finde postdistriktet Aarhus C ud fra navnet*

- Typed: `aarhus`
- Expected: 8000 Aarhus C (top 3) (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 124 ms

| # | Bifrost |
|---|---|
| 1 | pos: **8000 Aarhus C** |
| 2 | pos: 8200 Aarhus N |
| 3 | pos: 8210 Aarhus V |
| 4 | pos: 9600 Aars |
| 5 | pos: 6818 Årre |
| 6 | pos: 5560 Aarup |
| 7 | pos: 5792 Årslev |
| 8 | pos: 3140 Ålsgårde |
| 9 | pos: 9440 Aabybro |
| 10 | pos: 9982 Ålbæk |
| | … 10 more |

### pos-aar

*Brugeren vil finde Aarhus C og har kun skrevet 'aar'*

- Typed: `pos: aar`
- Expected: 8000 Aarhus C (top 5) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 5
- Geometry of the hit: Polygon
- Slowest search request: 225 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | pos: 9600 Aars |
| 2 | pos: 6818 Årre |
| 3 | pos: 5560 Aarup |
| 4 | pos: 5792 Årslev |
| 5 | pos: **8000 Aarhus C** |
| 6 | pos: 8200 Aarhus N |
| 7 | pos: 8210 Aarhus V |
| 8 | pos: 3140 Ålsgårde |
| 9 | pos: 9440 Aabybro |
| 10 | pos: 9982 Ålbæk |
| | … 23 more |

### pos-aabenraa-aa

*Brugeren skriver 'åbenrå' med å og vil finde 6200 Aabenraa*

- Typed: `pos: åbenrå`
- Expected: 6200 Aabenraa (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 129 ms

| # | Bifrost |
|---|---|
| 1 | pos: **6200 Aabenraa** |
| 2 | pos: 9440 Aabybro |
| 3 | pos: 8230 Åbyhøj |
| 4 | pos: 9600 Aars |
| 5 | pos: 9340 Asaa |
| 6 | pos: 5580 Nørre Aaby |
| 7 | pos: 9760 Vrå |
| 8 | pos: 6818 Årre |
| 9 | pos: 5560 Aarup |
| 10 | pos: 9982 Ålbæk |
| | … 13 more |

### mat-5a

*Brugeren vil finde matrikel 5a uden at angive ejerlav*

- Typed: `5a`
- Expected: 5a, Kirke Sonnerup By, Kirke Sonnerup (top 5) (polygon)
- Bifrost: ⚠️ known gap — '5a, Kirke Sonnerup By, Kirke Sonnerup' not found
- Slowest search request: 5524 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: 5a, Frederiksberg |
| 2 | mat: 5a, Gentofte |
| 3 | mat: 5a, Hellerup |
| 4 | mat: 5a, Herlev |
| 5 | mat: 5a, Rødovre By, Rødovre |
| 6 | mat: 5a, Skovshoved |
| 7 | mat: 5a, Holte By, Søllerød |
| 8 | mat: 5a, Søllerød By, Søllerød |
| 9 | mat: 5a, Taarbæk By, Taarbæk |
| 10 | mat: 5a, Løjtegård, Tårnby |
| | … 30 more |

### mat-1a-soenderby

*Brugeren vil finde matrikel 1a i ejerlavet Sønderby*

- Typed: `1a sønderby`
- Expected: 1a, Sønderby, Kegnæs (top 3) (polygon)
- Bifrost: ⚠️ known gap — '1a, Sønderby, Kegnæs' not found
- Slowest search request: 879 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: 1a, Sønderby By, Sønderby |
| 2 | mat: 1a, Sønderby By, Borre |
| 3 | mat: 1a, Sønderby By, Tved (del af ejendom med 3 matrikler) |
| 4 | mat: 1a, Sønderby By, Glud (del af ejendom med 7 matrikler) |
| 5 | mat: 10a, Sønderby By, Sønderby |
| 6 | mat: 11a, Sønderby By, Sønderby (del af ejendom med 2 matrikler) |
| 7 | mat: 12a, Sønderby By, Sønderby |
| 8 | mat: 16a, Sønderby By, Sønderby (del af ejendom med 4 matrikler) |
| 9 | mat: 17a, Sønderby By, Sønderby (del af ejendom med 9 matrikler) |
| 10 | mat: 18a, Sønderby By, Sønderby |
| | … 30 more |

### mat-162-vestervold

*Brugeren vil finde matrikel 162 i Vestervold Kvarter*

- Typed: `162 vestervold`
- Expected: 162, Vestervold Kvarter, København (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 276 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: **162, Vestervold Kvarter, København** |
| 2 | mat: 16a, Vestervig By, Vestervig (del af ejendom med 2 matrikler) |
| 3 | mat: 16f, Vestervig By, Vestervig |
| 4 | mat: 16i, Vestervig By, Vestervig |
| 5 | mat: 16k, Vestervig By, Vestervig |
| 6 | mat: 16l, Vestervig By, Vestervig |
| 7 | mat: 16m, Vestervig By, Vestervig |
| 8 | mat: 16n, Vestervig By, Vestervig |
| 9 | mat: 16o, Vestervig By, Vestervig |
| 10 | mat: 16p, Vestervig By, Vestervig |
| | … 30 more |

### mat-162-vesterv

*Brugeren vil finde matrikel 162 i Vestervold Kvarter og forkorter ejerlavet*

- Typed: `mat: 162 vesterv`
- Expected: 162, Vestervold Kvarter, København (polygon)
- Bifrost: ⚠️ known gap — '162, Vestervold Kvarter, København' not found
- Slowest search request: 296 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | mat: 16a, Vestervig By, Vestervig (del af ejendom med 2 matrikler) |
| 2 | mat: 16f, Vestervig By, Vestervig |
| 3 | mat: 16i, Vestervig By, Vestervig |
| 4 | mat: 16k, Vestervig By, Vestervig |
| 5 | mat: 16l, Vestervig By, Vestervig |
| 6 | mat: 16m, Vestervig By, Vestervig |
| 7 | mat: 16n, Vestervig By, Vestervig |
| 8 | mat: 16o, Vestervig By, Vestervig |
| 9 | mat: 16p, Vestervig By, Vestervig |
| 10 | mat: 16q, Vestervig By, Vestervig |
| | … 30 more |

### mat-bfe-6033528

*Brugeren vil finde en ejendom ud fra BFE-nummeret 6033528*

- Typed: `6033528`
- Expected: 162, Vestervold Kvarter, København (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 204 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: **162, Vestervold Kvarter, København** |

### mat-3kg-soell

*Brugeren vil finde matrikel 3kg i Søllerød og forkorter ejerlavet*

- Typed: `mat: 3kg søll`
- Expected: 3kg, Øverød By, Søllerød (top 2) (polygon)
- Bifrost: ⚠️ known gap — '3kg, Øverød By, Søllerød' not found
- Slowest search request: 170 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: 3kg, Søllerød By, Søllerød |
| 2 | mat: 2kg, Søllerød By, Søllerød |
| 3 | mat: 3g, Søllerød By, Søllerød |
| 4 | mat: 3k, Søllerød By, Søllerød |
| 5 | mat: 3ag, Søllerød By, Søllerød |
| 6 | mat: 3bg, Søllerød By, Søllerød |
| 7 | mat: 3cg, Søllerød By, Søllerød |
| 8 | mat: 3dg, Søllerød By, Søllerød |
| 9 | mat: 3eg, Søllerød By, Søllerød |
| 10 | mat: 3gg, Søllerød By, Søllerød |
| | … 30 more |

### mat-3kg-soelleroed

*Brugeren vil finde matrikel 3kg i Søllerød og skriver hele navnet*

- Typed: `3kg søllerød`
- Expected: 3kg, Søllerød By, Søllerød (top 2) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1
- Geometry of the hit: Polygon
- Slowest search request: 470 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: **3kg, Søllerød By, Søllerød** |
| 2 | mat: 3kg, Øverød By, Søllerød |
| 3 | mat: 2kg, Søllerød By, Søllerød |
| 4 | mat: 3g, Søllerød By, Søllerød |
| 5 | mat: 3k, Søllerød By, Søllerød |
| 6 | mat: 3ag, Søllerød By, Søllerød |
| 7 | mat: 3bg, Søllerød By, Søllerød |
| 8 | mat: 3cg, Søllerød By, Søllerød |
| 9 | mat: 3dg, Søllerød By, Søllerød |
| 10 | mat: 3eg, Søllerød By, Søllerød |
| | … 30 more |

### mat-3kg

*Brugeren vil se alle matrikler med nummer 3kg*

- Typed: `mat: 3kg`
- Expected: 3kg, Øverød By, Søllerød (top 40) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 3
- Geometry of the hit: Polygon
- Slowest search request: 376 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: 3kg, Buddinge |
| 2 | mat: 3kg, Søllerød By, Søllerød |
| 3 | mat: **3kg, Øverød By, Søllerød** |
| 4 | mat: 3kg, Virum By, Lundtofte |
| 5 | mat: 3kg, Holte By, Nærum |
| 6 | mat: 3kg, Rødovre By, Hendriksholm |
| 7 | mat: 3kg, Brøndbyøster By, Brøndbyøster |
| 8 | mat: 3kg, Bringe By, Værløse |
| 9 | mat: 3kg, Ll. Værløse By, Værløse |
| 10 | mat: 3kg, Måløv By, Måløv |
| | … 30 more |

### mat-1a-kommunefilter-615

*Brugeren har kommunefilter på Horsens og vil finde matrikel 1a*

- Typed: `1a`
- Kommunefilter: 615
- Expected: 1a, Nim By, Nim (top 3) (polygon)
- Bifrost: ⚠️ known gap — '1a, Nim By, Nim' not found
- Hidden by the kommune filter: mat 100
- Slowest search request: 519 ms
- Known gap: #2

*No rows.*

### mat-1an-gentofte

*Brugeren vil finde den udgåede matrikel 1an i Gentofte*

- Typed: `mat: 1an gentofte`
- Expected: (no rows)
- Bifrost: ⚠️ known gap — expected no rows, got 40
- Slowest search request: 376 ms
- Known gap: #4

| # | Bifrost |
|---|---|
| 1 | mat: 10an, Gentofte |
| 2 | mat: 11an, Gentofte |
| 3 | mat: 12an, Gentofte |
| 4 | mat: 14an, Gentofte |
| 5 | mat: 15an, Gentofte |
| 6 | mat: 16an, Gentofte (del af ejendom med 2 matrikler) |
| 7 | mat: 17an, Gentofte |
| 8 | mat: 18an, Gentofte |
| 9 | mat: 19an, Gentofte |
| 10 | mat: 21an, Gentofte |
| | … 30 more |

### kom-101

*Brugeren vil finde Københavns Kommune ud fra kommunekoden*

- Typed: `kom: 101`
- Expected: Københavns Kommune (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 121 ms

| # | Bifrost |
|---|---|
| 1 | kom: **Københavns Kommune** |

### kom-koeb

*Brugeren vil finde Københavns Kommune og har kun skrevet 'køb'*

- Typed: `kom: køb`
- Expected: Københavns Kommune (polygon)
- Bifrost: ⚠️ known gap — rank 2 > 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 208 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | kom: Køge Kommune |
| 2 | kom: **Københavns Kommune** |
| 3 | kom: Kolding Kommune |

### kom-aarhus-alle-typer

*Brugeren har alle typer slået til og vil finde Aarhus Kommune*

- Typed: `aarhus`
- Expected: Aarhus Kommune (top 20) (polygon)
- Bifrost: ✅ pass — rank 11
- Geometry of the hit: MultiPolygon
- Slowest search request: 240 ms

| # | Bifrost |
|---|---|
| 1 | ste: Århus (bygning, Thisted) |
| 2 | ste: Aarhus (bebyggelse, Aarhus) |
| 3 | ste: Århus Å (vandløb, Aarhus) |
| 4 | ste: Aarhus Ø (bebyggelse, Aarhus) |
| 5 | ste: Aarhus BSS (bygning, Herning) |
| 6 | pos: 8000 Aarhus C |
| 7 | pos: 8200 Aarhus N |
| 8 | pos: 8210 Aarhus V |
| 9 | pos: 9600 Aars |
| 10 | pos: 6818 Årre |
| | … 15 more |

### kom-aabenraa-aa

*Brugeren skriver 'åbenrå' med å og vil finde Aabenraa Kommune*

- Typed: `kommune: åbenrå`
- Expected: Aabenraa Kommune (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 123 ms

| # | Bifrost |
|---|---|
| 1 | kom: **Aabenraa Kommune** |
| 2 | kom: Aarhus Kommune |
| 3 | kom: Aalborg Kommune |

### ops-aarhus

*Brugeren vil finde opstillingskredsen Aarhus Nord*

- Typed: `ops: aarhus`
- Expected: Aarhus Nordkredsen (top 3) (polygon)
- Bifrost: ✅ pass — rank 2
- Geometry of the hit: Polygon
- Slowest search request: 123 ms

| # | Bifrost |
|---|---|
| 1 | ops: Aarhus Sydkredsen |
| 2 | ops: **Aarhus Nordkredsen** |
| 3 | ops: Aarhus Østkredsen |
| 4 | ops: Aarhus Vestkredsen |
| 5 | ops: Aabenraakredsen |
| 6 | ops: Aakirkebykredsen |
| 7 | ops: Aalborg Nordkredsen |
| 8 | ops: Aalborg Østkredsen |
| 9 | ops: Aalborg Vestkredsen |

### ops-aar

*Brugeren vil finde en opstillingskreds i Aarhus og har kun skrevet 'aar'*

- Typed: `ops: aar`
- Expected: Aarhus Nordkredsen (top 5) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 2
- Geometry of the hit: Polygon
- Slowest search request: 204 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | ops: Aarhus Sydkredsen |
| 2 | ops: **Aarhus Nordkredsen** |
| 3 | ops: Aarhus Østkredsen |
| 4 | ops: Aarhus Vestkredsen |
| 5 | ops: Aabenraakredsen |
| 6 | ops: Aakirkebykredsen |
| 7 | ops: Aalborg Nordkredsen |
| 8 | ops: Aalborg Østkredsen |
| 9 | ops: Aalborg Vestkredsen |
| 10 | ops: Assenskredsen |

### pol-midt

*Brugeren vil finde Midt- og Vestjyllands Politikreds*

- Typed: `pol: midt`
- Expected: Midt- og Vestjyllands Politikreds (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 117 ms

| # | Bifrost |
|---|---|
| 1 | pol: **Midt- og Vestjyllands Politikreds** |
| 2 | pol: Midt- og Vestsjællands Politikreds |

### pol-koebenhavn

*Brugeren vil finde Københavns Politikreds*

- Typed: `københavn`
- Expected: Københavns Politikreds (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 133 ms

| # | Bifrost |
|---|---|
| 1 | pol: **Københavns Politikreds** |
| 2 | pol: Københavns Vestegns Politikreds |

### reg-midt

*Brugeren vil finde Region Midtjylland*

- Typed: `reg: midt`
- Expected: Region Midtjylland (polygon)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 115 ms

| # | Bifrost |
|---|---|
| 1 | reg: **Region Midtjylland** |

### reg-hovedstaden-alle-typer

*Brugeren har alle typer slået til og vil finde Region Hovedstaden*

- Typed: `hovedstaden`
- Expected: Region Hovedstaden (top 20) (polygon)
- Bifrost: ✅ pass — rank 6
- Geometry of the hit: MultiPolygon
- Slowest search request: 670 ms

| # | Bifrost |
|---|---|
| 1 | ste: **Region Hovedstaden (bygning, Hillerød)** |
| 2 | ste: FGU Hovedstaden - Valby (bygning, København) |
| 3 | ste: FGU Hovedstaden - Amager (bygning, Tårnby) |
| 4 | ste: FGU Hovedstaden - Nørrebro (bygning, København) |
| 5 | ste: FGU Hovedstaden - Østerbro (bygning, København) |
| 6 | reg: **Region Hovedstaden** |
| 7 | adr: Hovedgaden (8410 Rønde) |
| 8 | adr: Hovedgaden (5853 Ørbæk) |
| 9 | adr: Hovedgaden (9330 Dronninglund) |
| 10 | adr: Hovedgaden (4623 Lille Skensved) |
| | … 21 more |

### pfx-kom-aar

*Brugeren bruger præfikset 'kom:' for kun at søge i kommuner*

- Typed: `kom: aar`
- Expected: Aarhus Kommune (top 3) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 1
- Geometry of the hit: MultiPolygon
- Slowest search request: 209 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | kom: **Aarhus Kommune** |
| 2 | kom: Aalborg Kommune |
| 3 | kom: Aabenraa Kommune |
| 4 | kom: Ærø Kommune |
| 5 | kom: Assens Kommune |

### pfx-adr-versaler-uden-mellemrum

*Brugeren skriver præfikset med store bogstaver og uden mellemrum*

- Typed: `ADR:vangebovej 71`
- Expected: Vangebovej 71, Søllerød, 2840 Holte (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 156 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vangebovej 71, Søllerød, 2840 Holte** |
| 2 | adr: Vangebovej 31, Søllerød, 2840 Holte |
| 3 | adr: Vangebovej 41, Søllerød, 2840 Holte |
| 4 | adr: Vangebovej 51, Søllerød, 2840 Holte |
| 5 | adr: Vangebovej 61, Søllerød, 2840 Holte |
| 6 | adr: Vangebovej 73, Søllerød, 2840 Holte |
| 7 | adr: Vangebovej 75, Søllerød, 2840 Holte |
| 8 | adr: Vangebovej 77, Søllerød, 2840 Holte |
| 9 | adr: Vangebovej 79, Søllerød, 2840 Holte |
| 10 | adr: Vangebovej 81, Søllerød, 2840 Holte |
| | … 10 more |

### pfx-ukendt-praefiks

*Brugeren skriver et præfiks som pluginet ikke kender ('udg:' for udgåede matrikler)*

- Typed: `udg: 1an gentofte`
- Expected: Husnumre - Der skete en fejl → Bifrost: none
- Bifrost differs on purpose: Bifrost svarer uden fejl på teksten inkl. 'udg:'; der er ikke noget bestemt hit at forvente.
- Bifrost: ➖ no expectation — no expectation
- Slowest search request: 756 ms

| # | Bifrost |
|---|---|
| 1 | adr: Gentoftevej (8000 Aarhus C) |
| 2 | adr: Gentoftegade (2820 Gentofte) |
| 3 | adr: Gentofte Hospitalsvej (2820 Gentofte, 2900 Hellerup) |
| 4 | adr: Grøntoften (2870 Dyssegård) |
| 5 | ste: Gentofte (bygning, Lemvig) |
| 6 | ste: Gentofte (bebyggelse, Gentofte) |
| 7 | ste: Gentofte HF (bygning, Gentofte) |
| 8 | ste: Gentofte Sø (sø, Gentofte) |
| 9 | ste: Gentofte Enge (naturareal, Gentofte) |
| 10 | pos: 2820 Gentofte |
| | … 9 more |

### pfx-kun-praefiks

*Brugeren har kun skrevet præfikset 'adr:'*

- Typed: `adr:`
- Expected: (no rows)
- Bifrost: ✅ pass — no rows

*No rows.*

### kf-vestergade-751

*Brugeren har kommunefilter på Aarhus og vil finde Vestergade*

- Typed: `vestergade`
- Kommunefilter: 751
- Expected: Vestergade 1B, 8000 Aarhus C (top 3) (point)
- Bifrost: ⚠️ known gap — 'Vestergade 1B, 8000 Aarhus C' not found
- Slowest search request: 138 ms
- Known gap: #3

| # | Bifrost |
|---|---|
| 1 | adr: Vestergade (8000 Aarhus C) |
| 2 | adr: Østergade (8000 Aarhus C) |
| 3 | adr: Vesterbrogade (8000 Aarhus C) |
| 4 | adr: F. Vestergaards Gade (8000 Aarhus C) |
| 5 | adr: Værkmestergade (8000 Aarhus C) |
| 6 | adr: Klostergade (8000 Aarhus C) |
| 7 | adr: Vestergaardsvej (8260 Viby J) |
| 8 | adr: Vestervej (8462 Harlev J) |
| 9 | adr: Vesterport (8000 Aarhus C) |
| 10 | adr: Vestervang (8000 Aarhus C) |
| | … 10 more |

### kf-vestergade-1-101

*Brugeren har kommunefilter på København og vil finde Vestergade 1*

- Typed: `vestergade 1`
- Kommunefilter: 101
- Expected: Vestergade 1, 1456 København K (point)
- Bifrost: ✅ pass — rank 1
- Geometry of the hit: Point
- Slowest search request: 239 ms

| # | Bifrost |
|---|---|
| 1 | adr: **Vestergade 1, 1456 København K** |
| 2 | adr: Vestergade 10, 1456 København K |
| 3 | adr: Vestergade 11, 1456 København K |
| 4 | adr: Vestergade 12, 1456 København K |
| 5 | adr: Vestergade 13, 1456 København K |
| 6 | adr: Vestergade 14, 1456 København K |
| 7 | adr: Vestergade 15, 1456 København K |
| 8 | adr: Vestergade 16, 1456 København K |
| 9 | adr: Vestergade 17, 1456 København K |
| 10 | adr: Vestergade 19, 1456 København K |
| | … 10 more |

### kf-lyngby-230-173

*Brugeren har kommunefilter på Rudersdal og Lyngby-Taarbæk og søger på 'lyngby'*

- Typed: `lyngby`
- Kommunefilter: 230, 173
- Expected: 2800 Kongens Lyngby (top 20) (polygon)
- Bifrost: 🎉 passes despite known gap — rank 11
- Hidden by the kommune filter: ste 80, pos 7, mat 100
- Geometry of the hit: Polygon
- Slowest search request: 1097 ms
- Known gap: #2

| # | Bifrost |
|---|---|
| 1 | adr: Lyngby Torv (2800 Kongens Lyngby) |
| 2 | adr: Lyngby Hovedgade (2800 Kongens Lyngby) |
| 3 | adr: Lyngbystræde (2800 Kongens Lyngby) |
| 4 | adr: Lyngby Storcenter (2800 Kongens Lyngby) |
| 5 | adr: Lyngby Rosenvænge (2800 Kongens Lyngby) |
| 6 | ste: Lyngby (bebyggelse, Lyngby-Taarbæk) |
| 7 | ste: Lyngby (standsningssted, Lyngby-Taarbæk) |
| 8 | ste: Lyngby Sø (sø, Lyngby-Taarbæk) |
| 9 | ste: TEC Lyngby (bygning, Lyngby-Taarbæk) |
| 10 | ste: VUC Lyngby (bygning, Lyngby-Taarbæk) |
| | … 3 more |
