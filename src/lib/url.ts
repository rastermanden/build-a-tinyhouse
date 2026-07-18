// Bygger en intern URL med den korrekte base-sti (virker både i produktion og
// i PR-previews, hvor base-stien er en undermappe).
export function href(path = ''): string {
  const base = import.meta.env.BASE_URL; // slutter altid med "/"
  const clean = path.replace(/^\//, '');
  return base + clean;
}
