# -*- coding: utf-8 -*-
"""
Bygger alle huse i huse.py og skriver model + tegninger for hvert af dem.

Koeres headless:

    ~/Applications/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \
        --console freecad/byg_alle.py

Resultatet lander i ud/<navn>/ med en .FCStd, tre SVG-ark og en
tegninger.html, plus en ud/index.html der samler dem.

Et hus der ikke kan lade sig goere stopper ikke de andre - fejlen skrives ud
og huset markeres i oversigten. Afslutter med status 1 hvis noget fejlede, saa
det kan fanges i et script.
"""

import os
import shutil
import sys
import traceback

HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path:
    sys.path.insert(0, HER)

import FreeCAD as App

import huse
import skelet
import tegninger

import builtins
import functools

# FreeCADs konsol bufrer stdout, og ved omdirigering forsvinder print()
# helt - kørslen virker, men man ser aldrig resultatet. stderr kommer
# pålideligt igennem, så al besked herfra gaar den vej.
print = functools.partial(builtins.print, file=sys.stderr, flush=True)


UD = os.path.join(os.path.dirname(HER), "ud")

INDEX_HOVED = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tinyhouse - alle huse</title>
<style>
 :root{color-scheme:light dark}
 body{font-family:system-ui,sans-serif;margin:2rem auto;max-width:50rem;
      padding:0 1rem;background:#fff;color:#111}
 h1{font-size:1.4rem}
 .tabel{overflow-x:auto}
 table{border-collapse:collapse;width:100%;margin-top:1rem}
 th,td{border:1px solid #ddd;padding:.4rem .7rem;text-align:left}
 td.tal{text-align:right;font-variant-numeric:tabular-nums}
 .fejl{color:#a00}
 a{color:inherit}
 @media (prefers-color-scheme:dark){
   body{background:#16181c;color:#e6e6e6}
   th,td{border-color:#3a3a3a}
   .fejl{color:#f66}
 }
</style>
<h1>Tinyhouse - alle huse</h1>
<div class="tabel">
<table>
<tr><th>Hus</th><th>Laengde</th><th>Bredde</th><th>Haeldning</th><th>Emner</th></tr>
"""


def byg_et(hus):
    """Bygger og tegner ét hus. Returnerer en raekke til oversigten."""
    navn = hus["navn"]
    titel = hus.get("titel", navn)
    udmappe = os.path.join(UD, navn)

    # Ryd husets mappe foerst. Ellers bliver omdoebte og fjernede emner
    # staaende som levn ved siden af de nye ark, og antallet af ark ser
    # hoejere ud end det er.
    if os.path.isdir(udmappe):
        shutil.rmtree(udmappe)

    doc = skelet.byg("Hus_" + navn, **hus["maal"])
    try:
        tegninger.tegn(doc, udmappe, titel)
        doc.saveAs(os.path.join(udmappe, "skelet.FCStd"))

        sheet = doc.Spreadsheet
        antal = len(skelet.emner(doc))
        print("  %-12s %5.0f x %5.0f mm  %.2f %%  %2d emner"
              % (navn, sheet.laengde, sheet.bredde, sheet.haeldning_pct, antal))
        return (
            '<tr><td><a href="%s/tegninger.html">%s</a></td>'
            '<td class="tal">%.0f</td><td class="tal">%.0f</td>'
            '<td class="tal">%.2f %%</td><td class="tal">%d</td></tr>\n'
            % (navn, titel, sheet.laengde, sheet.bredde,
               sheet.haeldning_pct, antal)
        )
    finally:
        App.closeDocument(doc.Name)


def main():
    if not os.path.isdir(UD):
        os.makedirs(UD)

    raekker = []
    fejlede = []

    for hus in huse.HUSE:
        navn = hus["navn"]
        try:
            raekker.append(byg_et(hus))
        except Exception as fejl:
            fejlede.append(navn)
            print("  %-12s FEJLEDE: %s" % (navn, fejl))
            traceback.print_exc()
            raekker.append(
                '<tr class="fejl"><td>%s</td><td colspan="4">%s</td></tr>\n'
                % (navn, fejl)
            )

    with open(os.path.join(UD, "index.html"), "w") as f:
        f.write(INDEX_HOVED)
        f.writelines(raekker)
        f.write("</table>\n</div>\n")

    bygget = len(huse.HUSE) - len(fejlede)
    print("\n%d af %d huse bygget -> %s/index.html"
          % (bygget, len(huse.HUSE), UD))
    if fejlede:
        print("fejlede: %s" % ", ".join(fejlede))
        sys.exit(1)


main()
