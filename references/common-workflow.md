# Common publisher workflow

## Identify the page

Use the current tab or supplied URL. Match the final hostname against the publisher guide. When the host is an institutional proxy, retain the proxy URL for access but record the canonical DOI and publisher URL when both are visible.

## Browse a journal

Open the journal home page, then use the visible `Latest`, `Current issue`, `All issues`, `Browse`, or search controls. Return only the requested range. Metrics are volatile: report the exact page label and retrieval date, never recalculate or silently substitute a third-party value.

## Inspect an article

Collect the following fields only if shown: title; authors; journal; publication date; volume; issue; pages or article number; DOI; abstract; keywords; article URL; and visible PDF URL. State whether full text is open, available through the current login, or unavailable.

## Export a citation

Look for `Cite`, `Citation`, `Export citation`, `Download citation`, `RIS`, or `BibTeX`. Prefer the publisher-provided file. If no native export appears, create normalized metadata from the page and mark it `page-extracted metadata`.

## Download an accessible PDF

Proceed only after the user asks for a download. Confirm that the article page visibly provides PDF access in the current session. Save via the normal browser download control to the user-chosen folder; validate that the saved file is nonempty and begins with `%PDF-`. If the page lacks access, report that outcome without attempting alternate endpoints.

## Failure handling

| Page state | Action |
|---|---|
| Login, institutional access, or verification required | Ask the user to complete it in their browser, then resume from the open tab. |
| Article has no visible PDF link | Report unavailable access; offer citation export or metadata extraction. |
| Native citation export missing | Produce page-extracted metadata and label it clearly. |
| Dynamic page has not rendered | Refresh once or ask the user to provide the article URL; do not guess selectors. |
