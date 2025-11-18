@echo off
echo ============================================
echo   UpPath API - Inicializacao Rapida
echo ============================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar se o arquivo .env existe
if not exist .env (
    echo [AVISO] Arquivo .env nao encontrado!
    echo Crie um arquivo .env com as credenciais do Oracle:
    echo.
    echo ORACLE_USER=seu_usuario
    echo ORACLE_PASSWORD=sua_senha
    echo ORACLE_DSN=localhost:1521/XEPDB1
    echo.
    pause
)

REM Instalar dependencias
echo [1/3] Instalando dependencias...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Iniciar a API
echo [2/3] Iniciando API REST...
echo ============================================
echo.
echo API estara disponivel em: http://localhost:5000
echo.
echo Endpoints principais:
echo   - Health: http://localhost:5000/api/v1/health
echo   - Info:   http://localhost:5000/api/v1/info
echo   - User:   http://localhost:5000/api/v1/dashboard/user/1/completo
echo.
echo Pressione Ctrl+C para parar o servidor
echo ============================================
echo.

python src\api\app.py

pause
