# Windows：操作当前 Edge 会话

用户要求使用日常 Edge 时，先尝试宿主实际提供的浏览器连接工具，并确认它能列出用户当前打开的标签页。`@Edge` 只是宿主可能提供的入口，不是本 Skill 自带的连接能力。

没有已连接工具时，Windows 交互桌面可以使用本包的 UI Automation 辅助脚本。它操作现有 Edge 窗口，不启动独立 profile、不复制 Cookie、不打开调试端口。需要 PowerShell、Edge 和可用的 Windows 交互桌面；锁屏或不可访问的控件可能导致失败。

```powershell
./scripts/edge_current_session.ps1 -Action Inspect
./scripts/edge_current_session.ps1 -Action Navigate -Url 'https://www.sciencedirect.com/'
./scripts/edge_current_session.ps1 -Action Inspect
```

Navigate 会改变当前标签页。先确认当前页适合用于任务；需要新标签时，从 Inspect 输出中找到“新建标签页”按钮，用 Invoke 点击后重新检查。不要覆盖用户不相关的页面。

```powershell
./scripts/edge_current_session.ps1 -Action Invoke -Name '新建标签页'
```

Invoke 的 Name 必须来自刚刚读取的可见控件，且只能匹配一个控件。多个 Edge 窗口时，按错误输出的句柄传入 `-WindowHandle`。脚本不支持的控件操作必须报告，不得声称已经点击。

找到文章页面的实际 PDF 控件后，可以用 Invoke 执行普通下载。下载完成仍需确认实际保存路径、PDF 文件头和文章身份；本脚本不提供自动等待下载、另存为对话框处理或文件身份核验。不能用“点击已成功”代替“文件已保存”。

出现学校登录或真人验证时，停留在同一标签页，由用户完成后再次 Inspect；不新建 profile，也不重复刷新验证页面。没有确认学校访问权限时，不将浏览器连接成功等同于订阅论文可下载。

2026-09-17 的本机试验：已验证读取现有 Edge 标签页、通过地址栏导航及读取 ScienceDirect 页面；该网站随后要求真人验证，尚未验证订阅 PDF 下载。此结果不能推断其他用户的机构访问状态。
