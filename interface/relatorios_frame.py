import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from bson import ObjectId

from config import vendas_col, produtos_col

class RelatoriosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Título
        self.title_label = ctk.CTkLabel(self, text="Relatórios", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Filtros
        self.filtros_frame = ctk.CTkFrame(self.main_frame)
        self.filtros_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.data_inicio_entry = self.create_labeled_entry("Data Início:", 0)
        self.data_fim_entry = self.create_labeled_entry("Data Fim:", 1)

        self.gerar_relatorio_btn = ctk.CTkButton(self.filtros_frame, text="Gerar Relatório", command=self.gerar_relatorio)
        self.gerar_relatorio_btn.grid(row=0, column=4, padx=5, pady=5)

        # Tabela de relatório
        self.relatorio_tree = ttk.Treeview(
            self.main_frame,
            columns=("data", "total_vendas", "qtd_vendas", "produto_mais_vendido"),
            show="headings"
        )
        for col in ("data", "total_vendas", "qtd_vendas", "produto_mais_vendido"):
            self.relatorio_tree.heading(col, text=col.replace("_", " ").capitalize())
        self.relatorio_tree.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.relatorio_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.relatorio_tree.configure(yscrollcommand=scrollbar.set)

        # Resumo
        self.resumo_frame = ctk.CTkFrame(self)
        self.resumo_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.total_periodo_label = ctk.CTkLabel(self.resumo_frame, text="Total no período: R$ 0.00", font=ctk.CTkFont(weight="bold"))
        self.total_periodo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.vendas_periodo_label = ctk.CTkLabel(self.resumo_frame, text="Vendas no período: 0", font=ctk.CTkFont(weight="bold"))
        self.vendas_periodo_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.carregar_relatorio_mensal()
        self.bind("<<ShowFrame>>", lambda e: self.carregar_relatorio_mensal())

    def create_labeled_entry(self, label, column):
        ctk.CTkLabel(self.filtros_frame, text=label).grid(row=0, column=column*2, padx=5, pady=5)
        entry = ctk.CTkEntry(self.filtros_frame, placeholder_text="DD/MM/AAAA")
        entry.grid(row=0, column=column*2 + 1, padx=5, pady=5)
        return entry

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def gerar_relatorio(self):
        data_inicio = self.parse_date(self.data_inicio_entry.get())
        data_fim = self.parse_date(self.data_fim_entry.get())

        if not data_inicio or not data_fim:
            messagebox.showwarning("Aviso", "Datas inválidas. Use o formato DD/MM/AAAA.")
            return

        if data_inicio > data_fim:
            messagebox.showwarning("Aviso", "Data de início não pode ser maior que data de fim.")
            return

        data_fim = datetime.combine(data_fim.date(), datetime.max.time())

        self.gerar_relatorio_periodo(data_inicio, data_fim)

    def gerar_relatorio_periodo(self, data_inicio, data_fim):
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
            self.atualizar_relatorio(resultados, data_inicio, data_fim)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def atualizar_relatorio(self, resultados, data_inicio, data_fim):
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

            produto_mais_vendido = self.obter_produto_mais_vendido(produtos_vendidos)

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

    def obter_produto_mais_vendido(self, produtos_vendidos):
        contagem = {}
        for produto_id in produtos_vendidos:
            contagem[produto_id] = contagem.get(produto_id, 0) + 1

        if contagem:
            produto_id_mais_vendido = max(contagem, key=contagem.get)
            produto = produtos_col.find_one({"_id": produto_id_mais_vendido})
            if produto:
                return produto["nome"]

        return "N/A"

    def carregar_relatorio_mensal(self):
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=30)

        self.data_inicio_entry.delete(0, "end")
        self.data_inicio_entry.insert(0, data_inicio.strftime("%d/%m/%Y"))

        self.data_fim_entry.delete(0, "end")
        self.data_fim_entry.insert(0, data_fim.strftime("%d/%m/%Y"))

        self.gerar_relatorio_periodo(data_inicio, data_fim)
