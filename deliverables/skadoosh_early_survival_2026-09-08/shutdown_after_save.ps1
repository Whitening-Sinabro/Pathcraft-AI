# Explicit user request: save the conversation/research record, then shut down.
# The short delay lets the final saved-file response reach the user.
Start-Sleep -Seconds 25
$shutdownRecordPath = 'D:\Pathcraft-AI\deliverables\skadoosh_early_survival_2026-09-08\conversation_checkpoint_validation.json'
$shutdownRecord = Get-Content -LiteralPath $shutdownRecordPath -Raw -Encoding UTF8 | ConvertFrom-Json
$shutdownRecord.shutdown.status = 'command_issued'
$shutdownRecord.shutdown.command_issued_at_utc = [DateTime]::UtcNow.ToString('o')
$shutdownUtf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($shutdownRecordPath, ($shutdownRecord | ConvertTo-Json -Depth 64), $shutdownUtf8)
& "$env:SystemRoot\System32\shutdown.exe" /s /t 0
$shutdownExitCode = $LASTEXITCODE
$shutdownRecord.shutdown.exit_code = $shutdownExitCode
if ($shutdownExitCode -eq 0) {
    $shutdownRecord.shutdown.status = 'windows_accepted_request'
} else {
    $shutdownRecord.shutdown.status = 'command_returned_error'
}
[System.IO.File]::WriteAllText($shutdownRecordPath, ($shutdownRecord | ConvertTo-Json -Depth 64), $shutdownUtf8)
