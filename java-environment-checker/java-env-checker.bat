@echo off
REM Java Environment Checker Launch Script for Windows
REM This script provides a convenient way to run the Java Environment Checker

setlocal

REM Script directory
set SCRIPT_DIR=%~dp0

REM JAR file location
set JAR_FILE=%SCRIPT_DIR%java-env-checker.jar

REM Check if JAR file exists
if not exist "%JAR_FILE%" (
    echo Error: JAR file not found at %JAR_FILE%
    echo Please ensure the application is properly built and packaged.
    exit /b 1
)

REM Check if Java is available
java -version >nul 2>&1
if errorlevel 1 (
    echo Error: Java is not installed or not in PATH
    echo Please install Java and ensure it's available in your PATH
    exit /b 1
)

REM Run the application
java -jar "%JAR_FILE%" %*

endlocal