@echo off
setlocal enabledelayedexpansion

:: Window Title - Avoid unescaped ampersand so cmd does not treat descriptive text as a command
title Multimodal Attendance and Engagement Agent

echo ==========================================================
echo Starting Multimodal Attendance and Engagement Agent...
echo ==========================================================

:: 1. Prefer user's direct local Python 3.13 installation
set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto found
)

:: 2. Search other LocalAppData Python versions
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto found
    )
)

:: 3. Check Program Files
for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto found
    )
)

:: 4. Test if 'python' command runs (verifying it is not a dead WindowsApps redirector)
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto found
)

:: 5. Test if 'py' launcher is configured
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py"
    goto found
)

:found
if "%PYTHON_EXE%"=="" (
    echo [ERROR] No working Python installation was found.
    echo Please install Python 3.10+ or add python.exe to PATH.
    echo ==========================================================
    pause
    exit /b 1
)

echo Using Python: "%PYTHON_EXE%"
echo Starting Streamlit on port 8501...
echo Dashboard URL: http://localhost:8501
echo ==========================================================
echo.

:: Automatically launch default web browser
start "" "http://localhost:8501"

"%PYTHON_EXE%" -m streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application stopped or encountered an error (exit code %ERRORLEVEL%).
    pause
)
