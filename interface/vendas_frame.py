import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from bson import ObjectId

from config import produtos_col, vendas_col, client

class VendasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        #layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #título
        self.title_label = ctk.CTkLabel(self, text="Registro de Vendas", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        #conteúdo
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        #lista de produtos
        self.produtos_frame = ctk.CTkFrame(self.main_frame)
        self.produtos_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.produtos_frame.grid_columnconfigure(0, weight=1)
        self.produtos_frame.grid_rowconfigure(1, weight=1)

        #busca de produtos
        self.search_produto_frame = ctk.CTkFrame(self.produtos_frame)
        self.search_produto_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.search_produto_frame.grid_columnconfigure(0, weight=1)

        self.search_produto_entry = ctk.CTkEntry(self.search_produto_frame, placeholder_text="Buscar produtos...")
        self.search_produto_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.search_produto_btn = ctk.CTkButton(self.search_produto_frame, text="Buscar", width=80, command=self.buscar_produtos_venda)
        self.search_produto_btn.grid(row=0, column=1, padx=5, pady=5)

        #tabela de produtos
        self.produtos_tree = ttk.Treeview(
            self.produtos_frame,
            columns=("id", "nome", "categoria", "tamanho", "cor", "preco", "estoque"),
            show="headings",
            selectmode="browse"
        )

        self.produtos_tree.heading("id", text="ID")
        self.produtos_tree.heading("nome", text="Nome")
        self.produtos_tree.heading("categoria", text="Categoria")
        self.produtos_tree.heading("tamanho", text="Tamanho")
        self.produtos_tree.heading("cor", text="Cor")
        self.produtos_tree.heading("preco", text="Preço")
        self.produtos_tree.heading("estoque", text="Estoque")

        self.produtos_tree.column("id", width=50, anchor="center")
        self.produtos_tree.column("nome", width=150)
        self.produtos_tree.column("categoria", width=100)
        self.produtos_tree.column("tamanho", width=70, anchor="center")
        self.produtos_tree.column("cor", width=100)
        self.produtos_tree.column("preco", width=80, anchor="e")
        self.produtos_tree.column("estoque", width=70, anchor="center")
        self.produtos_tree.grid(row=1, column=0, sticky="nsew")

        #scroll produtos
        scrollbar = ttk.Scrollbar(self.produtos_frame, orient="vertical", command=self.produtos_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.produtos_tree.configure(yscrollcommand=scrollbar.set)

        #carrinho
        self.carrinho_frame = ctk.CTkFrame(self.main_frame)
        self.carrinho_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.carrinho_frame.grid_columnconfigure(0, weight=1)
        self.carrinho_frame.grid_rowconfigure(1, weight=1)

        self.carrinho_label = ctk.CTkLabel(self.carrinho_frame, text="Carrinho de Compras", font=ctk.CTkFont(weight="bold"))
        self.carrinho_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.carrinho_tree = ttk.Treeview(
            self.carrinho_frame,
            columns=("produto", "quantidade", "preco", "subtotal"),
            show="headings"
        )

        self.carrinho_tree.heading("produto", text="Produto")
        self.carrinho_tree.heading("quantidade", text="Qtd")
        self.carrinho_tree.heading("preco", text="Preço Unit.")
        self.carrinho_tree.heading("subtotal", text="Subtotal")

        self.carrinho_tree.column("produto", width=150)
        self.carrinho_tree.column("quantidade", width=50, anchor="center")
        self.carrinho_tree.column("preco", width=80, anchor="e")
        self.carrinho_tree.column("subtotal", width=80, anchor="e")
        self.carrinho_tree.grid(row=1, column=0, sticky="nsew")

        #scroll carrinho
        scrollbar_carrinho = ttk.Scrollbar(self.carrinho_frame, orient="vertical", command=self.carrinho_tree.yview)
        scrollbar_carrinho.grid(row=1, column=1, sticky="ns")
        self.carrinho_tree.configure(yscrollcommand=scrollbar_carrinho.set)

        #controle de quantidade
        self.controle_carrinho_frame = ctk.CTkFrame(self.carrinho_frame)
        self.controle_carrinho_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.quantidade_label = ctk.CTkLabel(self.controle_carrinho_frame, text="Quantidade:")
        self.quantidade_label.grid(row=0, column=0, padx=5, pady=5)

        self.quantidade_entry = ctk.CTkEntry(self.controle_carrinho_frame, width=60)
        self.quantidade_entry.grid(row=0, column=1, padx=5, pady=5)
        self.quantidade_entry.insert(0, "1")

        self.adicionar_carrinho_btn = ctk.CTkButton(self.controle_carrinho_frame, text="Adicionar", width=80, command=self.adicionar_ao_carrinho)
        self.adicionar_carrinho_btn.grid(row=0, column=2, padx=5, pady=5)

        self.remover_carrinho_btn = ctk.CTkButton(self.controle_carrinho_frame, text="Remover", width=80, command=self.remover_do_carrinho, fg_color="#d9534f", hover_color="#c9302c")
        self.remover_carrinho_btn.grid(row=0, column=3, padx=5, pady=5)

        #resumo da venda
        self.resumo_frame = ctk.CTkFrame(self.carrinho_frame)
        self.resumo_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.total_label = ctk.CTkLabel(self.resumo_frame, text="Total: R$ 0.00", font=ctk.CTkFont(weight="bold"))
        self.total_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.forma_pagamento_label = ctk.CTkLabel(self.resumo_frame, text="Pagamento:")
        self.forma_pagamento_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.forma_pagamento_combobox = ctk.CTkComboBox(self.resumo_frame, values=["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix"])
        self.forma_pagamento_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.finalizar_venda_btn = ctk.CTkButton(self.resumo_frame, text="Finalizar Venda", command=self.finalizar_venda, fg_color="#5cb85c", hover_color="#4cae4c")
        self.finalizar_venda_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        #histórico de vendas
        self.historico_frame = ctk.CTkFrame(self)
        self.historico_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.historico_frame.grid_columnconfigure(0, weight=1)
        self.historico_frame.grid_rowconfigure(1, weight=1)

        self.historico_label = ctk.CTkLabel(self.historico_frame, text="Histórico de Vendas", font=ctk.CTkFont(weight="bold"))
        self.historico_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.historico_tree = ttk.Treeview(
            self.historico_frame,
            columns=("id", "data", "total", "pagamento"),
            show="headings"
        )

        self.historico_tree.heading("id", text="ID")
        self.historico_tree.heading("data", text="Data")
        self.historico_tree.heading("total", text="Total")
        self.historico_tree.heading("pagamento", text="Pagamento")

        self.historico_tree.column("id", width=80, anchor="center")
        self.historico_tree.column("data", width=150)
        self.historico_tree.column("total", width=100, anchor="e")
        self.historico_tree.column("pagamento", width=120)
        self.historico_tree.grid(row=1, column=0, sticky="nsew")

        #scroll histórico
        scrollbar_historico = ttk.Scrollbar(self.historico_frame, orient="vertical", command=self.historico_tree.yview)
        scrollbar_historico.grid(row=1, column=1, sticky="ns")
        self.historico_tree.configure(yscrollcommand=scrollbar_historico.set)

        #variáveis
        self.carrinho = []

        #carregar dados
        self.carregar_produtos_venda()
        self.carregar_historico_vendas()
        self.bind("<<ShowFrame>>", lambda e: self.carregar_historico_vendas())
    def carregar_produtos_venda(self): #carrega produtos com estoque > 0
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)

        produtos = produtos_col.find({"quantidade_estoque": {"$gt": 0}}).sort("nome", 1)
        for produto in produtos:
            self.produtos_tree.insert("", "end", values=(
                str(produto["_id"]),
                produto["nome"],
                produto["categoria"],
                produto["tamanho"],
                produto["cor"],
                f"R$ {produto['preco']:.2f}",
                produto["quantidade_estoque"]
            ))

    def buscar_produtos_venda(self): #busca produtos para venda
        termo = self.search_produto_entry.get().strip().lower()
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)

        query = {
            "quantidade_estoque": {"$gt": 0},
            "$or": [
                {"nome": {"$regex": termo, "$options": "i"}},
                {"categoria": {"$regex": termo, "$options": "i"}},
                {"cor": {"$regex": termo, "$options": "i"}}
            ]
        } if termo else {"quantidade_estoque": {"$gt": 0}}

        produtos = produtos_col.find(query).sort("nome", 1)
        for produto in produtos:
            self.produtos_tree.insert("", "end", values=(
                str(produto["_id"]),
                produto["nome"],
                produto["categoria"],
                produto["tamanho"],
                produto["cor"],
                f"R$ {produto['preco']:.2f}",
                produto["quantidade_estoque"]
            ))

    def adicionar_ao_carrinho(self): #adiciona produto ao carrinho
        selected = self.produtos_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar ao carrinho.")
            return

        try:
            quantidade = int(self.quantidade_entry.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade deve ser um número inteiro positivo.")
            return

        values = self.produtos_tree.item(selected, "values")
        produto_id = values[0]
        nome = values[1]
        preco = float(values[5].replace("R$ ", ""))
        estoque = int(values[6])

        if quantidade > estoque:
            messagebox.showwarning("Aviso", "Quantidade solicitada maior que o estoque disponível.")
            return

        for item in self.carrinho:
            if item["produto_id"] == produto_id:
                nova_quantidade = item["quantidade"] + quantidade
                if nova_quantidade > estoque:
                    messagebox.showwarning("Aviso", "Quantidade total solicitada maior que o estoque disponível.")
                    return

                item["quantidade"] = nova_quantidade
                item["subtotal"] = nova_quantidade * preco
                self.atualizar_carrinho()
                return

        self.carrinho.append({
            "produto_id": produto_id,
            "nome": nome,
            "preco": preco,
            "quantidade": quantidade,
            "subtotal": quantidade * preco
        })

        self.atualizar_carrinho()

    def remover_do_carrinho(self): #remove item do carrinho
        selected = self.carrinho_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover do carrinho.")
            return

        index = int(self.carrinho_tree.index(selected))
        if 0 <= index < len(self.carrinho):
            self.carrinho.pop(index)
            self.atualizar_carrinho()

    def atualizar_carrinho(self): #atualiza visual do carrinho e total
        for item in self.carrinho_tree.get_children():
            self.carrinho_tree.delete(item)

        total = 0
        for item in self.carrinho:
            self.carrinho_tree.insert("", "end", values=(
                item["nome"],
                item["quantidade"],
                f"R$ {item['preco']:.2f}",
                f"R$ {item['subtotal']:.2f}"
            ))
            total += item["subtotal"]

        self.total_label.configure(text=f"Total: R$ {total:.2f}")

    def finalizar_venda(self): #registra venda e atualiza estoque
        if not self.carrinho:
            messagebox.showwarning("Aviso", "O carrinho está vazio.")
            return

        forma_pagamento = self.forma_pagamento_combobox.get()
        if not forma_pagamento:
            messagebox.showwarning("Aviso", "Selecione uma forma de pagamento.")
            return

        venda = {
            "produtos": [],
            "valor_total": sum(item["subtotal"] for item in self.carrinho),
            "data_venda": datetime.now(),
            "forma_pagamento": forma_pagamento
        }

        for item in self.carrinho:
            venda["produtos"].append({
                "produto_id": ObjectId(item["produto_id"]),
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco"]
            })

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    vendas_col.insert_one(venda, session=session)
                    for item in self.carrinho:
                        produtos_col.update_one(
                            {"_id": ObjectId(item["produto_id"])},
                            {"$inc": {"quantidade_estoque": -item["quantidade"]}},
                            session=session
                        )

            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            self.carrinho.clear()
            self.atualizar_carrinho()
            self.carregar_produtos_venda()
            self.carregar_historico_vendas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar venda: {str(e)}")

    def carregar_historico_vendas(self): #carrega vendas recentes
        for item in self.historico_tree.get_children():
            self.historico_tree.delete(item)

        vendas = vendas_col.find().sort("data_venda", -1).limit(50)
        for venda in vendas:
            self.historico_tree.insert("", "end", values=(
                str(venda["_id"]),
                venda["data_venda"].strftime("%d/%m/%Y %H:%M"),
                f"R$ {venda['valor_total']:.2f}",
                venda["forma_pagamento"]
            ))
