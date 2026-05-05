$urlCopied = $false
$pattern = 'https://[^\s''"]+'
$tunnelPattern = 'https://[^\s''"]*trycloudflare\.com[^\s''"]*'
$previousNativeSetting = $null

if ($PSVersionTable.PSVersion.Major -ge 7) {
    $previousNativeSetting = $PSNativeCommandUseErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
}

try {
    & cloudflared tunnel --url http://127.0.0.1:5000 2>&1 | ForEach-Object {
        $line = "$_"
        Write-Host $line

        if (-not $urlCopied -and $line -match $tunnelPattern) {
            $url = $matches[0]
            Set-Clipboard -Value $url
            Write-Host ""
            Write-Host "Copied remote URL to clipboard:" -ForegroundColor Green
            Write-Host $url -ForegroundColor Green
            Write-Host ""
            $urlCopied = $true
        }
    }
}
finally {
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        $PSNativeCommandUseErrorActionPreference = $previousNativeSetting
    }
}
