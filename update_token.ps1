# Token自动更新脚本
# 使用方法: .\update_token.ps1 -NewToken "Bearer eyJ0eXAi..."

param(
    [Parameter(Mandatory=$true)]
    [string]$NewToken
)

$configPath = Join-Path $PSScriptRoot "config.py"

if (-not (Test-Path $configPath)) {
    Write-Error "找不到config.py文件"
    exit 1
}

try {
    # 读取配置文件
    $content = Get-Content $configPath -Raw
    
    # 备份原配置
    $backupPath = Join-Path $PSScriptRoot "config.py.backup"
    Copy-Item $configPath $backupPath -Force
    Write-Host "已备份配置文件到: $backupPath" -ForegroundColor Green
    
    # 更新Token
    $pattern = 'BEARER_TOKEN = "Bearer [^"]*"'
    $replacement = "BEARER_TOKEN = `"$NewToken`""
    $newContent = $content -replace $pattern, $replacement
    
    # 更新日期注释
    $today = Get-Date -Format "yyyy-MM-dd"
    $datePattern = '# 最后更新时间: \d{4}-\d{2}-\d{2}'
    $dateReplacement = "# 最后更新时间: $today"
    $newContent = $newContent -replace $datePattern, $dateReplacement
    
    # 保存文件
    Set-Content $configPath $newContent -Encoding UTF8
    
    Write-Host "Token更新成功！" -ForegroundColor Green
    Write-Host "最后更新时间: $today" -ForegroundColor Cyan
    
} catch {
    Write-Error "更新Token失败: $_"
    
    # 恢复备份
    if (Test-Path $backupPath) {
        Copy-Item $backupPath $configPath -Force
        Write-Host "已恢复备份" -ForegroundColor Yellow
    }
    exit 1
}
