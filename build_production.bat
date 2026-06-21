@echo off
cls
echo =======================================================================
echo          B3 SOFTWARE - PIPELINE KOMPILACJI PDF MERGER                
echo =======================================================================
echo.

:: 1. Czyszczenie starych plików buildów
echo [1/3] Czyszczenie poprzednich artefaktow...
if exist build (
    echo  - Usuwanie folderu build...
    rmdir /s /q build
)
if exist dist (
    echo  - Usuwanie folderu dist...
    rmdir /s /q dist
)
if exist PDF_Merger_Setup.exe (
    echo  - Usuwanie starego instalatora...
    del /f /q PDF_Merger_Setup.exe
)
echo OK. Stare pliki usuniete.
echo.

:: 2. Uruchomienie kompilatora PyInstaller
echo [2/3] Uruchamianie kompilatora PyInstaller...
pyinstaller --noconfirm pdf_merger.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [BLAD KRYTYCZNY] PyInstaller zakonczyl prace z bledem!
    goto :end
)
echo OK. PyInstaller pomyslnie zbudowal aplikacje w folderze dist.
echo.

:: 3. Kompilacja instalatora exe przez Inno Setup
echo [3/3] Kompilacja instalatora maszynowego (Inno Setup)...

if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    echo  - Znaleziono kompilator lokalny: "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" pdf_merger.iss
    goto :check_installer_result
)

where iscc >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo  - Znaleziono kompilator w systemowym PATH.
    iscc pdf_merger.iss
    goto :check_installer_result
)

if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" pdf_merger.iss
    goto :check_installer_result
)

echo [BLAD] Nie znaleziono Inno Setup 6! Instalator nie moze zostac zbudowany.
goto :end

:check_installer_result
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [BLAD KRYTYCZNY] Inno Setup napotkal blad podczas kompilacji pliku .iss!
    goto :end
)

echo.
echo =======================================================================
echo SUKCES: Nowy instalator 'PDF_Merger_Setup.exe' jest gotowy!
echo =======================================================================

:end
pause