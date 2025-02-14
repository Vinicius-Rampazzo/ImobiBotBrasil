@echo off
echo Criando ambiente virtual...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando dependências...
pip install -r backend/requirements.txt

echo Configuração concluída! Agora você pode rodar o projeto.
pause
