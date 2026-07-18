// Samler de tilgængelige materialelister ét sted, så både Materialeliste-siden
// og de enkelte byggetrin bruger samme data. Hver liste har underlister pr.
// byggetrin (materialerPrTrin) – strukturen ligger i selve JSON-filen.
import faktisk from '../data/faktisk-materialeliste.json';

export interface TrinVare {
  tekst: string;
  maengde: number;
  enhed: string;
  note?: string;
  kategori?: string;
}

export interface Liste {
  id: string;
  navn: string;
  maal: string;
  areal: number;
  materialerPrTrin: Record<string, TrinVare[]>;
  oevrigt: TrinVare[];
}

const maal = (l: number, b: number): string =>
  `${l / 100} × ${b / 100} m`.replace(/\./g, ',');

const faktiskListe: Liste = {
  id: faktisk.info.id,
  navn: faktisk.info.navn,
  maal: maal(faktisk.info.husLaengde_cm, faktisk.info.husBredde_cm),
  areal: faktisk.info.husAreal_m2,
  materialerPrTrin: faktisk.materialerPrTrin as Record<string, TrinVare[]>,
  oevrigt: faktisk.oevrigt as TrinVare[],
};

// P.t. findes kun den faktiske liste. Flere størrelser kan tilføjes her.
export const lister: Liste[] = [faktiskListe];

export const stepRaekkefolge: string[] = faktisk.stepRaekkefolge;
export const stepTitler: Record<string, string> = faktisk.stepTitler;

// localStorage-nøgle for den valgte liste (huskes på tværs af siden).
export const STORAGE_KEY = 'valgtMaterialeliste';
