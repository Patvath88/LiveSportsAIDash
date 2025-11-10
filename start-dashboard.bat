@echo off
REM ============================================================
REM  NBA AI Dashboard - Full Stack Startup (PowerShell-proof)
REM ============================================================

:: --- Detect if script was started from PowerShell -------------
:: PowerShell passes the variable $PSVersionTable, so this works
if "%ComSpec%"=="" (
    echo [INFO] Relaunching in Command Prompt...
    start cmd /k "%~f0"
    exit /b
)

:: --- Normal startup path -------------------------------------
title NBA AI Dashboard - Full Stack Startup
echo.
echo 🧱  Launching NBA AI Dashboard...
echo.

:: --- Start Backend -------------------------------------------
start cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload"

:: Wait a few seconds so backend is up before frontend starts
timeout /t 5 >nul

:: --- Start Frontend ------------------------------------------
start cmd /k "cd frontend && npm run dev"

echo.
echo ✅  All systems online!
echo ---------------------------------------
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173
echo ---------------------------------------
echo.
pause

