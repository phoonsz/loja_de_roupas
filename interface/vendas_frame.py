import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from config import produtos_collection, vendas_collection
from datetime import datetime
import pymongo

class VendasFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.carrinho = []  # Lista de dicionários: {produto_id, nome, preco_unitario, quantidade, subtotal}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ========== COLUNA ESQUERDA: Produtos Disponíveis ==========
        frame_esquerda = ctk.CTkFrame(self, fg_color="transparent")
        frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame_esquerda.grid_rowconfigure(1, weight=1)
        frame_esquerda.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_esquerda, text="🔍 Buscar Produto:").grid(row=0, column=0, sticky="w")
        self.entry_busca = ctk.CTkEntry(frame_esquerda)
        self.entry_busca.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.entry_busca.bind('<KeyRelease>', self.buscar_produtos)

        self.tree_produtos = ttk.Treeview(frame_esquerda, columns=("nome", "preco", "estoque"), show="headings")
        self.tree_produtos.heading("nome", text="Produto")
        self.tree_produtos.heading("preco", text="Preço (R$)")
        self.tree_produtos.heading("estoque", text="Em Estoque")
        self.tree_produtos.column("nome", width=180)
        self.tree_produtos.column("preco", width=100)
        self.tree_produtos.column("estoque", width=80)
        self.tree_produtos.grid(row=1, column=0, sticky="nsew")

        scroll_esq = ttk.Scrollbar(frame_esquerda, orient="vertical", command=self.tree_produtos.yview)
        scroll_esq.grid(row=1, column=1, sticky="ns")
        self.tree_produtos.configure(yscrollcommand=scroll_esq.set)

        self.btn_add = ctk.CTkButton(frame_esquerda, text="➕ Adicionar ao Carrinho", command=self.adicionar_ao_carrinho)
        self.btn_add.grid(row=2, column=0, pady=10, sticky="ew")

        self.carregar_produtos_disponiveis()

        # ========== COLUNA DIREITA: Carrinho ==========
        frame_direita = ctk.CTkFrame(self, fg_color="transparent")
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame_direita.grid_rowconfigure(1, weight=1)
        frame_direita.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_direita, text="🛒 Carrinho", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 10))

        self.tree_carrinho = ttk.Treeview(frame_direita, columns=("produto", "qtd", "preco_unit", "subtotal"), show="headings")
        self.tree_carrinho.heading("produto", text="Produto")
        self.tree_carrinho.heading("qtd", text="Qtd.")
        self.tree_carrinho.heading("preco_unit", text="Preço Unit.")
        self.tree_carrinho.heading("subtotal", text="Subtotal")
        self.tree_carrinho.column("produto", width=150)
        self.tree_carrinho.column("qtd", width=60)
        self.tree_carrinho.column("preco_unit", width=90)
        self.tree_carrinho.column("subtotal", width=90)
        self.tree_carrinho.grid(row=1, column=0, sticky="nsew")
        # CORREÇÃO: Duplo clique para editar quantidade
        self.tree_carrinho.bind('<Double-1>', self.editar_quantidade_carrinho)

        scroll_dir = ttk.Scrollbar(frame_direita, orient="vertical", command=self.tree_carrinho.yview)
        scroll_dir.grid(row=1, column=1, sticky="ns")
        self.tree_carrinho.configure(yscrollcommand=scroll_dir.set)

        self.label_total = ctk.CTkLabel(frame_direita, text="Total: R$ 0,00", font=("Arial", 14, "bold"))
        self.label_total.grid(row=2, column=0, pady=10, sticky="w")

        btn_frame = ctk.CTkFrame(frame_direita, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_limpar = ctk.CTkButton(btn_frame, text="🗑️ Limpar Carrinho", command=self.limpar_carrinho, fg_color="gray")
        self.btn_limpar.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_finalizar = ctk.CTkButton(btn_frame, text="✅ Finalizar Venda", command=self.finalizar_venda, fg_color="green")
        self.btn_finalizar.grid(row=0, column=1, padx=5, sticky="ew")

    def carregar_produtos_disponiveis(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        for p in produtos_collection.find():
            self.tree_produtos.insert("", "end", iid=str(p["_id"]), values=(p["nome"], f"R${p['preco']:.2f}", p["quantidade"]))

    def buscar_produtos(self, event=None):
        termo = self.entry_busca.get().strip()
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        query = {}
        if termo:
            query["nome"] = {"$regex": termo, "$options": "i"}
        for p in produtos_collection.find(query):
            self.tree_produtos.insert("", "end", iid=str(p["_id"]), values=(p["nome"], f"R${p['preco']:.2f}", p["quantidade"]))

    def adicionar_ao_carrinho(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um produto na lista!")
            return

        produto_id = selecionado[0]
        produto = produtos_collection.find_one({"_id": pymongo.ObjectId(produto_id)})
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado no banco!")
            return

        # CORREÇÃO: Validar estoque disponível
        estoque_atual = produto.get("quantidade", 0)
        if estoque_atual <= 0:
            messagebox.showerror("Erro", "Este produto está esgotado!")
            return

        qtd = simpledialog.askinteger("Quantidade", f"Quantos {produto['nome']}? (Estoque: {estoque_atual})", minvalue=1, maxvalue=estoque_atual)
        if not qtd:
            return

        # Verifica se o item já está no carrinho para somar
        for item in self.carrinho:
            if item["produto_id"] == produto_id:
                nova_qtd = item["quantidade"] + qtd
                if nova_qtd > estoque_atual:
                    messagebox.showerror("Erro", f"Quantidade total no carrinho ({nova_qtd}) excede o estoque ({estoque_atual})!")
                    return
                item["quantidade"] = nova_qtd
                item["subtotal"] = item["quantidade"] * item["preco_unitario"]
                self.atualizar_carrinho_ui()
                return

        # Adiciona novo item ao carrinho
        self.carrinho.append({
            "produto_id": produto_id,
            "nome": produto["nome"],  # CORREÇÃO: Salva o nome para snapshot futuro
            "preco_unitario": produto["preco"],
            "quantidade": qtd,
            "subtotal": qtd * produto["preco"]
        })
        self.atualizar_carrinho_ui()

    def editar_quantidade_carrinho(self, event):
        """Permite editar a quantidade com duplo clique no carrinho."""
        selecionado = self.tree_carrinho.selection()
        if not selecionado:
            return
        # Descobre o índice do item selecionado
        index = self.tree_carrinho.index(selecionado[0])
        item = self.carrinho[index]
        
        # Busca estoque atualizado
        produto_db = produtos_collection.find_one({"_id": pymongo.ObjectId(item["produto_id"])})
        if not produto_db:
            messagebox.showerror("Erro", "Produto não encontrado!")
            return
        
        nova_qtd = simpledialog.askinteger("Editar Quantidade", f"Nova quantidade para {item['nome']}? (Estoque: {produto_db['quantidade']})", minvalue=1, maxvalue=produto_db['quantidade'])
        if not nova_qtd:
            return
        
        item["quantidade"] = nova_qtd
        item["subtotal"] = nova_qtd * item["preco_unitario"]
        self.atualizar_carrinho_ui()

    def atualizar_carrinho_ui(self):
        for row in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(row)
        
        total = 0
        for item in self.carrinho:
            self.tree_carrinho.insert("", "end", values=(item["nome"], item["quantidade"], f"R${item['preco_unitario']:.2f}", f"R${item['subtotal']:.2f}"))
            total += item["subtotal"]
        
        self.label_total.configure(text=f"Total: R$ {total:.2f}")

    def limpar_carrinho(self):
        self.carrinho.clear()
        self.atualizar_carrinho_ui()

    # CORREÇÃO MAIS IMPORTANTE: Remove a transação e adiciona try/except + snapshot do nome
    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showerror("Erro", "Carrinho vazio!")
            return

        # Confirmação
        if not messagebox.askyesno("Confirmar", f"Finalizar venda no valor de {self.label_total.cget('text')}?"):
            return

        # Prepara o documento da venda com snapshot dos nomes
        itens_venda = []
        for item in self.carrinho:
            itens_venda.append({
                "produto_id": item["produto_id"],
                "nome_produto": item["nome"],  # <--- SALVANDO O NOME AQUI (SNAPSHOT)
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
                "subtotal": item["subtotal"]
            })

        documento_venda = {
            "data": datetime.now(),
            "itens": itens_venda,
            "total": sum(item["subtotal"] for item in self.carrinho)
        }

        # CORREÇÃO: Remove a transação (comentada) e faz sequencial com try/except
        try:
            # 1. Insere a venda
            vendas_collection.insert_one(documento_venda)

            # 2. Atualiza o estoque de cada produto (baixa)
            for item in self.carrinho:
                resultado = produtos_collection.update_one(
                    {"_id": pymongo.ObjectId(item["produto_id"])},
                    {"$inc": {"quantidade": -item["quantidade"]}}
                )
                if resultado.matched_count == 0:
                    raise Exception(f"Produto {item['nome']} não encontrado no estoque!")

            # Sucesso
            self.limpar_carrinho()
            messagebox.showinfo("Sucesso", "Venda finalizada com sucesso!")
            # Atualiza a lista de produtos disponíveis
            self.carregar_produtos_disponiveis()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao finalizar venda!\nDetalhes: {str(e)}")
