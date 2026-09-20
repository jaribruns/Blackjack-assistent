@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo   Blackjack Assistant - opstarten
echo ============================================
echo.

REM ---- Python vinden (probeer 'py' eerst, dan 'python') ----
set PYCMD=
py --version >nul 2>&1
if not errorlevel 1 set PYCMD=py
if "%PYCMD%"=="" (
    python --version >nul 2>&1
    if not errorlevel 1 set PYCMD=python
)
if "%PYCMD%"=="" (
    echo [FOUT] Python is niet gevonden.
    echo Installeer Python via https://www.python.org/downloads/
    echo Vink tijdens installatie AAN: "Add python.exe to PATH" EN "tcl/tk and IDLE"
    echo.
    pause
    exit /b 1
)
echo Python gevonden: !PYCMD!

REM ---- venv aanmaken als die nog niet bestaat ----
if not exist "venv\Scripts\activate.bat" (
    echo Eerste keer starten - virtuele omgeving aanmaken...
    !PYCMD! -m venv venv
    if errorlevel 1 (
        echo [FOUT] Kon de virtuele omgeving niet aanmaken.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

REM ---- dependencies installeren als ze nog missen ----
python -c "import cv2, mss, numpy" >nul 2>&1
if errorlevel 1 (
    echo Benodigde pakketten installeren, dit duurt even ^(eenmalig^)...
    pip install --disable-pip-version-check -q mss opencv-python numpy pyinstaller
    if errorlevel 1 (
        echo [FOUT] Installeren van pakketten mislukt. Zie foutmelding hierboven.
        pause
        exit /b 1
    )
)

REM ---- tkinter (schermvensters) testen ----
python -c "import tkinter; r=tkinter.Tk(); r.destroy()" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [FOUT] Python mist het tcl/tk-onderdeel ^(nodig voor de vensters^).
    echo Oplossing:
    echo   1. Instellingen ^> Apps ^> Geinstalleerde apps ^> Python 3.x ^> Wijzigen
    echo   2. Zorg dat "tcl/tk and IDLE" aangevinkt is, opnieuw installeren
    echo   3. Draai dit bestand daarna opnieuw
    echo.
    pause
    exit /b 1
)

:menu
echo.
echo Wat wil je doen?
echo   1 = Kaarten kalibreren ^(eerste keer op een nieuwe site^)
echo   2 = Live tool starten en regio's instellen ^(eerste keer^)
echo   3 = Live tool starten ^(regio's al ingesteld^)
echo   4 = Afsluiten
echo.
set /p KEUZE="Typ 1, 2, 3 of 4 en druk op Enter: "

if "%KEUZE%"=="1" (
    python src\calibrate.py
    goto menu
)
if "%KEUZE%"=="2" (
    python src\main.py --setup --decks 6
    goto menu
)
if "%KEUZE%"=="3" (
    python src\main.py
    goto menu
)
if "%KEUZE%"=="4" (
    exit /b 0
)

echo Ongeldige keuze, probeer opnieuw.
goto menu
