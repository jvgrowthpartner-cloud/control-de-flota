@echo off
chcp 65001 > nul
echo ========================================
echo   Control de Mantenimiento de Flota
echo ========================================
echo.

REM Buscar Python (intenta python, py, python3)
where python >nul 2>&1
if %errorlevel% == 0 (
    python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
    if %errorlevel% == 0 ( set PYTHON=python & goto :found )
)
where py >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :found
)
where python3 >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python3
    goto :found
)
echo [ERROR] Python no esta instalado o no esta en el PATH.
echo.
echo 1. Descarga Python desde: https://www.python.org/downloads/
echo 2. Ejecuta el instalador
echo 3. IMPORTANTE: marca "Add Python to PATH" en la primera pantalla
echo 4. Cierra esta ventana y vuelve a hacer doble clic en iniciar.bat
echo.
pause
exit /b 1

:found
echo [OK] Python encontrado: %PYTHON%
echo.

REM Instalar dependencias si no estan
%PYTHON% -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    %PYTHON% -m pip install -r requirements.txt
    echo.
)

echo Iniciando la aplicacion...
echo Abre tu navegador en:
echo   PC:      http://127.0.0.1:8000
echo   Movil:   http://192.168.0.146:8000
echo Para detener: presiona Ctrl+C
echo.
%PYTHON% -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
