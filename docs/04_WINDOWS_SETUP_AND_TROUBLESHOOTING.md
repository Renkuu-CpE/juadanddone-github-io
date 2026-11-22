# 04 · Windows Setup and Troubleshooting

## A. Unzip without double nesting

1. Right-click `Project_Juan_and_Done.zip` → **Extract All…**
2. In the destination box, **remove the last folder name** so it ends in `…\Downloads` (not `…\Downloads\Project_Juan_and_Done`). The zip already contains the `Project_Juan_and_Done` folder.
3. You should now have `C:\Users\<you>\Downloads\Project_Juan_and_Done\app.py`. **Do not extract into `C:\Windows\System32`** or `Program Files` (not writable).

## B. Launch (choose one)

**Option 1: double-click** `tools\launch_juan_and_done_windows.bat`. It:
- goes to the project folder automatically,
- picks one Python (`py -3`, else `python`) and uses it for both pip and Streamlit,
- installs Streamlit only if that Python does not have it,
- runs `tools\check_project.py`,
- starts the server in headless mode and opens `http://localhost:8501` after ~5 seconds.

**Option 2: PowerShell**

```powershell
cd "$HOME\Downloads\Project_Juan_and_Done"
Get-Location                       # must end in \Project_Juan_and_Done
Test-Path .\app.py, .\requirements.txt, .\data\documents.json   # True True True

python --version                   # 3.10+ recommended
python -m pip install -r requirements.txt
python -c "import sys, streamlit; print(sys.executable); print(streamlit.__version__)"
python tools\check_project.py      # expect: Summary: 0 FAIL
python -m streamlit run app.py
```

Open the printed **Local URL** (normally `http://localhost:8501`). Keep the window open; **Ctrl+C** stops the server.

If `python` opens the Microsoft Store or is "not recognized", use `py -3` everywhere (e.g. `py -3 -m pip install -r requirements.txt`, `py -3 -m streamlit run app.py`). If neither works, install Python from python.org and tick **Add python.exe to PATH**.

## C. The old `Email:` prompt

Streamlit asks for an e-mail on its first run only when not in headless mode. This project sets `server.headless = true` in `.streamlit\config.toml` and the launcher also passes `--server.headless true`, so the prompt should not appear. If you ever see `Email:` (e.g. you ran Streamlit from a different folder so the config was not read), **press Enter on the empty line**. Never type a command there; that produces `That doesn't look like an email :(`.

## D. Error dictionary

| Symptom | Likely cause | Fix |
|---|---|---|
| `No module named 'streamlit'` | Streamlit installed for a different Python | Run pip and streamlit with the **same** command: `python -m pip …` then `python -m streamlit …` (or `py -3` for both) |
| `Could not open requirements file` | Terminal is in the wrong folder | `cd` into the folder that contains `app.py`; check with `Test-Path .\app.py` |
| `python app.py` shows warnings and no website | Streamlit apps must start through Streamlit | `python -m streamlit run app.py` |
| Browser says "can't reach this page" | Server not running yet, stopped, or on another port | Look at the terminal for the Local URL / a traceback; wait a few seconds and refresh |
| Port 8501 busy | An older server is still running | Close the old window, or use the port Streamlit prints (8502…). Check with `netstat -ano \| findstr :8501` |
| Red "Hindi ma-load ang datos" screen | `data\documents.json` missing or edited into invalid JSON | Restore the file from the zip, run `python tools\check_project.py`, press **Retry** |
| Yellow "Hindi ma-save ang progress" banner | Folder is read-only (e.g. inside Program Files or a synced/locked folder) | Move the project to `Documents` or `Downloads` |
| Ticks disappear after reopening | Different profile name, or a different copy of the project folder | Use the same profile (shown under the header) and the same folder; progress lives in that folder's `data\juan_and_done_progress.db` |
| Layout looks plain / fonts missing | Very old or very new Streamlit, or `assets\fonts` missing | `python -m pip install "streamlit>=1.42,<2.0"`; re-extract `assets` |
| `.bat` window closes instantly | Opened from inside the zip without extracting | Extract first (section A), then double-click |
| PowerShell blocks scripts | Not needed: the launcher is a `.bat`, and `python -m …` commands are not scripts | — |

## E. Backups

`data\juan_and_done_progress.db` appears after the first tick. Copy it somewhere safe before deleting, moving or re-extracting the project; a fresh extract starts with no progress.

## F. What to send if it still fails

1. Output of `python --version` and `python -c "import sys, streamlit; print(sys.executable, streamlit.__version__)"`.
2. Full output of `python tools\check_project.py`.
3. A screenshot of the PowerShell window **after** running `python -m streamlit run app.py`, including any red traceback.
4. The URL you opened and what the browser showed.
