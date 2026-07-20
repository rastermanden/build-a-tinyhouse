# -*- coding: utf-8 -*-
"""
Maalsatte detaljetegninger af de enkelte emner.

FreeCADs TechDraw har rigtige maalsaetningsobjekter, men eksport af en
TechDraw-side til SVG kraever GUI'et (TechDrawGui), og hele denne pipeline
koerer headless. Derfor tegnes maalsaetningen her i staedet, oven paa en
kontur der hentes fra den faktiske geometri.

Maalene laeses fra regnearket og konturen fra emnets Shape - der regnes
altsaa ikke noget ud paa ny, saa en tegning kan ikke komme til at vise andre
maal end emnet faktisk har.
"""

import math

import FreeCAD as App

# Stregtykkelser og tekst regnes som en broekdel af tegningens stoerrelse, saa
# et 3612 mm langt spaer og et 145 mm udhug ser ens ud paa papiret.
STIL = """
 .kontur{fill:#f4f1ea;stroke:#222;stroke-width:%(tyk).2f;stroke-linejoin:round}
 .maal{stroke:#b23;stroke-width:%(tynd).2f;fill:none}
 .hjaelp{stroke:#b23;stroke-width:%(tynd).2f;fill:none;stroke-dasharray:%(stiplet)s}
 .pil{fill:#b23}
 .tal{fill:#b23;font-family:system-ui,sans-serif;font-size:%(tekst).1fpx;
      text-anchor:middle;dominant-baseline:auto}
 .note{fill:#036;font-family:system-ui,sans-serif;font-size:%(tekst).1fpx}
 .notelinje{stroke:#036;stroke-width:%(tynd).2f;fill:none}
 .midte{stroke:#888;stroke-width:%(tynd).2f;fill:none;stroke-dasharray:%(midte)s}
"""


class Tegning:
    """Samler en SVG op i mm. z regnes opad, saa der tegnes med (x, -z)."""

    def __init__(self, enhed):
        self.e = enhed          # teksthoejde i mm; alt andet skaleres herfra
        self.dele = []
        self.xs = []
        self.ys = []

    # ---------------------------------------------------------- lavniveau

    def _sesd(self, x, y):
        self.xs.append(x)
        self.ys.append(y)

    def linje(self, x1, z1, x2, z2, klasse="maal"):
        self.dele.append('<path class="%s" d="M %.2f %.2f L %.2f %.2f"/>'
                         % (klasse, x1, -z1, x2, -z2))
        self._sesd(x1, -z1)
        self._sesd(x2, -z2)

    def polygon(self, punkter, klasse="kontur"):
        d = "M " + " L ".join("%.2f %.2f" % (x, -z) for x, z in punkter) + " Z"
        self.dele.append('<path class="%s" d="%s"/>' % (klasse, d))
        for x, z in punkter:
            self._sesd(x, -z)

    def tekst(self, x, z, txt, klasse="tal", drej=0):
        t = ('<text class="%s" x="%.2f" y="%.2f"' % (klasse, x, -z))
        if drej:
            t += ' transform="rotate(%d %.2f %.2f)"' % (drej, x, -z)
        t += ">%s</text>" % txt
        self.dele.append(t)
        self._sesd(x - len(str(txt)) * self.e * 0.3, -z)
        self._sesd(x + len(str(txt)) * self.e * 0.3, -z - self.e)

    def _pil(self, x, z, retning):
        """Pilespids i (x,z) pegende i retning (dx,dz), normaliseret."""
        l = self.e * 0.9
        b = self.e * 0.28
        dx, dz = retning
        # vinkelret vektor
        px, pz = -dz, dx
        p = [(x, -z),
             (x - dx * l - px * b, -(z - dz * l - pz * b)),
             (x - dx * l + px * b, -(z - dz * l + pz * b))]
        self.dele.append('<path class="pil" d="M %s Z"/>'
                         % " L ".join("%.2f %.2f" % q for q in p))

    # ------------------------------------------------------- maalsaetning

    def maal_vandret(self, x1, x2, z, txt=None, hjaelp_fra=None):
        """Vandret maal mellem x1 og x2, maallinjen i koten z."""
        if txt is None:
            txt = "%.0f" % abs(x2 - x1)
        if hjaelp_fra is not None:
            for x in (x1, x2):
                self.linje(x, hjaelp_fra, x, z + math.copysign(self.e * .4,
                                                              z - hjaelp_fra),
                           "hjaelp")
        self.linje(x1, z, x2, z)
        kort = abs(x2 - x1) < self.e * 3
        if kort:
            # for lidt plads: pilene udefra og teksten ved siden af
            self._pil(x1, z, (-1, 0))
            self._pil(x2, z, (1, 0))
            self.tekst(max(x1, x2) + self.e * 2.2, z + self.e * .4, txt)
        else:
            self._pil(x1, z, (-1, 0))
            self._pil(x2, z, (1, 0))
            self.tekst((x1 + x2) / 2, z + self.e * .4, txt)

    def maal_lodret(self, z1, z2, x, txt=None, hjaelp_fra=None):
        """Lodret maal mellem z1 og z2, maallinjen i x."""
        if txt is None:
            txt = "%.0f" % abs(z2 - z1)
        if hjaelp_fra is not None:
            for z in (z1, z2):
                self.linje(hjaelp_fra, z,
                           x + math.copysign(self.e * .4, x - hjaelp_fra), z,
                           "hjaelp")
        self.linje(x, z1, x, z2)
        self._pil(x, z1, (0, -1))
        self._pil(x, z2, (0, 1))
        self.tekst(x, (z1 + z2) / 2, txt, drej=-90)

    def note(self, x, z, txt, mod_x, mod_z):
        """Henvisning: linje fra (mod_x, mod_z) til (x, z), tekst ved (x,z)."""
        self.linje(mod_x, mod_z, x, z, "notelinje")
        anker = "start" if x >= mod_x else "end"
        self.dele.append(
            '<text class="note" x="%.2f" y="%.2f" style="text-anchor:%s">%s</text>'
            % (x + math.copysign(self.e * .3, x - mod_x), -z - self.e * .3,
               anker, txt))
        self._sesd(x + (len(txt) * self.e * .55 if anker == "start"
                        else -len(txt) * self.e * .55), -z)

    # -------------------------------------------------------------- ud

    def svg(self):
        m = self.e * 1.5
        x0, x1 = min(self.xs) - m, max(self.xs) + m
        y0, y1 = min(self.ys) - m, max(self.ys) + m
        stil = STIL % {
            "tyk": self.e * .07, "tynd": self.e * .04,
            "tekst": self.e,
            "stiplet": "%.1f %.1f" % (self.e * .3, self.e * .25),
            "midte": "%.1f %.1f %.1f %.1f" % (self.e * .9, self.e * .3,
                                              self.e * .2, self.e * .3),
        }
        return ('<svg viewBox="%.1f %.1f %.1f %.1f" '
                'xmlns="http://www.w3.org/2000/svg"><style>%s</style>%s</svg>'
                % (x0, y0, x1 - x0, y1 - y0, stil, "".join(self.dele)))


# ------------------------------------------------------------------ kontur

def kontur(shape, normal, offset, akser):
    """Ordnet 2D-polygon af et plant snit gennem shape.

    normal   snitplanets normal, fx (1,0,0)
    offset   hvor langs normalen der snittes
    akser    hvilke to komponenter der bliver (x, z) i tegningen,
             fx ("y","z") - kan praefixes med "-" for at vende retningen
    """
    wires = shape.slice(App.Vector(*normal), offset)
    if not wires:
        raise ValueError("snittet ramte ikke emnet")
    w = max(wires, key=lambda x: x.Length)

    def komp(p, spec):
        v = getattr(p, spec.lstrip("-"))
        return -v if spec.startswith("-") else v

    pts = [(komp(p, akser[0]), komp(p, akser[1]))
           for p in w.discretize(Deflection=0.05)]
    ren = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - ren[-1][0]) > 1e-6 or abs(p[1] - ren[-1][1]) > 1e-6:
            ren.append(p)
    if (abs(ren[0][0] - ren[-1][0]) < 1e-6
            and abs(ren[0][1] - ren[-1][1]) < 1e-6):
        ren.pop()
    return ren


def flyt_til_nul(pts):
    """Flytter polygonen saa dens nederste venstre hjoerne ligger i (0,0)."""
    x0 = min(p[0] for p in pts)
    z0 = min(p[1] for p in pts)
    return [(round(x - x0, 2), round(z - z0, 2)) for x, z in pts]


def spaer_fladt(doc, navn="Spaer"):
    """Spaeret roteret tilbage saa det ligger fladt, som paa hoevlebaenken."""
    s = doc.Spreadsheet
    vinkel = float(s.spaer_vinkel)
    z0 = float(s.oplaeg_front) - float(s.udhug)
    sh = doc.getObject(navn).Shape.copy()
    pl = App.Placement(App.Vector(0, 0, 0),
                       App.Rotation(App.Vector(1, 0, 0), vinkel),
                       App.Vector(0, 0, z0))
    return sh.transformGeometry(pl.toMatrix())
