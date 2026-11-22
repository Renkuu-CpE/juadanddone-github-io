@echo off
setlocal EnableExtensions
title Juan and Done - local server

rem ============================================================
rem  Juan and Done - Windows launcher
rem  Double-click this file, or run it from PowerShell:
rem      .\tools\launch_juan_and_done_windows.bat
rem  Keep this window open while you use the website.
rem  Press Ctrl+C in this window to stop the server.
rem ============================================================

rem Go to the project folder (the folder that contains app.py), wherever it was unzipped.
cd /d "%~dp0.." || goto :nofolder
if not exist "app.py" goto :nofolder
if not exist "requirements.txt" goto :nofolder
if not exist "data\documents.json" (
  echo ERROR: data\documents.json is missing. Re-extract the full Project_Juan_and_Done zip.
  goto :end
)
echo.
echo ==== Juan and Done ====
echo Project folder: %CD%

rem Pick ONE Python and use it for everything (pip and streamlit), so they always match.
set "PY="
where py >nul 2>nul && py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && python -c "import sys" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo ERROR: Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
  echo        and tick "Add python.exe to PATH" during setup. See docs\04_WINDOWS_SETUP_AND_TROUBLESHOOTING.md
  goto :end
)
%PY% -c "import sys; print('Python', sys.version.split()[0], 'at', sys.executable); sys.exit(0 if sys.version_info >= (3, 9) else 1)"
if errorlevel 1 (
  echo ERROR: Python 3.9 or newer is required.
  goto :end
)

rem MSYS2 / MinGW Python (C:\msys64\...) has no pip and cannot install Streamlit's Windows packages.
%PY% -c "import sys; sys.exit(1 if 'msys' in sys.executable.lower() or 'mingw' in sys.version.lower() else 0)"
if errorlevel 1 (
  echo.
  echo ERROR: This is the MSYS2 Python ^(C:\msys64\...^). Streamlit cannot be installed into it.
  echo        Install the normal Windows Python 3.13 from https://www.python.org/downloads/
  echo        ^(tick "Add python.exe to PATH" and "py launcher"^), close this window, then run this file again.
  goto :end
)
%PY% -m pip --version >nul 2>nul
if errorlevel 1 (
  echo ERROR: pip is missing for this Python. Try:  %PY% -m ensurepip --upgrade
  echo        or reinstall Python from https://www.python.org/downloads/
  goto :end
)

rem Install Streamlit only if this same Python cannot import it yet.
%PY% -c "import streamlit" >nul 2>nul
if errorlevel 1 (
  echo Installing Streamlit for this Python ^(first run only, needs internet^)...
  %PY% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo ERROR: pip install failed. Copy the full message above for troubleshooting.
    goto :end
  )
)
%PY% -c "import streamlit; print('Streamlit', streamlit.__version__)"
if errorlevel 1 goto :end

rem Quick offline check of code + data (does not stop the launch on warnings).
%PY% tools\check_project.py >"%TEMP%\juan_and_done_check.txt" 2>&1
if errorlevel 1 (
  echo WARNING: tools\check_project.py reported a problem. Details: %TEMP%\juan_and_done_check.txt
) else (
  echo Project check: PASS
)

echo.
echo Starting Juan and Done... the browser will open at http://localhost:8501
echo If it does not open, copy the "Local URL" printed below into your browser.
echo There is NO "Email:" question any more (headless mode is set in .streamlit\config.toml).
echo Keep this window open. Press Ctrl+C here to stop.
echo.

rem Open the browser a few seconds later, in the background, so the server has time to start.
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 5; Start-Process 'http://localhost:8501'"

%PY% -m streamlit run app.py --server.headless true --browser.gatherUsageStats false
echo.
echo The Juan and Done server has stopped.
goto :end

:nofolder
echo ERROR: Could not find app.py. Keep this .bat file inside the "tools" folder of Project_Juan_and_Done.
goto :end

:end
echo.
pause
endlocal
