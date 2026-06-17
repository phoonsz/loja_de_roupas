import random
from datetime import datetime, timedelta
from config import produtos_collection, vendas_collection
from bson import ObjectId

# 4 produtos por categoria (ajuste conforme suas categorias)
CATEGORIAS_PRODUTOS = {
    "Camiseta": ["Camiseta Básica", "Camiseta Estampada", "Camiseta Oversized", "Camiseta Regata"],
    "Calça": ["Calça Jeans", "Calça Sarja", "Calça Moletom", "Calça Social"],
    "Vestido": ["Vestido Floral", "Vestido Longo", "Vestido Midi", "Vestido Cigana"],
    "Jaqueta": ["Jaqueta Jeans", "Jaqueta Couro", "Jaqueta Moletom", "Jaqueta Bomber"],
    "Bermuda": ["Bermuda Jeans", "Bermuda Sarja", "Bermuda Moletom", "Bermuda Social"],
    "Short": ["Short Jeans", "Short Sarja", "Short Moletom", "Short Social"],
    "Saia": ["Saia Jeans", "Saia Sarja", "Saia Moletom", "Saia Social"],
    "Blusa": ["Blusa Básica", "Blusa Estampada", "Blusa Oversized", "Blusa Regata"],
    "Casaco": ["Casaco Jeans", "Casaco Couro", "Casaco Moletom", "Casaco Bomber"],
    "Moletom": ["Moletom Básico", "Moletom Estampado", "Moletom Oversized", "Moletom Regata"],
}

# Produtos preferidos (venderão mais)
PRODUTOS_PREFERIDOS = [
    "Camiseta Estampada",
    "Calça Jeans",
    "Vestido Floral",
    "Jaqueta Couro"
]

def criar_produtos():
    """Cria os produtos no banco (se não existirem) e retorna lista de {id, nome, preco, categoria, quantidade}"""
    produtos_criados = []
    for categoria, nomes in CATEGORIAS_PRODUTOS.items():
        for nome in nomes:
            existente = produtos_collection.find_one({"nome": nome})
            if existente:
                produtos_criados.append({
                    "_id": existente["_id"],
                    "nome": existente["nome"],
                    "preco": existente["preco"],
                    "categoria": existente["categoria"],
                    "quantidade": existente.get("quantidade", 0)
                })
                continue
            preco = round(random.uniform(20.0, 150.0), 2)
            qtd = random.randint(50, 200)
            produto = {
                "nome": nome,
                "preco": preco,
                "quantidade": qtd,
                "tamanho": random.choice(["P", "M", "G", "GG"]),
                "categoria": categoria
            }
            result = produtos_collection.insert_one(produto)
            produtos_criados.append({
                "_id": result.inserted_id,
                "nome": nome,
                "preco": preco,
                "categoria": categoria,
                "quantidade": qtd
            })
    return produtos_criados

def gerar_vendas_periodo(produtos, data_inicio, data_fim):
    """
    Gera vendas para o período entre data_inicio e data_fim (inclusive).
    """
    delta = data_fim - data_inicio
    vendas_criadas = 0
    total_vendas = 0

    for i in range(delta.days + 1):
        data = data_inicio + timedelta(days=i)
        dia_semana = data.weekday()

        if dia_semana == 4:   # sexta
            num_vendas = random.randint(5, 12)
        elif dia_semana == 5: # sábado
            num_vendas = random.randint(8, 15)
        else:
            num_vendas = random.randint(1, 5)

        for _ in range(num_vendas):
            num_itens = random.randint(2, 5)
            itens = []
            total = 0
            for _ in range(num_itens):
                if random.random() < 0.6:
                    produto = random.choice([p for p in produtos if p["nome"] in PRODUTOS_PREFERIDOS])
                else:
                    produto = random.choice(produtos)

                produto_id = produto["_id"]
                doc = produtos_collection.find_one({"_id": ObjectId(produto_id)})
                if doc is None:
                    continue
                qtd_atual = doc.get("quantidade", 0)
                if qtd_atual <= 0:
                    continue
                max_qtd = min(qtd_atual, 4)
                if max_qtd == 0:
                    continue
                qtd = random.randint(1, max_qtd)
                novo_estoque = qtd_atual - qtd
                produtos_collection.update_one(
                    {"_id": ObjectId(produto_id)},
                    {"$set": {"quantidade": novo_estoque}}
                )
                produto["quantidade"] = novo_estoque

                preco_unit = produto["preco"]
                subtotal = qtd * preco_unit
                itens.append({
                    "produto_id": str(produto_id),
                    "nome_produto": produto["nome"],
                    "quantidade": qtd,
                    "preco_unitario": preco_unit,
                    "subtotal": subtotal
                })
                total += subtotal
                total_vendas += qtd

            if itens:
                venda = {
                    "data": data.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                    "itens": itens,
                    "total": total
                }
                vendas_collection.insert_one(venda)
                vendas_criadas += 1

    print(f"✅ {vendas_criadas} vendas geradas no período.")
    print(f"📦 {total_vendas} unidades vendidas no total.")
def resetar_estoque(valor=200):
    """Define a quantidade de todos os produtos para um valor padrão (alto)."""
    result = produtos_collection.update_many({}, {"$set": {"quantidade": valor}})
    print(f"✅ Estoque de {result.modified_count} produtos resetado para {valor}.")

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 GERADOR DE DADOS FALSOS")
    print("=" * 50)

    # Resetar estoque
    print("\n🔄 Resetando estoque para 200 unidades...")
    resetar_estoque(200)

    print("\n🔄 Criando produtos (se não existirem)...")
    produtos = criar_produtos()
    print(f"✅ {len(produtos)} produtos disponíveis.")

    # NOVO: Gerar vendas de maio/2025 a maio/2026
    print("\n🔄 Gerando vendas de 01/05/2025 a 31/05/2026...")
    inicio = datetime(2025, 5, 1)
    fim = datetime(2026, 6, 16)
    gerar_vendas_periodo(produtos, inicio, fim)

    print("\n🎉 Dados falsos gerados com sucesso!")