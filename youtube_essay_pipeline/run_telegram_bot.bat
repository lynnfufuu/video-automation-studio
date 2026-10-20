@echo off
title YouTube Horror Essay Pipeline - Telegram Bot
cd /d "%~dp0"
echo ======================================================================
echo    Starting YouTube Essay Pipeline - Telegram Remote Bot
echo ======================================================================
"C:\Users\yoshikiinyein\.gemini\antigravity\scratch\analog_lore_studio\.venv\Scripts\python.exe" -u bot\telegram_server.py
pause
