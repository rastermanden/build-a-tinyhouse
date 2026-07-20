# -*- coding: utf-8 -*-
"""
Parametrisk tiny house-skelet til FreeCAD 1.0+.

byg() laver et regneark og bygger bundrem, stroe, vaegregler, topskinne og
spaer oven paa det, hvor hvert eneste maal er bundet til regnearket med
udtryk. Skift et tal i regnearket, tryk F5, og hele skelettet foelger med.

Standardhuset er 6000 x 3600 mm. Ethvert input-maal kan overskrives pr. hus:

    byg("Hus_7200x4200", laengde=7200, bredde=4200)

Se huse.py for de huse der faktisk bygges, og byg_alle.py for at koere dem.

KONSTRUKTIONEN

Bundremmen staar paa hoejkant som gulvbjaelke, bundrem_h hoej:
  front / bag   2 laegter a regel_b limet sammen -> 2 * regel_b tyk
  gavlender     enkelt laegte                    -> regel_b tyk

De to laegter i front og bag er separate emner (_ydre og _indre), saa
limfugen ses paa tegningerne og hver laegte kan taelles i styklisten.

Der er INGEN bundskinne. Alle fire vaegges regler staar direkte paa
bundremmen. Der er heller ingen topskinne i gavlene - dér gaar reglerne
helt op til spaerene og skaeres af i spaerets vinkel.

Taget falder fra vaeg_front til vaeg_bag over husets bredde. Begge maal er
overkant regel maalt fra terraen, ikke traelaengder. Spaerene har vandret
udhugget saede i begge ender, saa de hviler plant paa topskinnerne.

MODULET

Alt sidder i et modul paa 600 mm, og laengde og bredde SKAL gaa op i det.
Hjoerne- og endestolperne ligger uden for modulet, saa yderfagene bliver
alligevel lidt smallere end resten - se kommentaren ved stroeene.
"""

import FreeCAD as App
import Draft

# Input-maal. Alle kan overskrives pr. hus.
STANDARD = {
    "laengde": 6000,
    "bredde": 3600,
    "modul": 600,
    "regel_b": 45,
    "regel_h": 145,
    "spaer_h": 120,
    "vaeg_front": 3150,
    "vaeg_bag": 2850,
    "udhug": 30,
    "bundrem_h": 195,
    "udskaering_h": 190,
}

PARAMETRE = [
    ("B1", "laengde", "Husets laengde (X)"),
    ("B2", "bredde", "Husets bredde (Y)"),
    ("B3", "modul", "c/c mellem regler og spaer"),
    ("B4", "regel_b", "Regelbredde / tykkelse paa skinner"),
    ("B5", "regel_h", "Regeldybde = vaegtykkelse"),
    ("B6", "spaer_h", "Spaerhoejde"),
    ("B7", "vaeg_front", "Overkant regel, forvaeg (over terraen)"),
    ("B20", "vaeg_bag", "Overkant regel, bagvaeg (over terraen)"),
    ("B21", "udhug", "Udhuggets dybde i spaeret ved oplaeg"),
    ("B8", "bundrem_h", "Bundremmens hoejde (paa hoejkant)"),
    ("B9", "udskaering_h", "Udskaeringens hoejde i reglen"),
]

# Udregnede maal. antal_* er totalen inkl. endestolpen; array_* er det antal
# Draft-arrayet skal lave, fordi endestolpen saettes separat (se nedenfor).
#
# RAEKKEFOELGEN BETYDER NOGET: en celle skal staa efter de aliaser den bruger.
# Gjorde den ikke det, ville FreeCAD klage over "Property not found" mens
# regnearket blev fyldt. Vaerdien retter sig ved recompute, men fejlen staar i
# konsollen og skjuler de advarsler man gerne vil se. Derfor kommer regel_z
# foer regel_l_front og regel_l_bag, og bundrem_b foer stroe_l.
UDREGNET = [
    ("B10", "=2 * regel_b", "bundrem_b", "Bundrem front/bag: 2 laegter limet"),
    ("B17", "=bundrem_h - udskaering_h", "regel_z", "Reglens underkant over terraen"),
    ("B11", "=round(laengde / modul) + 1", "antal_regler", "Regler i lang vaeg"),
    ("B12", "=antal_regler - 1", "array_x", "Heraf i array"),
    ("B13", "=round(bredde / modul) + 1", "antal_gavl", "Regler i gavl"),
    ("B14", "=antal_gavl - 1", "array_y", "Heraf i array"),
    ("B15", "=vaeg_front - regel_z", "regel_l_front", "Regel i forvaeg"),
    ("B16", "=vaeg_bag - regel_z", "regel_l_bag", "Regel i bagvaeg"),
    ("B18", "=laengde - 2 * regel_b", "bundrem_l", "Front/bag mellem gavlremmene"),
    ("B28", "=bredde - 2 * bundrem_b", "stroe_l", "Stroe mellem front- og bagrem"),
    ("B22", "=vaeg_front - vaeg_bag", "fald", "Tagets fald over husets bredde"),
    ("B23", "=fald / bredde * 100", "haeldning_pct", "Taghaeldning i procent"),
    ("B24", "=atan(fald / bredde)", "spaer_vinkel", "Spaerets vinkel i grader"),
    ("B25", "=sqrt(bredde ^ 2 + fald ^ 2)", "spaer_l", "Spaerets laengde langs taget"),
    ("B26", "=vaeg_front + regel_b", "oplaeg_front", "Overkant topskinne, forvaeg"),
    ("B27", "=vaeg_bag + regel_b", "oplaeg_bag", "Overkant topskinne, bagvaeg"),
]

# De to laegter i bundremmens front og bag faar hver sin traefarve, saa
# limfugen er tydelig i 3D-viewet. Rent visuelt - geometrien er uaendret.
FARVER = {
    "Bundrem_front_ydre": (0.87, 0.74, 0.55),
    "Bundrem_bag_ydre": (0.87, 0.74, 0.55),
    "Bundrem_front_indre": (0.62, 0.46, 0.30),
    "Bundrem_bag_indre": (0.62, 0.46, 0.30),
    "Bundrem_venstre": (0.75, 0.60, 0.42),
    "Bundrem_hoejre": (0.75, 0.60, 0.42),
}

S = "Spreadsheet."


def kontrollér(maal):
    """Kaster ValueError hvis husets maal ikke kan lade sig goere.

    Laengde og bredde skal gaa op i modulet. Gjorde de ikke det, ville
    arrayet stadig saette regler c/c modul, og hele resten ville havne i det
    sidste fag - et hus paa 6300 mm ville faa et sidste fag paa ca. 765 mm i
    stedet for de 555 mm alle andre fag har.
    """
    ukendte = set(maal) - set(STANDARD)
    if ukendte:
        raise ValueError(
            "ukendte maal: %s (kendte: %s)"
            % (", ".join(sorted(ukendte)), ", ".join(sorted(STANDARD)))
        )

    modul = maal["modul"]
    for navn in ("laengde", "bredde"):
        if maal[navn] % modul:
            raise ValueError(
                "%s = %s gaar ikke op i modulet paa %s mm (rest %s mm). "
                "Vaelg %s eller %s."
                % (navn, maal[navn], modul, maal[navn] % modul,
                   maal[navn] // modul * modul,
                   (maal[navn] // modul + 1) * modul)
            )

    if maal["vaeg_bag"] >= maal["vaeg_front"]:
        raise ValueError(
            "vaeg_bag (%s) skal vaere lavere end vaeg_front (%s), "
            "ellers falder taget den forkerte vej eller slet ikke"
            % (maal["vaeg_bag"], maal["vaeg_front"])
        )

    if maal["udskaering_h"] >= maal["bundrem_h"]:
        raise ValueError(
            "udskaering_h (%s) skal vaere mindre end bundrem_h (%s), "
            "ellers skaerer udskaeringen reglen helt igennem"
            % (maal["udskaering_h"], maal["bundrem_h"])
        )


def byg(navn, **afvigelser):
    """Bygger ét hus og returnerer dokumentet.

    navn        dokumentets navn i FreeCAD
    afvigelser  de maal der afviger fra STANDARD
    """
    maal = dict(STANDARD)
    maal.update(afvigelser)
    kontrollér(maal)

    doc = App.newDocument(navn)
    sheet = doc.addObject("Spreadsheet::Sheet", "Spreadsheet")

    for celle, alias, beskrivelse in PARAMETRE:
        sheet.set(celle, str(maal[alias]))
        sheet.setAlias(celle, alias)
        sheet.set(celle.replace("B", "A"), beskrivelse)

    for celle, formel, alias, beskrivelse in UDREGNET:
        sheet.set(celle, formel)
        sheet.setAlias(celle, alias)
        sheet.set(celle.replace("B", "A"), beskrivelse)

    doc.recompute()

    # ------------------------------------------------------------ hjaelpere

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

        Emnet er hoejere end den fri vaeghoejde: den gaar udskaering_h ned
        forbi bundremmens overkant. Udskaeringen fjernes med en Part::Cut, saa
        den ses i 3D og i snit, og saa emnet kan maalsaettes i styklisten.
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

    def vip(o):
        """Roterer om X-aksen med spaervinklen.

        Alle tre akse-komponenter saettes eksplicit: Axis staar som standard
        paa (0,0,1), saa hvis kun x saettes, bliver aksen (1,0,1) - en
        diagonal, og haeldningen bliver forkert.
        """
        o.setExpression("Placement.Rotation.Angle", "-" + S + "spaer_vinkel")
        o.setExpression("Placement.Rotation.Axis.x", "1")
        o.setExpression("Placement.Rotation.Axis.y", "0")
        o.setExpression("Placement.Rotation.Axis.z", "0")
        return o

    def array(base, retning, antal, interval):
        """Draft Ortho Array med antal og interval styret af regnearket."""
        v = App.Vector(600, 0, 0) if retning == "x" else App.Vector(0, 600, 0)
        a = Draft.make_ortho_array(
            base, v, App.Vector(0, 0, 0), App.Vector(0, 0, 0), 2, 1, 1
        )
        a.setExpression("NumberX", antal)
        a.setExpression("Interval%s.%s" % ("X", retning), interval)
        return a

    # ------------------------------------------------------------- bundrem
    # Gulvbjaelker paa hoejkant. Front og bag er to laegter limet sammen; de
    # tegnes som to separate emner, saa limfugen kan ses paa tegningen og hver
    # laegte kan taelles med i styklisten. Gavlenderne er enkelte laegter.
    #
    # Gavlremmene (venstre/hoejre) er monteret UDEN PAA og loeber i fuld
    # bredde fra y=0 til y=bredde. Front og bag gaar imellem dem og er derfor
    # 2 x regel_b kortere end huset.

    bjaelke("Bundrem_venstre", S + "regel_b", S + "bredde", S + "bundrem_h")
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

    # --------------------------------------------------------------- stroe
    # Gulvstroe paa hoejkant i samme hoejde som bundremmen, saa overkanten er
    # plan hele vejen. De gaar mellem front- og bagremmens INDERSIDER, altsaa
    # bundrem_b inde fra hver side.
    #
    # Stroeen ligger klods op ad sin regel, ikke i samme x. Reglerne er
    # regel_h dybe, men udskaeringen daekker kun bundremmens bundrem_b - de
    # sidste regel_h - bundrem_b gaar derfor helt ned til regel_z og staar
    # netop dér hvor en stroe i samme x ville ligge. Forskydningen paa regel_b
    # er altsaa en betingelse, ikke en detalje.
    #
    # Der er kun stroe ved arrayets regler. Ved hjoerne- og endestolpen er der
    # ikke plads: gavlreglerne er regel_h dybe men staar paa en gavlrem der
    # kun er regel_b bred, saa deres fod rager regel_h - regel_b ind over
    # gulvet helt ned til regel_z. Gavlremmen loeber til gengaeld i fuld
    # laengde og fungerer selv som kantbjaelke, saa en stroe der ville
    # alligevel vaere overfloedig. Yderfagene bliver derfor smallere end
    # resten.

    stroe = bjaelke(
        "Stroe", S + "regel_b", S + "stroe_l", S + "bundrem_h",
        x=S + "modul + " + S + "regel_b", y=S + "bundrem_b",
    )
    array(stroe, "x", S + "array_x - 1", S + "modul")

    # ----------------------------------------------------------- topskinne

    bjaelke("Topskinne_front", S + "laengde", S + "regel_h", S + "regel_b",
            z=S + "vaeg_front")
    bjaelke(
        "Topskinne_bag",
        S + "laengde",
        S + "regel_h",
        S + "regel_b",
        y=S + "bredde - " + S + "regel_h",
        z=S + "vaeg_bag",
    )
    # Ingen topskinne i gavlene - dér gaar reglerne helt op til spaerene.

    # -------------------------------------------------------------- regler
    # Arrayet placerer regler paa 600, 1200, 1800 ... Hjoerne- og endestolpe
    # saettes separat, fordi de skal hvile paa front/bag-remmen og ikke paa
    # gavlremmen. Arrayet starter derfor foerst ved modul.
    #
    # Alle regler gaar fra z = regel_z (bundremmens overkant minus
    # udskaeringen) op til underkant topskinne - i gavlene helt op til
    # spaerene.

    REGEL_Z = S + "regel_z"
    BAG_Y = S + "bredde - " + S + "regel_h"
    BAG_UDSK_Y = S + "bredde - " + S + "bundrem_b"
    HJOERNE_X = S + "regel_b"
    ENDE_X = S + "laengde - 2 * " + S + "regel_b"

    regel(
        "Regel_front_hjoerne", S + "regel_b", S + "regel_h",
        S + "regel_l_front", S + "regel_b", S + "bundrem_b",
        x=HJOERNE_X, z=REGEL_Z,
    )
    regel(
        "Regel_bag_hjoerne", S + "regel_b", S + "regel_h", S + "regel_l_bag",
        S + "regel_b", S + "bundrem_b",
        x=HJOERNE_X, y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
    )
    regel(
        "Regel_front_ende", S + "regel_b", S + "regel_h", S + "regel_l_front",
        S + "regel_b", S + "bundrem_b", x=ENDE_X, z=REGEL_Z,
    )
    regel(
        "Regel_bag_ende", S + "regel_b", S + "regel_h", S + "regel_l_bag",
        S + "regel_b", S + "bundrem_b",
        x=ENDE_X, y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
    )

    lang_front = regel(
        "Regel_front", S + "regel_b", S + "regel_h", S + "regel_l_front",
        S + "regel_b", S + "bundrem_b", x=S + "modul", z=REGEL_Z,
    )
    array(lang_front, "x", S + "array_x - 1", S + "modul")

    lang_bag = regel(
        "Regel_bag", S + "regel_b", S + "regel_h", S + "regel_l_bag",
        S + "regel_b", S + "bundrem_b",
        x=S + "modul", y=BAG_Y, z=REGEL_Z, udsk_y=BAG_UDSK_Y,
    )
    array(lang_bag, "x", S + "array_x - 1", S + "modul")

    # ------------------------------------------------------ hjoernestolper
    # Selve hjoernet (x 0..regel_b) havde ingen lodret stolpe: gavlreglerne
    # starter foerst ved modul, og front/bag-stolpen staar inde ved regel_b,
    # fordi den skal hvile paa front/bag-remmen. Yderbeklaedningen havde
    # dermed intet at sidde fast i hverken paa gavlfladen eller paa
    # frontfladen ude i selve hjoernet.
    #
    # Hjoernestolpen staar OVEN PAA gavlremmen og har derfor ingen
    # udskaering - gavlremmen er regel_b bred og baerer den i fuld bredde.
    # Sammen med front/bag-stolpen ved siden af danner den et 2 x regel_b
    # bredt hjoerne med fastgoerelse paa begge yderflader.

    HJ_FRONT = S + "vaeg_front - " + S + "bundrem_h"
    HJ_BAG = S + "vaeg_bag - " + S + "bundrem_h"
    HOEJRE_X = S + "laengde - " + S + "regel_b"

    for hjnavn, hjx, hjy, hjh in (
        ("Hjoernestolpe_front_venstre", "0", "0", HJ_FRONT),
        ("Hjoernestolpe_front_hoejre", HOEJRE_X, "0", HJ_FRONT),
        ("Hjoernestolpe_bag_venstre", "0", BAG_Y, HJ_BAG),
        ("Hjoernestolpe_bag_hoejre", HOEJRE_X, BAG_Y, HJ_BAG),
    ):
        bjaelke(hjnavn, S + "regel_b", S + "regel_h", hjh,
                x=hjx, y=hjy, z=S + "bundrem_h")

    # ----------------------------------------------------------- gavlregler
    # Bygges hoejere end taget og skaeres af med tagplanet nedenfor, saa hver
    # enkelt faar sin egen laengde og en top i spaerets vinkel.
    # Gavlremmen er en enkelt laegte, saa udskaeringen er kun regel_b dyb.

    GAVL_H = S + "vaeg_front - " + S + "regel_z + 500"

    gavl_venstre = regel(
        "Regel_gavl_venstre_raa", S + "regel_h", S + "regel_b", GAVL_H,
        S + "regel_b", S + "regel_b",
        y=S + "modul", z=REGEL_Z,
    )
    arr_gv = array(gavl_venstre, "y", S + "array_y - 1", S + "modul")

    gavl_hoejre = regel(
        "Regel_gavl_hoejre_raa", S + "regel_h", S + "regel_b", GAVL_H,
        S + "regel_b", S + "regel_b",
        x=S + "laengde - " + S + "regel_h", y=S + "modul", z=REGEL_Z,
        udsk_x=S + "laengde - " + S + "regel_b",
    )
    arr_gh = array(gavl_hoejre, "y", S + "array_y - 1", S + "modul")

    # -------------------------------------------------------------- tagplan
    # Spaerets underside ligger udhug under oplaegskoten i begge ender. Et
    # stort kasseemne roteret i spaervinklen bruges baade til at skaere
    # gavlreglernes toppe af og som reference for spaerene.
    #
    # y skal vaere 0: rotationen sker om placeringens eget nulpunkt, saa
    # z-koten gaelder netop dér. Startede kassen ved y = -200, ville tagplanet
    # ligge 200 * tan(spaervinkel) for hoejt over hele huset.

    def tagplan(navn):
        o = bjaelke(
            navn,
            S + "laengde + 400",
            S + "spaer_l + 400",
            "3000",
            x="-200",
            y="0",
            z=S + "oplaeg_front - " + S + "udhug",
        )
        vip(o)
        return o

    # Hver Part::Cut opsluger sit Tool, saa der laves et tagplan pr. snit.
    for i, (arr, arrnavn) in enumerate(
        ((arr_gv, "Regel_gavl_venstre"), (arr_gh, "Regel_gavl_hoejre"))
    ):
        snit = doc.addObject("Part::Cut", arrnavn)
        snit.Base = arr
        snit.Tool = tagplan("Tagplan_skaer%d" % i)

    # ---------------------------------------------------------------- spaer
    # Spaeret ligger i tagets plan med undersiden udhug under oplaegskoten.
    # I hver ende skaeres et vandret saede i hoejde med topskinnens overkant,
    # saa spaeret hviler med en vandret flade paa skinnen.

    def spaer(navn, x):
        emne = bjaelke(navn + "_emne", S + "regel_b", S + "spaer_l",
                       S + "spaer_h",
                       x=x, y="0", z=S + "oplaeg_front - " + S + "udhug")
        vip(emne)

        saede_f = bjaelke(navn + "_saede_front", S + "regel_b", S + "regel_h",
                          "500", x=x, y="0", z=S + "oplaeg_front - 500")
        trin1 = doc.addObject("Part::Cut", navn + "_t1")
        trin1.Base = emne
        trin1.Tool = saede_f

        saede_b = bjaelke(navn + "_saede_bag", S + "regel_b", S + "regel_h",
                          "500", x=x, y=S + "bredde - " + S + "regel_h",
                          z=S + "oplaeg_bag - 500")
        snit = doc.addObject("Part::Cut", navn)
        snit.Base = trin1
        snit.Tool = saede_b
        return snit

    sp = spaer("Spaer", "0")
    array(sp, "x", S + "array_x", S + "modul")
    spaer("Spaer_ende", S + "laengde - " + S + "regel_b")

    doc.recompute()

    # Kun i GUI; headless har ingen ViewObject og springer over.
    for objektnavn, farve in FARVER.items():
        o = doc.getObject(objektnavn)
        if o is not None and getattr(o, "ViewObject", None) is not None:
            o.ViewObject.ShapeColor = farve

    return doc


def emner(doc):
    """De emner der faktisk er trae i huset.

    Et Part::Cut opsluger sin Base og sit Tool, saa udskaeringer og tagplan
    skal filtreres fra - ellers ville de taelle med i bbox og blive tegnet.
    """
    forbrugt = set()
    for o in doc.Objects:
        for felt in ("Base", "Tool"):
            barn = getattr(o, felt, None)
            if barn:
                forbrugt.add(barn.Name)
    return [
        o for o in doc.Objects
        if o.Name not in forbrugt and hasattr(o, "Shape") and o.Shape.Volume > 0
    ]


def maalskema(doc):
    """Alle regnearkets maal som (alias, vaerdi, beskrivelse), i celleordenen.

    Laeses ud af modellen, ikke skrevet i haanden - saa kan et maalskema
    aldrig komme til at vise noget andet end det huset faktisk er bygget af.
    """
    sheet = doc.Spreadsheet
    raekker = []
    for celle, alias, beskrivelse in PARAMETRE:
        raekker.append((alias, sheet.get(alias), beskrivelse, "input"))
    for celle, formel, alias, beskrivelse in UDREGNET:
        raekker.append((alias, sheet.get(alias), beskrivelse, "udregnet"))
    return raekker
