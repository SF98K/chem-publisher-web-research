param(
    [ValidateSet('Inspect','Navigate','Invoke')][string]$Action = 'Inspect',
    [string]$Url,
    [string]$Name,
    [int]$WindowHandle = 0
)

# Control the existing interactive Edge session via Windows accessibility.
# Never starts an automation profile, copies cookies, or enables debugging ports.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
$scope = [System.Windows.Automation.TreeScope]
$all = [System.Windows.Automation.Condition]::TrueCondition
$edgeIds = @(Get-Process msedge -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$windows = @([System.Windows.Automation.AutomationElement]::RootElement.FindAll($scope::Children, $all) | Where-Object {
    $_.Current.ProcessId -in $edgeIds -and $_.Current.ClassName -eq 'Chrome_WidgetWin_1' -and
    ($WindowHandle -eq 0 -or $_.Current.NativeWindowHandle -eq $WindowHandle)
})
if ($windows.Count -ne 1) {
    $windows | ForEach-Object { [pscustomobject]@{Title=$_.Current.Name;Handle=$_.Current.NativeWindowHandle} } | ConvertTo-Json
    throw 'Expected one visible Edge window. Open Edge normally, or select a listed -WindowHandle.'
}
$window = $windows[0]
$items = @($window.FindAll($scope::Descendants, $all))
if ($Action -eq 'Inspect') {
    $items | Where-Object { $_.Current.ControlType.ProgrammaticName -match 'TabItem|Edit|Document|Hyperlink|Button|Text' } | ForEach-Object {
        $value = $null
        if ($_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit -and $_.Current.Name -match '地址和搜索栏|Address and search bar') {
            $pattern = $null
            if ($_.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) { $value = $pattern.Current.Value }
        }
        [pscustomobject]@{Type=$_.Current.ControlType.ProgrammaticName;Name=$_.Current.Name;Value=$value;Enabled=$_.Current.IsEnabled}
    } | ConvertTo-Json -Depth 3
    exit
}
if ($Action -eq 'Navigate') {
    $parsed = $null
    if (-not [uri]::TryCreate($Url,[UriKind]::Absolute,[ref]$parsed) -or $parsed.Scheme -notin @('http','https')) { throw 'Navigate requires an absolute HTTP(S) URL.' }
    $addresses = @($items | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit -and $_.Current.Name -match '地址和搜索栏|Address and search bar' })
    if ($addresses.Count -ne 1) { throw 'Cannot uniquely identify Edge address bar. No navigation performed.' }
    $addresses[0].SetFocus()
    $pattern = $addresses[0].GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    $pattern.SetValue($Url)
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Write-Output 'Navigation requested in the current Edge tab; inspect again to verify the result.'
    exit
}
if (-not $Name) { throw 'Invoke requires the exact visible control -Name obtained from Inspect.' }
$matches = @($items | Where-Object { $_.Current.Name -ceq $Name -and $_.Current.IsEnabled -and -not $_.Current.IsOffscreen })
if ($matches.Count -ne 1) { throw 'Control is missing or ambiguous. Inspect again; no click performed.' }
$invoke = $null
if (-not $matches[0].TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern,[ref]$invoke)) { throw 'Control does not expose InvokePattern. Manual interaction is required.' }
$invoke.Invoke()
Write-Output 'Control invoked; inspect again to verify the result.'
