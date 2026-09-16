#!/usr/bin/env python3
"""Create a resumable DOI download manifest from a CSV or XLSX table."""

import argparse
import csv
import re
import sys
import zipfile
from urllib.parse import quote
from pathlib import Path
from xml.etree import ElementTree as ET


SPREADSHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
MANIFEST_FIELDS = [
    "source_row",
    "source_doi",
    "doi",
    "doi_url",
    "status",
    "publisher",
    "article_url",
    "pdf_path",
    "error",
]


def normalize_doi(value):
    """Return a canonical DOI text or an empty string for an empty cell."""
    doi = DOI_PREFIX.sub("", str(value or "").strip()).strip()
    doi = doi.lower()
    if not doi:
        return ""
    if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        raise ValueError(f"Not a DOI: {value}")
    return doi


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def column_index(reference):
    letters = "".join(character for character in reference if character.isalpha()).upper()
    value = 0
    for character in letters:
        value = value * 26 + ord(character) - ord("A") + 1
    return value - 1


def shared_strings(archive):
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(node.itertext()) for node in root.findall(f"{SPREADSHEET_NS}si")]


def first_sheet_path(archive):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    sheet = workbook.find(f"{SPREADSHEET_NS}sheets/{SPREADSHEET_NS}sheet")
    if sheet is None:
        raise ValueError("XLSX does not contain a worksheet.")
    relation_id = sheet.attrib.get(f"{REL_NS}id")
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relation = next((item for item in relationships if item.attrib.get("Id") == relation_id), None)
    if relation is None:
        raise ValueError("XLSX worksheet relationship is missing.")
    target = relation.attrib["Target"].lstrip("/")
    return target if target.startswith("xl/") else f"xl/{target}"


def read_xlsx(path):
    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        root = ET.fromstring(archive.read(first_sheet_path(archive)))
    rows = []
    for row in root.findall(f".//{SPREADSHEET_NS}sheetData/{SPREADSHEET_NS}row"):
        row_number = int(row.attrib.get("r", len(rows) + 1))
        while len(rows) < row_number - 1:
            rows.append([])
        values = {}
        for cell in row.findall(f"{SPREADSHEET_NS}c"):
            reference = cell.attrib.get("r", "")
            index = column_index(reference)
            cell_type = cell.attrib.get("t")
            raw = cell.findtext(f"{SPREADSHEET_NS}v", default="")
            if cell_type == "s" and raw:
                values[index] = strings[int(raw)]
            elif cell_type == "inlineStr":
                values[index] = "".join(cell.itertext())
            else:
                values[index] = raw
        width = max(values, default=-1) + 1
        rows.append([values.get(index, "") for index in range(width)])
    return rows


def find_doi_column(header, requested):
    target = requested.strip().casefold()
    for index, value in enumerate(header):
        if str(value).strip().casefold() == target:
            return index
    raise ValueError(f"DOI column '{requested}' was not found. Available columns: {', '.join(map(str, header))}")


def load_rows(path):
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        return read_csv(path)
    if suffix == ".xlsx":
        return read_xlsx(path)
    raise ValueError("Supported input formats are .xlsx and .csv. Save legacy .xls files as .xlsx first.")


def build_manifest(rows, doi_column):
    if not rows:
        raise ValueError("The input table is empty.")
    index = find_doi_column(rows[0], doi_column)
    manifest = []
    seen = set()
    for source_row, row in enumerate(rows[1:], start=2):
        source_doi = row[index] if index < len(row) else ""
        try:
            doi = normalize_doi(source_doi)
        except ValueError as error:
            manifest.append({
                "source_row": source_row,
                "source_doi": source_doi,
                "doi": "",
                "doi_url": "",
                "status": "invalid-doi",
                "publisher": "",
                "article_url": "",
                "pdf_path": "",
                "error": str(error),
            })
            continue
        if not doi or doi in seen:
            continue
        seen.add(doi)
        manifest.append({
            "source_row": source_row,
            "source_doi": source_doi,
            "doi": doi,
            "doi_url": f"https://doi.org/{quote(doi, safe='/')}",
            "status": "pending",
            "publisher": "",
            "article_url": "",
            "pdf_path": "",
            "error": "",
        })
    return manifest


def write_manifest(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Source .xlsx or .csv file containing a DOI column")
    parser.add_argument("--output", required=True, help="Output CSV manifest path")
    parser.add_argument("--doi-column", default="doi", help="DOI column name; case-insensitive (default: doi)")
    args = parser.parse_args()
    try:
        rows = load_rows(Path(args.input))
        manifest = build_manifest(rows, args.doi_column)
        write_manifest(Path(args.output), manifest)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as error:
        parser.error(str(error))
    pending = sum(row["status"] == "pending" for row in manifest)
    invalid = sum(row["status"] == "invalid-doi" for row in manifest)
    print(f"Created {args.output}: {pending} pending DOI(s), {invalid} invalid DOI(s).")


if __name__ == "__main__":
    main()
