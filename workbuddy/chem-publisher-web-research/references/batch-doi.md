# DOI 表格批量处理

## 输入与首次建表

输入文件可以是 `.xlsx` 或 UTF-8 编码的 `.csv`。首行必须有 `doi` 列，列名不区分大小写；`.xls` 请先另存为 `.xlsx`。

从 Skill 根目录运行：

```bash
python3 scripts/prepare_doi_batch.py --input "/path/to/input.xlsx" --output "/path/to/doi-download-manifest.csv"
```

如果运行环境没有 `python3` 命令，可改用其已配置的 Python 命令。脚本不联网，不下载 PDF。它会清理 DOI 前缀、保留来源行号、忽略空行，并将重复 DOI 只保留一次。

清单包含：`source_row`、`source_doi`、`doi`、`doi_url`、`status`、`publisher`、`article_url`、`pdf_path` 和 `error`。

## 逐条访问和记录

仅当 WorkBuddy 当前提供的浏览器工具能打开出版社页面，并且该会话已经具有用户的学校 IP 或本人已登录账号所授予的访问权限时，才按清单顺序处理。不得假设 WorkBuddy 会共享本机 Chrome、Edge 或其他浏览器的登录状态。

对每篇文章：

1. 打开清单中的 `doi_url`，确认落地文章页及其页面显示的访问状态。
2. 用户明确要求下载且存在可访问的 PDF 链接时，下载到用户指定目录。
3. 无论成功或失败，立刻更新一行清单，确保任务可中断后恢复。

更新命令示例：

```bash
python3 scripts/record_doi_result.py --manifest "/path/to/doi-download-manifest.csv" --source-row 2 --status downloaded --publisher "ACS Publications" --article-url "https://..." --pdf-path "/path/to/file.pdf"
```

可用状态包括：

- `downloaded`：PDF 已实际保存，填写 `pdf_path`。
- `unavailable`：页面没有可访问 PDF，或用户无权访问。
- `login-required`：需要用户在当前浏览器会话中登录。
- `verification-required`：网站要求验证码或人工验证。
- `failed`：其他可说明的技术失败。

`record_doi_result.py` 用临时文件替换原清单，单次更新不会破坏原 CSV。不要并发修改同一个清单文件。

## 遇到认证页面时

停在认证或验证页面，并把当前条目记录为相应状态，暂停受影响站点。用户自行完成登录或验证后，只重试用户指定的失败条目及 pending 条目，跳过 invalid-doi。

已有清单时直接恢复；生成脚本拒绝覆盖已有文件。仅读取 XLSX 第一个工作表，第一行必须是表头。重复 DOI 只保留首次出现的来源行号。DOI 中的末尾标点可能属于标识符，因此保留原值；从正文复制的额外标点需人工核对。

没有浏览器工具时保留 pending，不得批量标记 unavailable。只有验证实际文件为目标文章 PDF 后才记录 downloaded。引用导出文件可在 Zotero 的“文件 → 导入”中手动导入；本包不自带 Zotero 自动连接脚本。
