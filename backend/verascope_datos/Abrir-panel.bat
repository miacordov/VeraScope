@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title VeraScope - Centro de datos
echo.
echo   VeraScope - Centro de datos
echo.

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto :sinpython
%PY% -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
if errorlevel 1 goto :sinpython

if not exist ".venv\Scripts\python.exe" (
  echo   Primera vez: preparando el programa. Puede tardar unos minutos...
  %PY% -m venv .venv
  if errorlevel 1 goto :error
)
if not exist ".venv\.listo-1.1.0" (
  echo   Instalando las piezas necesarias. Hace falta internet...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>nul
  ".venv\Scripts\python.exe" -m pip install -e .
  if errorlevel 1 goto :error
  echo ok> ".venv\.listo-1.1.0"
)

rem Dentro del repo VeraScope, los datos van a backend\data (la misma carpeta que lee la API).
if not defined VERASCOPE_DATOS if exist "..\data\" set "VERASCOPE_DATOS=%~dp0..\data"
echo   Abriendo el panel en tu navegador.
echo   NO cierres esta ventana negra mientras uses el panel.
echo.
".venv\Scripts\python.exe" -m verascope_datos panel
echo.
echo   El panel se cerro. Puedes cerrar esta ventana.
pause
exit /b 0

:sinpython
echo   No encuentro Python 3.10 o mas nuevo en esta computadora.
echo   Instalalo desde https://www.python.org/downloads/
echo   y marca la casilla "Add python.exe to PATH" al instalar.
echo   Luego vuelve a abrir este archivo.
pause
exit /b 1

:error
echo.
echo   Algo fallo durante la instalacion. Copia el texto de arriba
echo   y mandaselo a quien te ayuda.
pause
exit /b 1
