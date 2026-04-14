# 2026-04-14-08-14 Install Scoop and ffmpeg

**2026-04-14**
- Installed Scoop (Windows package manager) via PowerShell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` followed by `Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression`
- Installed ffmpeg via `scoop install ffmpeg`
- Future updates: `scoop update ffmpeg` or `scoop update *` to update everything at once
- No project code was changed
