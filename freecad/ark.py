# -*- coding: utf-8 -*-
"""
Maalsatte detaljeark for hvert emne i huset.

Hvert ark henter emnets kontur fra dets faktiske Shape og haenger maalene
op paa konturens egne hjoerner. Der skrives ingen maal i haanden - et ark
kan derfor ikke komme til at vise andet end emnet er bygget af.

Se detaljer.py for selve maalsaetningsvaerktoejet.
"""

import os

import FreeCAD as App

import detaljer
from detaljer import Tegning, kontur, flyt_til_nul, hjoerner, naermeste


def lig_ned(pts):
    """Vender emnet en kvart omgang, saa laengden ligger vandret.

    En regel er 145 x 3145 mm. Staaende ville arket blive smalt og
    umuligt at saette maal paa; liggende ser det ud som paa hoevlebaenken.
    """
    return [(z, x) for x, z in pts]


def _ark(t, titel, under=None):
    """Faelles bundtekst paa alle ark."""
    x0 = min(t.xs)
    y1 = max(t.ys)
    t.tekst(x0, -(y1 + t.e * 2.2), titel, "note")
    if under:
        t.tekst(x0, -(y1 + t.e * 3.8), under, "note")
    return t


# ------------------------------------------------------------------- spaer

def spaer(doc):
    """Hele spaeret plus et udsnit af hver sædeudskaering."""
    s = doc.Spreadsheet
    flad = detaljer.spaer_fladt(doc)
    pts = flyt_til_nul(kontur(flad, (1, 0, 0), float(s.regel_b) / 2,
                              ("y", "z")))
    hj = hjoerner(pts)
    L = max(p[0] for p in pts)
    H = max(p[1] for p in pts)

    # Sædets punkter findes paa geometrien: yderste og inderste hjoerne af
    # den vandrette saedeflade i hver ende.
    f_yder = naermeste(hj, x=0, z=H * .25)          # forende, underkant
    f_inder = naermeste(hj, x=float(s.regel_h), z=H * .35)
    b_inder = naermeste(hj, x=L - float(s.regel_h) * 1.05, z=H * .15)
    b_yder = naermeste(hj, x=L, z=H * .25)

    ud = {}

    t = Tegning(enhed=L / 55.0)
    t.polygon(pts)
    t.maal_vandret(0, L, -H * 1.7, hjaelp_fra=0)
    t.maal_lodret(0, H, L * 1.05, hjaelp_fra=L)
    t.note(L * .30, H * 2.4, "Saede front", f_inder[0], f_inder[1])
    t.note(L * .70, H * 2.4, "Saede bag", b_inder[0], b_inder[1])
    ud["spaer"] = _ark(
        t, "SPAER  -  %.0f x %.0f mm" % (s.regel_b, s.spaer_h),
        "Laengde langs taget %.1f mm  -  taghaeldning %.2f grader"
        % (L, s.spaer_vinkel))

    for navn, (yder, inder, vend) in (
            ("spaer_saede_front", (f_yder, f_inder, False)),
            ("spaer_saede_bag", (b_yder, b_inder, True))):
        bred = float(s.regel_h) * 1.7
        x0 = 0 if not vend else L - bred
        d = Tegning(enhed=bred / 24.0)
        d.polygon([p for p in pts if x0 <= p[0] <= x0 + bred]
                  + ([(x0 + bred, 0), (x0 + bred, H)] if not vend
                     else [(x0, H), (x0, 0)]))
        d.maal_vandret(yder[0], inder[0], -H * .6, hjaelp_fra=0)
        d.maal_lodret(0, yder[1], x0 - bred * .13 if not vend
                      else x0 + bred * 1.13, hjaelp_fra=yder[0])
        d.note(x0 + bred * .5, H * 1.5,
               "Vandret saedeflade - hviler paa topskinnen",
               (yder[0] + inder[0]) / 2, (yder[1] + inder[1]) / 2)
        ud[navn] = _ark(
            d, "UDSNIT: saedeudskaering, %s"
            % ("bagende" if vend else "forende"),
            "Dybde ved yderkant %.1f mm, ved inderkant %.1f mm"
            % (yder[1], inder[1]))
    return ud


# ------------------------------------------------------------------ regler

def regel_lang(doc, navn="Regel_front", titel="REGEL, FOR- OG BAGVAEG"):
    """Regel i for-/bagvaeg set fra siden, med udskaeringen i bunden."""
    s = doc.Spreadsheet
    sh = doc.getObject(navn).Shape
    bb = sh.BoundBox
    pts = flyt_til_nul(kontur(sh, (1, 0, 0), bb.XMin + float(s.regel_b) / 2,
                              ("y", "z")))
    dybde = max(p[0] for p in pts)
    uh = float(s.udskaering_h)

    # Udskaeringen maales paa konturen, ikke ud fra hvor jeg tror den ligger.
    # Bagvaeggens regel er spejlvendt af forvaeggens, saa udskaeringen ligger
    # i den modsatte ende af profilen - derfor maales det traae der ER
    # tilbage forneden, og udskaeringen er resten.
    forneden = [p[0] for p in pts if p[1] < uh * .5]
    tilbage = max(forneden) - min(forneden)
    udsk_b = dybde - tilbage
    # udskaeringens to hjoerner, uanset hvilken side den sidder i
    spejlet = min(forneden) > dybde - tilbage - 1
    u_x = udsk_b if not spejlet else dybde - udsk_b

    # Liggende: laengden vandret, vaegtykkelsen lodret.
    pts = lig_ned(pts)
    L = max(p[0] for p in pts)

    t = Tegning(enhed=L / 52.0)
    t.polygon(pts)
    t.maal_vandret(0, L, -dybde * 1.5, hjaelp_fra=0)
    t.maal_lodret(0, dybde, L * 1.04, hjaelp_fra=L)
    t.maal_lodret(min(u_x, dybde - udsk_b if spejlet else 0),
                  max(u_x, dybde - udsk_b if spejlet else 0) if spejlet
                  else udsk_b, -L * .055, txt="%.0f" % udsk_b, hjaelp_fra=0)
    t.maal_vandret(0, uh, dybde * 2.1, hjaelp_fra=u_x)
    t.note(L * .30, -dybde * 3.0, "Udskaering - hviler paa bundremmen",
           uh * .5, u_x * .5 if not spejlet else (dybde + u_x) * .5)
    return {navn.lower(): _ark(
        t, "%s  -  %.0f x %.0f mm" % (titel, s.regel_b, s.regel_h),
        "Laengde %.0f mm  -  udskaering %.0f mm bred x %.0f mm hoej"
        % (L, udsk_b, uh))}


# ------------------------------------------------------------- gavlregler

def _gavlregel_kontur(doc, solid, s):
    """Bredsiden: 145 mm bred, viser udskaeringen. Toppen er vandret her.

    Taget falder i Y, og gavlvaeggen loeber i Y, saa hver enkelt gavlregel
    har en flad top set fra denne side. Haeldningen viser sig dels som
    forskel MELLEM reglerne, dels som et lille fald hen over reglens egen
    tykkelse - se _gavlregel_top().
    """
    pts = kontur(solid, (0, 1, 0), solid.BoundBox.YMin + float(s.regel_b) / 2,
                 ("x", "z"))
    return flyt_til_nul(pts)


def _gavlregel_top(doc, solid, s):
    """(lang side, kort side) maalt paa smalsiden, hvor toppen er skraa."""
    pts = kontur(solid, (1, 0, 0), solid.BoundBox.XMin + float(s.regel_h) / 2,
                 ("y", "z"))
    pts = flyt_til_nul(pts)
    top = max(p[1] for p in pts)
    bund = min(p[1] for p in pts)
    # den skraa top: hoejeste og laveste punkt paa overkanten
    oeverst = [p for p in pts if p[1] > top - float(s.regel_b) * 2]
    return (max(p[1] for p in oeverst) - bund,
            min(p[1] for p in oeverst) - bund)


def gavlregler(doc):
    """Samleark med laengdetabel plus ét ark pr. gavlregel."""
    s = doc.Spreadsheet
    arr = doc.getObject("Regel_gavl_venstre")
    solids = sorted(arr.Shape.Solids, key=lambda so: so.BoundBox.YMin)

    raekker = []
    ud = {}
    for i, so in enumerate(solids, start=1):
        pts = _gavlregel_kontur(doc, so, s)
        hj = hjoerner(pts)
        B = max(p[0] for p in pts)
        lang, kort = _gavlregel_top(doc, so, s)
        knae = naermeste(hj, x=float(s.regel_b), z=float(s.udskaering_h))
        y = so.BoundBox.YMin
        raekker.append((i, y, lang, kort, knae[0], knae[1]))

        H = max(p[1] for p in pts)
        lp = lig_ned(pts)
        lknae = (knae[1], knae[0])
        t = Tegning(enhed=H / 52.0)
        t.polygon(lp)
        t.maal_vandret(0, H, -B * 1.5, hjaelp_fra=0)
        t.maal_lodret(0, B, H * 1.04, hjaelp_fra=H)
        t.maal_vandret(0, lknae[0], B * 2.1, hjaelp_fra=lknae[1])
        t.note(H * .34, -B * 3.0,
               "Top falder %.1f mm hen over tykkelsen (%.2f grader)"
               % (lang - kort, s.spaer_vinkel), H, B * .5)
        ud["gavlregel_%02d" % i] = _ark(
            t, "GAVLREGEL NR. %d  -  %.0f x %.0f mm" % (i, s.regel_b,
                                                        s.regel_h),
            "Ved y = %.0f mm  -  lang side %.1f mm, kort side %.1f mm"
            % (y, lang, kort))

    # samleark: den foerste regel tegnet, resten som tabel
    pts = _gavlregel_kontur(doc, solids[0], s)
    B = max(p[0] for p in pts)
    lang = max(p[1] for p in pts)
    hj = hjoerner(pts)
    knae = naermeste(hj, x=float(s.regel_b), z=float(s.udskaering_h))

    H = max(p[1] for p in pts)
    lp = lig_ned(pts)
    lknae = (knae[1], knae[0])
    t = Tegning(enhed=H / 52.0)
    t.polygon(lp)
    t.maal_lodret(0, B, H * 1.04, hjaelp_fra=H)
    t.maal_vandret(0, lknae[0], B * 2.1, hjaelp_fra=lknae[1])
    t.maal_lodret(0, lknae[1], -H * .05, hjaelp_fra=0)
    t.note(H * .30, -B * 3.0, "Alle gavlregler har samme udskaering",
           lknae[0] * .5, lknae[1] * .5)
    t.note(H * .30, -B * 4.6, "Toppen er vandret set herfra - taget falder "
           "i husets laengderetning", H, B * .5)
    ud["gavlregler"] = _ark(
        t, "GAVLREGLER  -  %.0f x %.0f mm  -  %d stk pr. gavl"
           % (s.regel_b, s.regel_h, len(solids)),
        "Laengder i tabellen; udskaering %.0f x %.0f mm er ens for alle"
        % (knae[0], knae[1]))
    return ud, raekker


# ------------------------------------------------- simple kassefformede emner

def kasse(doc, navn, titel, akse="x"):
    """Ark for et emne uden udskaeringer: en kasse med tre maal."""
    s = doc.Spreadsheet
    bb = doc.getObject(navn).Shape.BoundBox
    a, b, c = sorted([bb.XLength, bb.YLength, bb.ZLength], reverse=True)
    t = Tegning(enhed=a / 46.0)
    t.polygon([(0, 0), (a, 0), (a, b), (0, b)])
    t.maal_vandret(0, a, -b * .7, hjaelp_fra=0)
    t.maal_lodret(0, b, a * 1.06, hjaelp_fra=a)
    return {navn.lower(): _ark(
        t, "%s  -  %.0f x %.0f mm" % (titel, c, b),
        "Laengde %.0f mm" % a)}


# ------------------------------------------------------------------- samlet

def alle(doc, udmappe):
    """Skriver alle detaljeark som SVG og returnerer en HTML-blok.

    Arkene lander i udmappe/detaljer/ som selvstaendige SVG-filer, saa de
    kan bruges enkeltvis paa et website.
    """
    mappe = os.path.join(udmappe, "detaljer")
    if not os.path.isdir(mappe):
        os.makedirs(mappe)

    tegn = {}
    tegn.update(spaer(doc))
    tegn.update(regel_lang(doc))
    tegn.update(regel_lang(doc, "Regel_bag", "REGEL, BAGVAEG"))
    tegn.update(bundrem_hjoerne(doc))
    tegn.update(gavl_top(doc))
    tegn.update(kasse(doc, "Stroe", "STROE"))
    tegn.update(kasse(doc, "Gavllaegte_venstre", "GAVLLAEGTE"))
    tegn.update(kasse(doc, "Bundrem_venstre", "BUNDREM, GAVL"))
    tegn.update(kasse(doc, "Bundrem_front_ydre", "BUNDREM, FRONT/BAG"))
    tegn.update(kasse(doc, "Topskinne_front", "TOPSKINNE"))
    gavl, raekker = gavlregler(doc)
    tegn.update(gavl)

    for navn, t in tegn.items():
        with open(os.path.join(mappe, navn + ".svg"), "w") as f:
            f.write(t.svg())

    # raekkefoelge: oversigt foerst, saa udsnit, saa de enkelte gavlregler
    orden = ["spaer", "spaer_saede_front", "spaer_saede_bag",
             "regel_front", "regel_bag", "gavlregler", "gavl_top",
             "bundrem_hjoerne"]
    orden += sorted(n for n in tegn if n.startswith("gavlregel_"))
    orden += sorted(n for n in tegn if n not in orden)

    dele = ["<h2>Detaljer</h2>\n"]
    for navn in orden:
        dele.append('<div class="ark">%s</div>\n' % tegn[navn].svg())

    dele.append("<h2>Gavlregler - laengder</h2>\n<table>\n"
                "<tr><th>Nr.</th><th>Ved y</th><th>Lang side</th>"
                "<th>Kort side</th><th>Udskaering</th></tr>\n")
    for i, y, lang, kort, ub, uh in raekker:
        dele.append('<tr><td>%d</td><td class="tal">%.0f</td>'
                    '<td class="tal">%.1f</td><td class="tal">%.1f</td>'
                    '<td class="tal">%.0f x %.0f</td></tr>\n'
                    % (i, y, lang, kort, ub, uh))
    dele.append("</table>\n")
    return "".join(dele)


# ----------------------------------------------------------- samlingsdetaljer

def _konturer(doc, navne, normal, offset, akser):
    """Konturer for flere emner i samme snit. Emner der ikke rammes springes."""
    ud = []
    for n in navne:
        o = doc.getObject(n)
        if o is None:
            continue
        for solid in (o.Shape.Solids or [o.Shape]):
            try:
                ud.append((n, kontur(solid, normal, offset, akser)))
            except (ValueError, Exception):
                pass
    return ud


def bundrem_hjoerne(doc):
    """Vandret snit gennem bundremmens hjoerne.

    Viser at gavlremmen loeber i fuld bredde og at front/bag gaar imellem
    dem, samt limfugen mellem de to laegter i fronten.
    """
    s = doc.Spreadsheet
    rb, bb_ = float(s.regel_b), float(s.bundrem_b)
    stk = _konturer(doc, ["Bundrem_venstre", "Bundrem_front_ydre",
                          "Bundrem_front_indre", "Stroe"],
                    (0, 0, 1), float(s.bundrem_h) / 2, ("x", "y"))
    vis = rb * 9
    t = Tegning(enhed=vis / 30.0)
    for navn, pts in stk:
        t.polygon(pts)
    t.maal_vandret(0, rb, -rb * 1.4, hjaelp_fra=0)
    t.maal_lodret(0, rb, -rb * 1.4, hjaelp_fra=0)
    t.maal_lodret(rb, bb_, -rb * 3.0, hjaelp_fra=0)
    t.note(rb * 5.5, rb * 5.0, "Gavlrem i fuld bredde - front/bag gaar imellem",
           rb * .5, rb * 4.0)
    t.note(rb * 5.5, -rb * 3.4, "Limfuge mellem de to laegter",
           rb * 3.0, rb)
    t.udsnit(-rb * 4.5, -rb * 4.5, vis, vis)
    return {"bundrem_hjoerne": _ark(
        t, "DETALJE: bundremmens hjoerne",
        "Gavlrem %.0f mm, front/bag %.0f mm (2 x %.0f limet)"
        % (rb, bb_, rb))}


def gavl_top(doc):
    """Lodret snit gennem gavltoppen: gavlregel, hjoernespaer, gavllaegte."""
    s = doc.Spreadsheet
    rb, rh = float(s.regel_b), float(s.regel_h)
    y = float(s.modul) + rb / 2
    stk = _konturer(doc, ["Regel_gavl_venstre", "Spaer",
                          "Gavllaegte_venstre"],
                    (0, 1, 0), y, ("x", "z"))
    # kun de emner der faktisk ligger i gavlen
    stk = [(n, p) for n, p in stk if min(q[0] for q in p) < rh * 1.5]

    top = max(q[1] for _, p in stk for q in p)
    vis = rh * 4.0
    t = Tegning(enhed=vis / 30.0)
    for navn, pts in stk:
        t.polygon(pts)
    t.maal_vandret(-float(s.gavllaegte_b), 0, top + rh * .55, hjaelp_fra=top)
    t.maal_vandret(0, rb, top + rh * 1.15, hjaelp_fra=top)
    t.maal_vandret(0, rh, top - rh * 2.2, hjaelp_fra=top - rh * 1.9)
    t.note(rh * 1.9, top + rh * .30, "Gavllaegte - fastgoerelse for "
           "gavlbeklaedningens oeverste kant", -float(s.gavllaegte_b) / 2, top)
    t.note(rh * 1.9, top - rh * .55, "Hjoernespaer", rb / 2, top - rb)
    t.note(rh * 1.9, top - rh * 1.35, "Gavlregel, skaaret i tagets plan",
           rh * .75, top - rh * 1.5)
    t.udsnit(-rh * 1.1, top - vis * .72, vis, vis)
    return {"gavl_top": _ark(
        t, "DETALJE: gavltop",
        "Gavllaegte %.0f mm uden paa hjoernespaeret %.0f mm"
        % (s.gavllaegte_b, rb))}
