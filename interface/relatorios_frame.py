import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from bson import ObjectId

from config import vendas_col, produtos_col

class RelatoriosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        #layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #título
        self.title_label = ctk.CTkLabel(self, text="Relatórios", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        #conteúdo
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        #filtros de data
        self.filtros_frame = ctk.CTkFrame(self.main_frame)
        self.filtros_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.data_inicio_label = ctk.CTkLabel(self.filtros_frame, text="Data Início:")
        self.data_inicio_label.grid(row=0, column=0, padx=5, pady=5)

        self.data_inicio_entry = ctk.CTkEntry(self.filtros_frame, placeholder_text="DD/MM/AAAA")
        self.data_inicio_entry.grid(row=0, column=1, padx=5, pady=5)

        self.data_fim_label = ctk.CTkLabel(self.filtros_frame, text="Data Fim:")
        self.data_fim_label.grid(row=0, column=2, padx=5, pady=5)

        self.data_fim_entry = ctk.CTkEntry(self.filtros_frame, placeholder_text="DD/MM/AAAA")
        self.data_fim_entry.grid(row=0, column=3, padx=5, pady=5)

        self.gerar_relatorio_btn = ctk.CTkButton(self.filtros_frame, text="Gerar Relatório", command=self.gerar_relatorio)
        self.gerar_relatorio_btn.grid(row=0, column=4, padx=5, pady=5)

        #tabela de relatório
        self.relatorio_tree = ttk.Treeview(
            self.main_frame,
            columns=("data", "total_vendas", "qtd_vendas", "produto_mais_vendido"),
            show="headings"
        )

        self.relatorio_tree.heading("data", text="Data")
        self.relatorio_tree.heading("total_vendas", text="Total Vendas")
        self.relatorio_tree.heading("qtd_vendas", text="Qtd Vendas")
        self.relatorio_tree.heading("produto_mais_vendido", text="Produto Mais Vendido")

        self.relatorio_tree.column("data", width=100)
        self.relatorio_tree.column("total_vendas", width=100, anchor="e")
        self.relatorio_tree.column("qtd_vendas", width=100, anchor="center")
        self.relatorio_tree.column("produto_mais_vendido", width=200)
        self.relatorio_tree.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        #scroll relatório
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.relatorio_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.relatorio_tree.configure(yscrollcommand=scrollbar.set)

        #resumo do período
        self.resumo_frame = ctk.CTkFrame(self)
        self.resumo_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.total_periodo_label = ctk.CTkLabel(self.resumo_frame, text="Total no período: R$ 0.00", font=ctk.CTkFont(weight="bold"))
        self.total_periodo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.vendas_periodo_label = ctk.CTkLabel(self.resumo_frame, text="Vendas no período: 0", font=ctk.CTkFont(weight="bold"))
        self.vendas_periodo_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        #carrega relatório inicial
        self.carregar_relatorio_mensal()
        self.bind("<<ShowFrame>>", lambda e: self.carregar_relatorio_mensal())

    def parse_date(self, date_str): #converte string para data
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def gerar_relatorio(self): #gera relatório filtrado por data
        data_inicio = self.parse_date(self.data_inicio_entry.get())
        data_fim = self.parse_date(self.data_fim_entry.get())

        if not data_inicio or not data_fim:
            messagebox.showwarning("Aviso", "Datas inválidas. Use o formato DD/MM/AAAA.")
            return
        if data_inicio > data_fim:
            messagebox.showwarning("Aviso", "Data de início não pode ser maior que data de fim.")
            return

        data_fim = datetime.combine(data_fim.date(), datetime.max.time())

        pipeline = [
            {"$match": {"data_venda": {"$gte": data_inicio, "$lte": data_fim}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%d/%m/%Y", "date": "$data_venda"}},
                "total_vendas": {"$sum": "$valor_total"},
                "qtd_vendas": {"$sum": 1},
                "produtos_vendidos": {"$push": {"produtos": "$produtos"}}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            resultados = list(vendas_col.aggregate(pipeline))
            for item in self.relatorio_tree.get_children():
                self.relatorio_tree.delete(item)

            total_periodo = 0
            qtd_vendas_periodo = 0

            for resultado in resultados:
                data = resultado["_id"]
                total_vendas = resultado["total_vendas"]
                qtd_vendas = resultado["qtd_vendas"]
                produtos_vendidos = []

                for venda in resultado["produtos_vendidos"]:
                    for produto in venda["produtos"]:
                        produtos_vendidos.append(produto["produto_id"])

                contagem = {}
                for produto_id in produtos_vendidos:
                    contagem[produto_id] = contagem.get(produto_id, 0) + 1

                produto_mais_vendido = "N/A"
                if contagem:
                    produto_id_mais_vendido = max(contagem, key=contagem.get)
                    produto = produtos_col.find_one({"_id": produto_id_mais_vendido})
                    if produto:
                        produto_mais_vendido = produto["nome"]

                self.relatorio_tree.insert("", "end", values=(
                    data,
                    f"R$ {total_vendas:.2f}",
                    qtd_vendas,
                    produto_mais_vendido
                ))

                total_periodo += total_vendas
                qtd_vendas_periodo += qtd_vendas

            self.total_periodo_label.configure(text=f"Total no período: R$ {total_periodo:.2f}")
            self.vendas_periodo_label.configure(text=f"Vendas no período: {qtd_vendas_periodo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def carregar_relatorio_mensal(self): #carrega relatório dos últimos 30 dias
        for item in self.relatorio_tree.get_children():
            self.relatorio_tree.delete(item)

        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=30)

        pipeline = [
            {"$match": {"data_venda": {"$gte": data_inicio, "$lte": data_fim}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%d/%m/%Y", "date": "$data_venda"}},
                "total_vendas": {"$sum": "$valor_total"},
                "qtd_vendas": {"$sum": 1},
                "produtos_vendidos": {"$push": {"produtos": "$produtos"}}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            resultados = list(vendas_col.aggregate(pipeline))
            total_periodo = 0
            qtd_vendas_periodo = 0

            for resultado in resultados:
                data = resultado["_id"]
                total_vendas = resultado["total_vendas"]
                qtd_vendas = resultado["qtd_vendas"]
                produtos_vendidos = []

                for venda in resultado["produtos_vendidos"]:
                    for produto in venda["produtos"]:
                        produtos_vendidos.append(produto["produto_id"])

                contagem = {}
                for produto_id in produtos_vendidos:
                    contagem[produto_id] = contagem.get(produto_id, 0) + 1

                produto_mais_vendido = "N/A"
                if contagem:
                    produto_id_mais_vendido = max(contagem, key=contagem.get)
                    produto = produtos_col.find_one({"_id": produto_id_mais_vendido})
                    if produto:
                        produto_mais_vendido = produto["nome"]

                self.relatorio_tree.insert("", "end", values=(
                    data,
                    f"R$ {total_vendas:.2f}",
                    qtd_vendas,
                    produto_mais_vendido
                ))

                total_periodo += total_vendas
                qtd_vendas_periodo += qtd_vendas

            self.total_periodo_label.configure(text=f"Total no período: R$ {total_periodo:.2f}")
            self.vendas_periodo_label.configure(text=f"Vendas no período: {qtd_vendas_periodo}")
            self.data_inicio_entry.delete(0, "end")
            self.data_inicio_entry.insert(0, data_inicio.strftime("%d/%m/%Y"))
            self.data_fim_entry.delete(0, "end")
            self.data_fim_entry.insert(0, data_fim.strftime("%d/%m/%Y"))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatório: {str(e)}")
