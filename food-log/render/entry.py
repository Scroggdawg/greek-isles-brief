"""Load, validate and score a day's food-log entry.

One JSON per day in `food-log/entries/YYYY-MM-DD.json`. Totals stored in the
file are advisory only — everything downstream recomputes from `items`, which
are the source of truth.
"""

import datetime
import glob
import json
import os

ENTRIES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entries")

DEFAULT_TARGETS = {"cal": 2690, "p": 230, "f": 90, "c": 240}

MACROS = ("cal", "p", "f", "c")

# Ceiling macros: going over is the thing worth flagging. Protein is a floor —
# over is a good problem, not a warning.
CEILINGS = {"cal": "amber", "f": "red", "c": "red"}

STATUSES = ("plan", "open", "final")


class EntryError(ValueError):
    pass


def entry_path(date, entries_dir=None):
    return os.path.join(entries_dir or ENTRIES_DIR, "%s.json" % date)


def all_dates(entries_dir=None):
    """Every logged date, ascending."""
    pattern = os.path.join(entries_dir or ENTRIES_DIR, "*.json")
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(pattern))


def load(date, entries_dir=None):
    """Read one day and return it normalized. Raises EntryError on bad input."""
    path = entry_path(date, entries_dir)
    if not os.path.exists(path):
        raise EntryError("no entry for %s (looked in %s)" % (date, path))
    with open(path) as fh:
        try:
            raw = json.load(fh)
        except json.JSONDecodeError as exc:
            raise EntryError("%s is not valid JSON: %s" % (path, exc))
    return normalize(raw, date=date, entries_dir=entries_dir)


def load_all(entries_dir=None):
    return [load(d, entries_dir) for d in all_dates(entries_dir)]


def normalize(raw, date=None, entries_dir=None):
    """Fill defaults, validate, and attach computed totals and deltas."""
    e = dict(raw)
    e["date"] = e.get("date") or date
    if not e["date"]:
        raise EntryError("entry has no date")
    try:
        d = datetime.date.fromisoformat(e["date"])
    except ValueError:
        raise EntryError("bad date %r — want YYYY-MM-DD" % e["date"])

    e["weekday"] = (e.get("weekday") or d.strftime("%A")).lower()
    if e["weekday"] != d.strftime("%A").lower():
        raise EntryError(
            "%s is a %s, but the entry says %s"
            % (e["date"], d.strftime("%A").lower(), e["weekday"])
        )

    e["status"] = (e.get("status") or "plan").lower()
    if e["status"] not in STATUSES:
        raise EntryError("status %r — want one of %s" % (e["status"], ", ".join(STATUSES)))

    targets = dict(DEFAULT_TARGETS)
    targets.update(e.get("targets") or {})
    e["targets"] = targets

    e["notes"] = list(e.get("notes") or [])
    e["items"] = [_item(it, i, e["status"]) for i, it in enumerate(e.get("items") or [])]
    if not e["items"]:
        raise EntryError("%s has no items" % e["date"])

    e["day"] = e.get("day") or _day_number(e["date"], entries_dir)
    e["eaten"] = [it for it in e["items"] if it["eaten"]]
    e["ondeck"] = [it for it in e["items"] if not it["eaten"]]
    e["totals"] = sum_macros(e["eaten"])
    e["planned"] = sum_macros(e["items"])
    e["deltas"] = {k: e["totals"][k] - targets[k] for k in MACROS}
    e["estimated"] = any(it["estimated"] for it in e["items"])
    return e


def _item(raw, index, status):
    if not isinstance(raw, dict):
        raise EntryError("item %d is not an object" % index)
    it = dict(raw)
    it["name"] = (it.get("name") or "").strip()
    if not it["name"]:
        raise EntryError("item %d has no name" % index)
    for k in MACROS:
        try:
            it[k] = int(round(float(it.get(k, 0))))
        except (TypeError, ValueError):
            raise EntryError("item %r has a non-numeric %s: %r" % (it["name"], k, it.get(k)))
        if it[k] < 0:
            raise EntryError("item %r has a negative %s" % (it["name"], k))
    it["slot"] = (it.get("slot") or "").strip()
    it["estimated"] = bool(it.get("estimated"))
    # An item is eaten unless it says otherwise. On a plan sheet nothing has
    # been eaten yet, so the default flips.
    it["eaten"] = bool(it.get("eaten", status != "plan"))
    it["receipt"] = (it.get("receipt") or it["name"]).strip()
    it["ing"] = (it.get("ing") or "").strip()
    it["title"] = (it.get("title") or it["name"]).strip()
    it["at"] = (it.get("at") or it["slot"]).strip()
    # Position in the day, so a card keeps its color from the morning plan
    # through every update.
    it["index"] = index
    return it


def _day_number(date, entries_dir=None):
    """Day N of the log — its 1-based position among all logged days."""
    dates = all_dates(entries_dir)
    if date not in dates:
        return len(dates) + 1
    return dates.index(date) + 1


def sum_macros(items):
    return {k: sum(it[k] for it in items) for k in MACROS}


def cal_target(entry):
    """Calories are informational — the sheet quotes them to the nearest 100
    ("~2,700"), and every calorie caption is measured against that same
    rounded number so the card never argues with itself. The gram targets are
    the contract and are used exactly."""
    return int(round(entry["targets"]["cal"] / 100.0) * 100)


def bar(entry, macro):
    """Scoreboard row state for one macro.

    Returns (eaten, target, fraction, warn) where warn is None | 'amber' | 'red'.
    """
    got = entry["totals"][macro]
    target = cal_target(entry) if macro == "cal" else entry["targets"][macro]
    frac = 1.0 if target <= 0 else min(1.0, got / float(target))
    warn = None
    if macro in CEILINGS:
        if got > target:
            warn = CEILINGS[macro]
        elif target and got >= target * 0.94:
            warn = "amber"
    return got, target, frac, warn


def caption(entry, macro):
    """The short human line beside a macro label, e.g. '23 G OVER'."""
    got, target, _, _ = bar(entry, macro)
    delta = got - target
    closed = entry["status"] == "final"
    unit = "" if macro == "cal" else " G"

    if macro == "cal":
        if closed:
            if abs(delta) < 25:
                return "ON THE NUMBER"
            rounded = int(round(abs(delta) / 10.0) * 10)
            return "≈ %d %s" % (rounded, "OVER" if delta > 0 else "UNDER")
        if delta < 0:
            return "%s TO GO" % _num(-delta)
        return "%s OVER" % _num(delta)

    if macro == "p":
        if delta >= 0:
            if closed:
                return "+%d — GOOD PROBLEM" % delta if delta else "ON THE NUMBER"
            return "+%d — DONE" % delta if delta else "ON THE NUMBER"
        return "%d G %s" % (-delta, "SHORT" if closed else "TO GO")

    if delta > 0:
        return "%d%s OVER" % (delta, unit)
    if delta < 0:
        return "%d%s %s" % (-delta, unit, "UNDER" if closed else "LEFT")
    return "ON THE NUMBER"


def _num(n):
    return "{:,}".format(int(n))


def macro_line(totals):
    """'266 P · 68 F · 263 C'"""
    return "%d P · %d F · %d C" % (totals["p"], totals["f"], totals["c"])


def receipt_value(item):
    """'540 · 34P · 8F · 83C'"""
    return "%s · %dP · %dF · %dC" % (_num(item["cal"]), item["p"], item["f"], item["c"])


def totals_value(totals):
    return "%s · %dP · %dF · %dC" % (
        _num(totals["cal"]),
        totals["p"],
        totals["f"],
        totals["c"],
    )


def save(entry, entries_dir=None):
    """Write the entry back, with stored totals refreshed from items."""
    keep = (
        "date",
        "weekday",
        "scheme",
        "status",
        "day",
        "targets",
        "items",
        "totals",
        "notes",
        "story",
        "footnote",
    )
    item_keys = ("slot", "at", "name", "title", "receipt", "ing", "cal", "p", "f", "c",
                 "estimated", "eaten", "color")
    out = {}
    for k in keep:
        if k == "totals":
            out["totals"] = sum_macros(entry["eaten"])
        elif k == "items":
            out["items"] = [
                {ik: it[ik] for ik in item_keys if ik in it and it[ik] not in ("", None)}
                for it in entry["items"]
            ]
        elif k in entry and entry[k] not in ("", None, []):
            out[k] = entry[k]
    path = entry_path(entry["date"], entries_dir)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path
