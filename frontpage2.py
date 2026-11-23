"""frontpage2.py — the RICH edition of the news-image-20261122 page.

Same verified dossier as frontpage.py (36 stories, Sunday 22 November
2026, every figure two-sourced, COP31 printed at its end state),
rebuilt in the full-colour illustrated style of the winning daily
pages: gradient skies and seas in the hero scenes, a coloured
mini-illustration on every card, coloured certainty pills, a coloured
landmass world map on a pale-blue sea, and a dense, grid-disciplined
"mewah" page — rich ink everywhere, nothing clipped, nothing spilled.

frontpage.py stays in the repo as the first edition; this file is the
second. main.py is unchanged: it copies whichever entry.png is
committed. The render is deterministic — same data, same PNG.

Usage:  python3 frontpage2.py [out.png]   (default: entry-v2.png)
"""

import os
import sys

from PIL import Image, ImageDraw

from frontpage import (
    BRIEFS, CARDS, DATE_CHECK, DEK, HEROES, NUMBERS, PINS, REGION_TALLY,
    SANS, SANS_BOLD, SERIF, SERIF_BOLD, SERIF_ITALIC, STORY_COUNT,
    TAB_INK, TAB_ORDER, WORLD, block, fit, font, grain, middle, wrap_to,
)

# ------------------------------------------------------------------ ink

PAPER = (248, 244, 231)
FRAME = (13, 30, 44)
INK = (24, 23, 21)
FAINT = (96, 90, 76)
RED = (190, 30, 22)
DEEP_RED = (148, 27, 18)
NAVY = (19, 35, 57)
GOLD = (233, 165, 33)
ORANGE = (243, 121, 33)
PIN_BLUE = (23, 58, 107)
BADGE_BLUE = (36, 84, 158)
SEA = (203, 226, 243)
LAND = (233, 221, 193)
LAND_DEEP = (224, 209, 175)
RULE_SOFT = (198, 190, 168)

PILL_INK = {
    "REPORTED": (192, 32, 24),
    "CLAIM": (110, 52, 140),
    "FORECAST": (176, 110, 10),
}

PAGE = 1024
EDGE = 38
SPAN = PAGE - 2 * EDGE  # 948 px of content

DAY = "Sunday 22 November 2026"
FIELDS = 15

TIMELINE_SLOTS = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections close"),
    ("05:30", "Verstappen wins Vegas"),
    ("06:00", "COP31 closing plenary"),
    ("08:00", "Kyiv: 161 of 186 downed"),
    ("14:00", "HK turnout passes 93%"),
]

NUMBERS2 = [
    ("186", "DRONES FIRED AT UKRAINE", "OVERNIGHT, FROM 8 DIRECTIONS"),
    ("161", "DOWNED OR SUPPRESSED", "BY UKRAINE'S AIR DEFENCE"),
    ("$120bn", "ADAPTATION TARGET", "DROPPED FROM THE COP31 TEXT"),
    ("98.79%", "HONG KONG TURNOUT", "A RECORD · 5,640 VOTERS"),
    ("720/9", "INDIA'S TEST TOTAL", "A RECORD IN NEW ZEALAND"),
    ("50", "WEMBANYAMA POINTS", "WITH 19 REBOUNDS, 5 BLOCKS"),
]

REGION_SHORT = {
    "Europe": "EUROPE", "Middle East": "MID EAST",
    "Asia-Pacific": "ASIA-PAC", "Americas": "AMERICAS",
    "Africa": "AFRICA", "Oceania": "OCEANIA", "World": "WORLD",
}

HERO_PILL = {1: "REPORTED · AP", 2: "REPORTED · REUTERS",
             3: "CLAIM · AFP"}

# ------------------------------------------------------------------ helpers


def vgrad(w, h, top, bot):
    """A deterministic vertical gradient as an image of size (w, h)."""
    strip = Image.new("RGB", (1, h))
    for i in range(h):
        t = i / max(1, h - 1)
        strip.putpixel((0, i), tuple(
            round(top[c] + (bot[c] - top[c]) * t) for c in range(3)))
    return strip.resize((w, h))


def pill(d, x_right, y, text, color, size=8.5, h=15):
    fnt = font(SANS_BOLD, size)
    tw = d.textlength(text, font=fnt)
    w = tw + 11
    d.rounded_rectangle([x_right - w, y, x_right, y + h], 3, fill=color)
    d.text((x_right - w + 5.5, y + (h - size) / 2 - 1), text, font=fnt,
           fill=(255, 255, 255))
    return w


def badge(d, cx, cy, num, r=10):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BADGE_BLUE,
              outline=(255, 255, 255), width=2)
    label = str(num)
    fnt = font(SANS_BOLD, 12 if num < 10 else 11)
    box = d.textbbox((0, 0), label, font=fnt)
    d.text((cx - (box[2] - box[0]) / 2 - box[0], cy - 6.5), label,
           font=fnt, fill=(255, 255, 255))


def pin2(d, cx, cy, num, r=7):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PIN_BLUE,
              outline=(255, 255, 255), width=2)
    label = str(num)
    fnt = font(SANS_BOLD, 9 if num < 10 else 8)
    box = d.textbbox((0, 0), label, font=fnt)
    d.text((cx - (box[2] - box[0]) / 2 - box[0], cy - 5), label,
           font=fnt, fill=(255, 255, 255))


def burst2(d, cx, cy, r, fill=ORANGE, core=GOLD):
    import math
    spikes = []
    for i in range(24):
        ang = math.tau * i / 24
        rad = r if i % 2 == 0 else r * 0.45
        spikes.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(spikes, fill=fill)
    inner = r * 0.3
    d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=core)


def scene_tag(d, x, y, text):
    """The red scene tag the winning pages carry, bottom-left."""
    fnt = font(SANS_BOLD, 10)
    tw = d.textlength(text, font=fnt)
    d.rectangle([x, y, x + tw + 12, y + 17], fill=RED)
    d.text((x + 6, y + 3), text, font=fnt, fill=(255, 255, 255))

# ------------------------------------------------------------------ hero scenes
# Each scene is drawn on its own canvas and pasted, so nothing spills.


def hero_drones(w, h):
    img = vgrad(w, h, (9, 20, 42), (42, 70, 108))
    d = ImageDraw.Draw(img)
    # stars and a crescent moon
    for fx, fy in [(0.05, 0.14), (0.22, 0.08), (0.40, 0.20), (0.58, 0.10),
                   (0.70, 0.22), (0.84, 0.30), (0.13, 0.34), (0.48, 0.05)]:
        d.ellipse([fx * w, fy * h, fx * w + 2, fy * h + 2],
                  fill=(228, 232, 244))
    mx, my = 0.90 * w, 0.16 * h
    d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(238, 240, 246))
    d.ellipse([mx - 3, my - 9, mx + 11, my + 7], fill=(16, 30, 54))
    # jets with white missile trails arcing down to the city
    for jx, jy, tx in [(0.16, 0.20, 0.30), (0.38, 0.13, 0.52),
                       (0.60, 0.22, 0.72)]:
        d.arc([jx * w - 6, jy * h - 26, tx * w + 30, jy * h + 44],
              300, 65, fill=(235, 238, 245), width=2)
        d.polygon([(jx * w - 11, jy * h + 3), (jx * w + 12, jy * h - 2),
                   (jx * w + 4, jy * h + 5)], fill=(10, 14, 22))
        d.polygon([(jx * w - 11, jy * h + 3), (jx * w - 16, jy * h - 4),
                   (jx * w - 6, jy * h + 1)], fill=(10, 14, 22))
    # skyline silhouette with lit windows, one block burning
    base = h
    blocks = [(0.00, 0.16, 0.36), (0.17, 0.15, 0.52), (0.33, 0.14, 0.42),
              (0.48, 0.17, 0.60), (0.66, 0.14, 0.46), (0.81, 0.19, 0.34)]
    for i, (fx, fw, fh) in enumerate(blocks):
        bx = fx * w
        d.rectangle([bx, base - fh * h, bx + fw * w, base], fill=(7, 10, 16))
        for r in range(3):
            for c in range(3):
                if (i * 5 + r * 3 + c) % 3:
                    d.rectangle([bx + 4 + c * (fw * w - 9) / 3,
                                 base - fh * h + 4 + r * (fh * h - 9) / 3,
                                 bx + 7 + c * (fw * w - 9) / 3,
                                 base - fh * h + 7 + r * (fh * h - 9) / 3],
                                fill=GOLD)
    burst2(d, 0.565 * w, base - 0.60 * h, 12)
    burst2(d, 0.535 * w, base - 0.52 * h, 7)
    scene_tag(d, 8, h - 25, "186 DRONES OVERNIGHT")
    return img


def hero_cop(w, h):
    img = vgrad(w, h, (15, 40, 36), (47, 76, 58))
    d = ImageDraw.Draw(img)
    # hall panelling
    for fx in (0.04, 0.96):
        d.line([fx * w, 6, fx * w, h - 6], fill=(86, 116, 92), width=1)
    # the rejected document, centre-left, glowing cream
    px0, py0, px1, py1 = 0.30 * w, 7, 0.63 * w, h - 7
    d.rectangle([px0, py0, px1, py1], fill=(240, 236, 224))
    d.line([px0 + 5, py0 + 5, px1 - 5, py1 - 5], fill=RED, width=3)
    d.line([px0 + 5, py1 - 5, px1 - 5, py0 + 5], fill=RED, width=3)
    d.rectangle([px0 + 5, py0 + 4, px0 + 64, py0 + 17],
                fill=(240, 236, 224))
    d.text((px0 + 7, py0 + 5), "FINAL TEXT", font=font(SANS_BOLD, 9),
           fill=INK)
    ff = font(SERIF_ITALIC, 12)
    fy = py0 + h * 0.52
    tw = d.textlength("fossil fuels", font=ff)
    d.rectangle([px0 + 5, fy - 2, px0 + 13 + tw, fy + 14],
                fill=(240, 236, 224))
    d.text((px0 + 7, fy), "fossil fuels", font=ff, fill=INK)
    d.line([px0 + 5, fy + 7, px0 + 10 + tw, fy + 7], fill=RED, width=2)
    # four flags at half-mast, right: EU, UK-ish, Panama, Marshall-ish
    flags = [(0.70, (38, 62, 140)), (0.78, (30, 50, 110)),
             (0.86, (235, 235, 230)), (0.94, (235, 130, 40))]
    for fx, col in flags:
        gx = fx * w
        d.line([gx, 8, gx, h - 8], fill=(214, 212, 202), width=2)
        fy2 = h * 0.44
        d.rectangle([gx, fy2, gx + 0.055 * w, fy2 + 10], fill=col)
    # EU gold stars on the first flag
    for k in range(4):
        sx = 0.70 * w + 3 + (k % 2) * 5
        sy = h * 0.44 + 2 + (k // 2) * 5
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=GOLD)
    # a lone gavel at rest, left
    gx, gy = 0.11 * w, h * 0.60
    d.line([gx - 9, gy + 9, gx + 11, gy - 11], fill=(206, 160, 92), width=4)
    d.rectangle([gx + 3, gy - 15, gx + 15, gy - 5], fill=(160, 108, 56))
    d.line([0.04 * w, gy + 13, 0.24 * w, gy + 13], fill=(238, 234, 222),
           width=2)
    scene_tag(d, 8, h - 25, "NO DEAL ADOPTED")
    return img


def hero_radar(w, h):
    img = vgrad(w, h, (22, 30, 62), (196, 108, 54))
    d = ImageDraw.Draw(img)
    # sea band along the bottom
    d.rectangle([0, h * 0.78, w, h], fill=(18, 52, 66))
    for i in range(6):
        wx = (0.05 + 0.16 * i) * w
        d.arc([wx, h * 0.88 - 3, wx + 13, h * 0.88 + 4], 0, 180,
              fill=(110, 190, 215), width=2)
    base = h * 0.78
    # shore installations
    d.rectangle([0.05 * w, base - 12, 0.30 * w, base], fill=(30, 32, 40))
    d.rectangle([0.68 * w, base - 10, 0.95 * w, base], fill=(30, 32, 40))
    # radar dish on its mast, left
    mx = 0.15 * w
    d.line([mx, base - 12, mx, base - 32], fill=(226, 229, 236), width=3)
    d.arc([mx - 14, base - 50, mx + 16, base - 20], 300, 120,
          fill=(238, 240, 244), width=3)
    d.line([mx + 2, base - 35, mx + 20, base - 42], fill=RED, width=2)
    # claim arcs sweeping the dusk
    for off in (0, 7, 14):
        d.arc([0.20 * w, 12 + off, 0.90 * w, h * 0.92 + off], 200, 320,
              fill=(246, 186, 100), width=1)
    # the fire at the civilian site, centre
    burst2(d, 0.50 * w, base - 13, 12)
    d.rectangle([0.44 * w, base - 7, 0.56 * w, base], fill=(52, 42, 34))
    # Bahrain's shield of denial, right: white with a red serrated edge
    sx, sy = 0.83 * w, h * 0.34
    d.polygon([(sx - 10, sy - 11), (sx + 10, sy - 11), (sx + 10, sy + 3),
               (sx, sy + 13), (sx - 10, sy + 3)], fill=(240, 240, 240))
    for k in range(4):
        zx = sx - 10 + k * 5
        d.polygon([(zx, sy - 11), (zx + 5, sy - 11), (zx, sy - 5)],
                  fill=(178, 30, 40))
    d.line([sx - 5, sy + 1, sx + 5, sy + 8], fill=(178, 30, 40), width=2)
    d.line([sx + 5, sy + 1, sx - 5, sy + 8], fill=(178, 30, 40), width=2)
    scene_tag(d, 8, h - 25, "2 RADARS CLAIMED")
    return img


HERO_SCENES = {"drones": hero_drones, "cop": hero_cop, "radar": hero_radar}

# ------------------------------------------------------------------ card scenes
# Compact full-colour illustrations, one per pictured card.


def card_vote(w, h):
    img = vgrad(w, h, (74, 52, 110), (116, 84, 156))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    d.rectangle([cx - 23, cy + 2, cx + 23, cy + 15], fill=(228, 202, 150))
    d.rectangle([cx - 12, cy + 5, cx + 12, cy + 7], fill=(40, 32, 24))
    d.polygon([(cx - 9, cy - 13), (cx + 9, cy - 13), (cx + 5, cy + 3),
               (cx - 5, cy + 3)], fill=(247, 245, 238))
    d.line([cx - 4, cy - 7, cx - 1, cy - 3], fill=(30, 150, 76), width=2)
    d.line([cx - 1, cy - 3, cx + 5, cy - 10], fill=(30, 150, 76), width=2)
    d.text((6, cy - 7), "98.79%", font=font(SANS_BOLD, 10),
           fill=(255, 226, 150))
    return img


def card_cricket(w, h):
    img = vgrad(w, h, (22, 88, 42), (54, 142, 74))
    d = ImageDraw.Draw(img)
    cy = h / 2
    d.polygon([(0.42 * w, h), (0.52 * w, 0), (0.62 * w, 0), (0.56 * w, h)],
              fill=(226, 204, 158))
    for fx in (0.80, 0.845, 0.89):
        gx = fx * w
        d.line([gx, cy - 5, gx, cy + 11], fill=(242, 224, 164), width=2)
    d.line([0.80 * w, cy - 6, 0.845 * w, cy - 6], fill=(242, 224, 164),
           width=2)
    d.polygon([(0.14 * w, cy + 14), (0.28 * w, cy - 3), (0.34 * w, cy + 1),
               (0.20 * w, cy + 16)], fill=(228, 202, 150))
    d.line([0.28 * w, cy - 3, 0.36 * w, cy - 9], fill=(120, 84, 44),
           width=3)
    d.ellipse([0.68 * w, cy - 7, 0.68 * w + 7, cy], fill=(204, 42, 42))
    d.text((8, 2), "720/9", font=font(SANS_BOLD, 12),
           fill=(247, 243, 235))
    return img


def card_f1(w, h):
    img = vgrad(w, h, (12, 14, 28), (44, 32, 66))
    d = ImageDraw.Draw(img)
    base = h - 4
    for i, col in enumerate([(255, 120, 180), GOLD, (120, 200, 255),
                             (255, 120, 180), GOLD]):
        nx = (0.24 + 0.05 * i) * w
        d.ellipse([nx, 4, nx + 3, 7], fill=col)
    d.polygon([(0.08 * w, base - 6), (0.32 * w, base - 6),
               (0.40 * w, base - 13), (0.60 * w, base - 13),
               (0.68 * w, base - 6), (0.90 * w, base - 6),
               (0.90 * w, base - 2), (0.08 * w, base - 2)], fill=RED)
    d.rectangle([0.04 * w, base - 10, 0.12 * w, base - 2], fill=(70, 74, 86))
    d.rectangle([0.86 * w, base - 14, 0.92 * w, base - 2], fill=(70, 74, 86))
    for fx in (0.22, 0.76):
        cx = fx * w
        d.ellipse([cx - 6, base - 8, cx + 6, base + 2], fill=(8, 8, 10),
                  outline=(205, 205, 210), width=1)
    fx0, fy0 = 0.05 * w, 5
    d.line([fx0, fy0, fx0, fy0 + 13], fill=(232, 232, 232), width=2)
    for r in range(2):
        for c in range(3):
            d.rectangle([fx0 + 2 + c * 5, fy0 + r * 5, fx0 + 7 + c * 5,
                         fy0 + 5 + r * 5],
                        fill=(242, 242, 242) if (r + c) % 2 else (18, 18, 18))
    return img


def card_nba(w, h):
    img = vgrad(w, h, (150, 70, 20), (196, 104, 42))
    d = ImageDraw.Draw(img)
    d.line([0, h - 6, w, h - 6], fill=(120, 56, 16), width=2)
    d.arc([w * 0.28, h - 15, w * 0.68, h + 7], 180, 360,
          fill=(255, 214, 160), width=1)
    cx, cy = 0.70 * w, h * 0.66
    d.rectangle([cx - 15, cy - 9, cx + 15, cy + 4], outline=(245, 245, 245),
                width=2)
    d.rectangle([cx - 7, cy - 4, cx + 7, cy + 4], outline=(255, 150, 60),
                width=1)
    d.line([cx - 8, cy + 5, cx + 8, cy + 5], fill=(255, 150, 60), width=2)
    for k in range(4):
        d.line([cx - 8 + k * 5, cy + 5, cx - 5 + k * 4, cy + 12],
               fill=(235, 235, 235), width=1)
    d.ellipse([cx - 5, cy - 1, cx + 5, cy + 9], fill=(226, 112, 40))
    d.text((0.08 * w, h * 0.16), "50", font=font(SANS_BOLD, 21),
           fill=(255, 224, 170))
    d.text((0.08 * w, h * 0.16 + 22), "POINTS", font=font(SANS_BOLD, 8),
           fill=(255, 224, 170))
    return img


def card_ship(w, h):
    img = vgrad(w, h, (16, 50, 74), (32, 92, 112))
    d = ImageDraw.Draw(img)
    keel = h * 0.72
    for i in range(3):
        r = 4 + i * 3
        sx = 0.42 * w + i * 6
        d.ellipse([sx - r, 1 + i * 3, sx + r, 1 + i * 3 + r],
                  fill=(120, 124, 128))
    d.polygon([(0.06 * w, keel), (0.92 * w, keel), (0.86 * w, keel + 8),
               (0.12 * w, keel + 8)], fill=(96, 104, 114))
    for i, fx in enumerate((0.58, 0.68, 0.78)):
        d.rectangle([fx * w, keel - 8, fx * w + 12, keel],
                    fill=(150, 96, 62) if i != 1 else (74, 116, 136))
    d.rectangle([0.14 * w, keel - 11, 0.24 * w, keel], fill=(110, 118, 128))
    burst2(d, 0.40 * w, keel - 7, 8)
    hx, hy = 0.26 * w, h * 0.18
    d.ellipse([hx - 9, hy - 3, hx + 9, hy + 4], fill=(206, 210, 216))
    d.line([hx - 14, hy - 6, hx + 14, hy - 6], fill=(232, 234, 238), width=2)
    d.polygon([(hx - 2, hy + 4), (0.38 * w, keel - 10), (0.48 * w, keel - 10)],
              fill=(120, 130, 148))
    return img


def card_power(w, h):
    img = vgrad(w, h, (26, 24, 48), (54, 46, 84))
    d = ImageDraw.Draw(img)
    px = 0.30 * w
    d.line([px - 9, h, px, 3], fill=(176, 181, 191), width=2)
    d.line([px + 9, h, px, 3], fill=(176, 181, 191), width=2)
    d.line([px - 13, 8, px + 13, 8], fill=(176, 181, 191), width=2)
    d.line([px - 10, 14, px + 10, 14], fill=(176, 181, 191), width=2)
    d.arc([px + 8, 1, w + 10, 19], 90, 170, fill=(126, 130, 140), width=1)
    bx = 0.50 * w
    d.polygon([(bx + 5, 2), (bx - 3, h * 0.52), (bx + 2, h * 0.52),
               (bx - 4, h - 3), (bx + 8, h * 0.42), (bx + 3, h * 0.42)],
              fill=GOLD)
    for i, fx in enumerate((0.68, 0.86)):
        hx = fx * w
        d.rectangle([hx, h - 11, hx + 14, h], fill=(10, 10, 14))
        d.polygon([(hx - 2, h - 11), (hx + 7, h - 16), (hx + 16, h - 11)],
                  fill=(10, 10, 14))
        if i == 0:
            d.rectangle([hx + 5, h - 8, hx + 9, h - 4], fill=GOLD)
    return img


def card_icu(w, h):
    img = vgrad(w, h, (240, 244, 238), (212, 230, 218))
    d = ImageDraw.Draw(img)
    cy = h / 2
    cx = 0.20 * w
    d.rectangle([cx - 4, cy - 12, cx + 4, cy + 12], fill=RED)
    d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=RED)
    pts = [(0.42 * w, cy), (0.55 * w, cy), (0.59 * w, cy - 8),
           (0.64 * w, cy + 6), (0.68 * w, cy), (0.97 * w, cy)]
    d.line(pts, fill=(26, 138, 72), width=2)
    return img


def card_cyber(w, h):
    img = vgrad(w, h, (14, 22, 40), (26, 48, 76))
    d = ImageDraw.Draw(img)
    cy = h / 2
    cx = 0.32 * w
    d.ellipse([cx - 13, cy - 13, cx + 13, cy - 6], outline=(110, 196, 220),
              width=2)
    d.line([cx - 13, cy - 10, cx - 13, cy + 10], fill=(110, 196, 220),
           width=2)
    d.line([cx + 13, cy - 10, cx + 13, cy + 10], fill=(110, 196, 220),
           width=2)
    d.arc([cx - 13, cy + 3, cx + 13, cy + 13], 0, 180,
          fill=(110, 196, 220), width=2)
    mx, my = 0.56 * w, cy + 6
    d.ellipse([mx - 10, my - 10, mx + 10, my + 10], outline=GOLD, width=3)
    d.line([mx + 7, my + 7, mx + 13, my + 12], fill=GOLD, width=3)
    d.line([mx - 5, my - 5, mx + 1, my + 1], fill=RED, width=2)
    d.line([mx + 1, my + 1, mx - 2, my + 6], fill=RED, width=2)
    return img


def card_strike(w, h):
    img = vgrad(w, h, (66, 76, 94), (112, 122, 140))
    d = ImageDraw.Draw(img)
    base = h
    d.polygon([(0.08 * w, base - 8), (0.60 * w, base - 8),
               (0.68 * w, base - 13), (0.68 * w, base - 4),
               (0.08 * w, base - 4)], fill=(216, 220, 226))
    d.polygon([(0.10 * w, base - 8), (0.16 * w, base - 20),
               (0.22 * w, base - 8)], fill=RED)
    for i in range(5):
        d.ellipse([(0.28 + 0.06 * i) * w, base - 11,
                   (0.30 + 0.06 * i) * w, base - 8], fill=(38, 58, 88))
    sx = 0.84 * w
    d.line([sx, base - 13, sx, base], fill=(120, 84, 44), width=2)
    d.rectangle([sx - 10, base - 21, sx + 10, base - 13],
                fill=(247, 245, 238))
    d.text((sx - 8, base - 20), "STOP", font=font(SANS_BOLD, 7), fill=RED)
    return img


def card_liquor(w, h):
    img = vgrad(w, h, (52, 40, 26), (88, 66, 38))
    d = ImageDraw.Draw(img)
    base = h
    for fx in (0.14, 0.28):
        bx = fx * w
        d.rectangle([bx, base - 20, bx + 9, base], fill=(62, 96, 52))
        d.rectangle([bx + 3, base - 25, bx + 6, base - 20], fill=(62, 96, 52))
        d.rectangle([bx + 1, base - 13, bx + 8, base - 7],
                    fill=(232, 220, 180))
    bx = 0.44 * w
    d.rectangle([bx, base - 8, bx + 20, base], fill=(62, 96, 52))
    tx, ty = 0.76 * w, h * 0.68
    d.polygon([(tx, ty - 8), (tx - 9, ty + 8), (tx + 9, ty + 8)],
              outline=GOLD, width=2)
    d.text((tx - 2, ty - 3), "!", font=font(SANS_BOLD, 11), fill=GOLD)
    return img


def card_factory(w, h):
    img = vgrad(w, h, (56, 32, 26), (100, 54, 38))
    d = ImageDraw.Draw(img)
    floor_y = h
    d.rectangle([0.06 * w, floor_y - 14, 0.60 * w, floor_y], fill=(24, 18, 16))
    d.polygon([(0.06 * w, floor_y - 14), (0.22 * w, floor_y - 20),
               (0.33 * w, floor_y - 15), (0.44 * w, floor_y - 21),
               (0.60 * w, floor_y - 14)], fill=(24, 18, 16))
    for fx, fh in [(0.26, 0.30), (0.37, 0.44), (0.49, 0.26)]:
        cx = fx * w
        d.polygon([(cx - 5, floor_y - 15), (cx, floor_y - 15 - fh * h),
                   (cx + 5, floor_y - 15)], fill=ORANGE)
        d.polygon([(cx - 2, floor_y - 15),
                   (cx, floor_y - 15 - fh * h * 0.55),
                   (cx + 2, floor_y - 15)], fill=GOLD)
    for fx, fh in ((0.63, 18), (0.73, 15)):
        d.rectangle([fx * w, floor_y - fh, fx * w + 6, floor_y],
                    fill=(24, 18, 16))
    ex = 0.64 * w
    d.rectangle([ex, floor_y - 7, ex + 22, floor_y - 1], fill=(158, 42, 30))
    d.rectangle([ex + 15, floor_y - 11, ex + 22, floor_y - 7],
                fill=(158, 42, 30))
    for fx in (0.70, 0.86):
        cx = fx * w
        d.ellipse([cx - 3, floor_y - 4, cx + 3, floor_y + 1],
                  fill=(10, 10, 10))
    return img


def card_quake(w, h):
    img = vgrad(w, h, (242, 238, 226), (228, 220, 200))
    d = ImageDraw.Draw(img)
    mid_y = h * 0.44
    trace = [(0.03 * w, mid_y), (0.30 * w, mid_y), (0.36 * w, mid_y - 7),
             (0.42 * w, mid_y + 8), (0.48 * w, mid_y - 8),
             (0.54 * w, mid_y + 5), (0.60 * w, mid_y - 2), (0.97 * w, mid_y)]
    d.line(trace, fill=RED, width=2)
    wall_y = h * 0.68
    for row in range(3):
        ry = wall_y + row * 5
        d.line([0.08 * w, ry, 0.92 * w, ry], fill=(170, 122, 98), width=2)
        for col in range(4):
            vx = (0.16 + 0.20 * col + (0.10 if row % 2 else 0.0)) * w
            d.line([vx, ry, vx, ry + 5], fill=(170, 122, 98), width=1)
    crack = [(0.44 * w, wall_y - 2), (0.50 * w, wall_y + 4),
             (0.47 * w, wall_y + 8), (0.55 * w, wall_y + 12)]
    d.line(crack, fill=(16, 12, 10), width=3)
    return img


CARD_SCENES = {
    "vote": card_vote, "cricket": card_cricket, "f1": card_f1,
    "nba": card_nba, "ship": card_ship, "power": card_power,
    "icu": card_icu, "cyber": card_cyber, "strike": card_strike,
    "liquor": card_liquor, "factory": card_factory, "quake": card_quake,
}

# ------------------------------------------------------------------ page


def render():
    img = Image.new("RGB", (PAGE, PAGE), FRAME)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, PAGE - 8, PAGE - 8], fill=PAPER)

    # ---- masthead
    d.rectangle([EDGE, 22, EDGE + 9, 31], fill=RED)
    d.text((EDGE + 14, 19), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=font(SANS_BOLD, 15), fill=RED)
    total = (f"{STORY_COUNT} STORIES · 7 REGIONS · {FIELDS} FIELDS · "
             f"EVERY ONE FROM THIS SUNDAY")
    rf = font(SANS, 10)
    d.text((PAGE - EDGE - d.textlength(total, font=rf), 23), total,
           font=rf, fill=INK)
    d.line([EDGE, 42, PAGE - EDGE, 42], fill=INK, width=1)
    d.line([EDGE, 45, PAGE - EDGE, 45], fill=INK, width=3)

    # ---- date and dek
    middle(d, PAGE / 2, 52, DAY, font(SERIF_BOLD, 56), INK)
    middle(d, PAGE / 2, 118, DEK, font(SERIF_ITALIC, 16), RED)
    d.line([EDGE, 140, PAGE - EDGE, 140], fill=INK, width=1)

    # ---- the day in UTC: red label, six slots
    d.rectangle([EDGE, 146, EDGE + 66, 182], fill=RED)
    middle(d, EDGE + 33, 152, "THE DAY", font(SANS_BOLD, 10),
           (255, 255, 255))
    middle(d, EDGE + 33, 165, "IN UTC", font(SANS_BOLD, 10),
           (255, 255, 255))
    slot_x = EDGE + 74
    slot_w = (PAGE - EDGE - slot_x) / 6
    for i, (tm, what) in enumerate(TIMELINE_SLOTS):
        sx = slot_x + i * slot_w
        d.text((sx + 6, 149), tm, font=font(SANS_BOLD, 12), fill=RED)
        fit(d, sx + 6, 166, what, SANS, 9, slot_w - 10, INK, floor=7)
        if i:
            d.line([sx, 150, sx, 178], fill=RULE_SOFT, width=1)
    d.line([EDGE, 186, PAGE - EDGE, 186], fill=INK, width=1)

    # ---- the day in numbers
    d.text((EDGE, 192), "THE DAY IN NUMBERS", font=font(SANS_BOLD, 10),
           fill=RED)
    cell = SPAN / 6
    for i, (fig, cap1, cap2) in enumerate(NUMBERS2):
        cx = EDGE + cell * i + cell / 2
        middle(d, cx, 206, fig, font(SERIF_BOLD, 27), INK)
        middle(d, cx, 240, cap1, font(SANS, 9), FAINT)
        middle(d, cx, 251, cap2, font(SANS, 9), FAINT)
        if i:
            d.line([EDGE + cell * i, 208, EDGE + cell * i, 258],
                   fill=RULE_SOFT, width=1)
    d.line([EDGE, 264, PAGE - EDGE, 264], fill=INK, width=1)

    # ---- region tabs, counts computed from the story list
    tf = font(SANS_BOLD, 12)
    labels = [(r, f"{r.upper()} {REGION_TALLY[r]}") for r in TAB_ORDER]
    widths = [d.textlength(t, font=tf) + 20 for _r, t in labels]
    gap = (SPAN - sum(widths)) / (len(labels) - 1)
    tx = float(EDGE)
    for (r, t), tw in zip(labels, widths):
        d.rectangle([tx, 270, tx + tw, 292], fill=TAB_INK[r])
        middle(d, tx + tw / 2, 275, t, tf, (255, 255, 255))
        tx += tw + gap

    # ---- heroes: rich scenes, badge, tag, pill, headline, summary
    hero_w = 309
    for i, hero in enumerate(HEROES):
        hx = EDGE + i * (hero_w + 10)
        img.paste(HERO_SCENES[hero["scene"]](hero_w, 100), (hx, 300))
        badge(d, hx + 10, 414, hero["num"], r=10)
        pill(d, hx + hero_w, 406, HERO_PILL[hero["num"]],
             PILL_INK[hero["cert"]], size=9, h=15)
        pw = d.textlength(HERO_PILL[hero["num"]], font=font(SANS_BOLD, 9))
        fit(d, hx + 26, 407, hero["tag"], SANS_BOLD, 10,
            hero_w - 26 - pw - 20, RED, floor=8)
        block(d, hx, 428, hero["head"], font(SERIF_BOLD, 24), INK,
              hero_w, 26, cap=2)
        block(d, hx, 484, hero["summ"], font(SERIF, 12), INK,
              hero_w, 15, cap=3)
    d.line([EDGE, 534, PAGE - EDGE, 534], fill=INK, width=1)

    # ---- pictured cards, two rows of six
    card_w = 151
    for i, card in enumerate(CARDS):
        cx0 = EDGE + (i % 6) * (card_w + 8)
        cy0 = 542 + (i // 6) * 121
        img.paste(CARD_SCENES[card["scene"]](card_w, 38), (cx0, cy0))
        pill(d, cx0 + card_w - 3, cy0 + 3, card["cert"],
             PILL_INK[card["cert"]], size=8, h=13)
        d.rectangle([cx0, cy0 + 43, cx0 + 7, cy0 + 50],
                    fill=TAB_INK[card["region"]])
        fit(d, cx0 + 11, cy0 + 42, card["place"], SANS_BOLD, 9,
            card_w - 11, RED, floor=7)
        block(d, cx0, cy0 + 55, card["head"], font(SERIF_BOLD, 14), INK,
              card_w, 16, cap=2)
        block(d, cx0, cy0 + 88, card["summ"], font(SERIF, 11), INK,
              card_w, 13, cap=2)

    # ---- bottom band: coloured map left, briefs right
    by = 786
    d.text((EDGE, by), "WHERE IT HAPPENED", font=font(SANS_BOLD, 12),
           fill=INK)
    map_x, map_y = EDGE, by + 18
    pitch_x, pitch_y = 4.0, 3.6
    map_w = len(WORLD[0]) * pitch_x
    map_h = len(WORLD) * pitch_y
    d.rectangle([map_x - 5, map_y - 5, map_x + map_w + 5,
                 map_y + map_h + 5], fill=SEA)
    for ri, row in enumerate(WORLD):
        for ci, ch in enumerate(row):
            if ch == "#":
                cxp = map_x + ci * pitch_x + pitch_x / 2
                cyp = map_y + ri * pitch_y + pitch_y / 2
                tone = LAND_DEEP if (ri + ci) % 7 == 0 else LAND
                d.rectangle([cxp - pitch_x / 2 + 0.4,
                             cyp - pitch_y / 2 + 0.4,
                             cxp + pitch_x / 2 - 0.4,
                             cyp + pitch_y / 2 - 0.4], fill=tone)
    for num, (fx, fy) in PINS.items():
        pin2(d, map_x + fx * map_w, map_y + fy * map_h, num, r=7)
    # region legend under the map, coloured squares + computed counts
    lf = font(SANS, 9)
    for li, group in enumerate((TAB_ORDER[:3], TAB_ORDER[3:])):
        lx = float(EDGE)
        ly = map_y + map_h + 7 + li * 11
        for r in group:
            d.rectangle([lx, ly + 1, lx + 7, ly + 8], fill=TAB_INK[r])
            t = f"{REGION_SHORT[r]} {REGION_TALLY[r]}"
            d.text((lx + 10, ly), t, font=lf, fill=INK)
            lx += 10 + d.textlength(t, font=lf) + 13

    bx = 404
    d.text((bx, by), f"ALSO ON SUNDAY — {len(BRIEFS)} MORE STORIES",
           font=font(SANS_BOLD, 12), fill=INK)
    bf = font(SANS_BOLD, 8)
    col_w = 284
    for i, (num, text, _region) in enumerate(BRIEFS):
        col, row_i = divmod(i, 11)
        x0 = bx + col * (col_w + 12)
        y0 = by + 18 + row_i * 14.0
        d.rectangle([x0, y0 + 1, x0 + 15, y0 + 13], fill=RED)
        label = str(num)
        box = d.textbbox((0, 0), label, font=bf)
        d.text((x0 + 7.5 - (box[2] - box[0]) / 2 - box[0], y0 + 3),
               label, font=bf, fill=(255, 255, 255))
        fit(d, x0 + 19, y0 + 2, text, SANS, 10, col_w - 19, INK, floor=8)

    # ---- footer: dating line left, certainty key right
    d.text((EDGE, 964),
           "Every story happened, or was first reported, on Sunday "
           "22 November 2026.", font=font(SANS, 9), fill=FAINT)
    key = "REPORTED wires · CLAIM one side · FORECAST to come"
    kf = font(SANS_BOLD, 9)
    d.text((PAGE - EDGE - d.textlength(key, font=kf), 964), key,
           font=kf, fill=INK)

    # ---- date-check box
    box_y = 977
    d.rectangle([EDGE, box_y, PAGE - EDGE, box_y + 32],
                fill=(250, 238, 231), outline=RED, width=2)
    block(d, EDGE + 16, box_y + 6, DATE_CHECK, font(SERIF, 11), DEEP_RED,
          SPAN - 32, 12, cap=2)

    return grain(img)


def build(out_path):
    render().save(out_path, format="PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(os.path.dirname(here), "entry-v2.png")
    out = sys.argv[1] if len(sys.argv) > 1 else default
    print(build(out), os.path.getsize(out))
