@echo off
setlocal

REM === Configuration ===
set SPEC_FILE=RDR2ConflictChecker.spec
set UPX_PATH=D:\Games\R2D222ModManager\RDR2 Mod Manager
set LOG_FILE=build_log.txt

REM Clear old log
if exist "%LOG_FILE%" del "%LOG_FILE%"

REM Check if UPX is in PATH or at UPX_PATH
where upx >nul 2>&1
if errorlevel 1 (
    if exist "%UPX_PATH%\upx.exe" (
        set PATH=%UPX_PATH%;%PATH%
        echo UPX found at %UPX_PATH% >> "%LOG_FILE%" 2>&1
    ) else (
        echo WARNING: UPX not found in PATH or at %UPX_PATH%. >> "%LOG_FILE%" 2>&1
        echo UPX compression will be skipped. >> "%LOG_FILE%" 2>&1
    )
) else (
    echo UPX found in system PATH. >> "%LOG_FILE%" 2>&1
)

echo Starting PyInstaller build... >> "%LOG_FILE%" 2>&1

REM Run PyInstaller and redirect all output to log
pyinstaller "%SPEC_FILE%" --noconfirm --clean >> "%LOG_FILE%" 2>&1

REM Check for errors
findstr /C:"ERROR" "%LOG_FILE%" >nul
if %errorlevel% equ 0 (
    echo Build encountered ERRORS. See log below:
) else (
    echo Build completed successfully.
)

echo.
echo ----- Last 20 lines of build log -----
for /f "tokens=*" %%A in ('powershell -command "Get-Content -Tail 20 ''%LOG_FILE%''"') do echo %%A

echo.
echo Full log saved to %LOG_FILE%
echo Press any key to exit.
pause >nul
endlocal
