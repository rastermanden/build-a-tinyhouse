# Parametriske konstruktionstegninger i FreeCAD

En kort guide til at tegne tiny house-skelettet i [FreeCAD](https://www.freecad.org/) med
**vores dimensioner af konstruktionstræ**, sådan at du kan ændre husets længde og bredde
bagefter og få både 3D-model og tegninger til at følge med.

> Skrevet til **FreeCAD 1.0** eller nyere. Hent den nyeste version –
> den er markant bedre til byggekonstruktion end de gamle 0.x-udgaver.
> Download: <https://www.freecad.org/downloads.php>

## Vores dimensioner

Hele huset bygges op omkring et **modul på 60 cm**. De bærende trædimensioner er:

| Element | Dimension |
|---|---|
| Bundrem, vægregler, top-/bundskinne | 45 × 95 mm |
| Tagspær | 45 × 120 mm |
| Modul (c/c mellem regler og spær) | 600 mm |
| Reference-størrelse | 600 × 360 cm |

## Hvilke workbenches

Du skal bruge to – én til at bygge modellen, én til at lave tegningerne:

| Formål | Workbench | Dokumentation |
|---|---|---|
| Modellere træskelettet i 3D | **BIM** (hed tidligere *Arch*) | <https://wiki.freecad.org/BIM_Workbench> |
| Lave 2D-tegninger (plan, snit, opstalt, mål) | **TechDraw** | <https://wiki.freecad.org/TechDraw_Workbench> |
| Styre alle mål fra ét sted | **Spreadsheet** | <https://wiki.freecad.org/Spreadsheet_Workbench> |
| 60 cm-grid og kopiering af regler/spær | **Draft** | <https://wiki.freecad.org/Draft_Workbench> |

Alle fire følger med i standard-FreeCAD – ingen tilføjelser nødvendige.

## Sådan gør du det parametrisk

Målet: skift **ét tal**, og hele huset skalerer. Nøglen er **Spreadsheet + udtryk**.
Det skal planlægges *fra begyndelsen* – det er svært at eftermontere.

### 1. Lav et regneark med de styrende mål

Åbn **Spreadsheet**-workbenchen, opret et regneark og skriv dine parametre ind. Giv hver
celle et **alias** (højreklik på cellen → *Alias*), så du kan referere til den:

| Celle | Værdi | Alias |
|---|---|---|
| B1 | 6000 | `laengde` |
| B2 | 3600 | `bredde` |
| B3 | 600 | `modul` |
| B4 | 45 | `regel_b` |
| B5 | 95 | `regel_h` |
| B6 | 120 | `spaer_h` |

Læg gerne en udregnet celle ind for antal regler:

| Celle | Formel | Alias |
|---|---|---|
| B7 | `=laengde / modul + 1` | `antal_regler` |

> **Hold dig til hele moduler.** `laengde` og `bredde` bør altid være et multiplum af 600,
> så konstruktionen går op i 60 cm-rasteret ligesom det færdige byg.

### 2. Byg med udtryk i stedet for tal

Når du opretter en bjælke (BIM → *Structure*/*Beam*), så klik på det lille **f(x)-ikon**
i mål-feltet og skriv et **udtryk** i stedet for et fast tal:

- Bundremmens længde: `Spreadsheet.laengde`
- Bjælkeprofil: bredde `Spreadsheet.regel_b`, højde `Spreadsheet.regel_h`
- Spærhøjde: `Spreadsheet.spaer_h`

Nu er bjælken bundet til regnearket. Ændrer du `laengde`, følger bjælken med efter et
**recompute** (F5 / det blå genberegn-ikon).

Læs mere om udtrykssproget: <https://wiki.freecad.org/Expressions>

### 3. Lad antallet af regler skalere med

En enkelt bjælke strækker sig fint, men "der skal komme en ekstra stolpe når huset bliver
længere" kræver et **array**. Marker én regel og lav et **Draft Ortho Array**, hvor du
sætter *antallet* som et udtryk:

- Antal (X): `Spreadsheet.antal_regler`
- Interval (X): `Spreadsheet.modul`

Så popper der automatisk en ny regel op, hver gang du krydser et 60 cm-modul. Samme princip
for spærene.

Draft Array: <https://wiki.freecad.org/Draft_OrthoArray>

### 4. Definér profilerne én gang

Tegn 45 × 95- og 45 × 120-profilerne som **Sketcher**-rektangler (eller brug BIM' indbyggede
profil-bibliotek) og genbrug dem. Ændrer du profilet, opdaterer alle bjælker der bruger det.

Sketcher: <https://wiki.freecad.org/Sketcher_Workbench>

## Fra model til tegning

Når skelettet står, laver du tegningerne i **TechDraw**:

1. Opret et tegningsblad (*Insert Default Page*).
2. Vælg modellen og indsæt en **view** i den ønskede retning – plan (ovenfra), facade, og et
   **tværsnit** gennem væggen så man ser regler og isolering.
3. Tilføj **målsætning** og en titelblok.
4. Eksportér til **PDF** eller **SVG**.

Det bedste: **tegningerne er koblet til modellen.** Ændrer du huset fra 600 til 660 cm i
regnearket, opdaterer både 3D-modellen *og* alle tegninger med nye mål på ét recompute.

## Til illustrationer på sitet

Ud over de tekniske tegninger:

- **Isometrisk skærmbillede:** drej 3D-viewet til en let isometrisk vinkel og tag et
  screenshot – godt til "sådan ser skelettet ud"-billeder.
- **Farvede snit:** BIM' **Section Plane** laver gennemskårne snit, hvor lagene (træ,
  træfiberisolering, lerpuds) ses tydeligt – oplagt til en byggeguide.
- **Render (fotorealistisk):** *Render Workbench* installeres via Addon Manager. Overkill til
  konstruktion, men fint til det færdige hus.

## Realistisk forventning

| Ambitionsniveau | Indsats |
|---|---|
| Ændre en enkelt bjælkes mål | Gratis, virker altid |
| Ét regneark styrer alle **mål** (bjælker strækker sig) | Moderat – kræver udtryk fra start |
| Ét regneark styrer også **antal** regler/spær (arrays) | Mere arbejde, men fuldt muligt |
| Ændre størrelse på et *færdigbygget* projekt bagefter | Svært – planlæg det fra begyndelsen |

## Lad Claude bygge modellen (MCP-server)

Vil du ikke klikke det hele manuelt, findes der **MCP-servere til FreeCAD**, der lader Claude
styre FreeCAD direkte: oprette/ændre objekter, køre Python-kode inde i FreeCAD og tage
skærmbilleder af 3D-viewet, så Claude kan se modellen og rette til undervejs. Det passer godt
til den parametriske tilgang her, fordi hele setuppet (Spreadsheet, aliaser, udtryk,
Draft-arrays) kan skrives via FreeCADs Python-API.

**Anbefaling:** [`neka-nat/freecad-mcp`](https://github.com/neka-nat/freecad-mcp) – den mest
modne (understøtter FreeCAD 1.0/1.1, har skærmbillede-feedback, kører med **Claude Desktop**).
Vil du hellere bruge **Claude Code** i terminalen, så tag
[`contextform/freecad-mcp`](https://github.com/contextform/freecad-mcp) i stedet.

| Din situation | Vælg |
|---|---|
| Standard (Claude Desktop-appen) | `neka-nat/freecad-mcp` |
| Vil bruge Claude Code i terminalen | `contextform/freecad-mcp` |

Sådan kommer du i gang:

1. Installér serveren (kopiér addon'et til FreeCADs `Mod`-mappe og konfigurér Claude – se
   serverens README).
2. Giv Claude **denne guide** som kontekst, så den kender vores dimensioner (45×95, 45×120)
   og 60 cm-modulet.
3. Bed den bygge det parametriske skelet – f.eks. *"opret et Spreadsheet med laengde/bredde/
   modul som aliaser og byg bundrem + regler c/c 600 med udtryk"*.

> **Bemærk:** Det er et **superviseret** værktøj, ikke en autopilot. Det får hurtigt 80 % op
> at stå, men tjek altid mål og placeringer efter – konstruktionstegninger skal være
> korrekte. Serveren kører **lokalt** på din egen maskine (FreeCAD + Claude side om side).

## Nyttige links

- FreeCAD – download: <https://www.freecad.org/downloads.php>
- BIM Workbench (byg skelettet): <https://wiki.freecad.org/BIM_Workbench>
- TechDraw Workbench (lav tegninger): <https://wiki.freecad.org/TechDraw_Workbench>
- Spreadsheet Workbench (styrende mål): <https://wiki.freecad.org/Spreadsheet_Workbench>
- Expressions (udtrykssproget): <https://wiki.freecad.org/Expressions>
- Draft Array (kopier regler/spær): <https://wiki.freecad.org/Draft_OrthoArray>
- Al FreeCAD-dokumentation: <https://wiki.freecad.org/>
- MCP-server (Claude Desktop): <https://github.com/neka-nat/freecad-mcp>
- MCP-server (Claude Code): <https://github.com/contextform/freecad-mcp>
- FreeCAD-forummet (spørg om hjælp): <https://forum.freecad.org/>

---

> Del af den åbne byggeguide. Mål og fremgangsmåde er vejledende – tjek altid selv efter og
> følg gældende regler.
