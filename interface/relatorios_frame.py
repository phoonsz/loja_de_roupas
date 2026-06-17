import customtkinter as ctk
from tkinter import ttk, messagebox
from config import vendas_collection
from datetime import datetime

class RelatoriosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Filtros
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_filtros.grid_columnconfigure(0, weight=1)
        frame_filtros.grid_columnconfigure(1, weight=1)
        frame_filtros.grid_columnconfigure(2, weight=1)
        frame_filtros.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(frame_filtros, text="Data Início (DD/MM/AAAA):").grid(row=0, column=0, padx=5)
        self.entry_inicio = ctk.CTkEntry(frame_filtros)
        self.entry_inicio.grid(row=0, column=1, padx=5, sticky="ew")

        ctk.CTkLabel(frame_filtros, text="Data Fim (DD/MM/AAAA):").grid(row=0, column=2, padx=5)
        self.entry_fim = ctk.CTkEntry(frame_filtros)
        self.entry_fim.grid(row=0, column=3, padx=5, sticky="ew")

        self.btn_gerar = ctk.CTkButton(frame_filtros, text="Gerar Relatório", command=self.gerar_relatorio)
        self.btn_gerar.grid(row=0, column=4, padx=10)

        # Tabela de relatório
        self.tree = ttk.Treeview(self, columns=("data", "produtos", "total"), show="headings")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("produtos", text="Itens Vendidos")
        self.tree.heading("total", text="Total (R$)")
        self.tree.column("data", width=150)
        self.tree.column("produtos", width=400)
        self.tree.column("total", width=100)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scroll.grid(row=1, column=1, sticky="ns", pady=10)
        self.tree.configure(yscrollcommand=scroll.set)

    def gerar_relatorio(self):
        inicio_str = self.entry_inicio.get().strip()
        fim_str = self.entry_fim.get().strip()

        try:
            inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
            fim = datetime.strptime(fim_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
            return

        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Query no MongoDB
        query = {
            "data": {
                "$gte": inicio,
                "$lte": fim
            }
        }

        vendas = vendas_collection.find(query).sort("data", -1)
        encontrou = False

        for venda in vendas:
            encontrou = True
            data_str = venda["data"].strftime("%d/%m/%Y %H:%M")
            
            # CORREÇÃO: Constrói a string de produtos usando o snapshot salvo no array "itens"
            nomes_produtos = []
            if "itens" in venda:
                for item in venda["itens"]:
                    # Usa o nome salvo no momento da venda, com fallback para "Produto removido"
                    nome = item.get("nome_produto", "Produto removido")
                    qtd = item.get("quantidade", 0)
                    nomes_produtos.append(f"{nome} (x{qtd})")
            
            produtos_str = ", ".join(nomes_produtos) if nomes_produtos else "Nenhum item"
            
            self.tree.insert("", "end", values=(
                data_str,
                produtos_str,
                f"R${venda['total']:.2f}"
            ))

        if not encontrou:
            messagebox.showinfo("Relatório", "Nenhuma venda encontrada no período selecionado.")
