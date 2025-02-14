#!/bin/bash

echo "🔧 Criando ambiente virtual..."
python3 -m venv venv

echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

echo "📦 Instalando dependências..."
pip install -r backend/requirements.txt

echo "✅ Configuração concluída! Agora você pode rodar o projeto."
