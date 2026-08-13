"""Draw a day's one-sheet.

1200×2600, phone proportions, type sized to be read at arm's length.

Anatomy, top to bottom — blocks appear only when the day has something to put
in them, so one code path covers the morning plan, a midday update and the
stamped close:

    band header      kicker · weekday · date · 6-segment legend stripe
    scoreboard       4 macro bars vs target        (once anything is eaten)
    receipt          what went in, with a total    (once anything is eaten)
    on-deck cards    what is still coming          (while anything is planned)
    notes card       the day's lines               (final sheets)
    band footer      day total · target · story · footnote

The scoreboard/receipt pair and the on-deck cards are the two halves of the
day; a plan sheet is all cards, a final sheet is all receipt, and an update
sheet is both.
"""

import os

from PIL import Image, ImageDraw, ImageFont

import entry as E

W, H = 1200, 2600
MARGIN = 56

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Vertical rhythm
BLOCK_GAP = 28
CARD_GAP = 20
RECEIPT_CAPTION = 26      # caption baseline below the block above
RECEIPT_TOP = 70          # receipt card top below the block above
FOOTER_MIN = 246

BAR_PITCH = 116           # one macro row: label, value, bar
SCOREBOARD_PAD = 104 + 120  # header row above the bars, and the tail below


def scoreboard_h(bar_pitch):
    return SCOREBOARD_PAD + bar_pitch * 3

FOOTER_MAX = 420
CARD_MIN_H = 190

# Nominal pitch, the floor it may be squeezed to on a long day, and the ceiling
# it may open up to on a short one. Type size follows the nominal, never the
# stretch: a sparse day breathes, it does not shout.
ROW_PITCH, ROW_PITCH_MIN, ROW_PITCH_MAXOUT = 60, 42, 96
NOTE_PITCH, NOTE_PITCH_MIN, NOTE_PITCH_MAXOUT = 78, 58, 110

NOMINAL = {
    "gap_top": BLOCK_GAP,
    "bar_pitch": BAR_PITCH,
    "receipt_top": RECEIPT_TOP,
    "row_pitch": ROW_PITCH,
    "notes_gap": RECEIPT_CAPTION,
    "note_pitch": NOTE_PITCH,
    "footer_gap": 24,
}
# How far each knob may open up when the day is short. Applied together, scaled
# by one factor, so the whole sheet loosens evenly instead of one block
# ballooning.
STRETCH = {
    "gap_top": 44,
    "bar_pitch": 168,
    "receipt_top": 92,
    "row_pitch": ROW_PITCH_MAXOUT,
    "notes_gap": 46,
    "note_pitch": NOTE_PITCH_MAXOUT,
    "footer_gap": 44,
}
# How many times each knob repeats down the page, for the stretch solve.
REPEATS = {"bar_pitch": 3}


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def bs(s):
    return _font("BigShoulders-Bold.ttf", s)


def ws(s):
    return _font("WorkSans-Regular.ttf", s)


def wsb(s):
    return _font("WorkSans-Bold.ttf", s)


def gm(s):
    return _font("GeistMono-Regular.ttf", s)


def gmb(s):
    return _font("GeistMono-Bold.ttf", s)


# ---------------------------------------------------------------- primitives

def tracked(d, xy, text, font, fill, tracking=0, anchor="la"):
    """Letter-spaced text. Returns the width drawn."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(len(text) - 1, 0)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill, anchor="l" + anchor[1])
        x += w + tracking
    return total


def tracked_width(d, text, font, tracking=0):
    return sum(d.textlength(ch, font=font) for ch in text) + tracking * max(len(text) - 1, 0)


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for word in words:
        t = (cur + " " + word).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, maker, maxw, size, floor):
    """Largest font at or below `size` that keeps `text` inside `maxw`."""
    while size > floor and d.textlength(text, font=maker(size)) > maxw:
        size -= 1
    return maker(size)


def ellipsize(d, text, font, maxw, tracking=0):
    if tracked_width(d, text, font, tracking) <= maxw:
        return text
    while text and tracked_width(d, text + "…", font, tracking) > maxw:
        text = text[:-1]
    return text.rstrip(" ,·—-") + "…"


def tint(color, base, a=0.12):
    return tuple(int(base[i] * (1 - a) + color[i] * a) for i in range(3))


def _num(n):
    return "{:,}".format(int(n))


# ------------------------------------------------------------------- layout

def _measure(e, k, header_h, notes):
    """Stack the fixed blocks top-down for one set of knob values."""
    eaten, ondeck = e["eaten"], e["ondeck"]
    blocks = {}
    y = header_h + k["gap_top"]

    if eaten:
        sb_h = scoreboard_h(k["bar_pitch"])
        blocks["scoreboard"] = (y, sb_h)
        y += sb_h
        receipt_h = 34 + k["row_pitch"] * len(eaten) + 22 + 56
        blocks["receipt"] = (y + k["receipt_top"], receipt_h)
        y += k["receipt_top"] + receipt_h

    notes_h = 88 + k["note_pitch"] * len(notes) + 60 if notes else 0

    if ondeck:
        # Cards absorb the slack; the footer stays at its minimum.
        footer_y = H - FOOTER_MIN
        cards_bottom = footer_y - BLOCK_GAP
        if notes:
            notes_top = cards_bottom - notes_h
            blocks["notes"] = (notes_top, notes_h)
            cards_bottom = notes_top - k["notes_gap"]
        cards_top = y + (k["gap_top"] if eaten else 0)
        n = len(ondeck)
        card_h = (cards_bottom - cards_top - CARD_GAP * (n - 1)) / float(n)
    else:
        cards_top, card_h = None, 0
        if notes:
            notes_top = y + k["notes_gap"]
            blocks["notes"] = (notes_top, notes_h)
            y = notes_top + notes_h
        footer_y = y + k["footer_gap"]

    return blocks, cards_top, card_h, footer_y


def _plan(e):
    """Decide every block height before drawing a single pixel.

    Three passes: measure at nominal pitch, squeeze if the day runs long,
    loosen if it runs short. A day with the reference shape — ten items, four
    notes — comes out at the nominal values and is left alone.
    """
    final = e["status"] == "final"
    notes = e["notes"] if final else []
    header_h = 320 if final else 372
    k = dict(NOMINAL)

    def fits(k):
        _, _, card_h, footer_y = _measure(e, k, header_h, notes)
        if e["ondeck"]:
            return card_h >= CARD_MIN_H
        return footer_y <= H - FOOTER_MIN

    # Squeeze: walk the pitches down toward their floors until the page holds.
    while not fits(k):
        if k["row_pitch"] > ROW_PITCH_MIN and e["eaten"]:
            k["row_pitch"] -= 1
        elif k["note_pitch"] > NOTE_PITCH_MIN and notes:
            k["note_pitch"] -= 1
        else:
            break  # a genuinely oversized day; draw it and let the eye judge

    # Loosen: if the footer would swallow more than its share, spend the excess
    # on the stack instead — one factor across every knob.
    if not e["ondeck"]:
        _, _, _, footer_y = _measure(e, k, header_h, notes)
        excess = (H - footer_y) - FOOTER_MAX
        if excess > 0:
            counts = dict(REPEATS)
            counts["row_pitch"] = len(e["eaten"])
            counts["note_pitch"] = len(notes)
            room = sum(
                max(STRETCH[key] - k[key], 0) * counts.get(key, 1) for key in STRETCH
            )
            if room > 0:
                t = min(1.0, excess / float(room))
                for key in STRETCH:
                    k[key] = k[key] + int(round(max(STRETCH[key] - k[key], 0) * t))

    blocks, cards_top, card_h, footer_y = _measure(e, k, header_h, notes)
    return {
        "final": final,
        "header_h": header_h,
        "blocks": blocks,
        "bar_pitch": k["bar_pitch"],
        "row_pitch": k["row_pitch"],
        "row_size": max(22, min(30, int(round(min(k["row_pitch"], ROW_PITCH) * 0.5)))),
        "note_pitch": k["note_pitch"],
        "note_size": max(24, min(31, int(round(min(k["note_pitch"], NOTE_PITCH) * 0.4)))),
        "cards_top": cards_top,
        "card_h": card_h,
        "footer_y": footer_y,
    }


# -------------------------------------------------------------------- blocks

def _header(d, e, s, L):
    final = L["final"]
    h = L["header_h"]
    d.rectangle([0, 0, W, h], fill=s["band"])

    kicker = "DAILY MENU · DAY %d" % e["day"]
    if final:
        kicker += " FINAL"
    elif e["status"] == "open":
        kicker += " · UPDATE"
    tracked(d, (MARGIN, 66 if final else 72), kicker, gm(26), s["band_text"], tracking=6)
    tracked(d, (W - MARGIN, 66 if final else 72), "LUKE", gmb(26), s["band_text"],
            tracking=7, anchor="ra")

    badge = "FINAL" if final else ("UPDATE" if e["status"] == "open" else None)
    day = e["weekday"].upper()
    name_size = 140 if final else 158
    if badge:
        # Keep the day name clear of the badge box.
        avail = W - MARGIN - 30 - (tracked_width(d, badge, bs(64), 6) + 52) - MARGIN - 24
        while name_size > 96 and d.textlength(day, font=bs(name_size)) > avail:
            name_size -= 2
    d.text((MARGIN - 5, 104 if final else 112), day, font=bs(name_size),
           fill=s["band_text"], anchor="la")

    date_line = _date_words(e["date"])
    if final:
        date_line += " — FINAL"
    tracked(d, (MARGIN, 262 if final else 306), date_line, gm(31 if final else 33),
            s["band_sub"], tracking=5)

    if badge:
        by = 168 if final else 176
        bw = tracked(d, (W - MARGIN - 30, by), badge, bs(64), s["band_text"],
                     tracking=6, anchor="ra")
        d.rectangle([W - MARGIN - 30 - bw - 26, by - 16, W - MARGIN - 30 + 26, by + 74],
                    outline=s["band_text"], width=4)

    seg = W / 6.0
    for i, c in enumerate(s["accents"][:6]):
        d.rectangle([round(i * seg), h - 14, round((i + 1) * seg) + 1, h], fill=c)


def _date_words(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%B").upper(), d.day, d.year)


def _scoreboard(d, e, s, L):
    y0, h = L["blocks"]["scoreboard"]
    y1 = y0 + h
    final = L["final"]
    d.rounded_rectangle([MARGIN, y0, W - MARGIN, y1], radius=18, fill=s["card"])
    bx = MARGIN + 40
    bw = (W - MARGIN - 40) - bx

    tracked(d, (bx, y0 + 38), "FINAL VS TARGET" if final else "TODAY VS TARGET",
            gmb(25), s["ink"], tracking=7)
    tracked(d, (W - MARGIN - 40, y0 + 38), "DAY CLOSED" if final else "IN PROGRESS",
            gm(23), s["faint"], tracking=4, anchor="ra")

    rows = [("CALORIES", "cal"), ("PROTEIN", "p"), ("FAT", "f"), ("CARBS", "c")]
    ry = y0 + 104
    for label, macro in rows:
        got, target, frac, warn = E.bar(e, macro)
        note = E.caption(e, macro)
        wcol = s["amber"] if warn == "amber" else s["red"] if warn == "red" else s["faint"]
        wfont = gmb(21) if warn else gm(21)
        lw = tracked(d, (bx, ry), label, gm(24), s["mute"], tracking=5)
        tracked(d, (bx + lw + 26, ry + 2), "· " + note, wfont, wcol, tracking=3)

        if macro == "cal":
            value = "%s / ~%s" % (_num(got), _num(target))
        else:
            value = "%d / %d G" % (got, target)
        d.text((W - MARGIN - 40, ry + 16), value, font=bs(46), fill=s["ink"], anchor="rs")

        by = ry + 40
        d.rounded_rectangle([bx, by, bx + bw, by + 18], radius=9, fill=s["track"])
        fill_c = s["amber"] if warn == "amber" else s["red"] if warn == "red" else s["band"]
        d.rounded_rectangle([bx, by, bx + max(bw * frac, 24), by + 18], radius=9, fill=fill_c)
        ry += L["bar_pitch"]


def _receipt(d, e, s, L):
    y0, h = L["blocks"]["receipt"]
    y1 = y0 + h
    tracked(d, (MARGIN + 6, y0 - 44), "THE FULL DAY" if L["final"] else "EATEN SO FAR",
            gmb(24), s["mute"], tracking=8)
    d.rounded_rectangle([MARGIN, y0, W - MARGIN, y1], radius=16, fill=s["receipt"])

    x0, x1 = MARGIN + 36, W - MARGIN - 36
    name_f, val_f = ws(L["row_size"]), gm(max(20, L["row_size"] - 5))
    ty = y0 + 34
    for it in e["eaten"]:
        value = E.receipt_value(it)
        name = it["receipt"] + (" *" if it["estimated"] else "")
        vw = d.textlength(value, font=val_f)
        d.text((x0, ty), ellipsize(d, name, name_f, x1 - x0 - vw - 40),
               font=name_f, fill=s["grey"], anchor="la")
        d.text((x1, ty + 2), value, font=val_f, fill=s["mute"], anchor="ra")
        ty += L["row_pitch"]

    d.line([x0, ty + 2, x1, ty + 2], fill=s["rule"], width=2)
    label = "DAY %d TOTAL" % e["day"] if L["final"] else "SO FAR"
    d.text((x0, ty + 20), label, font=wsb(L["row_size"]), fill=s["ink"], anchor="la")
    d.text((x1, ty + 22), E.totals_value(e["totals"]),
           font=gmb(max(21, L["row_size"] - 4)), fill=s["ink"], anchor="ra")


def _cards(d, e, s, L):
    top, card_h = L["cards_top"], L["card_h"]
    card_w = W - 2 * MARGIN
    BAR, PAD = 14, 34
    y = top
    for i, it in enumerate(e["ondeck"]):
        color = _card_color(it, it.get("index", i), s)
        x0, y0 = MARGIN, round(y)
        x1, y1 = MARGIN + card_w, round(y + card_h)
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=tint(color, s["card"]))
        d.rounded_rectangle([x0, y0, x0 + BAR + 18, y1], radius=18, fill=color)
        d.rectangle([x0 + BAR, y0, x0 + BAR + 18, y1], fill=tint(color, s["card"]))
        cx = x0 + BAR + PAD
        inner = x1 - PAD - cx
        ch = y1 - y0

        # Type shrinks with the card so eight meals read as well as five.
        chip_s = 24 if ch >= 230 else 21
        title_s = 56 if ch >= 260 else 48 if ch >= 210 else 42
        ing_s = 29 if ch >= 260 else 26
        ing_lines = 2 if ch >= 250 else 1 if ch >= 190 else 0

        chip = (it["at"] or it["slot"] or "NEXT").upper()
        chip_f = gmb(chip_s)
        tw = tracked_width(d, chip, chip_f, 9)
        cy = y0 + 22
        d.rounded_rectangle([cx, cy, cx + tw + 42, cy + chip_s + 20], radius=22, fill=color)
        tracked(d, (cx + 21, cy + (chip_s + 20) / 2), chip, chip_f, s["card"],
                tracking=9, anchor="lm")

        title_y = y0 + chip_s + 52
        title_f = fit(d, it["title"].upper(), bs, inner, title_s, 30)
        d.text((cx, title_y), it["title"].upper(), font=title_f, fill=s["ink"], anchor="la")

        if ing_lines and it["ing"]:
            ing_f = ws(ing_s)
            iy = title_y + title_f.size + 12
            # Never let the ingredient line crowd the macro strip.
            room = int((y1 - 76 - 8 - iy) // (ing_s + 7))
            lines = wrap(d, it["ing"], ing_f, inner)
            show = lines[:max(0, min(ing_lines, room))]
            if show and len(show) < len(lines):
                # Say it was cut rather than trailing off mid-ingredient.
                show[-1] = ellipsize(d, show[-1] + " " + lines[len(show)], ing_f, inner)
            for line in show:
                d.text((cx, iy), line, font=ing_f, fill=s["grey"], anchor="la")
                iy += ing_s + 7

        mv_f, ml_f = bs(56 if ch >= 230 else 46), gmb(22 if ch >= 230 else 19)
        base = y1 - 36
        colw = inner / 4.0
        for j, (lab, val) in enumerate(
            [("CAL", _num(it["cal"])), ("P", str(it["p"])), ("F", str(it["f"])), ("C", str(it["c"]))]
        ):
            vw = d.textlength(val, font=mv_f)
            lw = d.textlength(lab, font=ml_f)
            sx = cx + colw * j + (colw - (vw + 10 + lw)) / 2
            d.text((sx, base), val, font=mv_f, fill=s["ink"], anchor="ls")
            d.text((sx + vw + 10, base - 3), lab, font=ml_f, fill=s["faint"], anchor="ls")
            if j:
                d.line([cx + colw * j, y1 - 76, cx + colw * j, y1 - 26], fill=s["rule"], width=2)
        y = y1 + CARD_GAP


def _card_color(item, index, s):
    c = item.get("color")
    if isinstance(c, int):
        return s["accents"][c % len(s["accents"])]
    if isinstance(c, str) and c.startswith("#") and len(c) == 7:
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return s["accents"][index % len(s["accents"])]


def _notes(d, e, s, L):
    y0, h = L["blocks"]["notes"]
    d.rounded_rectangle([MARGIN, y0, W - MARGIN, y0 + h], radius=16, fill=s["card"])
    nx = MARGIN + 36
    tracked(d, (nx, y0 + 34), "DAY %d NOTES" % e["day"], gmb(24), s["ink"], tracking=7)

    # One size for the whole card — notes are a list, and a list that changes
    # size line to line reads as a mistake. Shrink until the longest one fits.
    maxw = (W - MARGIN - 30) - (nx + 30)
    size = L["note_size"]
    while size > 24 and any(d.textlength(n, font=ws(size)) > maxw for n in e["notes"]):
        size -= 1
    nf = ws(size)

    ny = y0 + 88
    for note in e["notes"]:
        d.ellipse([nx, ny + 12, nx + 12, ny + 24], fill=s["band"])
        d.text((nx + 30, ny), ellipsize(d, note, nf, maxw),
               font=nf, fill=s["grey"], anchor="la")
        ny += L["note_pitch"]


def _footer(d, e, s, L):
    fy = L["footer_y"]
    fh = H - fy
    final = L["final"]
    d.rectangle([0, fy, W, H], fill=s["band"])

    if final:
        kicker = "DAY %d · CLOSED" % e["day"]
    elif e["status"] == "open" and e["ondeck"]:
        # The number below is the day as it will land, not the day so far —
        # say so, or the footer argues with the scoreboard above it.
        kicker = "DAY %d · IF THE PLAN HOLDS" % e["day"]
    elif e["status"] == "open":
        kicker = "DAY %d · IN PROGRESS" % e["day"]
    else:
        kicker = "DAY TOTAL"
    tracked(d, (MARGIN, fy + 40), kicker, gm(25), s["band_faint"], tracking=7)

    totals = e["totals"] if e["eaten"] else e["planned"]
    if e["ondeck"] and e["eaten"]:
        totals = e["planned"]  # an update sheet totals the day as it will land
    big_s = 104 if final else 118
    big = _num(totals["cal"])
    d.text((MARGIN - 4, fy + (70 if final else 72)), big, font=bs(big_s),
           fill=s["band_text"], anchor="la")
    cal_w = d.textlength(big, font=bs(big_s))
    tracked(d, (MARGIN + cal_w + 16, fy + (148 if final else 164)), "CAL", gm(25),
            s["band_faint"], tracking=5)

    rx = W - MARGIN
    d.text((rx, fy + (62 if final else 66)), E.macro_line(totals),
           font=bs(58 if final else 64), fill=s["band_text"], anchor="ra")
    t = e["targets"]
    tracked(d, (rx, fy + (138 if final else 150)),
            "TARGET %d P / %d F / %d C" % (t["p"], t["f"], t["c"]),
            gm(22 if final else 23), s["band_faint"], tracking=3, anchor="ra")

    footnote = (e.get("footnote") or _default_footnote(e)).upper()
    story = (e.get("story") or "").upper()
    fn_y = fy + fh - 40
    story_y = fn_y - 62
    if story and story_y > fy + 190:
        d.line([MARGIN, story_y - 24, W - MARGIN, story_y - 24], fill=s["band_foot"], width=1)
        tracked(d, (MARGIN, story_y),
                ellipsize(d, story, gm(21), W - 2 * MARGIN, tracking=3),
                gm(21), s["band_sub"], tracking=3)
    # If the band is too short for both, the footnote wins — it carries the
    # asterisks and the conventions. The story is a closing-day luxury.
    tracked(d, (MARGIN, fn_y),
            ellipsize(d, footnote, gm(19), W - 2 * MARGIN, tracking=3),
            gm(19), s["band_foot"], tracking=3)


def _default_footnote(e):
    bits = []
    est = [it["receipt"] for it in e["items"] if it["estimated"]]
    if est:
        bits.append("* %s estimated" % (est[0] if len(est) == 1 else "%d items" % len(est)))
    import datetime
    nxt = datetime.date.fromisoformat(e["date"]) + datetime.timedelta(days=1)
    bits.append("see you %s" % nxt.strftime("%A"))
    return " · ".join(bits)


# --------------------------------------------------------------------- draw

def render(e, scheme):
    """Return the finished sheet as a PIL image."""
    L = _plan(e)
    img = Image.new("RGB", (W, H), scheme["paper"])
    d = ImageDraw.Draw(img)

    _header(d, e, scheme, L)
    if "scoreboard" in L["blocks"]:
        _scoreboard(d, e, scheme, L)
    if "receipt" in L["blocks"]:
        _receipt(d, e, scheme, L)
    if e["ondeck"]:
        _cards(d, e, scheme, L)
    if "notes" in L["blocks"]:
        _notes(d, e, scheme, L)
    _footer(d, e, scheme, L)
    return img
