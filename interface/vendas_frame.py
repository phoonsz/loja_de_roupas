import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from bson import ObjectId

from config import produtos_col, vendas_col, client

class VendasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.carrinho = []

        # Título
        self.title_label = ctk.CTkLabel(self, text="Registro de Vendas", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Produtos
        self.produtos_frame = ctk.CTkFrame(self.main_frame)
        self.produtos_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.search_produto_entry = ctk.CTkEntry(self.produtos_frame, placeholder_text="Buscar produtos...")
        self.search_produto_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.search_produto_btn = ctk.CTkButton(self.produtos_frame, text="Buscar", command=self.buscar_produtos_venda)
        self.search_produto_btn.grid(row=0, column=1, padx=5, pady=5)

        self.produtos_tree = ttk.Treeview(
            self.produtos_frame,
            columns=("id", "nome", "categoria", "tamanho", "cor", "preco", "estoque"),
            show="headings",
            selectmode="browse"
        )
        for col in ("id", "nome", "categoria", "tamanho", "cor", "preco", "estoque"):
            self.produtos_tree.heading(col, text=col.capitalize())
        self.produtos_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.produtos_frame, orient="vertical", command=self.produtos_tree.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.produtos_tree.configure(yscrollcommand=scrollbar.set)

        # Carrinho
        self.carrinho_frame = ctk.CTkFrame(self.main_frame)
        self.carrinho_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.carrinho_tree = ttk.Treeview(
            self.carrinho_frame,
            columns=("produto", "quantidade", "preco", "subtotal"),
            show="headings"
        )
        for col in ("produto", "quantidade", "preco", "subtotal"):
            self.carrinho_tree.heading(col, text=col.capitalize())
        self.carrinho_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar_carrinho = ttk.Scrollbar(self.carrinho_frame, orient="vertical", command=self.carrinho_tree.yview)
        scrollbar_carrinho.grid(row=0, column=1, sticky="ns")
        self.carrinho_tree.configure(yscrollcommand=scrollbar_carrinho.set)

        # Controles
        self.quantidade_label = ctk.CTkLabel(self.carrinho_frame, text="Quantidade:")
        self.quantidade_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.quantidade_entry = ctk.CTkEntry(self.carrinho_frame, width=60)
        self.quantidade_entry.grid(row=1, column=1, padx=5, pady=5)
        self.quantidade_entry.insert(0, "1")

        self.adicionar_btn = ctk.CTkButton(self.carrinho_frame, text="Adicionar", command=self.adicionar_ao_carrinho)
        self.adicionar_btn.grid(row=2, column=0, padx=5, pady=5)

        self.remover_btn = ctk.CTkButton(self.carrinho_frame, text="Remover", command=self.remover_do_carrinho, fg_color="#d9534f")
        self.remover_btn.grid(row=2, column=1, padx=5, pady=5)

        self.total_label = ctk.CTkLabel(self.carrinho_frame, text="Total: R$ 0.00", font=ctk.CTkFont(weight="bold"))
        self.total_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.forma_pagamento_combobox = ctk.CTkComboBox(self.carrinho_frame, values=["Dinheiro", "Cartão", "Pix"])
        self.forma_pagamento_combobox.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.finalizar_btn = ctk.CTkButton(self.carrinho_frame, text="Finalizar Venda", command=self.finalizar_venda, fg_color="#5cb85c")
        self.finalizar_btn.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.carregar_produtos_venda()

    def carregar_produtos_venda(self):
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

    def buscar_produtos_venda(self):
        termo = self.search_produto_entry.get().strip().lower()
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)

        query = {"quantidade_estoque": {"$gt": 0}}
        if termo:
            query["$or"] = [
                {"nome": {"$regex": termo, "$options": "i"}},
                {"categoria": {"$regex": termo, "$options": "i"}},
                {"cor": {"$regex": termo, "$options": "i"}}
            ]

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

    def adicionar_ao_carrinho(self):
        selected = self.produtos_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return

        try:
            quantidade = int(self.quantidade_entry.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade inválida.")
            return

        values = self.produtos_tree.item(selected, "values")
        produto_id = values[0]
        nome = values[1]
        preco = float(values[5].replace("R$ ", ""))
        estoque = int(values[6])

        if quantidade > estoque:
            messagebox.showwarning("Aviso", "Estoque insuficiente.")
            return

        for item in self.carrinho:
            if item["produto_id"] == produto_id:
                if item["quantidade"] + quantidade > estoque:
                    messagebox.showwarning("Aviso", "Quantidade excede estoque.")
                    return
                item["quantidade"] += quantidade
                item["subtotal"] = item["quantidade"] * preco
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

    def remover_do_carrinho(self):
        selected = self.carrinho_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item.")
            return

        index = int(self.carrinho_tree.index(selected))
        if 0 <= index < len(self.carrinho):
            self.carrinho.pop(index)
            self.atualizar_carrinho()

    def atualizar_carrinho(self):
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

    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio.")
            return

        forma_pagamento = self.forma_pagamento_combobox.get()
        if not forma_pagamento:
            messagebox.showwarning("Aviso", "Selecione forma de pagamento.")
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
            messagebox.showinfo("Sucesso", "Venda registrada.")
            self.carrinho.clear()
            self.atualizar_carrinho()
            self.carregar_produtos_venda()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
