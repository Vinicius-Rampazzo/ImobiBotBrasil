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
        codigo_referencia TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        endereco TEXT NOT NULL,
        tipo TEXT CHECK(tipo IN ('casa', 'apartamento', 'terreno')),
        finalidade TEXT CHECK(finalidade IN ('venda', 'locacao')) NOT NULL DEFAULT 'venda',
        imagem TEXT,
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


def inserir_imovel(codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, quartos, banheiros, metragem, status="disponivel", imagem=None):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    codigo_referencia = str(codigo_referencia).strip().lower()
    # Padroniza o codigo de referencia e remove os espaçoes para poder fazer a verificacao com outro codigo de referencia
    
    cursor.execute("SELECT COUNT(*) FROM imoveis WHERE LOWER(codigo_referencia) = LOWER(?)", (codigo_referencia,))
    resultado = cursor.fetchone()

    if resultado[0] > 0:
        print(f"ERRO: O imóvel com código de referência '{codigo_referencia}' já está cadastrado!")
        conexao.close()
        return False
    # erro que retorna falso indicando que não foi cadastrado (caso nao tenha sido cadastrado)

  
    cursor.execute("""
    INSERT INTO imoveis (codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, quartos, banheiros, metragem, status, imagem) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, quartos, banheiros, metragem, status, imagem))

    conexao.commit()
    conexao.close()
    print(f"Imóvel '{titulo}' cadastrado com sucesso!")
    return True



if __name__ == '__main__':
  criar_tabela()

  inserir_imovel("REF002", "Apartamento Vista ao Mar", "Luxuoso com vista", 720000, "Rua do Sol, 78", "apartamento", "venda", 2, 2, 95)
  inserir_imovel("REF003", "Casa de Campo", "Casa espaçosa na serra", 380000, "Estrada da Montanha, 12", "casa", "venda", 5, 4, 350)
  inserir_imovel("REF004", "Casa de Festas", "Muito espaço para familia e amigos", 2500, "Rua bastista de morais, 25", "casa", "locacao", 8, 4, 420)

# Verificacao para saber se o arquivo database.py será executado diretamente, caso isso aconteca, chama a funcao para criar o banco.