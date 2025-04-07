import sqlite3
import random

def conectar_banco():
    return sqlite3.connect('imobibot.db')

def adicionar_50_imoveis_teste():
    """Adiciona 50 imóveis de teste ao banco de dados."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Verifica se a tabela já existe
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
    
    # Dados para gerar imóveis aleatórios
    tipos = ['casa', 'apartamento', 'terreno']
    finalidades = ['venda', 'locacao']
    status_opcoes = ['disponivel', 'vendido', 'alugado']
    
    bairros = ['Centro', 'Jardim América', 'Vila Nova', 'Santa Luzia', 'Bairro Nobre']
    ruas = ['Avenida Principal', 'Rua das Flores', 'Alameda dos Ipês', 'Rua do Comércio', 'Avenida Central']
    
    # Limpa os imóveis existentes para garantir que teremos exatamente 50
    cursor.execute("DELETE FROM imoveis")
    conexao.commit()
    
    # Adiciona 50 imóveis
    for i in range(1, 51):
        tipo = random.choice(tipos)
        finalidade = random.choice(finalidades)
        status = random.choice(status_opcoes)
        
        # Ajuste os valores conforme o tipo e finalidade
        if finalidade == 'venda':
            if tipo == 'casa':
                preco = random.randint(300000, 1500000)
            elif tipo == 'apartamento':
                preco = random.randint(200000, 1000000)
            else:  # terreno
                preco = random.randint(100000, 500000)
        else:  # locacao
            if tipo == 'casa':
                preco = random.randint(1500, 5000)
            elif tipo == 'apartamento':
                preco = random.randint(800, 3000)
            else:  # terreno (raro, mas possível)
                preco = random.randint(500, 2000)
        
        # Quartos e banheiros conforme o tipo
        if tipo == 'terreno':
            quartos = 0
            banheiros = 0
        else:
            quartos = random.randint(1, 5)
            banheiros = min(quartos, random.randint(1, 4))
        
        # Metragem
        if tipo == 'terreno':
            metragem = random.randint(250, 2000)
        elif tipo == 'casa':
            metragem = random.randint(80, 500)
        else:  # apartamento
            metragem = random.randint(40, 200)
        
        # Endereço
        bairro = random.choice(bairros)
        rua = random.choice(ruas)
        numero = random.randint(1, 1000)
        endereco = f"{rua}, {numero}, {bairro}"
        
        # Título e descrição
        if tipo == 'casa':
            titulo = f"Casa em {bairro} - {quartos} quartos"
            descricao = f"Linda casa com {quartos} quartos e {banheiros} banheiros. Área de {metragem}m². Localizada em {bairro}."
        elif tipo == 'apartamento':
            titulo = f"Apartamento em {bairro} - {quartos} quartos"
            descricao = f"Excelente apartamento com {quartos} quartos e {banheiros} banheiros. Área de {metragem}m². Localizado em {bairro}."
        else:  # terreno
            titulo = f"Terreno em {bairro} - {metragem}m²"
            descricao = f"Ótimo terreno com {metragem}m². Localizado em {bairro}."
        
        # Referência única
        codigo_referencia = f"TESTE{i:03d}"
        
        # Imagem (placeholder, já que não temos imagens reais)
        imagem = f"/assets/images/imoveis/{tipo}-placeholder.jpg"
        
        # Inserir o imóvel
        try:
            cursor.execute("""
            INSERT INTO imoveis 
            (codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, imagem, quartos, banheiros, metragem, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, imagem, quartos, banheiros, metragem, status))
            print(f"Imóvel {i}: {titulo} adicionado com sucesso.")
        except sqlite3.IntegrityError as e:
            print(f"Erro ao adicionar imóvel {i}: {e}")
    
    conexao.commit()
    conexao.close()
    
    print("\nForam adicionados 50 imóveis de teste ao banco de dados.")
    print("Para ver 10 imóveis por página, ajuste o parâmetro 'itens_por_pagina' para 10 nas requisições.")

if __name__ == "__main__":
    adicionar_50_imoveis_teste()

  # inserir_imovel("REF002", "Apartamento Vista ao Mar", "Luxuoso com vista", 720000, "Rua do Sol, 78", "apartamento", "venda", 2, 2, 95)
  # inserir_imovel("REF003", "Casa de Campo", "Casa espaçosa na serra", 380000, "Estrada da Montanha, 12", "casa", "venda", 5, 4, 350)
  # inserir_imovel("REF004", "Casa de Festas", "Muito espaço para familia e amigos", 2500, "Rua bastista de morais, 25", "casa", "locacao", 8, 4, 420)

# Verificacao para saber se o arquivo database.py será executado diretamente, caso isso aconteca, chama a funcao para criar o banco.