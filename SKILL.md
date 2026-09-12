---
name: publisher-web-research
description: Use when browsing, searching, extracting metadata, exporting citations, downloading accessible PDFs, or sending citations to Zotero from ScienceDirect, ACS Publications, RSC Publishing, Wiley Online Library, Science/AAAS, or Nature Portfolio.
---

# Publisher web research

Use publisher pages as the source of record for a journal, article, and native citation export. Route the request by its URL or journal/publisher name. Use existing browser-page tools when available; otherwise give the user the exact page to open and continue from supplied URLs or exported files.

Supported publishers: ScienceDirect, ACS Publications, RSC Publishing, Wiley Online Library, Science/AAAS, and Nature Portfolio.

## Choose the workflow

| User intent | Read |
|---|---|
| Browse a journal, issue, or recent articles | [common workflow](references/common-workflow.md), then [publisher guide](references/publishers.md) |
| Find or inspect an article | [common workflow](references/common-workflow.md), then [publisher guide](references/publishers.md) |
| Export RIS/BibTeX or add a citation to Zotero | [zotero guide](references/zotero.md) |
| Download an article PDF | [common workflow](references/common-workflow.md) |

## Operating rules

1. State the detected publisher and use its official domain. If a DOI redirects elsewhere, follow the final official publisher URL.
2. Extract only visible page data. Label an output `native export` only when it comes from the publisher's RIS/BibTeX/export control; otherwise label it `page-extracted metadata`.
3. Download only when the user asks for it and the browser session visibly shows an accessible PDF link. Report `open access`, `authenticated access`, or `unavailable` before saving.
4. If the site asks for sign-in, institutional access, or human verification, stop and ask the user to complete it in their own browser. Do not submit credentials, preserve session data, or retry around verification.
5. Send citations to Zotero only on request. Prefer RIS. Use `scripts/push_to_zotero.py` for RIS or normalized JSON, then add any already-downloaded PDF from Zotero desktop.

## Result shape

For journal browsing, report journal title, official URL, requested issue/current content, retrieval date, and article links.

For articles, report title, authors, journal, publication date, volume/issue/pages or article number, DOI, abstract when visible, URL, citation-source label, and access state. Preserve unknown fields as `not shown on page`; do not infer them.

For exports, report format, source (`native export` or `page-extracted metadata`), local file path if saved, and Zotero import outcome if requested.
