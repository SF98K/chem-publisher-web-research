# DOI 批量下载

## 输入与清单

输入支持 `.xlsx` 与 UTF-8 CSV。XLSX 仅读取第一个工作表。表格第一行必须有 `doi` 列名，大小写不敏感；可通过 `--doi-column` 指定其他列名。脚本会清除 `doi:` 和 `https://doi.org/` 前缀、按 DOI 去重，并生成 CSV 清单。重复 DOI 保留首次出现的行号；末尾标点可能属于 DOI，因此不自动删除，额外复制的标点需人工核对。原 Excel 不会被改写。输出文件已存在时拒绝覆盖，请直接恢复已有清单。

```powershell
python scripts\prepare_doi_batch.py --input .\papers.xlsx --output .\doi-download-manifest.csv
```

清单中的 `source_row` 指向原始表格行；`pending` 是等待处理的条目，`invalid-doi` 表示该单元格不是可用 DOI。

## 选择浏览器

先在 Chrome 或 Edge 完成学校校园网、VPN、WebVPN、EZproxy 或统一认证登录。使用 `@Chrome` 或 `@Edge` 启动任务。两个浏览器均可用时，优先选已经打开出版社页面且拥有访问权限的那个。

## 顺序处理

对每一条 `pending` 记录：

1. 打开 `doi_url`，确认最终的官方出版社页面和访问状态。
2. 仅在用户已授权下载且页面可见 PDF 下载入口时下载。
3. 将 PDF 保存到用户指定文件夹；检查文件非空且文件开头为 `%PDF-`。
4. 立即写入下载结果，避免中断后重复处理。

下载成功的示例：

```powershell
python scripts\record_doi_result.py --manifest .\doi-download-manifest.csv --source-row 12 --status downloaded --publisher "ACS Publications" --article-url "https://pubs.acs.org/doi/..." --pdf-path "D:\Papers\10.1021_example.pdf"
```

可用状态：`downloaded`、`unavailable`、`login-required`、`verification-required`、`failed`。`login-required` 和 `verification-required` 时，暂停浏览器操作，让用户在该浏览器完成认证后继续；不要尝试绕过认证。`unavailable` 可继续处理下一条。恢复时只处理 `pending` 或用户明确要求重试的失败状态。

## 输出字段

| 字段 | 含义 |
|---|---|
| `source_row` | 原始 Excel/CSV 的行号 |
| `source_doi` | 原始单元格内容 |
| `doi` / `doi_url` | 清洗后的 DOI 与 DOI 解析链接 |
| `status` | 当前处理状态 |
| `publisher` / `article_url` | 已识别的出版社和官方文章页 |
| `pdf_path` | 已下载 PDF 的本地路径 |
| `error` | 无法下载、认证失败或其他错误原因 |
