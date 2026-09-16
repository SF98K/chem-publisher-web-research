---
name: chem-publisher-web-research
display_name: 出版社网页文献与 DOI 批量下载
display_name_en: Publisher Web Research and DOI Batch Download
description: 面向六类出版社网页的文献浏览、引用导出与 DOI 表格批量下载工作流
description_zh: 面向 ScienceDirect、ACS、RSC、Wiley、Science 和 Nature 的网页文献浏览、引用导出与 DOI 表格批量下载工作流。
description_en: Browse publisher-hosted literature, export citations, and prepare authorized DOI batch downloads for six major publisher families.
category: research
version: 1.0.1
author: SF98K
disable-model-invocation: false
user-invocable: true
---

# 出版社网页文献与 DOI 批量下载

用于在出版社网页上查找化学及相关学科文献，并处理引用导出、Zotero 导入和 DOI 表格批量下载。支持 ScienceDirect、ACS Publications、RSC Publishing、Wiley Online Library、Science/AAAS 和 Nature Portfolio。

## 先确认用户目标

用户可以提供单篇 DOI、文章或期刊网页链接、期刊名称，或含 `doi` 列的 Excel/CSV 表格。先说明将输出什么：网页元数据、RIS/BibTeX 引用文件、Zotero 导入结果、DOI 清单，或已获授权访问的 PDF 文件。

识别出版社和页面入口时，读取 @references/publishers.md。处理 DOI 表格时，读取 @references/batch-doi.md。

## 单篇文献工作流

1. 打开或定位用户提供的文章页、期刊页或 DOI 解析后的网页，确认文章标题、作者、期刊、年份、DOI 和页面所示的访问状态。
2. 用户要求引用时，优先使用页面提供的 RIS、BibTeX 或 EndNote 导出入口；若页面没有导出入口，再明确说明引用信息来自页面字段。
3. 用户要求加入 Zotero 时，先保存 RIS/BibTeX。仅当当前环境已连接可写入的 Zotero 工具时执行导入并核验条目；否则交付引用文件，指导用户在 Zotero 中选择“文件 → 导入”。本包没有自动连接桌面 Zotero 的脚本，不能声称已自动导入。
4. 用户要求下载 PDF 时，只有在当前 WorkBuddy 环境可用的浏览器或 Agent Browser 已打开该出版社页面、页面显示可访问的 PDF 链接且该会话具有用户学校或个人的合法访问权限时，才执行下载。

不要尝试绕过付费墙、登录、验证码、访问限制或机构认证。若页面要求登录、验证或没有可访问 PDF 链接，报告页面状态并提供文章页和 DOI 链接。

## DOI 表格批量工作流

从本 Skill 目录执行下列命令生成可恢复的清单：

```bash
python3 scripts/prepare_doi_batch.py --input "/path/to/input.xlsx" --output "/path/to/doi-download-manifest.csv"
```

输入支持 `.xlsx` 和 UTF-8 `.csv`，第一行需要有名为 `doi` 的列名（不区分大小写）。脚本会保留原始行号、规范化 DOI、DOI URL 和处理状态，并将重复 DOI 合并为一条待处理记录。

如当前环境提供并已连接到具有合法访问权限的浏览器，按清单逐条访问 `doi_url`，不要并发批量点击下载。每完成一条，立即更新清单：

```bash
python3 scripts/record_doi_result.py --manifest "/path/to/doi-download-manifest.csv" --source-row 2 --status downloaded --publisher "Publisher" --article-url "https://..." --pdf-path "/path/to/file.pdf"
```

`--source-row` 必须取自当前清单条目的 source_row，不是清单自身的行号。已有清单时直接恢复，不要重新生成覆盖进度；默认只处理 pending，失败条目仅在用户要求重试时处理。

若当前 WorkBuddy 没有可用浏览器工具，保留 pending 并报告环境限制，不得记成文献无法访问。需要登录或验证码时，记录 login-required 或 verification-required 并暂停受影响站点，等待用户完成操作，不要反复访问该站点。只有实际保存并确认文件为对应文章 PDF 后才记录 downloaded；HTML 登录页不能算下载成功。

## 输出要求

- 对单篇文献，给出出版社页面链接、确认过的 DOI、访问状态，以及引用导出或 PDF 的实际结果。
- 对批量任务，交付 `doi-download-manifest.csv`；不要把“已生成 DOI 链接”表述为“已下载 PDF”。
- 说明下载是否依赖当前浏览器会话的学校 IP 或已登录账号。WorkBuddy 的浏览器会话是否共享本机浏览器登录状态取决于平台实际能力，未确认时不得假定共享。

## 常用请求示例

- “查找这个 DOI 在 ACS 页面上的信息，并导出 RIS。”
- “浏览 Nature Communications 的某期目录，列出与催化有关的文章。”
- “把这个 Excel 中 `doi` 列生成下载清单；只有页面已显示可下载 PDF 时才保存。”
- “将这几篇 Wiley 文章的引用导入 Zotero，并保留 RIS 文件。”
