# Tegninger til byggeguiden

## Brainstorm og valg

FreeCAD-modellen har allerede seks byggegrupper i faktisk rækkefølge (bundrem, vægregler, topskinner, gavlregler, spær og gulv) og `tegninger.py` bygger plan/facade/gavl fra den samlede geometri. `ark.py`/`detaljer.py` genererer desuden SVG-detaljer med mål fra modelgeometrien: spærets sæder, vægreglernes bundudskæring, gavlregler, bundremshjørne og gavltop. Astro-siden finder nu kun fotoformater fra `src/assets/steps/<slug>/`; den viser ikke tegninger. Guideindholdet spænder videre end modellens nuværende omfang (fx isolering, vinduer, tagdækning og lerpuds), og bør ikke give indtryk af at disse dele er modelleret.

Mulige tilgange:

1. Generér kumulative 3D-SVG-visninger for hvert FreeCAD-byggetrin og udvalgte målte udskæringsdetaljer, gem dem som statiske assets, og vis dem på de tilsvarende guide-sider. Knyt kun de seks modellerede trin og relevante detaljer til tegninger; vis ikke tegninger på de senere trin, som modellen ikke dækker.
2. Eksportér 3D-visninger direkte til PNG fra FreeCAD og læg rasterbilleder ind i det eksisterende galleri. Det kræver GUI-/renderopsætning, mister skalerbarhed og gør målsatte detaljer sværere at læse.
3. Tegn illustrationer separat i hånden eller med HTML/SVG-komponenter. Det er hurtigt for få billeder, men duplikerer mål og geometri, som allerede findes i FreeCAD, og risikerer at tegninger driver fra modellen.

**Valg:** tilgang 1. Den genbruger modellens grupper, geometri og eksisterende målte detaljeark, er læsbar på web i SVG og kan bygges uden at opfinde geometri. Integrationen skal være eksplicit og statisk; FreeCAD behøver ikke at køre under Astro-build. Hvis FreeCAD ikke findes i arbejdsmiljøet, skal dette dokumenteres, og asset-genereringen/valideringen skal køres senere i FreeCAD 1.0+.

## Kort plan

1. Tilføj til `byg_alle.py` generering af kumulative trinvisninger med TechDraw fra gruppens faktiske emner, med udklip beregnet fra projektionen og selvstændige SVG-filer.
2. Saml trin-SVG'er og relevante eksisterende detalje-SVG'er i `public/tegninger/`, og vis dem via en tilgængelig billedsektion på de relevante Astro byggevejledninger. Beskriv FreeCAD-kommandoen og at senere byggetrin ikke er del af modellen.
3. Byg sitet og kør FreeCADs `tjek.py`; ret eventuelle fejl og commit plan samt implementering på arbejdsgrenen.

## Vigtigt om snit

De viste målte udskæringer er i den nuværende model: sæde/notch i spær, fod-udskæring i vægregel, ens udskæring i gavlregler, hjørnesamling i bundrem og gavltop. Det er konstruktionstegninger fra den parametriske model, ikke dokumentation for lokale regler, dimensionering eller bæreevne; de endelige mål og snit skal verificeres af den byggende.

## Implementeringsstatus

Plan skrevet efter gennemgang af `freecad/skelet.py`, `tegninger.py`, `detaljer.py`, `huse.py`, `byg_alle.py`, `ark.py` samt Astro-trinsiderne.

- [x] Kumulative trinvisninger og målsatte detalje-SVG'er genereret for 6000x3600; vist på bundrem, spær/regler, loft og gulv.
- [x] `npm run build` (15 sider bygget). Første forsøg viste at `sharp` manglede efter `npm install`; installeret som projekt-afhængighed og låsefil opdateret, hvorefter build lykkedes.
- [x] `freecadcmd --console freecad/tjek.py` (`ALT OK`, alle tre huse)
- [x] Git commit på `loom/tinyhouse-drawings` (ingen push)

`npm install` rapporterede 12 audit-advarsler (1 low, 1 moderate, 9 high, 1 critical) i dependency-træet; ingen automatisk `npm audit fix` blev kørt.

Genopbyg og synkronisér assets fra repo-roden med:

```sh
freecadcmd --console freecad/byg_alle.py
```

Kommandoen genererer også modellerne 7200x4200 og 4800x3000 under `ud/`, men website-assets synkroniseres bevidst kun fra standardhuset 6000x3600. SVG-filerne er source-controlled under `public/tegninger/6000x3600/`, så almindeligt Astro-build ikke kræver FreeCAD.

## Åbne spørgsmål til Martin

Ingen afklaringer er nødvendige for at implementere første udgave. Vil Martin senere have detaljer vist som printvenlige PDF'er, eller er SVG-visning på de relevante trin tilstrækkelig?

*Brainstorm og førsteudgave planlagt af kodeagent; Martin bør godkende endelige byggetegninger før brug til savning eller konstruktion.*

*Opdateres ved afslutning.*
