@echo off
cd /d "%~dp0.."
".venv-demo\Scripts\python.exe" -m streamlit run demo/app.py --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false --theme.base=light --theme.primaryColor=#126453 --theme.backgroundColor=#fbfaf6 --theme.secondaryBackgroundColor=#edf1ec --client.toolbarMode=minimal
if errorlevel 1 pause

