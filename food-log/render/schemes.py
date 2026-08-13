"""Weekday color schemes for the daily one-sheet.

One scheme per weekday — the day announces itself before you read a word.

Two are locked (they shipped on real sheets and must not drift):
  tuesday   = warm   near-black ink on cream, amber/gold/red
  wednesday = navy   navy band on cool paper, indigo/cerulean/teal

The other five are proposals awaiting Luke's sign-off. They render fine
today; treat their exact values as provisional until `locked` flips to True.

Scheme keys
-----------
band        header + footer background
band_text   headline type on the band
band_sub    date line on the band
band_faint  small caps labels on the band
band_foot   footnote strip on the band
paper       page background
card        scoreboard / notes / meal card background
receipt     the receipt block background
ink         primary type on paper
grey        body copy on paper
mute        secondary mono type on paper
faint       tertiary type on paper
track       unfilled portion of a macro bar
rule        hairlines
amber       "tight" warning (calories over, ceiling macro close)
red         "over" warning (a ceiling macro blown)
accents     six meal-card colors, also the header legend stripe
"""

SCHEMES = {
    "warm": {
        "label": "Warm — cream paper, near-black ink, amber/gold/red",
        "weekday": "tuesday",
        "locked": True,
        "band": (20, 20, 22),
        "band_text": (255, 255, 255),
        "band_sub": (196, 190, 180),
        "band_faint": (156, 150, 142),
        "band_foot": (124, 119, 112),
        "paper": (250, 247, 242),
        "card": (255, 255, 255),
        "receipt": (240, 238, 234),
        "ink": (26, 24, 22),
        "grey": (78, 74, 68),
        "mute": (122, 117, 110),
        "faint": (146, 141, 134),
        "track": (232, 228, 221),
        "rule": (208, 203, 195),
        "amber": (222, 130, 10),
        "red": (219, 58, 52),
        "accents": [
            (238, 156, 26),
            (212, 160, 60),
            (231, 76, 70),
            (120, 92, 214),
            (41, 152, 99),
            (52, 188, 158),
        ],
    },
    "navy": {
        "label": "Navy — cool paper, navy band, indigo/cerulean/teal",
        "weekday": "wednesday",
        "locked": True,
        "band": (23, 28, 48),
        "band_text": (255, 255, 255),
        "band_sub": (188, 194, 210),
        "band_faint": (150, 156, 174),
        "band_foot": (118, 124, 142),
        "paper": (245, 247, 250),
        "card": (255, 255, 255),
        "receipt": (235, 237, 242),
        "ink": (24, 26, 34),
        "grey": (72, 76, 88),
        "mute": (116, 120, 134),
        "faint": (140, 144, 156),
        "track": (228, 231, 238),
        "rule": (200, 203, 212),
        "amber": (214, 126, 12),
        "red": (219, 58, 52),
        "accents": [
            (108, 74, 46),
            (32, 128, 206),
            (199, 58, 92),
            (14, 164, 178),
            (16, 124, 92),
            (122, 72, 190),
        ],
    },
    # ---- proposals, pending sign-off -------------------------------------
    "oxblood": {
        "label": "Oxblood — blush paper, deep maroon band, crimson/rust/rose",
        "weekday": "monday",
        "locked": False,
        "band": (58, 20, 26),
        "band_text": (255, 255, 255),
        "band_sub": (216, 186, 186),
        "band_faint": (176, 146, 148),
        "band_foot": (140, 112, 114),
        "paper": (250, 245, 244),
        "card": (255, 255, 255),
        "receipt": (241, 234, 233),
        "ink": (32, 22, 24),
        "grey": (82, 70, 72),
        "mute": (126, 112, 114),
        "faint": (150, 138, 139),
        "track": (233, 224, 223),
        "rule": (208, 197, 196),
        "amber": (206, 122, 22),
        "red": (196, 42, 50),
        "accents": [
            (162, 38, 52),
            (206, 96, 72),
            (148, 76, 122),
            (94, 106, 168),
            (34, 130, 116),
            (198, 148, 48),
        ],
    },
    "forest": {
        "label": "Forest — sand paper, deep green band, moss/olive/brass",
        "weekday": "thursday",
        "locked": False,
        "band": (18, 44, 36),
        "band_text": (255, 255, 255),
        "band_sub": (186, 206, 196),
        "band_faint": (148, 170, 160),
        "band_foot": (116, 138, 128),
        "paper": (247, 247, 241),
        "card": (255, 255, 255),
        "receipt": (236, 238, 231),
        "ink": (22, 28, 24),
        "grey": (70, 78, 72),
        "mute": (114, 122, 116),
        "faint": (140, 148, 141),
        "track": (227, 231, 223),
        "rule": (199, 205, 196),
        "amber": (204, 132, 16),
        "red": (203, 62, 48),
        "accents": [
            (24, 108, 82),
            (108, 142, 46),
            (166, 132, 32),
            (30, 122, 138),
            (140, 84, 44),
            (86, 96, 158),
        ],
    },
    "plum": {
        "label": "Plum — lilac paper, deep purple band, violet/magenta/rose",
        "weekday": "friday",
        "locked": False,
        "band": (42, 26, 60),
        "band_text": (255, 255, 255),
        "band_sub": (200, 190, 216),
        "band_faint": (162, 152, 180),
        "band_foot": (128, 120, 146),
        "paper": (248, 246, 251),
        "card": (255, 255, 255),
        "receipt": (238, 235, 244),
        "ink": (28, 24, 36),
        "grey": (74, 70, 88),
        "mute": (118, 113, 134),
        "faint": (143, 138, 158),
        "track": (230, 227, 238),
        "rule": (203, 198, 214),
        "amber": (210, 126, 14),
        "red": (212, 52, 88),
        "accents": [
            (108, 62, 172),
            (176, 54, 132),
            (66, 96, 190),
            (206, 96, 62),
            (28, 140, 140),
            (140, 116, 40),
        ],
    },
    "clay": {
        "label": "Clay — sand paper, burnt sienna band, rust/ochre/copper",
        "weekday": "saturday",
        "locked": False,
        "band": (74, 40, 24),
        "band_text": (255, 255, 255),
        "band_sub": (216, 198, 184),
        "band_faint": (178, 158, 144),
        "band_foot": (142, 124, 112),
        "paper": (251, 246, 239),
        "card": (255, 255, 255),
        "receipt": (242, 236, 228),
        "ink": (32, 26, 20),
        "grey": (82, 72, 62),
        "mute": (126, 114, 102),
        "faint": (150, 139, 128),
        "track": (234, 227, 217),
        "rule": (209, 200, 189),
        "amber": (214, 132, 16),
        "red": (198, 62, 44),
        "accents": [
            (176, 84, 36),
            (200, 140, 40),
            (150, 62, 58),
            (108, 118, 62),
            (58, 122, 128),
            (122, 84, 148),
        ],
    },
    "slate": {
        "label": "Slate — near-white paper, grey-blue band, steel/teal/muted",
        "weekday": "sunday",
        "locked": False,
        "band": (44, 54, 64),
        "band_text": (255, 255, 255),
        "band_sub": (196, 204, 214),
        "band_faint": (158, 166, 178),
        "band_foot": (126, 134, 146),
        "paper": (248, 249, 250),
        "card": (255, 255, 255),
        "receipt": (237, 240, 243),
        "ink": (26, 30, 36),
        "grey": (74, 80, 88),
        "mute": (118, 125, 134),
        "faint": (142, 149, 158),
        "track": (229, 233, 238),
        "rule": (202, 207, 213),
        "amber": (208, 130, 20),
        "red": (206, 62, 56),
        "accents": [
            (58, 96, 130),
            (46, 134, 138),
            (108, 122, 148),
            (86, 132, 96),
            (166, 118, 62),
            (134, 92, 140),
        ],
    },
}

# The map Luke steers by. Tuesday and Wednesday are locked; the rest are
# proposals — see food-log/README.md, "Weekday schemes".
WEEKDAY_SCHEME = {
    "monday": "oxblood",
    "tuesday": "warm",
    "wednesday": "navy",
    "thursday": "forest",
    "friday": "plum",
    "saturday": "clay",
    "sunday": "slate",
}


def scheme_for(weekday, override=None):
    """Resolve a scheme dict. `override` wins over the weekday map."""
    if override:
        key = override.lower()
        if key not in SCHEMES:
            raise KeyError(
                "unknown scheme %r — known: %s" % (override, ", ".join(sorted(SCHEMES)))
            )
        return dict(SCHEMES[key], key=key)
    key = WEEKDAY_SCHEME[weekday.lower()]
    return dict(SCHEMES[key], key=key)
