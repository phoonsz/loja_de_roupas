import customtkinter as ctk
from tkinter import ttk, messagebox
from config import produtos_collection

class ProdutosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configurar grid do frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ========== LADO ESQUERDO (Formulário) ==========
        frame_form = ctk.CTkFrame(self, fg_color="transparent")
        frame_form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame_form, text="Nome:").pack(pady=(10, 0), anchor="w")
        self.entry_nome = ctk.CTkEntry(frame_form)
        self.entry_nome.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Preço:").pack(pady=(10, 0), anchor="w")
        self.entry_preco = ctk.CTkEntry(frame_form)
        self.entry_preco.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Quantidade:").pack(pady=(10, 0), anchor="w")
        self.entry_qtd = ctk.CTkEntry(frame_form)
        self.entry_qtd.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Tamanho:").pack(pady=(10, 0), anchor="w")
        self.entry_tamanho = ctk.CTkEntry(frame_form)
        self.entry_tamanho.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Categoria:").pack(pady=(10, 0), anchor="w")
        self.entry_categoria = ctk.CTkEntry(frame_form)
        self.entry_categoria.pack(fill="x", pady=5)

        self.btn_adicionar = ctk.CTkButton(frame_form, text="Adicionar Produto", command=self.adicionar_produto)
        self.btn_adicionar.pack(pady=20)

        self.btn_limpar = ctk.CTkButton(frame_form, text="Limpar Campos", command=self.limpar_campos, fg_color="gray")
        self.btn_limpar.pack(pady=5)

        # ========== LADO DIREITO (Busca e Tabela) ==========
        frame_lista = ctk.CTkFrame(self, fg_color="transparent")
        frame_lista.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame_lista.grid_rowconfigure(1, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_lista, text="Buscar Produto:").grid(row=0, column=0, sticky="w")
        self.entry_busca = ctk.CTkEntry(frame_lista)
        self.entry_busca.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        # CORREÇÃO: Busca automática ao digitar
        self.entry_busca.bind('<KeyRelease>', self.buscar_produto)

        # CORREÇÃO: Removida a coluna "_id" da exibição
        self.tree = ttk.Treeview(frame_lista, columns=("nome", "preco", "quantidade", "tamanho", "categoria"), show="headings")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("quantidade", text="Qtd.")
        self.tree.heading("tamanho", text="Tamanho")
        self.tree.heading("categoria", text="Categoria")
        self.tree.column("nome", width=150)
        self.tree.column("preco", width=100)
        self.tree.column("quantidade", width=70)
        self.tree.column("tamanho", width=80)
        self.tree.column("categoria", width=100)
        self.tree.grid(row=1, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.atualizar_tabela()

    def adicionar_produto(self):
        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        qtd = self.entry_qtd.get().strip()
        tamanho = self.entry_tamanho.get().strip()
        categoria = self.entry_categoria.get().strip()

        if not all([nome, preco, qtd, tamanho, categoria]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            preco_float = float(preco)
            qtd_int = int(qtd)
            # CORREÇÃO: Validar valores negativos
            if preco_float < 0:
                messagebox.showerror("Erro", "O preço não pode ser negativo!")
                return
            if qtd_int < 0:
                messagebox.showerror("Erro", "A quantidade não pode ser negativa!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser número e Quantidade deve ser inteiro!")
            return

        produto = {
            "nome": nome,
            "preco": preco_float,
            "quantidade": qtd_int,
            "tamanho": tamanho,
            "categoria": categoria
        }
        produtos_collection.insert_one(produto)
        self.limpar_campos()
        self.atualizar_tabela()
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

    def limpar_campos(self):
        self.entry_nome.delete(0, 'end')
        self.entry_preco.delete(0, 'end')
        self.entry_qtd.delete(0, 'end')
        self.entry_tamanho.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')

    def atualizar_tabela(self):
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Busca todos os produtos
        for produto in produtos_collection.find():
            # CORREÇÃO: O _id vai como iid (oculto), não como coluna visível
            self.tree.insert("", "end", iid=str(produto["_id"]), values=(
                produto["nome"],
                f"R${produto['preco']:.2f}",
                produto["quantidade"],
                produto["tamanho"],
                produto["categoria"]
            ))

    def buscar_produto(self, event=None):  # event=None para funcionar com bind e botão
        termo = self.entry_busca.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if termo == "":
            self.atualizar_tabela()
            return

        # Busca no MongoDB usando regex (case insensitive)
        query = {"nome": {"$regex": termo, "$options": "i"}}
        for produto in produtos_collection.find(query):
            self.tree.insert("", "end", iid=str(produto["_id"]), values=(
                produto["nome"],
                f"R${produto['preco']:.2f}",
                produto["quantidade"],
                produto["tamanho"],
                produto["categoria"]
            ))
