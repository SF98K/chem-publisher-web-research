# Publisher Web Research Skill（出版社网页文献助手）

这是一个面向 Codex 的学术文献工作流 Skill，帮助中文使用者在出版社官网完成期刊浏览、文章信息提取、引用导出、已授权 PDF 下载和 Zotero 导入。

支持的出版商：ScienceDirect、ACS Publications、RSC Publishing、Wiley Online Library、Science/AAAS 和 Nature Portfolio。

## 它能做什么

| 你想做的事 | Skill 会输出什么 |
|---|---|
| 浏览期刊、最新文章或指定期次 | 期刊官网链接、所选期次/最新文章和文章链接 |
| 查看一篇论文的信息 | 标题、作者、期刊、日期、卷期页码或文章号、DOI、摘要/关键词（页面可见时）和访问状态 |
| 导出引用 | 优先导出出版社页面提供的 RIS 或 BibTeX；没有原生导出时，明确标记为“页面提取元数据” |
| 下载 PDF | 在你已有访问权限时下载 PDF，并报告开放获取、已认证访问或不可访问状态 |
| 导入 Zotero | 将 RIS 文件或整理好的 JSON 文献信息导入正在运行的 Zotero 桌面端 |

## 使用前：先让浏览器获得学校访问权限

这个 Skill 不会登录学校系统，也不会输入账号密码。你需要先用浏览器完成访问认证，之后再让 Skill 从已打开的页面继续操作。

### 场景 1：在校园网内

1. 连接学校有线网或校园 Wi-Fi。
2. 在浏览器打开出版社文章页，例如 ScienceDirect、ACS、RSC、Wiley、Science 或 Nature。
3. 确认网页显示 `PDF`、`Download PDF`、`View PDF` 等可用下载入口。
4. 在 Codex 中使用下方示例发出请求。

### 场景 2：校外访问

1. 先登录学校提供的 VPN、WebVPN、EZproxy 或统一认证入口。
2. 保持该浏览器标签页处于登录状态，再打开出版社文章页。
3. 确认文章页能显示 PDF 下载入口。
4. 在 Codex 中告诉 Skill 你已经登录学校 VPN，并给出文章链接或说明当前浏览器页已打开。

如果网页要求重新登录、机构认证或人工验证，Skill 会暂停并提示你在浏览器中完成该操作；完成后再继续。

## 安装

将本仓库完整复制到 Codex 的 Skill 目录：

```text
C:\Users\你的用户名\.codex\skills\publisher-web-research
```

然后重新开始一轮 Codex 对话，使 Skill 被发现。

## 怎么调用

在对话中使用 `$publisher-web-research` 加上你的任务。以下命令可以直接复制后修改：

```text
$publisher-web-research 浏览 ACS Catalysis 最新一期，列出催化方向文章及文章链接。
```

```text
$publisher-web-research 我在校园网中打开了这篇 ScienceDirect 文章：https://www.sciencedirect.com/… 。提取 DOI、摘要、作者、卷期页码，并导出 RIS 引用。
```

```text
$publisher-web-research 我已经通过学校 VPN 登录 Wiley。检查当前文章能否下载 PDF；若可访问，下载到 D:\Papers，并报告保存路径。
```

```text
$publisher-web-research 从这个 Nature 文章页面提取元数据，导出 BibTeX，并导入 Zotero。
```

```text
$publisher-web-research 浏览 RSC 的 Journal of Materials Chemistry A 当前期，筛选电催化相关文章。
```

## PDF 下载与访问边界

Skill 只会在以下条件同时满足时下载 PDF：

1. 你明确要求下载；
2. 当前浏览器页面可见 PDF 下载入口；
3. 当前校园 IP、VPN 或个人订阅确实允许访问。

它不会绕过付费墙、机构访问限制或人工验证。页面没有访问权限时，仍可提取论文元数据、导出引用或帮助你定位官方文章页。

## 导入 Zotero

先启动 Zotero 桌面端，并在其中选中一个可写入的文献库或文件夹。进入本 Skill 目录后，运行以下任一命令：

```powershell
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --ris-file .\citation.ris
```

```powershell
C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe scripts\push_to_zotero.py --json-file .\paper.json
```

工具只连接本机 Zotero Connector 地址 `127.0.0.1`，不会访问出版社网站。若已经下载 PDF，请在 Zotero 中选择对应条目，再使用“添加附件”→“附加文件副本”加入本地 PDF。

## 浏览器控制说明

要让 Skill 直接操作已登录的浏览器页面，当前 Codex 会话需要接入浏览器控制工具。没有这类工具时，Skill 仍可：

- 提供出版社官方页面路径；
- 整理你给出的文章链接和页面信息；
- 处理你手动下载的 RIS/BibTeX；
- 将 RIS 或 JSON 导入 Zotero。

## 验证

```powershell
.\tests\test_skill_contract.ps1
.\tests\test_zotero_script.ps1
```

## 来源与许可证

本项目的工作流边界参考了 [cookjohn/sd-skills](https://github.com/cookjohn/sd-skills) 的 ScienceDirect 工作流，并针对 Codex 和多出版商网页使用场景改写。本仓库不包含其 Chrome 自动化、反检测配置或会话处理代码。

本项目采用 [MIT License](LICENSE)。
