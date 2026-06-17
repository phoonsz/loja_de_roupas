import customtkinter as ctk
from tkinter import ttk, messagebox
from bson import ObjectId
from config import produtos_collection, CATEGORIAS, TAMANHOS

class ProdutosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.produto_editando_id = None
        self.produto_selecionado_atual = None
        
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

        ctk.CTkLabel(frame_form, text="Preço (R$):").pack(pady=(10, 0), anchor="w")
        self.entry_preco = ctk.CTkEntry(frame_form)
        self.entry_preco.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Quantidade:").pack(pady=(10, 0), anchor="w")
        self.entry_qtd = ctk.CTkEntry(frame_form)
        self.entry_qtd.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Tamanho:").pack(pady=(10, 0), anchor="w")
        self.tamanho_var = ctk.StringVar(value=TAMANHOS[0])
        self.option_tamanho = ctk.CTkOptionMenu(frame_form, values=TAMANHOS, variable=self.tamanho_var)
        self.option_tamanho.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_form, text="Categoria:").pack(pady=(10, 0), anchor="w")
        self.categoria_var = ctk.StringVar(value=CATEGORIAS[0])
        self.option_categoria = ctk.CTkOptionMenu(frame_form, values=CATEGORIAS, variable=self.categoria_var)
        self.option_categoria.pack(fill="x", pady=5)

        # Botão Adicionar / Atualizar
        self.btn_adicionar = ctk.CTkButton(frame_form, text="Adicionar Produto", command=self.adicionar_produto)
        self.btn_adicionar.pack(pady=10, fill="x")

        self.btn_limpar = ctk.CTkButton(frame_form, text="Limpar Campos", command=self.limpar_campos, fg_color="gray")
        self.btn_limpar.pack(pady=5, fill="x")

        # Botões Editar e Remover (inicialmente desabilitados)
        self.btn_editar = ctk.CTkButton(frame_form, text="✏️ Editar Produto", command=self.editar_produto, fg_color="orange", state="disabled")
        self.btn_editar.pack(pady=5, fill="x")

        self.btn_remover = ctk.CTkButton(frame_form, text="🗑️ Remover Produto", command=self.remover_produto, fg_color="gray", state="disabled")
        self.btn_remover.pack(pady=5, fill="x")

        # ========== LADO DIREITO (Busca e Tabela) ==========
        frame_lista = ctk.CTkFrame(self, fg_color="transparent")
        frame_lista.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame_lista.grid_rowconfigure(1, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_lista, text="Buscar Produto:").grid(row=0, column=0, sticky="w")
        self.entry_busca = ctk.CTkEntry(frame_lista)
        self.entry_busca.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.entry_busca.bind('<KeyRelease>', self.buscar_produto)

        # Tabela sem a coluna ID (visível)
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

        # Scrollbar com estilo escuro
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Evento de seleção na tabela
        self.tree.bind('<<TreeviewSelect>>', self.on_selecionar_produto)

        # Carregar dados iniciais
        self.atualizar_tabela()

    # ==================== MÉTODOS PRINCIPAIS ====================

    def adicionar_produto(self):
        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        qtd = self.entry_qtd.get().strip()
        tamanho = self.tamanho_var.get().strip()
        categoria = self.categoria_var.get().strip()

        if not all([nome, preco, qtd, tamanho, categoria]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            preco_float = float(preco)
            qtd_int = int(qtd)
            if preco_float < 0:
                messagebox.showerror("Erro", "O preço não pode ser negativo!")
                return
            if qtd_int < 0:
                messagebox.showerror("Erro", "A quantidade não pode ser negativa!")
                return
            if qtd_int > 99999:
                messagebox.showerror("Erro", "Quantidade muito alta (máx 99999)!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser número e Quantidade inteiro!")
            return

        # Verifica se já existe produto com mesmo nome (case-insensitive)
        existente = produtos_collection.find_one({"nome": {"$regex": f"^{nome}$", "$options": "i"}})
        if existente:
            nova_qtd = existente["quantidade"] + qtd_int
            produtos_collection.update_one(
                {"_id": existente["_id"]},
                {"$set": {"quantidade": nova_qtd}}
            )
            self.limpar_campos()
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", f"Quantidade atualizada para {nova_qtd} (produto já existente)!")
        else:
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

    def editar_produto(self):
        """Ativa o modo de edição carregando os dados do produto selecionado."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um produto para editar!")
            return
        self.carregar_dados_edicao(selecionado[0])

    def carregar_dados_edicao(self, produto_id):
        produto = produtos_collection.find_one({"_id": ObjectId(produto_id)})
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado!")
            return

        self.produto_editando_id = produto_id
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, produto["nome"])
        self.entry_preco.delete(0, 'end')
        self.entry_preco.insert(0, str(produto["preco"]))
        self.entry_qtd.delete(0, 'end')
        self.entry_qtd.insert(0, str(produto["quantidade"]))
        self.tamanho_var.set(produto["tamanho"])
        self.categoria_var.set(produto["categoria"])

        self.btn_adicionar.configure(text="Atualizar Produto", command=self.atualizar_produto)

    def atualizar_produto(self):
        if not self.produto_editando_id:
            messagebox.showerror("Erro", "Nenhum produto em edição!")
            return

        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        qtd = self.entry_qtd.get().strip()
        tamanho = self.tamanho_var.get().strip()
        categoria = self.categoria_var.get().strip()

        if not all([nome, preco, qtd, tamanho, categoria]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            preco_float = float(preco)
            qtd_int = int(qtd)
            if preco_float < 0 or qtd_int < 0:
                messagebox.showerror("Erro", "Valores não podem ser negativos!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser número e Quantidade inteiro!")
            return

        produtos_collection.update_one(
            {"_id": ObjectId(self.produto_editando_id)},
            {"$set": {
                "nome": nome,
                "preco": preco_float,
                "quantidade": qtd_int,
                "tamanho": tamanho,
                "categoria": categoria
            }}
        )

        self.limpar_campos()
        self.atualizar_tabela()
        self.produto_selecionado_atual = None
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

    def remover_produto(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um produto para remover!")
            return

        produto_id = selecionado[0]
        produto = produtos_collection.find_one({"_id": ObjectId(produto_id)})
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado!")
            return

        if messagebox.askyesno("Confirmar", f"Remover '{produto['nome']}' permanentemente?"):
            produtos_collection.delete_one({"_id": ObjectId(produto_id)})
            self.limpar_campos()
            self.atualizar_tabela()
            # Desabilita botões após remoção
            self.btn_editar.configure(state="disabled", fg_color="gray")
            self.btn_remover.configure(state="disabled", fg_color="gray")
            self.btn_adicionar.configure(text="Adicionar Produto", command=self.adicionar_produto)
            self.produto_editando_id = None
            messagebox.showinfo("Sucesso", "Produto removido!")

    def limpar_campos(self):
        self.entry_nome.delete(0, 'end')
        self.entry_preco.delete(0, 'end')
        self.entry_qtd.delete(0, 'end')
        self.tamanho_var.set(TAMANHOS[0])
        self.categoria_var.set(CATEGORIAS[0])
        # Reset do modo de edição
        self.btn_adicionar.configure(text="Adicionar Produto", command=self.adicionar_produto)
        self.produto_editando_id = None
        # Desabilita botões de editar/remover
        self.btn_editar.configure(state="disabled", fg_color="gray")
        self.btn_remover.configure(state="disabled", fg_color="gray")
        self.produto_selecionado_atual = None
    # ==================== EVENTOS E ATUALIZAÇÃO ====================

    def on_selecionar_produto(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            produto_id = selecionado[0]
            if produto_id == self.produto_selecionado_atual:
                return  # já está selecionado, evita tremor
            self.produto_selecionado_atual = produto_id
            self.btn_editar.configure(state="normal", fg_color="orange")
            self.btn_remover.configure(state="normal", fg_color="red")
            self.carregar_dados_edicao(produto_id)
        else:
            self.produto_selecionado_atual = None
            self.btn_editar.configure(state="disabled", fg_color="gray")
            self.btn_remover.configure(state="disabled", fg_color="gray")

    def atualizar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for produto in produtos_collection.find():
            self.tree.insert("", "end", iid=str(produto["_id"]), values=(
                produto["nome"],
                f"R${produto['preco']:.2f}",
                produto["quantidade"],
                produto["tamanho"],
                produto["categoria"]
            ))

    def buscar_produto(self, event=None):
        termo = self.entry_busca.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not termo:
            self.atualizar_tabela()
            return

        query = {"nome": {"$regex": termo, "$options": "i"}}
        for produto in produtos_collection.find(query):
            self.tree.insert("", "end", iid=str(produto["_id"]), values=(
                produto["nome"],
                f"R${produto['preco']:.2f}",
                produto["quantidade"],
                produto["tamanho"],
                produto["categoria"]
            ))