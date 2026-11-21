@echo off
rem Same as start.bat, but also shares the Camera Only and Guest overlays (scenes 5 and 6)
rem with other computers on the local network. The control panel stays on this PC only.
cd /d "%~dp0"
title District Assembly Overlay Server (network mode)
set DA_LAN=1
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
