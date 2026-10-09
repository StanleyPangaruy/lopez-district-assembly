@echo off
cd /d "%~dp0"
title District Assembly Overlay Server
where py >nul 2>nul
if %errorlevel%==0 (
  py server.py
  goto done
)
where python >nul 2>nul
if %errorlevel%==0 (
  python server.py
  goto done
)
echo Python was not found. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
:done
pause
