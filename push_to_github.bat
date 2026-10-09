@echo off
cd /d "%~dp0"
title Push District Assembly to GitHub
where git >nul 2>nul
if not %errorlevel%==0 (
  echo Git is not installed. Get it from https://git-scm.com/download/win
  pause
  exit /b
)
if not exist ".git" (
  git init -b main
  git remote add origin https://github.com/StanleyPangaruy/lopez-district-assembly.git
)
git add -A
git commit -m "Update District Assembly overlays"
git push -u origin main
echo.
echo Done. If a GitHub sign-in window appeared, sign in and run this again if needed.
pause
