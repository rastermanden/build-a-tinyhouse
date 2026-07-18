// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// Base-stien kan sættes ved build-tid, så det samme projekt kan bygges både til
// produktion (roden af gh-pages) og til PR-previews (en undermappe pr. PR).
// F.eks. PUBLIC_BASE_PATH=/build-a-tinyhouse/pr-preview/pr-12/
const base = process.env.PUBLIC_BASE_PATH ?? '/build-a-tinyhouse/';

export default defineConfig({
  site: 'https://rastermanden.github.io',
  base,
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
});
