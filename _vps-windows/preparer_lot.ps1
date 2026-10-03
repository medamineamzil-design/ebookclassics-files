# BookClassics - 10 h : le bibliothecaire (Claude) prepare le lot du jour dans ~/bookclassics-auto/inbox.
$OutputEncoding = [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
$A = "$env:USERPROFILE\bookclassics-auto"
$J = "$A\journal\preparation-$(Get-Date -Format yyyy-MM-dd).txt"
New-Item -ItemType Directory -Force "$A\travail-lot" | Out-Null

git -C "$env:USERPROFILE\ebookclassics-site" pull -q --rebase --autostash
git -C "$env:USERPROFILE\ebookclassics-files" pull -q --rebase --autostash

Set-Location "$env:USERPROFILE\ebookclassics-site"
Get-Content "$A\kit\bibliothecaire.md" -Raw -Encoding UTF8 |
  claude -p --allowedTools "Bash Read Write Edit Glob Grep WebSearch WebFetch" *>&1 |
  Out-File $J -Encoding utf8
"FIN preparation $(Get-Date -Format 'yyyy-MM-dd HH:mm') (code $LASTEXITCODE)" | Out-File $J -Append -Encoding utf8
