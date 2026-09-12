# Publisher Web Research Skill

Codex Skill for publisher-hosted research workflows across ScienceDirect, ACS Publications, RSC Publishing, Wiley Online Library, Science/AAAS, and Nature Portfolio.

It helps with journal and issue browsing, visible article metadata extraction, publisher-native RIS/BibTeX export, accessible PDF downloads, and local Zotero import.

## What it supports

| Workflow | Result |
|---|---|
| Journal browsing | Journal URL, requested issue/current content, and article links |
| Article inspection | Normalized visible metadata, DOI, abstract/keywords when shown, and access state |
| Citation export | Publisher-native RIS/BibTeX where available; otherwise clearly labelled page-extracted metadata |
| PDF download | Downloads a PDF only when the user requests it and the active browser session visibly has access |
| Zotero | Imports a publisher RIS file or normalized JSON into a running local Zotero desktop app |

## Access model

Use it on campus through institutional IP access, or off campus after you have completed your institution's VPN, WebVPN, EZproxy, or single-sign-on flow in a browser.

The Skill uses the access already visible in that browser session. It does not enter credentials, retain browser session information, forward session data to scripts, bypass paywalls, or work around human-verification requests.

## Install

Copy this directory into your Codex Skills directory:

```text
C:\Users\<you>\.codex\skills\publisher-web-research
```

Then invoke it with requests such as:

```text
$publisher-web-research 浏览 ACS Catalysis 最新一期，列出催化方向文章。
$publisher-web-research 从这个 Nature 文章页提取 DOI、摘要和 RIS 引用。
$publisher-web-research 在我已经登录学校 VPN 的 Wiley 页面下载 PDF，并导入 Zotero。
```

Browser-page operations require a Codex session with an available browser-control integration. Without one, the Skill can still provide the official page route, normalize metadata supplied by the user, and import locally exported citation files into Zotero.

## Zotero import

Start Zotero desktop and select a writable collection. Then run either command from this directory:

```powershell
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --ris-file .\citation.ris
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --json-file .\paper.json
```

The helper only contacts Zotero's local Connector endpoint (`127.0.0.1`). For a downloaded PDF, attach the local file in Zotero desktop after importing its citation.

## Validation

```powershell
.\tests\test_skill_contract.ps1
.\tests\test_zotero_script.ps1
```

## Provenance

The workflow boundaries were adapted for Codex from [cookjohn/sd-skills](https://github.com/cookjohn/sd-skills), which provides a ScienceDirect-focused Claude Code workflow under the MIT License. This repository does not include its Chrome automation, browser-evasion settings, or session-handling code.

## License

MIT. See [LICENSE](LICENSE).
