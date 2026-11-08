# 🛖 Byg dit eget tiny house

En åben, trin-for-trin byggeguide til at bygge sit eget tiny house i naturmaterialer –
træ, træfiberisolering og lerpuds. Sitet dokumenterer processen, så andre nemt kan bygge
deres eget.

Bygget med [Astro](https://astro.build/) + [Tailwind CSS](https://tailwindcss.com/).

## 🙏 Stor tak til småBYG & Jonas

Hele metoden, materialevalget og inspirationen kommer fra tiny house-kurset hos
**[småBYG](https://smaabyg.nu/)** ved **Jonas**. Teksterne er skrevet med egne ord, men
bygger helt på deres undervisning og filosofi om at bo småt, billigt og klimavenligt.
Al ære går til dem – tag på kursus, hvis du selv drømmer om et tiny house!

## Kom i gang

```bash
npm install
npm run dev      # udviklingsserver på http://localhost:4321
npm run build    # bygger sitet til dist/
npm run preview  # forhåndsvis produktions-build lokalt
```

## Projektstruktur

```
src/
  content/steps/        # ét byggetrin = én markdown-fil (rækkefølge via "order")
  data/materialelister.json          # prædefinerede mål → fuld materialeliste pr. trin
  data/faktisk-materialeliste.json   # den rigtige indkøbsliste fra fakturaen (konkrete varer)
  assets/steps/<slug>/  # billeder for hvert byggetrin (organiseret i mapper)
  assets/faktisk-materialeliste/  # billeder til den faktiske materialeliste (fx skrueæsker)
  components/           # Header, Footer, Galleri, MaterialTabel, m.fl.
  pages/                # forside, planlægning, materialeliste (faktisk-materialeliste), om-og-credits, steps/[slug]
public/                 # favicon m.m.
```

### Byggetrin (rækkefølge)

Bundrem → Spær og regler → Gulv → Loft → Vægge og isolering → Vinduer og døre → Tag →
Yderbeklædning → Lerpuds af vægge.

## Sådan tilføjer du billeder

Læg billedfiler i mappen for det pågældende trin, fx:

```
src/assets/steps/bundrem/mit-billede.jpg
```

Understøttede formater: `.jpg`, `.jpeg`, `.png`, `.webp`, `.avif`. Billederne vises
automatisk i galleriet på trinnets side, optimeres ved build, og filnavnet bruges som
alt-tekst. Ingen kodeændring nødvendig.

## Materialeliste (én side)

Siden `src/pages/faktisk-materialeliste.astro` (rute `/faktisk-materialeliste`, vist som
**Materialeliste**) er den ene side for materialelister. Den indeholder to ting:

1. **Min faktiske indkøbsliste** fra fakturaen, delt op pr. byggetrin (se nedenfor).
2. **Vejledende estimater** for andre størrelser – en størrelsesvælger, der tegner
   estimatet for det valgte mål klient-side, med print/kopi.

Siden er ikke en live-beregner, men færdige, statiske lister.

> `/beregner` er slået sammen med denne side og findes ikke længere som selvstændig side.
> `src/pages/beregner.astro` er nu kun en viderestilling (meta refresh + JS) til
> `/faktisk-materialeliste`, så gamle links og bogmærker stadig virker.

Estimatmålene ligger under `praedefineredeMaal` i `src/data/materialelister.json` med
`laengde_cm`, `bredde_cm` og en `materialerPrStep` for hvert af de 9 trin (mål i **60 cm**-trin).
Vil du tilføje en ny størrelse, så læg et objekt mere i `praedefineredeMaal` – vælgeren på
siden bygges automatisk ud fra listen.

> Mængderne i `materialelister.json` er **vejledende estimater** – den faktiske liste
> (600 × 335 cm) er derimod konkrete indkøb fra fakturaen.

`info.standardHus` i samme fil er standardhuset, sådan som **modellen** måler det
(`freecad/skelet.py` STANDARD): 6000 × 3350 mm = 6,0 × 3,35 m (20,1 m²), udledt som
`gavlrem_l 3170 + 2 × bundrem 90`. Det er de tal, savværks-e-mailen bruger, og det er det
samme hus som den faktiske liste (`faktisk-600x335`).

## Faktisk materialeliste (fakturaen)

Ud over de vejledende estimater viser siden den **rigtige indkøbsliste** fra et konkret byg:
`src/data/faktisk-materialeliste.json`. Fakturaens varer er delt op **pr. byggetrin** i
`materialerPrTrin` (samme trin-nøgler som estimatet), plus en `oevrigt`-liste til varer, der
ikke er trinspecifikke (bits, tape, afgift m.m.). Hver vare har `tekst`, `maengde`, `enhed` og
en `kategori`. Billeder til siden (fx skrueæsker) lægges i `src/assets/faktisk-materialeliste/`.

**Valgt liste på byggetrinnene:** `src/lib/lister.ts` samler de tilgængelige lister ét sted.
Man vælger en liste på Materialeliste-siden (gemmes i `localStorage` under nøglen
`valgtMaterialeliste`), og hvert byggetrin viser derefter et banner med den valgte liste og
netop det trins materialer. Er der ikke aktivt valgt en liste, bruges **den første liste som
standard**, så trinnet altid viser materialer. Man kan skifte mellem lister (der findes p.t.
kun én, men flere kan tilføjes ved at udvide `lister` i `lister.ts`).

Hvert byggetrin viser **kun** materialer, når trinnet er markeret som klar med
`materialerKlar: true` i frontmatter; ellers står der **"Kommer senere"**. Sæt flaget, når du
har opdateret trinnets `materialerPrTrin` i `faktisk-materialeliste.json` med faktiske tal. Der
er ikke længere en separat, generisk materialetabel på trinnene – den valgte liste er kilden.

## Sådan redigerer du et byggetrin

Rediger den tilsvarende markdown-fil i `src/content/steps/`. Frontmatter styrer titel,
resumé, værktøjsliste og `materialerKlar`-flaget; brødteksten skrives i markdown.

## Hosting: GitHub Pages + PR-preview

Sitet udgives til `gh-pages`-branchen:

- **Produktion** (`.github/workflows/deploy.yml`): bygges ved push til `main` og lægges i
  roden af `gh-pages` → `https://rastermanden.github.io/build-a-tinyhouse/`.
- **PR-preview** (`.github/workflows/pr-preview.yml`): hver pull request bygges til
  `pr-preview/pr-<nr>/` og der kommenteres et preview-link på PR'en (via
  [`rossjrw/pr-preview-action`](https://github.com/rossjrw/pr-preview-action)). Previewet
  fjernes automatisk, når PR'en lukkes.

### Engangsopsætning (repo-ejer)

Under **Settings → Pages** skal *Source* sættes til **Deploy from a branch** og branchen
til **`gh-pages`** (mappe `/ (root)`). Herefter kører det automatisk.

## Tegninger i FreeCAD

Vil du lave dine egne konstruktionstegninger, ligger der en kort guide i
[`docs/freecad-parametrisk-konstruktion.md`](docs/freecad-parametrisk-konstruktion.md).
Den viser, hvordan du bygger træskelettet parametrisk i FreeCAD med vores dimensioner
(45×145 og 45×195 mm, bundrem 90×195 mm, 60 cm-modul), så du kan ændre husets længde/bredde
ét sted og få både 3D-model og tegninger til at følge med. Med links til de relevante
FreeCAD-workbenches.

## Ansvarsfraskrivelse

Dette er et personligt hobbyprojekt og er ikke officielt tilknyttet småBYG. Materialemængder
og mål er vejledende. Følg altid gældende regler og vejledninger, og tjek selv efter.
