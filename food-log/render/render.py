#!/usr/bin/env python3
"""Render a day's one-sheet from its JSON entry.

    python3 render/render.py --date 2026-08-12 --final
    python3 render/render.py --date 2026-08-13            # plan, from the entry
    python3 render/render.py --all                        # every logged day

Writes `sheets/YYYY-MM-DD-<status>.png` and `.pdf`. `--final` is a shorthand
for "close the day": it overrides the entry's status for this render, so a
sheet can be stamped without editing the file first.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import entry as E          # noqa: E402
import sheet               # noqa: E402
from schemes import scheme_for  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS_DIR = os.path.join(ROOT, "sheets")

# The seed PDFs are 900×1950 pt — 1200×2600 px at 96 dpi. Keep it there so old
# and new sheets print the same size.
PDF_DPI = 96.0


def render_day(date, final=False, scheme=None, outdir=None, entries_dir=None, quiet=False):
    e = E.load(date, entries_dir)
    if final:
        e["status"] = "final"
        for it in e["items"]:
            it["eaten"] = True
        e = E.normalize(e, entries_dir=entries_dir)

    s = scheme_for(e["weekday"], scheme or e.get("scheme"))
    img = sheet.render(e, s)

    outdir = outdir or SHEETS_DIR
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.join(outdir, "%s-%s" % (e["date"], e["status"]))
    png, pdf = stem + ".png", stem + ".pdf"
    img.save(png)
    img.save(pdf, "PDF", resolution=PDF_DPI)

    if not quiet:
        t = e["totals"] if e["eaten"] else e["planned"]
        flag = "" if s["locked"] else "  (scheme not yet signed off)"
        print(
            "%s  %s · %s%s\n  %s\n  %s cal · %dP · %dF · %dC%s"
            % (
                e["date"],
                e["weekday"],
                e["status"],
                "" if s["locked"] else " · %s" % s["key"],
                png,
                "{:,}".format(t["cal"]),
                t["p"], t["f"], t["c"],
                flag,
            )
        )
    return png, pdf


def main(argv=None):
    p = argparse.ArgumentParser(description="Render a food-log one-sheet.")
    p.add_argument("--date", help="YYYY-MM-DD")
    p.add_argument("--all", action="store_true", help="render every logged day")
    p.add_argument("--final", action="store_true", help="stamp the day closed")
    p.add_argument("--scheme", help="override the weekday scheme")
    p.add_argument("--outdir", help="where to write (default food-log/sheets)")
    p.add_argument("--entries-dir", help="read entries from here (default food-log/entries)")
    args = p.parse_args(argv)

    if not args.date and not args.all:
        p.error("give --date YYYY-MM-DD or --all")

    dates = E.all_dates(args.entries_dir) if args.all else [args.date]
    if not dates:
        print("no entries yet", file=sys.stderr)
        return 1

    for date in dates:
        try:
            render_day(date, final=args.final, scheme=args.scheme, outdir=args.outdir,
                       entries_dir=args.entries_dir)
        except E.EntryError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
