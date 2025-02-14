@echo off
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo Erro ao criar o ambiente virtual!
    exit /b %errorlevel%
)

echo Ativando ambiente virtual...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Erro ao ativar o ambiente virtual!
    exit /b %errorlevel%
)

echo Instalando dependências...
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo Erro ao instalar dependências!
    exit /b %errorlevel%
)

echo Configuração concluída! Agora você pode rodar o projeto.
pause
