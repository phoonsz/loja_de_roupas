import pymongo
import customtkinter as ctk

# ====================================================
# 1. CONEXÃO COM O MONGODB (com tratamento de erro)
# ====================================================
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    # Testa rapidamente se o banco responde (evita falsos positivos)
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
    # (Antes ele quebrava na hora do import)
    client = None
    db = None
    produtos_collection = None
    vendas_collection = None

# ====================================================
# 2. CONFIGURAÇÕES DE TEMA (CustomTkinter)
# ====================================================
TEMA_ATUAL = "dark"  # Opções: "dark" ou "light"
ctk.set_appearance_mode(TEMA_ATUAL)
ctk.set_default_color_theme("dark-blue")

# ====================================================
# 3. CORES PADRÃO (usadas nos frames)
# ====================================================
BG_COLOR = "#242424"
FG_COLOR = "#2b2b2b"
BUTTON_COLOR = "#3a7ebf"
HOVER_COLOR = "#2b6a9e"
TEXT_COLOR = "#ffffff"

# Cores específicas para as Treeviews (para manter paridade com o base.py corrigido)
# Você pode usar esse dicionário no método aplicar_tema_tabelas() se quiser,
# mas os valores batem exatamente com os que coloquei no base.py.
CORES_TABELA = {
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "heading_bg": "#333333"
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "heading_bg": "#e0e0e0"
    }
}

# ====================================================
# 4. LISTAS ESTÁTICAS (centralizadas para facilitar manutenção)
# ====================================================
# Antes estavam espalhadas pelos arquivos de interface.
# Agora, se precisar adicionar uma nova categoria ou tamanho,
# você altera só aqui e todos os lugares que importarem vão refletir.
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
