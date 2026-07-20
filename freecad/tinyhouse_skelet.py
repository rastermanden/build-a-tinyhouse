# -*- coding: utf-8 -*-
"""
Parametrisk tiny house-skelet til FreeCAD 1.0+.

Bygger regneark + bundrem, vaegregler, topskinne og spaer, hvor alle maal er
bundet til regnearket med udtryk. Skift et tal i regnearket, tryk F5, og hele
skelettet foelger med.

Dimensioner fra docs/freecad-parametrisk-konstruktion.md:
  regler / skinner   45 x 95 mm
  spaer              45 x 120 mm
  modul (c/c)        600 mm
  reference          6000 x 3600 mm

Bundremmen er IKKE 45 x 95. Den staar paa hoejkant som gulvbjaelke:
  front / bag        2 laegter a 45 mm limet sammen -> 90 mm tyk, 195 mm hoej
  gavlender          enkelt laegte                  -> 45 mm tyk, 195 mm hoej

De to laegter i front og bag er separate emner i modellen (_ydre og _indre),
saa limfugen ses paa tegningerne og hver laegte kan taelles i styklisten.

Der er INGEN bundskinne. Alle fire vaegges regler staar direkte paa
bundremmen og gaar op til underkant topskinne.

Vaeggen staar OVEN PAA bundremmen. vaeghoejde (2400) er vaeggens egen hoejde
maalt fra gulv (regler + topskinne). Samlet hoejde til overkant topskinne
bliver dermed bundrem_h + vaeghoejde = 2595 mm.

Brug: FreeCAD -> View -> Panels -> Python console -> indsaet hele filen.
"""

import FreeCAD as App
import Draft

DOC = "TinyhouseSkelet"

# ---------------------------------------------------------------- regneark

doc = App.newDocument(DOC)
sheet = doc.addObject("Spreadsheet::Sheet", "Spreadsheet")

PARAMETRE = [
    ("B1", 6000, "laengde", "Husets laengde (X)"),
    ("B2", 3600, "bredde", "Husets bredde (Y)"),
    ("B3", 600, "modul", "c/c mellem regler og spaer"),
    ("B4", 45, "regel_b", "Regelbredde / tykkelse paa skinner"),
    ("B5", 145, "regel_h", "Regeldybde = vaegtykkelse"),
    ("B6", 120, "spaer_h", "Spaerhoejde"),
    ("B7", 2400, "vaeghoejde", "Vaeggens egen hoejde over bundrem"),
    ("B8", 195, "bundrem_h", "Bundremmens hoejde (paa hoejkant)"),
    ("B9", 190, "udskaering_h", "Udskaeringens hoejde i reglen"),
]

for celle, vaerdi, alias, beskrivelse in PARAMETRE:
    sheet.set(celle, str(vaerdi))
    sheet.setAlias(celle, alias)
    sheet.set(celle.replace("B", "A"), beskrivelse)

# Udregnede maal. antal_* er totalen inkl. endestolpen; array_* er det antal
# Draft-arrayet skal lave, fordi endestolpen saettes separat (se nedenfor).
UDREGNET = [
    ("B10", "=2 * regel_b", "bundrem_b", "Bundrem front/bag: 2 laegter limet"),
    ("B11", "=round(laengde / modul) + 1", "antal_regler", "Regler i lang vaeg"),
    ("B12", "=antal_regler - 1", "array_x", "Heraf i array"),
    ("B13", "=round(bredde / modul) + 1", "antal_gavl", "Regler i gavl"),
    ("B14", "=antal_gavl - 1", "array_y", "Heraf i array"),
    ("B15", "=vaeghoejde - regel_b + udskaering_h", "regel_l", "Regel i lang vaeg, inkl. udskaering"),
    ("B16", "=bundrem_h + vaeghoejde", "total_h", "Overkant topskinne over terraen"),
    ("B17", "=bundrem_h - udskaering_h", "regel_z", "Reglens underkant over terraen"),
    ("B18", "=laengde - 2 * regel_b", "bundrem_l", "Front/bag mellem gavlremmene"),
    ("B19", "=vaeghoejde + udskaering_h", "regel_l_gavl", "Gavlregel, inkl. udskaering"),
]

for celle, formel, alias, beskrivelse in UDREGNET:
    sheet.set(celle, formel)
    sheet.setAlias(celle, alias)
    sheet.set(celle.replace("B", "A"), beskrivelse)

doc.recompute()

# ---------------------------------------------------------------- hjaelpere

S = "Spreadsheet."


def bjaelke(navn, laengde, bredde, hoejde, x=None, y=None, z=None):
    """Part::Box hvor alle maal er udtryk mod regnearket."""
    o = doc.addObject("Part::Box", navn)
    o.setExpression("Length", laengde)
    o.setExpression("Width", bredde)
    o.setExpression("Height", hoejde)
    for akse, udtryk in (("x", x), ("y", y), ("z", z)):
        if udtryk:
            o.setExpression("Placement.Base." + akse, udtryk)
    return o


def regel(navn, l, w, h, udsk_l, udsk_w, x=None, y=None, z=None,
          udsk_x=None, udsk_y=None):
    """Regel med udskaering i bunden, saa den hviler paa bundremmen.

    Emnet er hoejere end den fri vaeghoejde: den gaar udskaering_h ned forbi
    bundremmens overkant. Udskaeringen fjernes med en Part::Cut, saa den ses
    i 3D og i snit, og saa emnet kan maalsaettes korrekt i styklisten.
    """
    emne = bjaelke(navn + "_emne", l, w, h, x, y, z)
    udsk = bjaelke(
        navn + "_udsk",
        udsk_l,
        udsk_w,
        S + "udskaering_h",
        x=udsk_x if udsk_x else x,
        y=udsk_y if udsk_y else y,
        z=z,
    )
    snit = doc.addObject("Part::Cut", navn)
    snit.Base = emne
    snit.Tool = udsk
    return snit


def array(base, retning, antal, interval):
    """Draft Ortho Array med antal og interval styret af regnearket."""
    v = App.Vector(600, 0, 0) if retning == "x" else App.Vector(0, 600, 0)
    a = Draft.make_ortho_array(
        base, v, App.Vector(0, 0, 0), App.Vector(0, 0, 0), 2, 1, 1
    )
    a.setExpression("NumberX", antal)
    a.setExpression("Interval%s.%s" % ("X", retning), interval)
    return a


# ---------------------------------------------------------------- bundrem
# Gulvbjaelker paa hoejkant, 195 mm hoeje. Front og bag er to laegter limet
# sammen; de tegnes som to separate emner, saa limfugen kan ses paa tegningen
# og hver laegte kan taelles med i styklisten. Gavlenderne er enkelte laegter.
#
# Gavlremmene (venstre/hoejre) er monteret UDEN PAA og loeber i fuld bredde
# fra y=0 til y=bredde. Front og bag gaar imellem dem og er derfor
# 2 x regel_b kortere end huset.

bjaelke(
    "Bundrem_venstre",
    S + "regel_b",
    S + "bredde",
    S + "bundrem_h",
)
bjaelke(
    "Bundrem_hoejre",
    S + "regel_b",
    S + "bredde",
    S + "bundrem_h",
    x=S + "laengde - " + S + "regel_b",
)
bjaelke(
    "Bundrem_front_ydre",
    S + "bundrem_l",
    S + "regel_b",
    S + "bundrem_h",
    x=S + "regel_b",
)
bjaelke(
    "Bundrem_front_indre",
    S + "bundrem_l",
    S + "regel_b",
    S + "bundrem_h",
    x=S + "regel_b",
    y=S + "regel_b",
)
bjaelke(
    "Bundrem_bag_indre",
    S + "bundrem_l",
    S + "regel_b",
    S + "bundrem_h",
    x=S + "regel_b",
    y=S + "bredde - " + S + "bundrem_b",
)
bjaelke(
    "Bundrem_bag_ydre",
    S + "bundrem_l",
    S + "regel_b",
    S + "bundrem_h",
    x=S + "regel_b",
    y=S + "bredde - " + S + "regel_b",
)

# ---------------------------------------------------------------- topskinne

TOP_Z = S + "bundrem_h + " + S + "vaeghoejde - " + S + "regel_b"

bjaelke("Topskinne_front", S + "laengde", S + "regel_h", S + "regel_b", z=TOP_Z)
bjaelke(
    "Topskinne_bag",
    S + "laengde",
    S + "regel_h",
    S + "regel_b",
    y=S + "bredde - " + S + "regel_h",
    z=TOP_Z,
)
# Ingen topskinne i gavlene - dér gaar reglerne helt op til spaerene.

# ---------------------------------------------------------------- regler
# Arrayet placerer regler paa 600, 1200, 1800 ... Hjoerne- og endestolpe
# saettes separat, fordi de skal hvile paa front/bag-remmen og ikke paa
# gavlremmen.
#
# Alle regler gaar fra z = regel_z (bundremmens overkant minus udskaeringen)
# op til underkant topskinne - i gavlene helt op til spaerene.

REGEL_Z = S + "regel_z"
BAG_Y = S + "bredde - " + S + "regel_h"
BAG_UDSK_Y = S + "bredde - " + S + "bundrem_b"

# Hjoernestolpen staar - ligesom endestolpen - paa front/bag-remmen og ikke
# paa gavlremmen. Den saettes derfor separat ved x = regel_b, og arrayet
# starter foerst ved modul (600).
#
# AABENT PUNKT: selve hjoernet (x 0..regel_b) har ingen lodret stolpe.
# Gavlreglerne starter foerst ved y = modul, saa hjoernet staar tomt.
# Skal afklares: enten en hjoernestolpe med 45 mm udskaering i stedet for 90,
# eller gavlreglen foert helt ud i hjoernet.
HJOERNE_X = S + "regel_b"

regel(
    "Regel_front_hjoerne", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b",
    x=HJOERNE_X, z=REGEL_Z,
)
regel(
    "Regel_bag_hjoerne", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b",
    x=HJOERNE_X, y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
)

lang_front = regel(
    "Regel_front", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b", x=S + "modul", z=REGEL_Z,
)
array(lang_front, "x", S + "array_x - 1", S + "modul")

lang_bag = regel(
    "Regel_bag", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b",
    x=S + "modul", y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
)
array(lang_bag, "x", S + "array_x - 1", S + "modul")

# Endestolperne rykkes en regelbredde ind, saa de staar paa bundremmens
# front/bag-laegter i stedet for paa gavlremmen - ellers passer udskaeringen
# ikke med det traeet den skal hvile paa.
ENDE_X = S + "laengde - 2 * " + S + "regel_b"

regel(
    "Regel_front_ende", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b",
    x=ENDE_X, z=REGEL_Z,
)
regel(
    "Regel_bag_ende", S + "regel_b", S + "regel_h", S + "regel_l",
    S + "regel_b", S + "bundrem_b",
    x=ENDE_X, y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
)



# Gavlregler fra y = modul og indefter. Se AABENT PUNKT ovenfor: hjoernet
# staar tomt, fordi hverken gavlregel eller hjoernestolpe naar helt derud.
# Gavlremmen er en enkelt laegte, saa udskaeringen er kun regel_b dyb.
gavl_venstre = regel(
    "Regel_gavl_venstre", S + "regel_h", S + "regel_b", S + "regel_l_gavl",
    S + "regel_b", S + "regel_b",
    y=S + "modul", z=REGEL_Z,
)
array(gavl_venstre, "y", S + "array_y - 1", S + "modul")

gavl_hoejre = regel(
    "Regel_gavl_hoejre", S + "regel_h", S + "regel_b", S + "regel_l_gavl",
    S + "regel_b", S + "regel_b",
    x=S + "laengde - " + S + "regel_h", y=S + "modul", z=REGEL_Z,
    udsk_x=S + "laengde - " + S + "regel_b",
)
array(gavl_hoejre, "y", S + "array_y - 1", S + "modul")

# ---------------------------------------------------------------- spaer
# Vandrette spaer paa tvaers af huset, oven paa topskinnen. Ingen taghaeldning
# - se noten i toppen af filen.

SPAER_Z = S + "bundrem_h + " + S + "vaeghoejde"

spaer = bjaelke(
    "Spaer",
    S + "regel_b",
    S + "bredde",
    S + "spaer_h",
    z=SPAER_Z,
)
array(spaer, "x", S + "array_x", S + "modul")

bjaelke(
    "Spaer_ende",
    S + "regel_b",
    S + "bredde",
    S + "spaer_h",
    x=S + "laengde - " + S + "regel_b",
    z=SPAER_Z,
)

# ----------------------------------------------------------------

doc.recompute()

# ---------------------------------------------------------------- farver
# De to laegter i bundremmens front og bag faar hver sin traefarve, saa
# limfugen er tydelig i 3D-viewet. Rent visuelt - geometrien er uaendret.
# Kun i GUI; headless (freecad.cmd) har ingen ViewObject og springer over.

FARVER = {
    "Bundrem_front_ydre": (0.87, 0.74, 0.55),
    "Bundrem_bag_ydre": (0.87, 0.74, 0.55),
    "Bundrem_front_indre": (0.62, 0.46, 0.30),
    "Bundrem_bag_indre": (0.62, 0.46, 0.30),
    "Bundrem_venstre": (0.75, 0.60, 0.42),
    "Bundrem_hoejre": (0.75, 0.60, 0.42),
}

for navn, farve in FARVER.items():
    o = doc.getObject(navn)
    if o is not None and getattr(o, "ViewObject", None) is not None:
        o.ViewObject.ShapeColor = farve

print("Skelet bygget. Skift B1/B2 i regnearket og tryk F5.")
