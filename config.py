from pymongo import MongoClient
import customtkinter as ctk

# Configuração do banco de dados
client = MongoClient('mongodb://localhost:27017/')
db = client['loja_roupas']
produtos_col = db['produtos']
vendas_col = db['vendas']

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
