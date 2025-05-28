import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from bson import ObjectId

from config import produtos_col

class ProdutosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Título
        self.title_label = ctk.CTkLabel(self, text="Gerenciamento de Produtos", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Tabela de produtos
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("id", "nome", "categoria", "tamanho", "cor", "preco", "estoque"),
            show="headings",
            selectmode="browse"
        )

        #colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("tamanho", text="Tamanho")
        self.tree.heading("cor", text="Cor")
        self.tree.heading("preco", text="Preço")
        self.tree.heading("estoque", text="Estoque")

        self.tree.column("id", width=50, anchor="c")
        self.tree.column("nome", width=80,)
        self.tree.column("categoria", width=20,)
        self.tree.column("tamanho", width=70, anchor="c")      #fiquei com preguica de
        self.tree.column("cor", width=1)                       #tentar entender o width
        self.tree.column("preco", width=20, anchor="c")        #mas ta legal assim fodasekkkkkkkkk
        self.tree.column("estoque", width=20, anchor="c")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Formulário
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.nome_entry = self.create_labeled_entry("Nome:", 0)
        self.categoria_combobox = self.create_labeled_combobox("Categoria:", ["Camiseta", "Calça", "Vestido"], 1)
        self.tamanho_combobox = self.create_labeled_combobox("Tamanho:", ["PP", "P", "M", "G", "GG"], 2)
        self.cor_entry = self.create_labeled_entry("Cor:", 3)
        self.preco_entry = self.create_labeled_entry("Preço:", 4)
        self.estoque_entry = self.create_labeled_entry("Estoque:", 5)

        # Botões
        self.btn_frame = ctk.CTkFrame(self.form_frame)
        self.btn_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        ctk.CTkButton(self.btn_frame, text="Adicionar", command=self.adicionar_produto).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.btn_frame, text="Editar", command=self.editar_produto).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.btn_frame, text="Excluir", command=self.excluir_produto, fg_color="#d9534f").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.btn_frame, text="Limpar", command=self.limpar_formulario).pack(side="left", expand=True, padx=5)

        # Busca
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar produtos...")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.search_btn = ctk.CTkButton(self.search_frame, text="Buscar", command=self.buscar_produtos)
        self.search_btn.grid(row=0, column=1, padx=5, pady=5)

        self.carregar_produtos()
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_produto)
        self.bind("<<ShowFrame>>", lambda e: self.carregar_produtos())

    def create_labeled_entry(self, label, row):
        ctk.CTkLabel(self.form_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(self.form_frame)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def create_labeled_combobox(self, label, values, row):
        ctk.CTkLabel(self.form_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        combobox = ctk.CTkComboBox(self.form_frame, values=values)
        combobox.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return combobox

    def carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        produtos = produtos_col.find().sort("nome", 1)
        for produto in produtos:
            self.tree.insert("", "end", values=(
                str(produto["_id"]),
                produto["nome"],
                produto["categoria"],
                produto["tamanho"],
                produto["cor"],
                f"R$ {produto['preco']:.2f}",
                produto["quantidade_estoque"]
            ))

    def selecionar_produto(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        if values:
            self.limpar_formulario()
            self.nome_entry.insert(0, values[1])
            self.categoria_combobox.set(values[2])
            self.tamanho_combobox.set(values[3])
            self.cor_entry.insert(0, values[4])
            self.preco_entry.insert(0, values[5].replace("R$ ", ""))
            self.estoque_entry.insert(0, values[6])

    def adicionar_produto(self):
        if not self.validar_campos():
            return

        produto = {
            "nome": self.nome_entry.get(),
            "categoria": self.categoria_combobox.get(),
            "tamanho": self.tamanho_combobox.get(),
            "cor": self.cor_entry.get(),
            "preco": float(self.preco_entry.get()),
            "quantidade_estoque": int(self.estoque_entry.get()),
            "data_cadastro": datetime.now()
        }

        try:
            produtos_col.insert_one(produto)
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            self.limpar_formulario()
            self.carregar_produtos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def editar_produto(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        if not self.validar_campos():
            return

        produto_id = self.tree.item(selected, "values")[0]

        produto = {
            "nome": self.nome_entry.get(),
            "categoria": self.categoria_combobox.get(),
            "tamanho": self.tamanho_combobox.get(),
            "cor": self.cor_entry.get(),
            "preco": float(self.preco_entry.get()),
            "quantidade_estoque": int(self.estoque_entry.get())
        }

        try:
            produtos_col.update_one({"_id": ObjectId(produto_id)}, {"$set": produto})
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            self.carregar_produtos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir_produto(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return

        produto_id = self.tree.item(selected, "values")[0]

        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este produto?"):
            try:
                produtos_col.delete_one({"_id": ObjectId(produto_id)})
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                self.limpar_formulario()
                self.carregar_produtos()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def buscar_produtos(self):
        termo = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = {"$or": [{"nome": {"$regex": termo, "$options": "i"}},
                         {"categoria": {"$regex": termo, "$options": "i"}},
                         {"cor": {"$regex": termo, "$options": "i"}}]} if termo else {}

        produtos = produtos_col.find(query).sort("nome", 1)
        for produto in produtos:
            self.tree.insert("", "end", values=(
                str(produto["_id"]),
                produto["nome"],
                produto["categoria"],
                produto["tamanho"],
                produto["cor"],
                f"R$ {produto['preco']:.2f}",
                produto["quantidade_estoque"]
            ))

    def limpar_formulario(self):
        self.nome_entry.delete(0, "end")
        self.categoria_combobox.set("")
        self.tamanho_combobox.set("")
        self.cor_entry.delete(0, "end")
        self.preco_entry.delete(0, "end")
        self.estoque_entry.delete(0, "end")

    def validar_campos(self):
        campos = [
            (self.nome_entry, "Nome"),
            (self.categoria_combobox, "Categoria"),
            (self.tamanho_combobox, "Tamanho"),
            (self.cor_entry, "Cor"),
            (self.preco_entry, "Preço"),
            (self.estoque_entry, "Estoque")
        ]

        for campo, nome in campos:
            if not campo.get().strip():
                messagebox.showwarning("Aviso", f"O campo {nome} é obrigatório.")
                campo.focus_set()
                return False

        try:
            float(self.preco_entry.get())
            int(self.estoque_entry.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Preço e Estoque devem ser numéricos.")
            return False

        return True
