# BookClassics : publication automatique 24 h/24 sur un VPS Windows

Une fois installé, le VPS fait tout seul, chaque jour :

| Heure | Tâche | Ce qu'elle fait |
|---|---|---|
| 10 h 07 | `BookClassics-Preparation` | Claude choisit 5 nouveaux livres, vérifie le domaine public, écrit les textes et dépose le lot dans `inbox\` |
| 13 h 03 | `BookClassics-Publication` | `auto.sh` fabrique EPUB/PDF/TXT/HTML, publie sur GitHub et sur le site, ajoute l'audio LibriVox |

Les comptes rendus vont dans `%USERPROFILE%\bookclassics-auto\journal\` (un fichier `preparation-…` et un fichier `publication-…` par jour).

## Installation (environ 15 minutes, une seule fois)

1. Connectez-vous au VPS par Bureau à distance.
2. Ouvrez **PowerShell en administrateur** et collez ces lignes :
   ```powershell
   $u = "https://raw.githubusercontent.com/medamineamzil-design/ebookclassics-files/main/_vps-windows"
   New-Item -ItemType Directory -Force "$env:USERPROFILE\kit-bookclassics" | Set-Location
   foreach ($f in "installer.ps1","preparer_lot.ps1","publier.ps1","bibliothecaire.md") { Invoke-WebRequest "$u/$f" -OutFile $f }
   powershell -ExecutionPolicy Bypass -File installer.ps1
   ```
   L'installation demande une fois votre mot de passe Windows. Il permet aux tâches de tourner même quand personne n'est connecté.
3. Fermez PowerShell, rouvrez-en un (normal), puis faites les étapes que l'installateur affiche à la fin :
   - `claude` → `/login` → connexion à votre compte Claude → `/exit`
   - `git -C $env:USERPROFILE\ebookclassics-files push` → acceptez la connexion GitHub (droit d'écrire sur vos dépôts)
   - copiez `r2.conf` du PC vers `C:\Users\<vous>\r2.conf` (pour les livres audio)
   - dans le Planificateur de tâches **du PC**, désactivez la tâche « BookClassics » (sinon double publication)
4. Réglez le fuseau horaire du VPS sur Paris (Paramètres > Heure et langue).
5. Test : `Start-ScheduledTask BookClassics-Preparation`, puis regardez `journal\` et `inbox\` (comptez jusqu'à 1 h).

## Garde-fous

- Claude **ne publie rien** : il dépose seulement le lot. La publication est faite par `auto.sh`, qui n'utilise pas d'IA.
- Claude n'a le droit ni de faire `git push`, ni de toucher aux mots de passe et clés, ni d'envoyer des emails.
- Si un lot du jour précédent n'a pas été publié, Claude n'en prépare pas de nouveau.
- Pour tout arrêter : désactivez les deux tâches `BookClassics-…` dans le Planificateur de tâches.
