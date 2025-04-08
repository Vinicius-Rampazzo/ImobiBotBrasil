@echo off
echo ========================================
echo  Configurando ambiente ImobiBotBrasil
echo ========================================

REM Verificar se Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python não encontrado. Por favor, instale o Python 3.8 ou superior.
    echo Visite https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado. Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo Erro ao criar o ambiente virtual!
    pause
    exit /b %errorlevel%
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Erro ao ativar o ambiente virtual!
    pause
    exit /b %errorlevel%
)

echo Atualizando pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Aviso: Não foi possível atualizar o pip, mas continuando...
)

echo Instalando dependências do requirements.txt...
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo Erro ao instalar dependências!
    pause
    exit /b %errorlevel%
)

REM Verificar se arquivo database.py existe
if exist backend\database.py (
    echo Criando banco de dados com imóveis de exemplo...
    python backend\database.py
    if %errorlevel% neq 0 (
        echo Aviso: Não foi possível criar o banco de dados de exemplo.
        echo Você pode precisar executar este comando manualmente depois.
    )
)

echo.
echo ========================================
echo  Configuração concluída com sucesso!
echo ========================================
echo.
echo Para iniciar o servidor, use o comando:
echo    python backend\main.py
echo.
echo Você pode acessar o sistema em:
echo    http://localhost:8080
echo.

pause