# Publisher guide

Use this guide to locate official sites and visible controls. Publisher templates change; inspect the live page instead of relying on a fixed selector or undocumented endpoint.

| Publisher | Official host | Journal and article cues | Citation and PDF cues |
|---|---|---|---|
| ScienceDirect | `www.sciencedirect.com` | Journal home, `All issues`, article PII page | `Export citation`, RIS/BibTeX, `View PDF` |
| ACS Publications | `pubs.acs.org` | Journal landing page, `Issue`, `Latest` | `Citation`, export format controls, PDF control |
| RSC Publishing | `pubs.rsc.org` | Journal page, issue archive, article page | `Cite this`, RIS/BibTeX controls, `PDF` |
| Wiley Online Library | `onlinelibrary.wiley.com` | Journal home, `Issues`, `Early View` | `Tools`, citation export, PDF control |
| Science/AAAS | `www.science.org` | Journal content, issue/archive, article page | `Citation`, downloadable citation, PDF control |
| Nature Portfolio | `www.nature.com` | Journal landing page, issue/archive, article page | `Cite this article`, RIS/BibTeX controls, `Download PDF` |

## Publisher-specific notes

### ScienceDirect

Search pages may expose a PII. Preserve it as a publisher identifier, but use the DOI as the cross-publisher identifier. Journal metrics are optional page content; report only the metric shown and its label.

### ACS Publications and RSC Publishing

ACS and RSC pages commonly use DOIs prominently. For chemistry workflows, preserve article type and supporting-information links if explicitly requested, but do not treat supporting information as a PDF download unless the user requests it separately.

### Wiley Online Library

Wiley hosts journals, books, and reference works. Confirm the content type before normalizing it as `journalArticle`; use `bookSection` or `book` only when the page makes that type clear.

### Science/AAAS and Nature Portfolio

These sites include news, commentary, research briefings, and research articles. Preserve the page's content type. Do not label editorial content as a research article.
