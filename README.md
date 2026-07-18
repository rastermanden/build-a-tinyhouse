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
  data/materialelister.json   # prædefinerede mål → fuld materialeliste pr. trin
  assets/steps/<slug>/  # billeder for hvert byggetrin (organiseret i mapper)
  components/           # Header, Footer, Galleri, MaterialTabel, m.fl.
  pages/                # forside, planlægning, beregner, om-og-credits, steps/[slug]
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

## Sådan tilføjer du et mål til beregneren

Materialeberegneren slår op i `src/data/materialelister.json`. Tilføj et nyt objekt under
`praedefineredeMaal` med `laengde_cm`, `bredde_cm` og en `materialerPrStep` for hvert af de
9 trin. Mål skal gå op i **60 cm** (længde max 600, bredde max 360).

> Mængderne i JSON-filen er **vejledende estimater** til planlægning – tjek altid selv efter.

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
