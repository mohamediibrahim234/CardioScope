@echo off
setlocal
cd /d "%~dp0"
title CardioScope - Heart Disease API

rem ---- create the project environment on first run ----
if not exist ".venv\Scripts\python.exe" (
    echo [setup] Creating virtual environment in .venv ...
    where uv >nul 2>nul
    if errorlevel 1 (
        python -m venv .venv || goto :fail
        .venv\Scripts\python.exe -m pip install --upgrade pip
        .venv\Scripts\python.exe -m pip install -r requirements.txt || goto :fail
    ) else (
        uv venv .venv --python 3.12 || goto :fail
        uv pip install --python .venv\Scripts\python.exe -r requirements.txt || goto :fail
    )
)

echo.
rem Picks a free port (8000 or the next free one), starts the server and
rem opens the browser once THIS API answers /health.
.venv\Scripts\python.exe -m app.launcher
if errorlevel 1 goto :fail
goto :eof

:fail
echo.
echo [error] Something went wrong. Read the messages above.
pause
exit /b 1
