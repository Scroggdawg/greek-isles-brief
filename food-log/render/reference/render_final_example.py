from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 2600
MARGIN = 56
PAPER = (245, 247, 250)
NAVY = (23, 28, 48)
INK = (24, 26, 34)
GREY = (72, 76, 88)
FAINT = (140, 144, 156)
MUTE = (116, 120, 134)
AMBER = (214, 126, 12)
RED = (219, 58, 52)

F = "/home/claude/menu/"
def bs(s):  return ImageFont.truetype(F+"BigShoulders-Bold.ttf", s)
def ws(s):  return ImageFont.truetype(F+"WorkSans-Regular.ttf", s)
def wsb(s): return ImageFont.truetype(F+"WorkSans-Bold.ttf", s)
def gm(s):  return ImageFont.truetype(F+"GeistMono-Regular.ttf", s)
def gmb(s): return ImageFont.truetype(F+"GeistMono-Bold.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

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

COLS = [(108,74,46),(32,128,206),(199,58,92),(14,164,178),(16,124,92),(122,72,190)]

# HEADER
d.rectangle([0,0,W,320], fill=NAVY)
tracked(d, (MARGIN, 66), "DAILY MENU · DAY 2 FINAL", gm(26), (255,255,255), tracking=6)
tracked(d, (W-MARGIN, 66), "LUKE", gmb(26), (255,255,255), tracking=7, anchor="ra")
d.text((MARGIN-5, 104), "WEDNESDAY", font=bs(140), fill=(255,255,255), anchor="la")
tracked(d, (MARGIN, 262), "AUGUST 12, 2026 — FINAL", gm(31), (188,194,210), tracking=5)
sw = tracked(d, (W-MARGIN-30, 168), "FINAL", bs(64), (255,255,255), tracking=6, anchor="ra")
d.rectangle([W-MARGIN-30-sw-26, 152, W-MARGIN-30+26, 242], outline=(255,255,255), width=4)
seg = W/6
for i, c in enumerate(COLS):
    d.rectangle([round(i*seg), 306, round((i+1)*seg)+1, 320], fill=c)

# SCOREBOARD
by0, by1 = 348, 920
d.rounded_rectangle([MARGIN, by0, W-MARGIN, by1], radius=18, fill=(255,255,255))
bx = MARGIN+40
bw = (W-MARGIN-40)-bx
tracked(d, (bx, by0+38), "FINAL VS TARGET", gmb(25), INK, tracking=7)
tracked(d, (W-MARGIN-40, by0+38), "DAY CLOSED", gm(23), FAINT, tracking=4, anchor="ra")

bars = [
    ("CALORIES", "≈ 70 OVER",         "2,770 / ~2,700", 1.0,    "amber"),
    ("PROTEIN",  "+36 — GOOD PROBLEM","266 / 230 G",    1.0,    None),
    ("FAT",      "22 G UNDER",        "68 / 90 G",      68/90,  None),
    ("CARBS",    "23 G OVER",         "263 / 240 G",    1.0,    "red"),
]
ry = by0+104
for lab, note, val, frac, warn in bars:
    wcol = AMBER if warn=="amber" else RED if warn=="red" else FAINT
    wfont = gmb(21) if warn else gm(21)
    lw = tracked(d, (bx, ry), lab, gm(24), MUTE, tracking=5)
    tracked(d, (bx+lw+26, ry+2), "· "+note, wfont, wcol, tracking=3)
    d.text((W-MARGIN-40, ry+16), val, font=bs(46), fill=INK, anchor="rs")
    bar_y = ry+40
    d.rounded_rectangle([bx, bar_y, bx+bw, bar_y+18], radius=9, fill=(228,231,238))
    fill_c = AMBER if warn=="amber" else RED if warn=="red" else NAVY
    d.rounded_rectangle([bx, bar_y, bx+max(bw*frac, 24), bar_y+18], radius=9, fill=fill_c)
    ry += 116

# RECEIPT
tracked(d, (MARGIN+6, by1+26), "THE FULL DAY", gmb(24), MUTE, tracking=8)
rc0 = by1+70
rc1 = rc0+712
d.rounded_rectangle([MARGIN, rc0, W-MARGIN, rc1], radius=16, fill=(235,237,242))
rx0 = MARGIN+36
rx1 = W-MARGIN-36
rows = [
    ("Espresso + 1 tsp butter",           "40 · 0P · 4F · 0C"),
    ("Cottage cheese bowl",               "540 · 34P · 8F · 83C"),
    ("Poke — the last pound",             "590 · 102P · 10F · 12C"),
    ("½ avocado",                         "120 · 2P · 11F · 6C"),
    ("Dave's Killer bread ×2, 21-grain",  "220 · 10P · 3F · 44C"),
    ("Harmless Harvest, 32 oz",           "240 · 0P · 0F · 60C"),
    ("Chomps turkey stick",               "80 · 12P · 4F · 0C"),
    ("Starbucks shaken espresso, soy *",  "190 · 6P · 3F · 30C"),
    ("Chicken 10.5 oz + asparagus, oil + honey", "670 · 95P · 24F · 13C"),
    ("Yasso strawberries & cream bar",    "80 · 5P · 1F · 15C"),
]
ty = rc0+34
for name, val in rows:
    d.text((rx0, ty), name, font=ws(30), fill=GREY, anchor="la")
    d.text((rx1, ty+2), val, font=gm(25), fill=MUTE, anchor="ra")
    ty += 60
d.line([rx0, ty+2, rx1, ty+2], fill=(200,203,212), width=2)
d.text((rx0, ty+20), "DAY 2 TOTAL", font=wsb(30), fill=INK, anchor="la")
d.text((rx1, ty+22), "2,770 · 266P · 68F · 263C", font=gmb(26), fill=INK, anchor="ra")

# NOTES
n0 = rc1+26
n1 = n0+460
d.rounded_rectangle([MARGIN, n0, W-MARGIN, n1], radius=16, fill=(255,255,255))
nx = MARGIN+36
tracked(d, (nx, n0+34), "DAY 2 NOTES", gmb(24), INK, tracking=7)
notes = [
    "Protein 266 — biggest day yet; the 10.5 oz of chicken did it.",
    "Fat finished 22 under target. Under is free on a cut.",
    "Carbs +23 — the honey habit is worth watching, not fixing.",
    "Two days in: 2,785 average, protein averaging 242. On plan.",
]
ny = n0+88
for n in notes:
    d.ellipse([nx, ny+12, nx+12, ny+24], fill=NAVY)
    d.text((nx+30, ny), n, font=ws(31), fill=GREY, anchor="la")
    ny += 78

# FOOTER
fy = n1+24
FH = H-fy
d.rectangle([0, fy, W, H], fill=NAVY)
tracked(d, (MARGIN, fy+40), "DAY 2 · CLOSED", gm(25), (150,156,174), tracking=7)
d.text((MARGIN-4, fy+70), "2,770", font=bs(104), fill=(255,255,255), anchor="la")
cal_w = d.textlength("2,770", font=bs(104))
tracked(d, (MARGIN+cal_w+16, fy+148), "CAL", gm(25), (150,156,174), tracking=5)
rxr = W-MARGIN
d.text((rxr, fy+62), "266 P · 68 F · 263 C", font=bs(58), fill=(255,255,255), anchor="ra")
tracked(d, (rxr, fy+138), "TARGET 230 P / 90 F / 240 C", gm(22), (150,156,174), tracking=3, anchor="ra")
tracked(d, (MARGIN, fy+FH-40), "* STARBUCKS ESTIMATED · HONEY AT 1 TSP · SEE YOU THURSDAY", gm(19), (118,124,142), tracking=3)

img.save("/home/claude/menu/wednesday-final.png")
print("footer:", fy, "height:", FH)
