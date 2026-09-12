#!/usr/bin/env python3
"""Import RIS or normalized publisher metadata into a running Zotero desktop app."""

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ZOTERO_ROOT = "http://127.0.0.1:23119/connector"
TIMEOUT_SECONDS = 15


def post(endpoint, payload):
    request = urllib.request.Request(
        f"{ZOTERO_ROOT}/{endpoint}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Zotero-Connector-API-Version": "3",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            text = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)
    except TimeoutError:
        return 0, "request timed out"


def session_id(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def import_ris(ris):
    if not ris.strip():
        raise ValueError("RIS input is empty.")
    identifier = session_id(ris.strip())
    request = urllib.request.Request(
        f"{ZOTERO_ROOT}/import?session={identifier}",
        data=json.dumps(ris).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, f"Imported RIS into Zotero (session {identifier})."
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            return 409, f"RIS was already imported in session {identifier}; no duplicate added."
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, f"Cannot reach Zotero: {exc.reason}"


def normalize_item(paper):
    if not paper.get("title", "").strip():
        raise ValueError("JSON input requires a nonempty title.")
    item = {
        "itemType": "journalArticle" if paper.get("contentType", "journalArticle") == "journalArticle" else paper["contentType"],
        "title": paper["title"],
        "abstractNote": paper.get("abstract", ""),
        "date": paper.get("date", ""),
        "url": paper.get("url", ""),
        "DOI": paper.get("doi", ""),
        "volume": paper.get("volume", ""),
        "issue": paper.get("issue", ""),
        "pages": paper.get("pages", ""),
        "publicationTitle": paper.get("journal", ""),
        "ISSN": paper.get("issn", ""),
        "accessDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "creators": [{"name": author, "creatorType": "author"} for author in paper.get("authors", [])],
        "tags": [{"tag": keyword, "type": 1} for keyword in paper.get("keywords", [])],
    }
    return {key: value for key, value in item.items() if value not in ("", [], None)}


def import_json(papers):
    if isinstance(papers, dict):
        papers = [papers]
    if not isinstance(papers, list):
        raise ValueError("JSON input must be an object or an array of objects.")
    items = [normalize_item(paper) for paper in papers]
    identifier = session_id("|".join(item["title"] for item in items))
    status, response = post("saveItems", {"sessionID": identifier, "items": items})
    if status == 201:
        return status, f"Imported {len(items)} item(s) into Zotero (session {identifier})."
    if status == 409:
        return status, f"Items were already imported in session {identifier}; no duplicate added."
    return status, f"Zotero rejected the import: {response}"


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ris-file", help="UTF-8 RIS file exported by a publisher")
    group.add_argument("--json-file", help="Normalized publisher metadata JSON file")
    args = parser.parse_args()

    if args.ris_file:
        status, message = import_ris(read_text(args.ris_file))
    else:
        data = json.loads(read_text(args.json_file))
        status, message = import_json(data)

    print(message)
    sys.exit(0 if status in (201, 409) else 1)


if __name__ == "__main__":
    main()
