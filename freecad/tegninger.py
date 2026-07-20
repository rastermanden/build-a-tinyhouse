# -*- coding: utf-8 -*-
"""
2D-konstruktionstegninger ud af en bygget model.

tegn() skriver plan_ovenfra.svg, opstalt_facade.svg, opstalt_gavl.svg og en
tegninger.html der samler dem sammen med et maalskema.

Udsnittet (viewBox) regnes ud af selve projektionen, og maalskemaet laeses ud
af regnearket. Der staar altsaa ingen faste tal i denne fil, og et hus'
tegninger kan ikke komme til at vise andre maal end huset er bygget af.
"""

import os
import re

import FreeCAD as App
import TechDraw

import ark
import skelet

MARGEN = 150  # mm luft omkring tegningen

# retning er projektionsretningen; drej saetter et rotate(90) uden om
# fragmentet, saa opstalterne staar op og ned i stedet for at ligge ned.
ARK = [
    ("plan_ovenfra", "Plan, set ovenfra", (0, 0, 1), False),
    ("opstalt_facade", "Opstalt, facade (lang vaeg)", (0, -1, 0), True),
    ("opstalt_gavl", "Opstalt, gavl", (-1, 0, 0), True),
]

HTML_HOVED = """<!doctype html>
<meta charset="utf-8">
<title>%(titel)s - konstruktionstegninger</title>
<style>
 body{font-family:system-ui,sans-serif;margin:2rem;max-width:60rem}
 h1{font-size:1.4rem} h2{font-size:1.1rem;margin-top:2rem}
 .ark{border:1px solid #ccc;padding:1rem;background:#fff}
 .ark svg{width:100%%;height:auto;display:block}
 table{border-collapse:collapse;font-size:.9rem;margin-top:.5rem}
 th,td{border:1px solid #ddd;padding:.25rem .6rem;text-align:left}
 td.tal{text-align:right;font-variant-numeric:tabular-nums}
 tr.udregnet{color:#666}
 a{color:inherit}
</style>
<p><a href="../index.html">&larr; Alle huse</a></p>
<h1>%(titel)s</h1>
<p>Genereret ud fra den parametriske model. Maal i mm.</p>
"""


def projicer(form, retning, drej):
    """Projicerer formen og regner udsnittet ud af de faktiske koordinater.

    TechDraw.projectToSVG giver et bart <g>-fragment med
    transform="scale(1, -1)" indbygget, altsaa uden <svg>-rod. Et punkt (x, y)
    i path-data ender derfor paa (x, -y). Drejes fragmentet 90 grader oveni,
    bliver det (y, x).
    """
    fragment = TechDraw.projectToSVG(form, App.Vector(*retning))

    tal = re.findall(
        r"-?\d+\.?\d*(?:[eE][-+]?\d+)?",
        " ".join(re.findall(r'd="([^"]+)"', fragment)),
    )
    raa = [(float(tal[i]), float(tal[i + 1])) for i in range(0, len(tal), 2)]
    punkter = [(y, x) if drej else (x, -y) for x, y in raa]

    xs = [p[0] for p in punkter]
    ys = [p[1] for p in punkter]
    kasse = (
        min(xs) - MARGEN,
        min(ys) - MARGEN,
        max(xs) - min(xs) + 2 * MARGEN,
        max(ys) - min(ys) + 2 * MARGEN,
    )
    return fragment, kasse, (max(xs) - min(xs), max(ys) - min(ys))


def skema_html(doc):
    raekker = ['<h2>Maal</h2>\n<table>\n'
               '<tr><th>Maal</th><th>Vaerdi</th><th>Beskrivelse</th></tr>\n']
    for alias, vaerdi, beskrivelse, slags in skelet.maalskema(doc):
        try:
            tekst = "%.1f" % float(vaerdi)
            tekst = tekst[:-2] if tekst.endswith(".0") else tekst
        except (TypeError, ValueError):
            tekst = str(vaerdi)
        raekker.append(
            '<tr class="%s"><td>%s</td><td class="tal">%s</td><td>%s</td></tr>\n'
            % (slags, alias, tekst, beskrivelse)
        )
    raekker.append("</table>\n")
    return "".join(raekker)


def tegn(doc, udmappe, titel):
    """Skriver de tre ark og en tegninger.html til udmappe. Returnerer maal."""
    if not os.path.isdir(udmappe):
        os.makedirs(udmappe)

    former = [o.Shape for o in skelet.emner(doc)]
    samlet = former[0].fuse(former[1:])

    dele = [HTML_HOVED % {"titel": titel}]
    stoerrelser = {}

    for filnavn, overskrift, retning, drej in ARK:
        fragment, kasse, (bred, hoej) = projicer(samlet, retning, drej)
        stoerrelser[filnavn] = (bred, hoej)

        with open(os.path.join(udmappe, filnavn + ".svg"), "w") as f:
            f.write(fragment)

        indhold = ('<g transform="rotate(90)">%s</g>' % fragment
                   if drej else fragment)
        dele.append(
            '<h2>%s - %.0f x %.0f mm</h2>\n'
            '<div class="ark"><svg viewBox="%.0f %.0f %.0f %.0f" '
            'xmlns="http://www.w3.org/2000/svg">%s</svg></div>\n'
            % (overskrift, bred, hoej,
               kasse[0], kasse[1], kasse[2], kasse[3], indhold)
        )

    dele.append(ark.alle(doc, udmappe))
    dele.append(skema_html(doc))

    with open(os.path.join(udmappe, "tegninger.html"), "w") as f:
        f.write("".join(dele))

    return stoerrelser
