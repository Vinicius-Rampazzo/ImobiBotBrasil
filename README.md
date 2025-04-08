# ImobiBotBrasil

Sistema de chatbot para imobiliárias com assistente virtual Louis.

## Requisitos

- Python 3.8 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## AVISO!

- Antes de qualquer coisa, instale o python em sua máquina na versão 3.8 ou superior.
- Visite o site para instalar: https://www.python.org/downloads/
- Antes de inciar a instalação do Python, selecione a opção "Add Python to PATH".
- Ao concluir as configurações iniciais, crie uma conta na GROQ AI: https://groq.com/
- Ao criar uma chave da API na GROQ AI, cria na raiz do projeto um arquivo `.env`.
- Copie sua chave da API e navegue até o arquivo `.env`.
- Logo em seguida coloque na primeira linha da seguinte forma `GROQ_API_KEY=Cole_Sua_Chave_Aqui`.

## Dependências

O sistema utiliza as seguintes bibliotecas Python:
- Flask 3.1.0
- flask-cors 5.0.1
- mysql-connector-python 9.2.0
- python-dotenv 1.0.1
- requests 2.32.3
- E outras dependências listadas no arquivo `requirements.txt`

## Instalação Rápida

### Windows

1. Clone este repositório
2. No terminal, Execute o arquivo `setup.bat` (digite --> ./setup.bat)
3. Aguarde a instalação das dependências e criação do banco de dados
4. Após a conclusão, execute o servidor com o comando indicado ao final da instalação

### Linux/Mac

1. Clone ou baixe este repositório
2. Execute o script de instalação:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Aguarde a instalação das dependências e criação do banco de dados
4. Após a conclusão, execute o servidor com o comando indicado ao final da instalação

## Executando o Sistema

Após a instalação, você pode iniciar o servidor com:

```bash
# No Windows (a partir da pasta raiz do projeto)
python backend\main.py

# No Linux/Mac (a partir da pasta raiz do projeto)
python backend/main.py
```

Acesse o sistema em seu navegador através do endereço:
http://localhost:8080

## Recursos

- Interface de chat amigável
- Busca de imóveis por diversos critérios
- Visualização paginada de resultados
- Assistente virtual inteligente (Louis)

## Estrutura do Projeto

```
ImobiBotBrasil/
├── backend/
│   ├── chatbot.py
│   ├── database.py
│   ├── imoveis.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── assets/
│   │   ├── images/
│   │   └── videos/
│   ├── scripts/
│   ├── styles/
│   └── index.html
├── setup.bat
├── setup.sh
└── README.md
```

## Solução de Problemas

Se encontrar problemas durante a instalação:

1. Verifique se o Python está instalado corretamente
2. Certifique-se de que o arquivo `requirements.txt` está na pasta `backend/`
3. Verifique se há permissões suficientes para criar e modificar arquivos
4. Para erros específicos, verifique as mensagens exibidas durante a execução do script de instalação