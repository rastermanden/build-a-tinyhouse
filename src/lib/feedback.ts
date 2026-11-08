// Ét sted til feedback-formularen: base-URL til Google Forms og id'et på det
// felt, hvor emnet forudfyldes. Alle feedback-links bygges herfra, så URL og
// felt-id kun står ét sted.
const FORM_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScCDcK98la9Bnkx1APBer6kvOWjCOgo62Dt_4qEX4dlS_gApw/viewform';

const EMNE_FELT = 'entry.2097547285';

// Emne for feedback, der gælder hele siden (bruges i footeren).
export const HELE_SIDEN = 'hele siden';

// Bygger formularens URL med emnet forudfyldt. Emnet URL-encodes, så fx
// mellemrum bliver %20 og "æ" bliver %C3%A6.
export function feedbackUrl(emne: string): string {
  return `${FORM_URL}?usp=pp_url&${EMNE_FELT}=${encodeURIComponent(emne)}`;
}
