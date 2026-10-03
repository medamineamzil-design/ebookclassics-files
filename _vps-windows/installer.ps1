# BookClassics - installation complete sur le VPS Windows (a lancer UNE fois, PowerShell en administrateur) :
#   powershell -ExecutionPolicy Bypass -File installer.ps1
# Ensuite, chaque jour sans intervention : 10 h preparation du lot (Claude), 13 h publication (auto.sh).
$ErrorActionPreference = "Stop"
$K = $PSScriptRoot
$A = "$env:USERPROFILE\bookclassics-auto"

Write-Host "== 1/6 Logiciels (Git + Git Bash, Python, Pandoc, Typst, ImageMagick)"
foreach ($id in "Git.Git", "Python.Python.3.12", "JohnMacFarlane.Pandoc", "Typst.Typst", "ImageMagick.ImageMagick") {
  winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
}
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
# auto.sh appelle « python3 » : on cree python3.exe a cote de python.exe s'il manque
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($py -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { Copy-Item $py (Join-Path (Split-Path $py) "python3.exe") }

Write-Host "== 2/6 Claude Code"
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) { Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression }

Write-Host "== 3/6 Depots GitHub"
foreach ($r in "ebookclassics-site", "ebookclassics-files") {
  if (-not (Test-Path "$env:USERPROFILE\$r")) { git clone "https://github.com/medamineamzil-design/$r.git" "$env:USERPROFILE\$r" }
  git -C "$env:USERPROFILE\$r" config user.name "BookClassics VPS"
  git -C "$env:USERPROFILE\$r" config user.email "medamine.amzil@gmail.com"
}

Write-Host "== 4/6 Dossiers"
foreach ($d in "inbox", "faits", "erreurs", "journal", "travail-lot", "kit") { New-Item -ItemType Directory -Force "$A\$d" | Out-Null }
Copy-Item "$K\preparer_lot.ps1", "$K\publier.ps1", "$K\bibliothecaire.md" "$A\kit\" -Force

Write-Host "== 5/6 Taches planifiees (heure du VPS ; mettez le fuseau de Paris : Parametres > Heure)"
$user = "$env:USERDOMAIN\$env:USERNAME"
$pw = Read-Host "Mot de passe Windows de $user (pour lancer les taches meme sans session ouverte)" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pw))
foreach ($t in @(@{n="BookClassics-Preparation"; f="preparer_lot.ps1"; h="10:07"}, @{n="BookClassics-Publication"; f="publier.ps1"; h="13:03"})) {
  $act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$A\kit\$($t.f)`""
  $trg = New-ScheduledTaskTrigger -Daily -At $t.h
  $set = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 6)
  Register-ScheduledTask -TaskName $t.n -Action $act -Trigger $trg -Settings $set -User $user -Password $plain -Force | Out-Null
  Write-Host "   tache $($t.n) a $($t.h)"
}
$plain = $null

Write-Host "== 6/6 A faire par vous (une seule fois) - voir LISEZMOI.md :"
Write-Host "  1. Connecter Claude :        claude   (puis /login, puis /exit)"
Write-Host "  2. Autoriser GitHub en ecriture : git -C $env:USERPROFILE\ebookclassics-files push   (une fenetre de connexion GitHub s'ouvre)"
Write-Host "  3. Copier r2.conf du PC vers $env:USERPROFILE\r2.conf   (livres audio)"
Write-Host "  4. DESACTIVER la tache Windows « BookClassics » sur le PC (sinon double publication)"
Write-Host "  5. Test : Start-ScheduledTask BookClassics-Preparation, puis regarder $A\journal et $A\inbox"
