# BookClassics - 13 h : publie les lots de l'inbox avec auto.sh (meme script que sur le PC) et ecrit le journal du jour.
$A = "$env:USERPROFILE\bookclassics-auto"
$J = "$A\journal\publication-$(Get-Date -Format yyyy-MM-dd).txt"
$Bash = "C:\Program Files\Git\bin\bash.exe"
git -C "$env:USERPROFILE\ebookclassics-files" pull -q --rebase --autostash
& $Bash -lc "~/ebookclassics-site/_auto/auto.sh" *>&1 | Out-File $J -Encoding utf8
