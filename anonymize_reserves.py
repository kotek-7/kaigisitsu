#!/usr/bin/env python3
"""Generate an anonymized reserves json where organization titles are masked.

Usage:
    python3 anonymize_reserves.py [input_json] [output_json]

Defaults:
    input_json  = reserves.json
    output_json = reserves_anonymized.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Iterable

DEFAULT_INPUT = Path("reserves.json")
DEFAULT_OUTPUT = Path("reserves_anonymized.json")


def load_json(path: Path) -> Iterable[dict]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise SystemExit(f"入力ファイルが見つかりません: {path}") from exc


def save_json(path: Path, data: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def generate_labels(count: int) -> Iterable[str]:
    """Yield labels like A, B, ..., Z, AA, AB ... sufficient for `count`."""
    base = 26
    for num in range(count):
        label = ""
        n = num
        while True:
            label = chr(ord("A") + (n % base)) + label
            n //= base
            if n == 0:
                break
            n -= 1  # adjust for 0-indexed base conversion
        yield label


def build_mapping(titles: Iterable[str]) -> Dict[str, str]:
    unique_titles = sorted(set(titles))
    labels = list(generate_labels(len(unique_titles)))
    return dict(zip(unique_titles, labels))


def anonymize(data: Iterable[dict]) -> Iterable[dict]:
    titles = []
    for room in data:
        for entry in room.get("entries", []):
            if "title" in entry:
                titles.append(entry["title"])
    mapping = build_mapping(titles)

    anonymized = []
    for room in data:
        new_room = {"room": room.get("room"), "entries": []}
        for entry in room.get("entries", []):
            new_entry = dict(entry)
            title = entry.get("title")
            if title in mapping:
                new_entry["title"] = mapping[title]
            new_room["entries"].append(new_entry)
        anonymized.append(new_room)
    return anonymized


def main(argv: list[str]) -> None:
    input_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    output_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT

    data = load_json(input_path)
    anonymized = anonymize(data)
    save_json(output_path, anonymized)

    print(f"Anonymized {input_path} -> {output_path}")


if __name__ == "__main__":
    main(sys.argv)
