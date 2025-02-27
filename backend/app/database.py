import sqlite3

def conectar_banco():
  return sqlite3.connect('imobibot.db')

# funcao para conectar ao banco de dados que estará no arquivo arquivo 'imobibot.db', caso já tenha. Caso não tenha irá criar automaticamente esse arquivo 

def criar_tabela():
  conexao = conectar_banco()
  cursor = conexao.cursor()

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS imoveis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        endereco TEXT NOT NULL,
        tipo TEXT CHECK(tipo IN ('casa', 'apartamento', 'terreno')),
        quartos INTEGER,
        banheiros INTEGER,
        metragem REAL,
        status TEXT CHECK(status IN ('disponivel', 'vendido', 'alugado'))
    )
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT CHECK(tipo IN ('corretor', 'cliente proprietario', 'locatario', 'interessado', 'outros')) NOT NULL,
        contato TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        imovel_id INTEGER NOT NULL,
        interacoes INTEGER DEFAULT 0,
        status TEXT CHECK(status IN ('fria', 'morna', 'quente')) DEFAULT 'fria',
        ultima_interacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (imovel_id) REFERENCES imoveis(id)
    )
    ''')

  conexao.commit()
  conexao.close()
  print('banco de dados e tabela de imóveis criados com sucesso!')

# funcao para criar minhas tabelas "imoveis" e "clientes". Nessa funcao eu chamei a funcao 'conectar_banco()' para abrir uma conexao com o banco e criei um cursor para conseguir executar comandos SQLs dentro do banco. Chamando a variavel 'cursor' eu consigo chamar a funcao 'executar' onde me permite criar tabelas com comandos SQL.

if __name__ == '__main__':
  criar_tabela()

# Verificacao para saber se o arquivo database.py será executado diretamente, caso isso aconteca, chama a funcao para criar o banco.