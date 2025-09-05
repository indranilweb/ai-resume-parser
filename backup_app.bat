@echo off
setlocal enabledelayedexpansion

echo AI Resume Parser - App Backup Script
echo =====================================

:: Get current date and time for backup filename
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

:: Set directories
set "SOURCE_DIR=%~dp0app"
set "BACKUP_DIR=%~dp0backups"
set "BACKUP_FILE=%BACKUP_DIR%\app_backup_%timestamp%.zip"

:: Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Source directory: %SOURCE_DIR%
echo Backup file: %BACKUP_FILE%
echo.

:: Check if source directory exists
if not exist "%SOURCE_DIR%" (
    echo Error: Source directory '%SOURCE_DIR%' does not exist!
    pause
    exit /b 1
)

:: Check if 7-Zip is available (common compression tool)
where 7z >nul 2>nul
if %errorlevel% equ 0 (
    echo Using 7-Zip for compression...
    echo.
    
    :: Create backup using 7-Zip with exclusions
    7z a -tzip "%BACKUP_FILE%" "%SOURCE_DIR%\*" ^
        -x!*\node_modules\* ^
        -x!*\__pycache__\* ^
        -x!*\venv\* ^
        -x!*\.venv\* ^
        -x!*\env\* ^
        -x!*\.env\* ^
        -x!*\.git\* ^
        -x!*\.vscode\* ^
        -x!*\dist\* ^
        -x!*\build\* ^
        -x!*\.next\* ^
        -x!*\coverage\* ^
        -x!*\.nyc_output\* ^
        -x!*\logs\* ^
        -x!*\cache_dir\* ^
        -x!*.pyc ^
        -x!*.pyo ^
        -x!*.log ^
        -x!*.tmp ^
        -x!*.cache ^
        -x!.DS_Store ^
        -x!Thumbs.db ^
        -x!npm-debug.log ^
        -x!yarn-error.log ^
        -x!.env.local ^
        -x!.env.development.local ^
        -x!.env.test.local ^
        -x!.env.production.local
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ Backup completed successfully!
        echo 📁 Backup location: %BACKUP_FILE%
        
        :: Get file size
        for %%F in ("%BACKUP_FILE%") do (
            set "size=%%~zF"
            set /a "sizeMB=!size!/1048576"
            echo 📊 Backup size: !sizeMB! MB
        )
    ) else (
        echo ❌ Backup failed with 7-Zip!
    )
    
) else (
    :: Fallback to PowerShell if 7-Zip is not available
    echo 7-Zip not found, using PowerShell for compression...
    echo.
    
    :: Create PowerShell script content
    echo $source = '%SOURCE_DIR%' > temp_backup.ps1
    echo $destination = '%BACKUP_FILE%' >> temp_backup.ps1
    echo. >> temp_backup.ps1
    echo $excludePatterns = @( >> temp_backup.ps1
    echo     '*\node_modules\*', >> temp_backup.ps1
    echo     '*\__pycache__\*', >> temp_backup.ps1
    echo     '*\venv\*', >> temp_backup.ps1
    echo     '*\.venv\*', >> temp_backup.ps1
    echo     '*\env\*', >> temp_backup.ps1
    echo     '*\.env\*', >> temp_backup.ps1
    echo     '*\.git\*', >> temp_backup.ps1
    echo     '*\.vscode\*', >> temp_backup.ps1
    echo     '*\dist\*', >> temp_backup.ps1
    echo     '*\build\*', >> temp_backup.ps1
    echo     '*\.next\*', >> temp_backup.ps1
    echo     '*\coverage\*', >> temp_backup.ps1
    echo     '*\.nyc_output\*', >> temp_backup.ps1
    echo     '*\logs\*', >> temp_backup.ps1
    echo     '*\cache_dir\*', >> temp_backup.ps1
    echo     '*.pyc', >> temp_backup.ps1
    echo     '*.pyo', >> temp_backup.ps1
    echo     '*.log', >> temp_backup.ps1
    echo     '*.tmp', >> temp_backup.ps1
    echo     '*.cache', >> temp_backup.ps1
    echo     '.DS_Store', >> temp_backup.ps1
    echo     'Thumbs.db', >> temp_backup.ps1
    echo     'npm-debug.log', >> temp_backup.ps1
    echo     'yarn-error.log' >> temp_backup.ps1
    echo ^) >> temp_backup.ps1
    echo. >> temp_backup.ps1
    echo Write-Host "Creating backup archive..." >> temp_backup.ps1
    echo $files = Get-ChildItem -Path $source -Recurse ^| Where-Object { >> temp_backup.ps1
    echo     $file = $_ >> temp_backup.ps1
    echo     $shouldExclude = $false >> temp_backup.ps1
    echo     foreach ($pattern in $excludePatterns^) { >> temp_backup.ps1
    echo         if ($file.FullName -like $pattern^) { >> temp_backup.ps1
    echo             $shouldExclude = $true >> temp_backup.ps1
    echo             break >> temp_backup.ps1
    echo         } >> temp_backup.ps1
    echo     } >> temp_backup.ps1
    echo     return -not $shouldExclude >> temp_backup.ps1
    echo } >> temp_backup.ps1
    echo. >> temp_backup.ps1
    echo Add-Type -AssemblyName System.IO.Compression.FileSystem >> temp_backup.ps1
    echo $zip = [System.IO.Compression.ZipFile]::Open($destination, 'Create'^) >> temp_backup.ps1
    echo. >> temp_backup.ps1
    echo foreach ($file in $files^) { >> temp_backup.ps1
    echo     if (-not $file.PSIsContainer^) { >> temp_backup.ps1
    echo         $relativePath = $file.FullName.Substring($source.Length + 1^) >> temp_backup.ps1
    echo         Write-Host "Adding: $relativePath" >> temp_backup.ps1
    echo         [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $relativePath^) ^| Out-Null >> temp_backup.ps1
    echo     } >> temp_backup.ps1
    echo } >> temp_backup.ps1
    echo. >> temp_backup.ps1
    echo $zip.Dispose(^) >> temp_backup.ps1
    echo Write-Host "Backup completed successfully!" >> temp_backup.ps1
    
    :: Run PowerShell script
    powershell -ExecutionPolicy Bypass -File temp_backup.ps1
    
    :: Clean up temporary script
    del temp_backup.ps1
    
    if exist "%BACKUP_FILE%" (
        echo.
        echo ✅ Backup completed successfully!
        echo 📁 Backup location: %BACKUP_FILE%
        
        :: Get file size
        for %%F in ("%BACKUP_FILE%") do (
            set "size=%%~zF"
            set /a "sizeMB=!size!/1048576"
            echo 📊 Backup size: !sizeMB! MB
        )
    ) else (
        echo ❌ Backup failed!
    )
)

echo.
echo Backup process completed.
pause
