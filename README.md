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
  pages/                # forside, planlægning, beregner, faktisk-materialeliste, om-og-credits, steps/[slug]
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

## Materialelister (statiske lister)

Siden `src/pages/beregner.astro` (rute `/beregner`, vist som **Materialelister**) er ikke en
live-beregner, men viser færdige, statiske lister. Længde/bredde-vælgeren indeholder p.t. kun
den ene færdige størrelse, **600 × 360 cm** (mit faktiske byg), som henviser til den faktiske
liste. Vil du tilføje en ny størrelse, så udvid `laengder`/`bredder` i frontmatter og læg et
objekt under `praedefineredeMaal` i `src/data/materialelister.json` med `laengde_cm`,
`bredde_cm` og en `materialerPrStep` for hvert af de 9 trin (mål i **60 cm**-trin).

> Mængderne i `materialelister.json` er **vejledende estimater** – den faktiske liste
> (600 × 360 cm) er derimod konkrete indkøb fra fakturaen.

## Faktisk materialeliste (fakturaen)

Ud over de vejledende estimater findes en side med den **rigtige indkøbsliste** fra et
konkret byg: `src/pages/faktisk-materialeliste.astro`, der læser
`src/data/faktisk-materialeliste.json`. Varerne er grupperet i kategorier (konstruktionstræ,
gulv, loft, tag, isolering & tætning, skruer & befæstelse, lim/sand/øvrigt) med tekst og
mængde afskrevet fra fakturaen. Billeder til siden (fx skrueæsker) lægges i
`src/assets/faktisk-materialeliste/`.

## Sådan redigerer du et byggetrin

Rediger den tilsvarende markdown-fil i `src/content/steps/`. Frontmatter styrer titel,
resumé, værktøjsliste og den generiske materialeliste; brødteksten skrives i markdown.

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

## Ansvarsfraskrivelse

Dette er et personligt hobbyprojekt og er ikke officielt tilknyttet småBYG. Materialemængder
og mål er vejledende. Følg altid gældende regler og vejledninger, og tjek selv efter.
