from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 2600
MARGIN = 56
PAPER = (245, 247, 250)
NAVY = (23, 28, 48)
INK = (24, 26, 34)
GREY = (72, 76, 88)
FAINT = (140, 144, 156)

F = "/home/claude/menu/"
def bs(s):  return ImageFont.truetype(F+"BigShoulders-Bold.ttf", s)
def ws(s):  return ImageFont.truetype(F+"WorkSans-Regular.ttf", s)
def gm(s):  return ImageFont.truetype(F+"GeistMono-Regular.ttf", s)
def gmb(s): return ImageFont.truetype(F+"GeistMono-Bold.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def tint(color, a=0.12, base=(255,255,255)):
    return tuple(int(base[i]*(1-a)+color[i]*a) for i in range(3))

def tracked(draw, xy, text, font, fill, tracking=0, anchor="la"):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths)+tracking*(len(text)-1)
    x, y = xy
    if anchor[0]=="m": x -= total/2
    elif anchor[0]=="r": x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="l"+anchor[1])
        x += w+tracking
    return total

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur+" "+w_).strip()
        if draw.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

MEALS = [
    dict(slot="7:00 AM", title="ESPRESSO + BREAKFAST BOWL",
         ing="butter espresso (< 1 tsp) · 1 cup cottage cheese · 1 serving protein oats · blueberries + strawberries · 1 tbsp honey · 1 tbsp cacao nibs",
         color=(108,74,46),  cal="545", p="35", f="15", c="72"),
    dict(slot="~9:00 AM", title="SHAKE Nº1 — TRAIN AROUND IT",
         ing="1 scoop whey + 1 scoop dextrose",
         color=(32,128,206), cal="230", p="26", f="2", c="28"),
    dict(slot="10:00 AM", title="POKE + SWEET POTATO",
         ing="1 lb ahi, the last of it · 300 g roasted sweet potato + 1 tsp olive oil · whole avocado · cucumber",
         color=(199,58,92), cal="1,130", p="110", f="37", c="85"),
    dict(slot="PM", title="SHAKE Nº2 + COCONUT WATER",
         ing="1 scoop whey in water · one C2O with pulp — budgeted this time",
         color=(14,164,178), cal="230", p="28", f="2", c="28"),
    dict(slot="DINNER", title="CHICKEN + ASPARAGUS",
         ing="6 oz chicken breast (raw weight) · 1 bunch asparagus · 2 tbsp olive oil, split",
         color=(16,124,92), cal="460", p="43", f="30", c="7"),
    dict(slot="NIGHT", title="YASSO MINT CHIP BAR",
         ing="1 bar — closes carbs on the number",
         color=(122,72,190), cal="100", p="5", f="2", c="16"),
]

# ---------------- HEADER ----------------
HEADER_H = 372
d.rectangle([0, 0, W, HEADER_H], fill=NAVY)
tracked(d, (MARGIN, 72), "DAILY MENU · DAY 2", gm(26), (255,255,255), tracking=7)
tracked(d, (W-MARGIN, 72), "LUKE", gmb(26), (255,255,255), tracking=7, anchor="ra")
d.text((MARGIN-6, 112), "WEDNESDAY", font=bs(158), fill=(255,255,255), anchor="la")
tracked(d, (MARGIN, 306), "AUGUST 12, 2026", gm(33), (188,194,210), tracking=5)
seg = W/6
for i, m in enumerate(MEALS):
    d.rectangle([round(i*seg), HEADER_H-14, round((i+1)*seg)+1, HEADER_H], fill=m["color"])

# ---------------- MEAL CARDS ----------------
FOOTER_H = 246
top = HEADER_H+28
bottom = H-FOOTER_H-28
GAP = 20
card_h = (bottom-top-GAP*5)/6
card_w = W-2*MARGIN
BAR = 14
PAD = 34

y = top
for m in MEALS:
    x0, y0, x1, y1 = MARGIN, round(y), MARGIN+card_w, round(y+card_h)
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=tint(m["color"]))
    d.rounded_rectangle([x0, y0, x0+BAR+18, y1], radius=18, fill=m["color"])
    d.rectangle([x0+BAR, y0, x0+BAR+18, y1], fill=tint(m["color"]))
    cx = x0+BAR+PAD
    inner_w = x1-PAD-cx

    chip_f = gmb(24)
    tw = sum(d.textlength(ch, font=chip_f) for ch in m["slot"])+9*(len(m["slot"])-1)
    ch_y = y0+22
    d.rounded_rectangle([cx, ch_y, cx+tw+42, ch_y+44], radius=22, fill=m["color"])
    tracked(d, (cx+21, ch_y+23), m["slot"], chip_f, (255,255,255), tracking=9, anchor="lm")

    d.text((cx, y0+80), m["title"], font=bs(56), fill=INK, anchor="la")

    ing_f = ws(29)
    i_y = y0+148
    for ln in wrap(d, m["ing"], ing_f, inner_w)[:2]:
        d.text((cx, i_y), ln, font=ing_f, fill=GREY, anchor="la")
        i_y += 36

    mv_f, ml_f = bs(56), gmb(22)
    base_y = y1-36
    colw = inner_w/4
    labels = [("CAL", m["cal"]), ("P", m["p"]), ("F", m["f"]), ("C", m["c"])]
    for i, (lab, val) in enumerate(labels):
        vw = d.textlength(val, font=mv_f)
        lw = d.textlength(lab, font=ml_f)
        sx = cx+colw*i+(colw-(vw+10+lw))/2
        d.text((sx, base_y), val, font=mv_f, fill=INK, anchor="ls")
        d.text((sx+vw+10, base_y-3), lab, font=ml_f, fill=FAINT, anchor="ls")
        if i:
            d.line([cx+colw*i, y1-76, cx+colw*i, y1-26], fill=(196,200,210), width=2)
    y = y1+GAP

# ---------------- FOOTER ----------------
fy = H-FOOTER_H
d.rectangle([0, fy, W, H], fill=NAVY)
tracked(d, (MARGIN, fy+40), "DAY TOTAL", gm(25), (150,156,174), tracking=7)
d.text((MARGIN-4, fy+72), "2,690", font=bs(118), fill=(255,255,255), anchor="la")
cal_w = d.textlength("2,690", font=bs(118))
tracked(d, (MARGIN+cal_w+16, fy+164), "CAL", gm(25), (150,156,174), tracking=5)
rx = W-MARGIN
d.text((rx, fy+66), "247 P · 88 F · 236 C", font=bs(64), fill=(255,255,255), anchor="ra")
tracked(d, (rx, fy+150), "TARGET 230 P / 90 F / 240 C", gm(23), (150,156,174), tracking=3, anchor="ra")
tracked(d, (MARGIN, fy+FOOTER_H-46), "DEXTROSE = YES ON TRAINING DAYS · ROAST ALL 2 LB SALMON TODAY → THU + FRI", gm(19), (120,126,144), tracking=3)

img.save("/home/claude/menu/wednesday-menu.png")
print("rendered")
