# -*- coding: utf-8 -*-
"""Verificerer alle huse i huse.py geometrisk. \n\nKoeres headless:\n\n    ~/Applications/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage \\\n        --console freecad/tjek.py\n\nTjekker bbox, at gavlreglerne rammer spaerets underside, at stroefagene er\njaevne, at ingen emner overlapper, og at valideringen afviser umulige maal."""
import os
import sys
import math

HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path:
    sys.path.insert(0, HER)

import FreeCAD as App
import Part
import huse
import skelet

import builtins
import functools

# FreeCADs konsol bufrer stdout, og ved omdirigering forsvinder print()
# helt - kørslen virker, men man ser aldrig resultatet. stderr kommer
# pålideligt igennem, så al besked herfra gaar den vej.
print = functools.partial(builtins.print, file=sys.stderr, flush=True)


fejl = 0
for hus in huse.HUSE:
    doc = skelet.byg("T_" + hus["navn"], **hus["maal"])
    s = doc.Spreadsheet
    top = skelet.emner(doc)
    L, B = float(s.laengde), float(s.bredde)
    print("\n=== %s (%.0f x %.0f) ===" % (hus["navn"], L, B))

    xs = [];  ys = [];  zs = []
    for o in top:
        bb = o.Shape.BoundBox
        xs += [bb.XMin, bb.XMax]; ys += [bb.YMin, bb.YMax]; zs += [bb.ZMin, bb.ZMax]
    print("bbox X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f  (%d emner)"
          % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), len(top)))
    # Gavllaegten ligger uden paa hjoernespaeret og rager derfor gavllaegte_b ud
    # over konstruktionsmaalet i begge gavle. Alt andet skal ligge indenfor.
    N = float(s.gavllaegte_b)
    if abs(min(xs) + N) > .1 or abs(max(xs) - (L + N)) > .1 or abs(min(ys)) > .1:
        print("  !! bbox er ikke -%.0f..%.0f i x og 0.. i y" % (N, L + N))
        fejl += 1

    # gavlregler skal ramme spaerets underside
    tan = math.tan(math.radians(float(s.spaer_vinkel)))
    gv = doc.getObject("Regel_gavl_venstre")
    modul = float(s.modul)
    y = modul
    vaerst = 0
    while y < B - modul + 1:
        boks = Part.makeBox(300, float(s.regel_b), 6000, App.Vector(-20, y, 0))
        del_ = gv.Shape.common(boks)
        if del_.Volume > 0:
            forv = float(s.oplaeg_front) - float(s.udhug) - y * tan
            vaerst = max(vaerst, abs(del_.BoundBox.ZMax - forv))
        y += modul
    print("gavlregler mod spaer: stoerste afvigelse %.2f mm" % vaerst)
    if vaerst > 0.6:
        print("  !! gavlregler rammer ikke spaeret"); fejl += 1

    # stroe
    arr = [o for o in doc.Objects if o.Name.startswith("Array")
           and getattr(o, "Base", None) and "Stroe" in o.Base.Name]
    sx = sorted((s_.BoundBox.XMin, s_.BoundBox.XMax)
                for a in arr for s_ in a.Shape.Solids)
    mellem = [round(sx[i + 1][0] - sx[i][1]) for i in range(len(sx) - 1)]
    print("stroe: %d stk, fri afstand %s" % (len(sx), sorted(set(mellem))))
    if len(set(mellem)) > 1:
        print("  !! ujaevne stroefag"); fejl += 1

    # klask
    klask = 0
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            if top[i].Shape.common(top[j].Shape).Volume > 1.0:
                print("  !! KLASK %s <-> %s" % (top[i].Name, top[j].Name))
                klask += 1
    print("sammenstoed: %s" % ("ingen" if not klask else klask))
    fejl += klask
    App.closeDocument(doc.Name)

# validering skal afvise umulige maal
print("\n=== validering ===")
for navn, maal in (("6300 ikke modul", {"laengde": 6300}),
                   ("bredde 3500", {"bredde": 3500}),
                   ("fladt tag", {"vaeg_bag": 3150}),
                   ("ukendt maal", {"hoejde": 2000})):
    try:
        skelet.kontrollér(dict(skelet.STANDARD, **maal))
        print("  !! %s blev IKKE afvist" % navn); fejl += 1
    except ValueError as e:
        print("  afvist: %s -> %s" % (navn, str(e)[:70]))

print("\n%s" % ("ALT OK" if not fejl else "%d FEJL" % fejl))
