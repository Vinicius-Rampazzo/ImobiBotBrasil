#!/bin/bash

echo "========================================"
echo " Configurando ambiente ImobiBotBrasil"
echo "========================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    echo "Visite https://www.python.org/downloads/"
    exit 1
fi

echo "Python encontrado. Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Erro ao criar o ambiente virtual!"
    exit 1
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Erro ao ativar o ambiente virtual!"
    exit 1
fi

echo "Atualizando pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Aviso: Não foi possível atualizar o pip, mas continuando..."
fi

echo "Instalando dependências do requirements.txt..."
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências!"
    exit 1
fi

# Verificar se arquivo database.py existe
if [ -f backend/database.py ]; then
    echo "Criando banco de dados com imóveis de exemplo..."
    python backend/database.py
    if [ $? -ne 0 ]; then
        echo "Aviso: Não foi possível criar o banco de dados de exemplo."
        echo "Você pode precisar executar este comando manualmente depois."
    fi
fi

echo ""
echo "========================================"
echo " Configuração concluída com sucesso!"
echo "========================================"
echo ""
echo "Para iniciar o servidor, use o comando:"
echo "    python backend/main.py"
echo ""
echo "Você pode acessar o sistema em:"
echo "    http://localhost:8080"
echo ""

# Tornar o script executável para futuras instalações
chmod +x "$0"