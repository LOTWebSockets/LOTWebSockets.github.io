#!/usr/bin/env python3

import csv
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
CSV_OUT = ROOT / "data" / "websockets.csv"
BADGE_OUT = ROOT / "data" / "badge.json"


def cell_text(cell):
    """Plain text of a cell, collapsing whitespace."""
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()


def parse_rows(soup):
    table = soup.find("table", id="sockets")
    if table is None:
        sys.exit("Could not find <table id=\"sockets\"> in index.html")

    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 4:
            continue

        name = cell_text(cells[0])

        endpoint_code = cells[1].find("code")
        endpoint = endpoint_code.get_text(strip=True) if endpoint_code else cell_text(cells[1])

        abuse_cell = cells[2]
        dir_tag = abuse_cell.find("span", class_="dir-tag")
        direction = ""
        if dir_tag:
            direction = dir_tag.get_text(strip=True).strip("()")
            dir_tag.extract()  # remove so it's not duplicated in the abuse text
        abuse = cell_text(abuse_cell)

        status_badge = cells[3].find("span", class_="status-badge")
        status = cell_text(status_badge) if status_badge else cell_text(cells[3])

        rows.append(
            {
                "name": name,
                "endpoint": endpoint,
                "abuse": abuse,
                "direction": direction,
                "status": status,
            }
        )
    return rows


def write_csv(rows):
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "endpoint", "abuse", "direction", "status"]
        )
        writer.writeheader()
        writer.writerows(rows)


def write_badge(count):
    badge = {
        "schemaVersion": 1,
        "label": "entries",
        "message": str(count),
        "color": "00ccff",
    }
    BADGE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with BADGE_OUT.open("w", encoding="utf-8") as f:
        json.dump(badge, f, indent=2)
        f.write("\n")


def main():
    soup = BeautifulSoup(INDEX_HTML.read_text(encoding="utf-8"), "html.parser")
    rows = parse_rows(soup)
    write_csv(rows)
    write_badge(len(rows))
    print(f"Wrote {len(rows)} rows to {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote entry-count badge to {BADGE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
