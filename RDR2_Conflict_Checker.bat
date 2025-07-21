@echo off
echo Starting RDR2 Conflict Checker...
python "%~dp0RDR2ConflictChecker.py"
if errorlevel 1 (
  echo Python not found. Please install Python from https://www.python.org/downloads/
  pause
)
