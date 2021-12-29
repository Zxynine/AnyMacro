@echo off
for %%i in ("%~dp0*.svg") do (
    echo %%i to %%~ni.png
    "C:\Program Files\Inkscape\bin\inkscape.exe" --export-type="png" "%%i"
)