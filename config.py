import pymongo


#CONEXÃO COM O MONGODB (com tratamento de erro)
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    client.admin.command('ping')
    
    db = client['loja_roupas']
    produtos_collection = db['produtos']
    vendas_collection = db['vendas']
    
    print("✅ Conectado ao MongoDB com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")
    print("⚠️  Certifique-se de que o MongoDB está rodando em mongodb://localhost:27017/")
    
    # CRÍTICO: Para não quebrar a importação nos outros arquivos,
    # criamos as variáveis como None. As funções nos outros arquivos
    # vão falhar ao tentar usar, mas o programa pelo menos abre.
    client = None
    db = None
    produtos_collection = None
    vendas_collection = None


#LISTAS ESTÁTICAS para facilitar testes.
CATEGORIAS = [
    "Camiseta", 
    "Calça", 
    "Vestido", 
    "Jaqueta", 
    "Bermuda",
    "Short", 
    "Saia", 
    "Blusa",
    "Casaco",
    "Moletom"
]

TAMANHOS = [
    "PP", 
    "P", 
    "M", 
    "G", 
    "GG", 
    "XG", 
    "Único"
]
