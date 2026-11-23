"""frontpage.py — renders the news-image-20261122 front page.

The page is a classic illustrated broadsheet for one day — Sunday
22 November 2026 — drawn entirely in code with Pillow and the
Liberation family: masthead, giant serif date, red italic dek, a UTC
timeline of the day, a six-figure numbers strip, region tabs counted
from the story list itself, three hero panels with drawn scenes,
twelve pictured story cards with certainty tags, a filled-block world
map carrying a numbered pin for every pictured story, twenty-one
one-line briefs, and a red date-check box that names the neighbouring
days' stories this page deliberately leaves out.

All 36 stories come from a verified research dossier: every figure
was confirmed by two independent sources before it was allowed on
the page, one-sided claims are labelled CLAIM, and the COP31 hero
prints the day's end state — the summit closed with no deal adopted —
rather than the morning's expectation of one. The render is
deterministic: same data, same PNG, every run.

Usage:  python3 frontpage.py   ->   entry.png + fallback.png (1024x1024)
"""

import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ fonts

FONT_ROOT = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_ROOT, "LiberationSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_ROOT, "LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_ROOT, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_ROOT, "LiberationSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_ROOT, "LiberationSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ ink

PAPER = (247, 242, 227)
PAPER_SHADE = (239, 232, 211)
INK = (26, 25, 23)
FAINT = (99, 94, 81)
RED = (178, 34, 24)
DEEP_RED = (148, 27, 18)
NAVY = (19, 35, 57)
NAVY_LIGHT = (31, 55, 84)
NIGHT = (11, 21, 35)
GOLD = (233, 165, 33)
ORANGE = (243, 121, 33)
MAP_DOT = (106, 120, 148)
MAP_SEA = (226, 232, 240)
RULE_SOFT = (192, 184, 161)

TAB_INK = {
    "Europe": (43, 90, 166),
    "Middle East": (125, 60, 152),
    "Asia-Pacific": (178, 62, 32),
    "Americas": (183, 149, 11),
    "Africa": (30, 132, 73),
    "Oceania": (40, 116, 166),
    "World": (93, 109, 126),
}
TAB_ORDER = ["Europe", "Middle East", "Asia-Pacific", "Americas",
             "Africa", "Oceania", "World"]

PAGE = 1024
EDGE = 28
SPAN = PAGE - 2 * EDGE  # 968 px of content

DAY = "Sunday 22 November 2026"
DEK = ("186 drones over Ukraine in the night · COP31 ends with no deal "
       "at all · Iran's radar claim meets Bahrain's denial")
TIMELINE = ("01:00 HK polls open · 03:00 COP31 objections close · "
            "05:30 Verstappen wins Vegas · 06:00 COP31 closing plenary · "
            "08:00 Kyiv: 161 of 186 downed · 14:00 HK turnout passes 93%")

# ------------------------------------------------------------------ heroes
# num, place tag, headline, summary, region, scene key, certainty

HEROES = [
    dict(num=1, region="Europe", scene="drones", cert="REPORTED",
         tag="KYIV REGION · UKRAINE — WAR",
         head="Russia Fires 186 Drones in the Night",
         summ="161 of 186 strike drones were downed or suppressed. A "
              "five-storey block in Vyshhorod was destroyed — three "
              "killed, rescuers in the rubble. (Air Force / AP)"),
    dict(num=2, region="World", scene="cop", cert="REPORTED",
         tag="ANTALYA · TÜRKİYE — CLIMATE",
         head="COP31 Ends With No Deal at All",
         summ="The EU, UK and Panama rejected the final draft, which "
              "never named fossil fuels; the $120bn adaptation target "
              "was dropped. (Reuters / BBC / Guardian)"),
    dict(num=3, region="Middle East", scene="radar", cert="CLAIM",
         tag="MANAMA · BAHRAIN — IRAN",
         head="Iran Claims Radars Hit; Bahrain Denies",
         summ="The IRGC says two Patriot radars were struck. Bahrain "
              "answers: a civilian site burned, two injured — and the "
              "US reports no damage. (AFP / Al Jazeera)"),
]

# ------------------------------------------------------------------ cards
# num, place, certainty, headline, summary, region, scene key

CARDS = [
    dict(num=4, region="Asia-Pacific", scene="vote",
         place="HONG KONG", cert="REPORTED",
         head="Election Committee Chosen",
         summ="856 candidates, 723 seats; record 98.79% turnout. (SCMP)"),
    dict(num=5, region="Oceania", scene="cricket",
         place="WELLINGTON", cert="REPORTED",
         head="India Declare on 720/9",
         summ="A record in NZ: Rahul 136, Pant 128; hosts 119/2. (ESPN)"),
    dict(num=6, region="Americas", scene="f1",
         place="LAS VEGAS", cert="REPORTED",
         head="Verstappen Wins in Vegas",
         summ="From pole, 1:27:39.624; Norris +0.639. (FIA)"),
    dict(num=7, region="Americas", scene="nba",
         place="SAN ANTONIO", cert="REPORTED",
         head="Wembanyama Scores 50",
         summ="50 points, 19 rebounds, 5 blocks; 114–91. (AP)"),
    dict(num=8, region="Europe", scene="ship",
         place="GULF OF FINLAND", cert="REPORTED",
         head="Sparta II Still Burning",
         summ="Hit by drones Saturday; Finland leads rescue. (Reuters)"),
    dict(num=9, region="Middle East", scene="power",
         place="TEHRAN · IRAN", cert="REPORTED",
         head="Iran Rations Electricity",
         summ="Rolling cuts up to two hours a day. (Wires)"),
    dict(num=10, region="Americas", scene="icu",
         place="BRASÍLIA · BRAZIL", cert="REPORTED",
         head="Bolsonaro in Intensive Care",
         summ="Bowel obstruction; stable, surgery possible. (Reuters)"),
    dict(num=11, region="Americas", scene="cyber",
         place="WASHINGTON", cert="REPORTED",
         head="FBI Probes Database Hack",
         summ="Apparent hack of its crime database assessed. (AP)"),
    dict(num=12, region="Europe", scene="strike",
         place="BRUSSELS", cert="REPORTED",
         head="Controllers Join Strike",
         summ="Monday's national strike grounds most flights. (Wires)"),
    dict(num=13, region="Asia-Pacific", scene="liquor",
         place="MANIPUR · INDIA", cert="REPORTED",
         head="Toxic-Liquor Toll at 19",
         summ="600 in hospital, six held over the brew. (Xinhua)"),
    dict(num=14, region="Asia-Pacific", scene="factory",
         place="CIKANDE · INDONESIA", cert="REPORTED",
         head="Factory Fire: 36 Missing",
         summ="Three dead in the Banten candy plant blaze. (Detiknews)"),
    dict(num=15, region="Americas", scene="quake",
         place="JUNÍN · PERU", cert="REPORTED",
         head="Quake Toll: 1 Dead, 16 Hurt",
         summ="170 homes damaged; the count is completed. (Reuters)"),
]

# ------------------------------------------------------------------ briefs
# num, one-line text (place first, source last), region

BRIEFS = [
    (16, "Estonia — Five Russia crossings shut 1 Dec (Reuters)", "Europe"),
    (17, "Denmark — Russian attaché expelled over plot (Guardian)", "Europe"),
    (18, "Kryvyi Rih — Missile kills 2, hurts 58 (BBC)", "Europe"),
    (19, "Delhi — Nepal PM Shah lands on first visit (IANS)", "Asia-Pacific"),
    (20, "Manila — Chinese bomber turns back 170 km out (AP)", "Asia-Pacific"),
    (21, "Palawan — M5.9 quake, 898 km deep (EMSC)", "Asia-Pacific"),
    (22, "Tokyo — Record 92% feel friendly to Seoul (JKN)", "Asia-Pacific"),
    (23, "Kinmen — Taiwan live-fire drill held (CNA)", "Asia-Pacific"),
    (24, "Mogadishu — UAE ambassador expelled (Wires)", "Africa"),
    (25, "Kordofan — RSF accused of killing civilians (Claim)", "Africa"),
    (26, "Nairobi — Last Ebola patient discharged (Wires)", "Africa"),
    (27, "Bayelsa — Boat toll rises to 26 (Vanguard)", "Africa"),
    (28, "Melbourne — 70 years since the 1956 Games (ABC)", "Oceania"),
    (29, "Sydney — Cummins keeps Test captaincy (ABC)", "Oceania"),
    (30, "Doha — Trump seeks 'permanent' Iran deal (Al Jazeera)", "Middle East"),
    (31, "Washington — Nvidia faces SEC probe (Reports)", "Americas"),
    (32, "Gaza — Hamas seeks urgent mediator talks (Al Jazeera)", "Middle East"),
    (33, "Markets — Bitcoin back above $60,000 (Market data)", "World"),
    (34, "Markets — Gold holds near $5,555 (Reuters)", "World"),
    (35, "London — England beat New Zealand 37–12 (Reuters)", "Europe"),
    (36, "Turin — Zverev v Alcaraz final, 17:00 (Forecast)", "Europe"),
]

# ------------------------------------------------------------------ numbers

NUMBERS = [
    ("186", "DRONES FIRED AT UKRAINE OVERNIGHT"),
    ("161", "DOWNED OR SUPPRESSED BY AIR DEFENCE"),
    ("$120bn", "ADAPTATION TARGET DROPPED AT COP31"),
    ("98.79%", "RECORD HONG KONG TURNOUT, 5,640 VOTERS"),
    ("720/9", "INDIA'S RECORD TEST TOTAL IN NEW ZEALAND"),
    ("50", "WEMBANYAMA POINTS, WITH 19 REBOUNDS"),
]

DATE_CHECK = (
    "DATE CHECK — Left out as other days' news: the 400-drone, "
    "110-missile barrage (Thu 19–Fri 20 Nov) · the 148-drone night and "
    "the Kryvyi Rih double-tap (Fri–Sat) · BepiColombo's Mercury burn "
    "(Sat) · the Shenzhen summit (19 Nov) · the Peru quake itself "
    "(Fri) — only Sunday's completed toll count is on this page. "
    "Tonight's real count: 186 drones, at the top of this page."
)

STORY_COUNT = len(HEROES) + len(CARDS) + len(BRIEFS)
REGION_TALLY = Counter(
    [h["region"] for h in HEROES]
    + [c["region"] for c in CARDS]
    + [region for _n, _t, region in BRIEFS]
)

# ------------------------------------------------------------------ map
# A coarse block world, one character per cell: '#' is land.
# 48 columns x 21 rows, drawn by hand for this page.

WORLD = [
    "                                                ",
    "   #####        ##########################      ",
    " #########     ############################     ",
    "  #########    ###########################      ",
    "   ########     #########################       ",
    "    ######       #######################        ",
    "     #####        #####################         ",
    "      ####         ##################           ",
    "      ###           ################            ",
    "       ###           ##############             ",
    "       ####           ############              ",
    "        #####          ##########               ",
    "        ######          ########        ##      ",
    "         ####            ######        ####     ",
    "         ###              ####          ##      ",
    "          ##               ##                   ",
    "          #                         #######     ",
    "                                    #######     ",
    "                                     #####      ",
    "                                                ",
    "                                                ",
]

# Pin for every pictured story, as a fraction of the map box.
PINS = {
    1: (0.545, 0.16),    # Kyiv region
    2: (0.565, 0.30),    # Antalya
    3: (0.615, 0.40),    # Manama, Bahrain
    4: (0.800, 0.42),    # Hong Kong
    5: (0.850, 0.85),    # Wellington
    6: (0.075, 0.30),    # Las Vegas
    7: (0.115, 0.37),    # San Antonio
    8: (0.525, 0.07),    # Gulf of Finland
    9: (0.635, 0.36),    # Tehran
    10: (0.235, 0.68),   # Brasília
    11: (0.155, 0.28),   # Washington
    12: (0.475, 0.19),   # Brussels
    13: (0.700, 0.46),   # Manipur
    14: (0.758, 0.60),   # Cikande, Java
    15: (0.175, 0.66),   # Junín, Peru
}

# ------------------------------------------------------------------ helpers


def wrap_to(draw, text, fnt, width):
    """Greedy word wrap; returns the list of lines that fit width."""
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def block(draw, x, y, text, fnt, fill, width, leading, cap=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap_to(draw, text, fnt, width)
    if cap is not None:
        lines = lines[:cap]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def middle(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def fit(draw, x, y, text, path, size, width, fill, floor=8):
    """Draw one line, shrinking the font until it fits the width."""
    s = size
    while s > floor and draw.textlength(text, font=font(path, s)) > width:
        s -= 1
    draw.text((x, y), text, font=font(path, s), fill=fill)


def pin(draw, cx, cy, num, r=8.5):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=2)
    fnt = font(SANS_BOLD, 10 if num < 10 else 9)
    label = str(num)
    draw.text((cx - draw.textlength(label, font=fnt) / 2, cy - 5.5),
              label, font=fnt, fill=(255, 255, 255))


def burst(draw, cx, cy, r, fill=ORANGE, core=GOLD):
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)
    draw.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3],
                 fill=core)

# ------------------------------------------------------------------ scenes
# Every scene is drawn from primitives at call time: no image assets.


def _sea(d, x, y, w, h, tone=(16, 58, 82)):
    d.rectangle([x, y, x + w, y + h], fill=tone)


def _waves(d, x, y, w, rows_y):
    for wy in rows_y:
        for i in range(7):
            wx = x + (0.04 + 0.135 * i) * w
            d.arc([wx, wy - 3, wx + 13, wy + 4], 0, 180,
                  fill=(110, 190, 215), width=2)


def scene_drones(d, x, y, w, h):
    """Night sky over a city block: drone silhouettes coming in from
    eight directions, a searchlight cone, one block burning."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    # stars
    for fx, fy in [(0.06, 0.12), (0.30, 0.08), (0.52, 0.16), (0.86, 0.10),
                   (0.68, 0.06), (0.16, 0.30)]:
        d.ellipse([x + fx * w, y + fy * h, x + fx * w + 2, y + fy * h + 2],
                  fill=(220, 224, 235))
    # drone silhouettes with dashed approach trails
    for fx, fy in [(0.16, 0.20), (0.38, 0.13), (0.60, 0.22), (0.80, 0.14)]:
        dx, dy = x + fx * w, y + fy * h
        d.line([dx - 9, dy - 6, dx + 9, dy + 6], fill=(235, 235, 240), width=2)
        d.line([dx - 9, dy + 6, dx + 9, dy - 6], fill=(235, 235, 240), width=2)
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED)
        for k in range(3):
            tx = dx - 16 - k * 9
            d.point((tx, dy + 8 + k * 5), fill=(170, 175, 190))
    # searchlight cone from the ground, right
    d.polygon([(x + 0.90 * w, y + h), (x + 0.52 * w, y + 4),
               (x + 0.64 * w, y + 4)], fill=(96, 108, 128))
    # city blocks along the bottom, one of them burning
    base = y + h
    for i, (fx, fw, fh) in enumerate([(0.03, 0.13, 0.34), (0.19, 0.15, 0.46),
                                      (0.37, 0.14, 0.38), (0.54, 0.16, 0.52),
                                      (0.73, 0.13, 0.40), (0.88, 0.10, 0.30)]):
        bx = x + fx * w
        d.rectangle([bx, base - fh * h, bx + fw * w, base], fill=(30, 34, 44))
        for r in range(3):
            for c in range(3):
                if (i * 7 + r * 3 + c) % 3:
                    d.rectangle([bx + 4 + c * (fw * w - 8) / 3,
                                 base - fh * h + 4 + r * (fh * h - 8) / 3,
                                 bx + 6 + c * (fw * w - 8) / 3,
                                 base - fh * h + 6 + r * (fh * h - 8) / 3],
                                fill=GOLD)
    burst(d, x + 0.615 * w, base - 0.52 * h - 4, 11)
    burst(d, x + 0.585 * w, base - 0.46 * h, 6)
    tag = "186 DRONES OVERNIGHT"
    d.text((x + 34, y + 4), tag, font=font(SANS_BOLD, 9),
           fill=(240, 236, 226))
    tag2 = "161 DOWNED"
    tw = d.textlength(tag2, font=font(SANS_BOLD, 9))
    d.rectangle([x + w - tw - 10, y + 3, x + w - 4, y + 16], fill=RED)
    d.text((x + w - tw - 7, y + 5), tag2, font=font(SANS_BOLD, 9),
           fill=(255, 255, 255))


def scene_cop(d, x, y, w, h):
    """A summit clock run past the hour; the draft text with its
    fossil-fuels line struck out; a calendar whose days run out —
    the summit closed two days late, with nothing adopted."""
    d.rectangle([x, y, x + w, y + h], fill=(38, 46, 40))
    cy = y + h / 2
    # clock, left
    cx = x + 0.14 * w
    r = h * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(235, 232, 220), width=3)
    d.line([cx, cy, cx, cy - r * 0.72], fill=(235, 232, 220), width=3)
    d.line([cx, cy, cx + r * 0.55, cy + r * 0.30], fill=RED, width=3)
    d.text((cx - 16, cy + r + 4), "OVERTIME", font=font(SANS_BOLD, 8),
           fill=(235, 232, 220))
    # the draft, centre: a page whose key line is struck through
    dx0, dy0 = x + 0.28 * w, y + 7
    dx1, dy1 = x + 0.60 * w, y + h - 7
    d.rectangle([dx0, dy0, dx1, dy1], fill=(238, 234, 222))
    d.text((dx0 + 6, dy0 + 4), "FINAL TEXT", font=font(SANS_BOLD, 8), fill=INK)
    for i, wd in enumerate((0.78, 0.60)):
        ly = dy0 + 21 + i * 10
        d.line([dx0 + 6, ly, dx0 + wd * (dx1 - dx0), ly],
               fill=(120, 118, 110), width=2)
    fy = dy0 + 45
    ff = font(SERIF_ITALIC, 11)
    d.text((dx0 + 6, fy), "fossil fuels", font=ff, fill=INK)
    d.line([dx0 + 4, fy + 6, dx0 + 8 + d.textlength("fossil fuels", font=ff),
            fy + 6], fill=RED, width=2)
    d.text((dx0 + 6, fy + 16), "NOT ADOPTED", font=font(SANS_BOLD, 8),
           fill=RED)
    # calendar, right: the scheduled days run out on the red 22nd
    gx = x + 0.65 * w
    cell = 0.335 * w / 6
    for i, day in enumerate(("17", "18", "19", "20", "21", "22")):
        cx0 = gx + i * cell
        d.rectangle([cx0 + 1, cy - 13, cx0 + cell - 1, cy + 7],
                    fill=RED if day == "22" else (72, 82, 74))
        middle(d, cx0 + cell / 2, cy - 9, day, font(SANS_BOLD, 9),
               (245, 243, 235))
    d.text((gx + 1, cy + 12), "TWO DAYS OVER", font=font(SANS_BOLD, 8),
           fill=(245, 243, 235))


def scene_radar(d, x, y, w, h):
    """Claim against denial: a radar dish under dashed claim arcs on
    the left, Bahrain's shield of denial on the right, a fire between
    them at a civilian site."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 44))
    base = y + h
    # ground installations
    d.rectangle([x + 0.06 * w, base - 14, x + 0.30 * w, base], fill=(52, 58, 70))
    d.rectangle([x + 0.66 * w, base - 12, x + 0.94 * w, base], fill=(52, 58, 70))
    # radar dish on a mast, left
    mx = x + 0.16 * w
    d.line([mx, base - 14, mx, base - 34], fill=(200, 205, 215), width=3)
    d.arc([mx - 14, base - 52, mx + 16, base - 22], 300, 120,
          fill=(225, 228, 235), width=3)
    d.line([mx + 2, base - 37, mx + 20, base - 44], fill=RED, width=2)
    # dashed claim arcs crossing the sky
    for off in (0, 7, 14):
        d.arc([x + 0.20 * w, y + 2 + off, x + 0.86 * w, y + h * 0.9 + off],
              200, 320, fill=(240, 170, 90), width=1)
    # the fire at the civilian site, centre
    burst(d, x + 0.50 * w, base - 16, 12)
    d.rectangle([x + 0.44 * w, base - 8, x + 0.56 * w, base], fill=(70, 60, 50))
    # denial shield, right
    sx, sy = x + 0.80 * w, y + h * 0.30
    d.polygon([(sx - 9, sy - 10), (sx + 9, sy - 10), (sx + 9, sy + 2),
               (sx, sy + 12), (sx - 9, sy + 2)], outline=(240, 240, 240),
              fill=(120, 40, 40))
    d.line([sx - 5, sy - 2, sx + 5, sy + 6], fill=(255, 255, 255), width=2)
    d.line([sx + 5, sy - 2, sx - 5, sy + 6], fill=(255, 255, 255), width=2)
    tag = "CLAIM VS DENIAL"
    d.text((x + 34, y + 4), tag, font=font(SANS_BOLD, 9),
           fill=(240, 236, 226))
    tag2 = "2 RADARS?"
    tw = d.textlength(tag2, font=font(SANS_BOLD, 9))
    d.rectangle([x + w - tw - 10, y + 3, x + w - 4, y + 16], fill=RED)
    d.text((x + w - tw - 7, y + 5), tag2, font=font(SANS_BOLD, 9),
           fill=(255, 255, 255))


def scene_vote(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 40, 66))
    cx, cy = x + w / 2, y + h / 2
    # ballot box with a paper going in
    d.rectangle([cx - 22, cy + 2, cx + 22, cy + 14], fill=(226, 200, 150))
    d.rectangle([cx - 12, cy + 5, cx + 12, cy + 7], fill=(40, 32, 24))
    d.polygon([(cx - 9, cy - 12), (cx + 9, cy - 12), (cx + 5, cy + 3),
               (cx - 5, cy + 3)], fill=(245, 243, 235))
    d.line([cx - 4, cy - 6, cx - 1, cy - 2], fill=(30, 132, 73), width=2)
    d.line([cx - 1, cy - 2, cx + 5, cy - 9], fill=(30, 132, 73), width=2)
    d.text((x + 26, y + 3), "VOTE", font=font(SANS_BOLD, 9),
           fill=(240, 236, 226))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 96, 46))
    cy = y + h / 2
    # stumps and bails
    for fx in (0.60, 0.65, 0.70):
        gx = x + fx * w
        d.line([gx, cy - 10, gx, cy + 11], fill=(240, 220, 160), width=2)
    d.line([x + 0.60 * w, cy - 11, x + 0.65 * w, cy - 11],
           fill=(240, 220, 160), width=2)
    # bat, angled, left
    d.polygon([(x + 0.16 * w, cy + 12), (x + 0.30 * w, cy - 8),
               (x + 0.36 * w, cy - 4), (x + 0.22 * w, cy + 14)],
              fill=(226, 200, 150))
    d.line([x + 0.30 * w, cy - 8, x + 0.38 * w, cy - 14],
           fill=(120, 84, 44), width=3)
    # ball in flight
    d.ellipse([x + 0.46 * w, cy - 6, x + 0.50 * w, cy - 2], fill=(200, 40, 40))
    d.text((x + 0.78 * w, cy - 8), "720/9", font=font(SANS_BOLD, 12),
           fill=(245, 243, 235))


def scene_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 18, 28))
    base = y + h - 4
    # low car silhouette
    d.polygon([(x + 0.10 * w, base - 6), (x + 0.34 * w, base - 6),
               (x + 0.42 * w, base - 13), (x + 0.62 * w, base - 13),
               (x + 0.70 * w, base - 6), (x + 0.92 * w, base - 6),
               (x + 0.92 * w, base - 2), (x + 0.10 * w, base - 2)],
              fill=(178, 34, 24))
    d.rectangle([x + 0.06 * w, base - 10, x + 0.14 * w, base - 2],
                fill=(60, 64, 74))
    d.rectangle([x + 0.88 * w, base - 14, x + 0.94 * w, base - 2],
                fill=(60, 64, 74))
    for fx in (0.24, 0.78):
        cx = x + fx * w
        d.ellipse([cx - 6, base - 8, cx + 6, base + 2], fill=(8, 8, 10),
                  outline=(200, 200, 205), width=1)
    # chequered flag, top right
    fx0, fy0 = x + 0.80 * w, y + 3
    d.line([fx0, fy0, fx0, fy0 + 14], fill=(230, 230, 230), width=2)
    for r in range(2):
        for c in range(3):
            d.rectangle([fx0 + 2 + c * 5, fy0 + r * 5, fx0 + 7 + c * 5,
                         fy0 + 5 + r * 5],
                        fill=(240, 240, 240) if (r + c) % 2 else (20, 20, 20))
    d.text((x + 26, y + 3), "LAS VEGAS", font=font(SANS_BOLD, 9),
           fill=(240, 236, 226))


def scene_nba(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 52, 24))
    cx = x + 0.62 * w
    cy = y + h * 0.30
    # backboard, rim, net
    d.rectangle([cx - 16, cy - 10, cx + 16, cy + 4], outline=(240, 240, 240),
                width=2)
    d.rectangle([cx - 7, cy - 5, cx + 7, cy + 4], outline=ORANGE, width=1)
    d.line([cx - 8, cy + 5, cx + 8, cy + 5], fill=ORANGE, width=2)
    for k in range(4):
        d.line([cx - 8 + k * 5, cy + 5, cx - 5 + k * 4, cy + 13],
               fill=(230, 230, 230), width=1)
    # ball dropping through
    d.ellipse([cx - 5, cy - 1, cx + 5, cy + 9], fill=(220, 110, 40))
    # the number of the night, left
    d.text((x + 0.17 * w, y + h * 0.22), "50", font=font(SANS_BOLD, 20),
           fill=(255, 220, 170))
    d.text((x + 0.17 * w, y + h * 0.22 + 21), "POINTS",
           font=font(SANS_BOLD, 8), fill=(255, 220, 170))


def scene_ship(d, x, y, w, h):
    """Grey cargo ship, fire on deck, dawn sea (Gulf of Finland)."""
    _sea(d, x, y, w, h, tone=(24, 48, 70))
    d.rectangle([x, y, x + w, y + h * 0.30], fill=(70, 66, 60))
    gy = y + h * 0.58
    d.polygon([(x + 0.10 * w, gy), (x + 0.88 * w, gy), (x + 0.82 * w, gy + 13),
               (x + 0.16 * w, gy + 13)], fill=(96, 104, 114))
    d.rectangle([x + 0.68 * w, gy - 16, x + 0.78 * w, gy], fill=(110, 118, 128))
    for fx in (0.24, 0.38, 0.52):
        d.rectangle([x + fx * w, gy - 8, x + fx * w + 16, gy], fill=(140, 90, 60))
    burst(d, x + 0.45 * w, gy - 10, 10)
    for i, (fx, fy) in enumerate([(0.44, 0.40), (0.50, 0.33), (0.57, 0.27)]):
        r = 5 + i * 2
        d.ellipse([x + fx * w - r, y + fy * h - r, x + fx * w + r,
                   y + fy * h + r], fill=(122, 120, 114))
    _waves(d, x, y, w, [y + h - 6])
    d.text((x + 0.28 * w, gy + 3), "SPARTA II", font=font(SANS_BOLD, 8),
           fill=(228, 232, 238))


def scene_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 26, 38))
    # pylon
    px = x + 0.30 * w
    d.line([px - 9, y + h, px, y + 4], fill=(170, 175, 185), width=2)
    d.line([px + 9, y + h, px, y + 4], fill=(170, 175, 185), width=2)
    d.line([px - 13, y + 9, px + 13, y + 9], fill=(170, 175, 185), width=2)
    d.line([px - 10, y + 15, px + 10, y + 15], fill=(170, 175, 185), width=2)
    # sagging wires going dark
    d.arc([px + 8, y + 2, x + w + 10, y + 20], 90, 170,
          fill=(120, 124, 134), width=1)
    # lightning bolt, right
    bx = x + 0.68 * w
    d.polygon([(bx + 5, y + 2), (bx - 3, y + h * 0.52), (bx + 2, y + h * 0.52),
               (bx - 4, y + h - 3), (bx + 8, y + h * 0.42),
               (bx + 3, y + h * 0.42)], fill=GOLD)
    # dark houses with one lit window
    for i, fx in enumerate((0.52, 0.82)):
        hx = x + fx * w
        d.rectangle([hx, y + h - 11, hx + 14, y + h], fill=(12, 12, 16))
        d.polygon([(hx - 2, y + h - 11), (hx + 7, y + h - 16),
                   (hx + 16, y + h - 11)], fill=(12, 12, 16))
        if i == 0:
            d.rectangle([hx + 5, y + h - 8, hx + 9, y + h - 4], fill=GOLD)


def scene_icu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
    cy = y + h / 2
    cx = x + 0.24 * w
    d.rectangle([cx - 4, cy - 12, cx + 4, cy + 12], fill=RED)
    d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=RED)
    # pulse line running flat-stable
    pts = [(x + 0.44 * w, cy), (x + 0.56 * w, cy), (x + 0.60 * w, cy - 8),
           (x + 0.65 * w, cy + 6), (x + 0.69 * w, cy), (x + 0.97 * w, cy)]
    d.line(pts, fill=(30, 132, 73), width=2)
    d.text((x + 0.44 * w, y + 3), "ICU", font=font(SANS_BOLD, 9), fill=INK)


def scene_cyber(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 24, 36))
    cy = y + h / 2
    # database cylinder
    cx = x + 0.34 * w
    d.ellipse([cx - 13, cy - 13, cx + 13, cy - 6], outline=(110, 190, 215),
              width=2)
    d.line([cx - 13, cy - 10, cx - 13, cy + 10], fill=(110, 190, 215), width=2)
    d.line([cx + 13, cy - 10, cx + 13, cy + 10], fill=(110, 190, 215), width=2)
    d.arc([cx - 13, cy + 3, cx + 13, cy + 13], 0, 180,
          fill=(110, 190, 215), width=2)
    # magnifier over it, with a crack of red
    mx, my = x + 0.62 * w, cy - 2
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], outline=GOLD, width=3)
    d.line([mx + 8, my + 8, mx + 16, my + 15], fill=GOLD, width=3)
    d.line([mx - 5, my - 5, mx + 1, my + 1], fill=RED, width=2)
    d.line([mx + 1, my + 1, mx - 2, my + 6], fill=RED, width=2)


def scene_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 66, 78))
    base = y + h
    # parked plane, tail up, going nowhere
    d.polygon([(x + 0.10 * w, base - 8), (x + 0.62 * w, base - 8),
               (x + 0.70 * w, base - 13), (x + 0.70 * w, base - 4),
               (x + 0.10 * w, base - 4)], fill=(210, 214, 220))
    d.polygon([(x + 0.12 * w, base - 8), (x + 0.18 * w, base - 20),
               (x + 0.24 * w, base - 8)], fill=(178, 34, 24))
    for i in range(5):
        d.ellipse([x + (0.30 + 0.06 * i) * w, base - 11,
                   x + (0.32 + 0.06 * i) * w, base - 8], fill=(40, 60, 90))
    # picket sign
    sx = x + 0.82 * w
    d.line([sx, base - 16, sx, base], fill=(120, 84, 44), width=2)
    d.rectangle([sx - 9, base - 24, sx + 9, base - 16], fill=(245, 243, 235))
    d.line([sx - 6, base - 20, sx + 6, base - 20], fill=RED, width=2)


def scene_liquor(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(44, 36, 28))
    base = y + h
    # three bottles, one tipped over
    for i, fx in enumerate((0.16, 0.30)):
        bx = x + fx * w
        d.rectangle([bx, base - 20, bx + 9, base], fill=(60, 90, 50))
        d.rectangle([bx + 3, base - 25, bx + 6, base - 20], fill=(60, 90, 50))
    bx = x + 0.48 * w
    d.rectangle([bx, base - 8, bx + 20, base], fill=(60, 90, 50))
    # warning triangle
    tx, ty = x + 0.76 * w, y + h / 2
    d.polygon([(tx, ty - 11), (tx - 10, ty + 8), (tx + 10, ty + 8)],
              outline=GOLD, width=2)
    d.text((tx - 2, ty - 4), "!", font=font(SANS_BOLD, 12), fill=GOLD)


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(56, 40, 34))
    base = y + h
    d.rectangle([x + 0.10 * w, base - 16, x + 0.62 * w, base], fill=(30, 24, 20))
    d.polygon([(x + 0.10 * w, base - 16), (x + 0.26 * w, base - 22),
               (x + 0.42 * w, base - 16)], fill=(30, 24, 20))
    d.rectangle([x + 0.70 * w, base - 26, x + 0.76 * w, base], fill=(30, 24, 20))
    for fx, fh in [(0.24, 0.34), (0.36, 0.46), (0.50, 0.30)]:
        cx = x + fx * w
        d.polygon([(cx - 6, base - 14), (cx, base - 14 - fh * h),
                   (cx + 6, base - 14)], fill=ORANGE)
        d.polygon([(cx - 3, base - 14), (cx, base - 14 - fh * h * 0.6),
                   (cx + 3, base - 14)], fill=GOLD)
    for i, fx in enumerate((0.30, 0.44, 0.58)):
        r = 6 + i * 3
        d.ellipse([x + fx * w - r, y + 2 + i * 2, x + fx * w + r,
                   y + 2 + i * 2 + r], fill=(96, 88, 82))


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(66, 58, 48))
    base = y + h
    d.polygon([(x, base), (x + 0.34 * w, y + 6), (x + 0.55 * w, base)],
              fill=(44, 38, 32))
    d.polygon([(x + 0.30 * w, y + 12), (x + 0.34 * w, y + 6),
               (x + 0.38 * w, y + 12)], fill=(235, 235, 235))
    pts = [(x + 0.52 * w, base - 2), (x + 0.60 * w, base - 12),
           (x + 0.66 * w, base - 8), (x + 0.74 * w, base - 18),
           (x + 0.82 * w, base - 12), (x + 0.92 * w, base - 20)]
    d.line(pts, fill=(12, 10, 8), width=3)
    d.line([x, base - 1, x + w, base - 1], fill=(12, 10, 8), width=2)
    hx = x + 0.60 * w
    d.rectangle([hx, base - 12, hx + 13, base - 2], fill=(226, 200, 150))
    d.polygon([(hx - 2, base - 12), (hx + 6, base - 17), (hx + 15, base - 12)],
              fill=(150, 60, 40))


SCENES = {
    "drones": scene_drones, "cop": scene_cop, "radar": scene_radar,
    "vote": scene_vote, "cricket": scene_cricket, "f1": scene_f1,
    "nba": scene_nba, "ship": scene_ship, "power": scene_power,
    "icu": scene_icu, "cyber": scene_cyber, "strike": scene_strike,
    "liquor": scene_liquor, "factory": scene_factory, "quake": scene_quake,
}

# ------------------------------------------------------------------ page


def grain(img, step=2, mod=89, hits=2, delta=7):
    """A deterministic paper speckle, seeded by pure arithmetic."""
    px = img.load()
    w, h = img.size
    for yy in range(0, h, step):
        for xx in range(0, w, step):
            if (xx * 31 + yy * 17) % mod < hits:
                r, g, b = px[xx, yy]
                px[xx, yy] = (max(0, r - delta), max(0, g - delta),
                              max(0, b - delta))
    return img


def masthead(d, total_line):
    d.text((EDGE, 13), "THE WORLD IN ONE DAY", font=font(SANS_BOLD, 17),
           fill=RED)
    rf = font(SANS, 11)
    d.text((PAGE - EDGE - d.textlength(total_line, font=rf), 17), total_line,
           font=rf, fill=INK)
    d.line([EDGE, 40, PAGE - EDGE, 40], fill=INK, width=3)
    d.line([EDGE, 45, PAGE - EDGE, 45], fill=INK, width=1)


def render():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    masthead(d, f"{STORY_COUNT} STORIES · 7 REGIONS · EVERY ONE DATED "
                f"SUNDAY 22 NOVEMBER 2026")

    # ---- date, dek, timeline
    middle(d, PAGE / 2, 48, DAY, font(SERIF_BOLD, 62), INK)
    middle(d, PAGE / 2, 122, DEK, font(SERIF_ITALIC, 17), RED)
    d.line([EDGE, 146, PAGE - EDGE, 146], fill=INK, width=1)
    d.text((EDGE, 152), "THE DAY IN UTC", font=font(SANS_BOLD, 10), fill=RED)
    lab_w = d.textlength("THE DAY IN UTC  ", font=font(SANS_BOLD, 10))
    fit(d, EDGE + lab_w, 152, TIMELINE, SANS, 10, SPAN - lab_w, INK)
    # an hour-tick ruler under the line, with a dot for each printed time
    tl_x, tl_span = EDGE + lab_w, SPAN - lab_w
    for k in range(25):
        txp = tl_x + tl_span * k / 24
        d.line([txp, 165, txp, 168], fill=FAINT, width=1)
    for frac in (0.042, 0.125, 0.229, 0.250, 0.333, 0.583):
        ex = tl_x + tl_span * frac
        d.ellipse([ex - 2, 161, ex + 2, 165], fill=RED)
    d.line([EDGE, 168, PAGE - EDGE, 168], fill=INK, width=1)

    # ---- numbers strip
    cell = SPAN / 6
    for i, (fig, cap) in enumerate(NUMBERS):
        cx = EDGE + cell * i + cell / 2
        middle(d, cx, 176, fig, font(SERIF_BOLD, 31), INK)
        for j, ln in enumerate(wrap_to(d, cap, font(SANS, 10), cell - 14)):
            middle(d, cx, 212 + j * 11, ln, font(SANS, 10), FAINT)
        if i:
            d.line([EDGE + cell * i, 178, EDGE + cell * i, 232],
                   fill=RULE_SOFT, width=1)
    d.line([EDGE, 242, PAGE - EDGE, 242], fill=INK, width=1)

    # ---- region tabs, counts computed from the story list
    tf = font(SANS_BOLD, 12)
    labels = [(r, f"{r.upper()} {REGION_TALLY[r]}") for r in TAB_ORDER]
    widths = [d.textlength(t, font=tf) + 20 for _r, t in labels]
    gap = (SPAN - sum(widths)) / (len(labels) - 1)
    tx = float(EDGE)
    for (r, t), tw in zip(labels, widths):
        d.rectangle([tx, 250, tx + tw, 272], fill=TAB_INK[r])
        middle(d, tx + tw / 2, 255, t, tf, (255, 255, 255))
        tx += tw + gap

    # ---- heroes
    hy, hero_w = 282, 316
    for i, hero in enumerate(HEROES):
        hx = EDGE + i * (hero_w + 10)
        SCENES[hero["scene"]](d, hx, hy, hero_w, 88)
        pin(d, hx + 15, hy + 15, hero["num"], r=10)
        d.text((hx, hy + 96), hero["tag"], font=font(SANS_BOLD, 11), fill=RED)
        # each hero carries its own certainty pill, same as the cards
        pill = f"● {hero['cert']}"
        pf = font(SANS_BOLD, 9)
        pw = d.textlength(pill, font=pf) + 12
        d.rounded_rectangle([hx + hero_w - pw, hy + 94, hx + hero_w,
                             hy + 110], 3, fill=INK)
        d.text((hx + hero_w - pw + 6, hy + 97), pill, font=pf,
               fill=(255, 255, 255))
        block(d, hx, hy + 114, hero["head"], font(SERIF_BOLD, 27), INK,
              hero_w, 29, cap=2)
        block(d, hx, hy + 174, hero["summ"], font(SERIF, 13), INK,
              hero_w, 16, cap=3)
    d.line([EDGE, 510, PAGE - EDGE, 510], fill=INK, width=1)

    # ---- pictured cards, two rows of six
    card_w = 154
    for i, card in enumerate(CARDS):
        cx0 = EDGE + (i % 6) * (card_w + 8)
        cy0 = 518 + (i // 6) * 118
        SCENES[card["scene"]](d, cx0, cy0, card_w, 34)
        pin(d, cx0 + 10, cy0 + 10, card["num"], r=8)
        fit(d, cx0, cy0 + 39, f"{card['place']} · {card['cert']}",
            SANS_BOLD, 10, card_w, RED)
        block(d, cx0, cy0 + 53, card["head"], font(SERIF_BOLD, 15), INK,
              card_w, 17, cap=2)
        block(d, cx0, cy0 + 89, card["summ"], font(SERIF, 12), INK,
              card_w, 13, cap=2)

    # ---- bottom band: map left, briefs right
    by = 758
    d.text((EDGE, by), "WHERE IT HAPPENED", font=font(SANS_BOLD, 12), fill=INK)
    map_x, map_y = EDGE, by + 24
    pitch_x, pitch_y = 7.5, 7.0
    map_w = len(WORLD[0]) * pitch_x
    map_h = len(WORLD) * pitch_y
    d.rectangle([map_x - 5, map_y - 5, map_x + map_w + 5, map_y + map_h + 5],
                fill=MAP_SEA)
    for ri, row in enumerate(WORLD):
        for ci, ch in enumerate(row):
            if ch == "#":
                cxp = map_x + ci * pitch_x + pitch_x / 2
                cyp = map_y + ri * pitch_y + pitch_y / 2
                d.rectangle([cxp - pitch_x / 2 + 0.6, cyp - pitch_y / 2 + 0.6,
                             cxp + pitch_x / 2 - 0.6, cyp + pitch_y / 2 - 0.6],
                            fill=MAP_DOT)
    for num, (fx, fy) in PINS.items():
        pin(d, map_x + fx * map_w, map_y + fy * map_h, num, r=8.5)
    d.text((EDGE, map_y + map_h + 8),
           "Each number is the pictured story of that number on this page.",
           font=font(SERIF_ITALIC, 10), fill=FAINT)

    bx = 404
    d.text((bx, by), f"ALSO ON SUNDAY — {len(BRIEFS)} MORE STORIES",
           font=font(SANS_BOLD, 12), fill=INK)
    bf = font(SANS_BOLD, 12)
    col_w = 288
    for i, (num, text, _region) in enumerate(BRIEFS):
        col, row_i = divmod(i, 11)
        x0 = bx + col * (col_w + 16)
        y0 = by + 16 + row_i * 14
        label = f"{num} "
        d.text((x0, y0), label, font=bf, fill=RED)
        fit(d, x0 + d.textlength(label, font=bf), y0, text, SANS, 12,
            col_w - d.textlength(label, font=bf), INK, floor=10)

    # ---- date-check box
    box_y = 952
    d.rectangle([EDGE, box_y, PAGE - EDGE, box_y + 36], fill=(250, 238, 231),
                outline=RED, width=2)
    block(d, EDGE + 8, box_y + 6, DATE_CHECK, font(SERIF, 11), DEEP_RED,
          SPAN - 16, 12, cap=2)

    # ---- footer: the certainty legend, then the dating line
    d.text((EDGE, 994),
           "HOW SURE — ● REPORTED: carried by the day's wires, sources "
           "named · ● CLAIM: one side's account, labelled as such · "
           "● FORECAST: still to happen when drawn.",
           font=font(SANS_BOLD, 9), fill=INK)
    d.text((EDGE, 1008),
           "Every story here happened, or was first reported, on Sunday "
           "22 November 2026. Officials' counts are attributed in place.",
           font=font(SANS, 9), fill=FAINT)
    tail = "Sources named beside each story · original drawings"
    tf2 = font(SANS, 9)
    d.text((PAGE - EDGE - d.textlength(tail, font=tf2), 1008), tail,
           font=tf2, fill=FAINT)

    return grain(img)


def render_fallback():
    """A compact edition of the same page, kept as the safety copy."""
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d, f"{STORY_COUNT} STORIES · SUNDAY 22 NOVEMBER 2026")
    middle(d, PAGE / 2, 60, DAY, font(SERIF_BOLD, 58), INK)
    block(d, EDGE, 150, DEK, font(SERIF_ITALIC, 17), RED, SPAN, 22)
    d.line([EDGE, 190, PAGE - EDGE, 190], fill=INK, width=1)
    y = 210
    for hero in HEROES:
        d.text((EDGE, y), f"{hero['num']}  {hero['tag']}",
               font=font(SANS_BOLD, 12), fill=RED)
        y = block(d, EDGE, y + 20, hero["head"], font(SERIF_BOLD, 30), INK,
                  SPAN, 34, cap=1)
        y = block(d, EDGE, y + 4, hero["summ"], font(SERIF, 15), INK,
                  SPAN, 20, cap=2)
        y += 26
    d.line([EDGE, y, PAGE - EDGE, y], fill=INK, width=1)
    cell = SPAN / 6
    for i, (fig, cap) in enumerate(NUMBERS):
        cx = EDGE + cell * i + cell / 2
        middle(d, cx, y + 14, fig, font(SERIF_BOLD, 28), INK)
        for j, ln in enumerate(wrap_to(d, cap, font(SANS, 10), cell - 14)):
            middle(d, cx, y + 48 + j * 11, ln, font(SANS, 10), FAINT)
    d.text((EDGE, PAGE - 40),
           "Compact edition — the full front page is entry.png.",
           font=font(SANS, 10), fill=FAINT)
    return grain(img)


def build():
    here = os.path.dirname(os.path.abspath(__file__))
    entry = os.path.join(here, "entry.png")
    render().save(entry, format="PNG", optimize=True)
    fallback = os.path.join(here, "fallback.png")
    render_fallback().save(fallback, format="PNG", optimize=True)
    return entry, fallback


if __name__ == "__main__":
    for path in build():
        print(path, os.path.getsize(path))
