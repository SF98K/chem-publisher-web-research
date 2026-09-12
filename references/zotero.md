# Zotero workflow

## Preferred route

1. Download the publisher's RIS file, or save a `page-extracted metadata` JSON file.
2. Start Zotero desktop and select a writable target collection.
3. Run the helper locally. It imports citations through Zotero Connector's local API and does not contact a publisher website.
4. Add a previously downloaded PDF in Zotero desktop with `Add Attachment` → `Attach Stored Copy of File`.

## Commands

```powershell
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --ris-file .\citation.ris
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --json-file .\paper.json
```

The JSON object accepts: `title` (required), `authors` (array), `journal`, `date`, `volume`, `issue`, `pages`, `doi`, `url`, `abstract`, `keywords` (array), `issn`, and `contentType`. The helper constructs a Zotero item from only the supplied fields.

## Outcomes

`201` means Zotero accepted the import. `409` means the same deterministic session was already imported and is treated as a successful no-duplicate result. If Zotero is closed or its Connector is unreachable, the helper stops with an actionable error.
