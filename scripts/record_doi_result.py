#!/usr/bin/env python3
"""Record one browser-download result in a DOI batch manifest."""

import argparse
import csv
import os
import tempfile
from pathlib import Path


STATUSES = ("downloaded", "unavailable", "login-required", "verification-required", "failed")


def read_manifest(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "source_row" not in reader.fieldnames:
            raise ValueError("Manifest does not contain the required source_row column.")
        return reader.fieldnames, list(reader)


def write_manifest(path, fieldnames, rows):
    descriptor, temporary = tempfile.mkstemp(prefix="doi-manifest-", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Manifest CSV created by prepare_doi_batch.py")
    parser.add_argument("--source-row", required=True, type=int, help="Original spreadsheet row number")
    parser.add_argument("--status", required=True, choices=STATUSES)
    parser.add_argument("--publisher", default="")
    parser.add_argument("--article-url", default="")
    parser.add_argument("--pdf-path", default="")
    parser.add_argument("--error", default="")
    args = parser.parse_args()

    path = Path(args.manifest)
    try:
        fieldnames, rows = read_manifest(path)
        target = next((row for row in rows if row.get("source_row") == str(args.source_row)), None)
        if target is None:
            raise ValueError(f"No manifest entry for source row {args.source_row}.")
        target.update({
            "status": args.status,
            "publisher": args.publisher,
            "article_url": args.article_url,
            "pdf_path": args.pdf_path,
            "error": args.error,
        })
        write_manifest(path, fieldnames, rows)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Recorded source row {args.source_row} as {args.status}.")


if __name__ == "__main__":
    main()
