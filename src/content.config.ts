import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Ét byggestep = én markdown-fil i src/content/steps/.
// Filnavnet (fx "01-bundrem") bestemmer id/slug og rækkefølgen.
const steps = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/steps' }),
  schema: z.object({
    // Rækkefølge i byggeprocessen (1 = først).
    order: z.number().int().positive(),
    // Titel som vist på siden og i navigationen.
    titel: z.string(),
    // Kort resumé til oversigt/kort.
    resume: z.string(),
    // Nøglen der matcher materialelister.json (materialerPrStep).
    beregnerNoegle: z.string(),
    // Estimeret tid (fri tekst, fx "1-2 dage").
    tid: z.string().optional(),
    // Generisk referenceliste over værktøj til dette step.
    vaerktoj: z.array(z.string()).default([]),
    // Generisk referenceliste over materialer (mængder findes i beregneren).
    materialer: z
      .array(
        z.object({
          navn: z.string(),
          dimension: z.string().optional(),
          note: z.string().optional(),
        }),
      )
      .default([]),
  }),
});

export const collections = { steps };
