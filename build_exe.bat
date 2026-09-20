@echo off
REM Bouwt BJAssistant.exe en BJKalibreren.exe met PyInstaller.
REM Vereist: venv al aangemaakt en requirements.txt geinstalleerd (zie README).

call venv\Scripts\activate
if errorlevel 1 (
    echo Kon de venv niet activeren. Draai eerst: python -m venv venv
    pause
    exit /b 1
)

echo Bouwen...
pyinstaller build.spec --noconfirm

if errorlevel 1 (
    echo.
    echo Er ging iets mis tijdens het bouwen. Zie de foutmelding hierboven.
    pause
    exit /b 1
)

echo.
echo Klaar. De .exe-bestanden staan in de map "dist":
echo   dist\BJAssistant.exe
echo   dist\BJKalibreren.exe
echo.
echo Zet beide .exe-bestanden samen in 1 map voordat je ze gebruikt
echo (ze delen config.json en de templates-map, die ernaast worden aangemaakt).
pause
