import customtkinter as ctk
from tkinter import ttk
from interface.produtos_frame import ProdutosFrame
from interface.vendas_frame import VendasFrame
from interface.relatorios_frame import RelatoriosFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Loja de Roupas - Gestão")
        self.geometry("1000x600")
        self.configure(bg='#2b2b2b')  # mesma cor do tema escuro
        self.resizable(True, True)   # permite redimensionar
        self.minsize(800, 500)       # tamanho mínimo razoável
        self.bind('<Configure>', self.on_resize)
        # CORREÇÃO 1: Removido o alpha transparente (mas quero colocar novamente grr)
        # CORREÇÃO 2: Estilizar as Treeviews para combinarem com o tema escuro
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Permite customização completa
        self.aplicar_tema_tabelas("dark")  # Tema inicial escuro

        # Configurar grid da janela principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Criar sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.btn_produtos = ctk.CTkButton(self.sidebar, text="Produtos", command=self.mostrar_produtos)
        self.btn_produtos.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.btn_vendas = ctk.CTkButton(self.sidebar, text="Vendas", command=self.mostrar_vendas)
        self.btn_vendas.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_relatorios = ctk.CTkButton(self.sidebar, text="Relatórios", command=self.mostrar_relatorios)
        self.btn_relatorios.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Container principal para as telas
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dicionário de telas
        self.frames = {}
        for F in (ProdutosFrame, VendasFrame, RelatoriosFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_produtos()

    def on_resize(self, event):
        if event.widget == self:
            self.update_idletasks()  # força redesenho imediato
        
    def aplicar_tema_tabelas(self, modo):
        """Aplica as cores corretas nas Treeviews baseado no tema (dark/light)"""
        if modo == "dark":
            bg = "#2b2b2b"
            fg = "#ffffff"
            heading_bg = "#333333"
        else:
            bg = "#ffffff"
            fg = "#000000"
            heading_bg = "#e0e0e0"
        
        self.style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, borderwidth=0, highlightthickness=0)
        self.style.configure("Treeview.Heading", background=heading_bg, foreground=fg, font=('Arial', 10, 'bold'), borderwidth=0)
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.style.configure("Vertical.TScrollbar", background=bg, troughcolor=bg, bordercolor=bg, arrowcolor=fg, width=10)
        self.style.map("Vertical.TScrollbar", background=[('active', '#555555')])

    def mostrar_produtos(self):
        self.frames["ProdutosFrame"].tkraise()

    def mostrar_vendas(self):
        self.frames["VendasFrame"].tkraise()

    def mostrar_relatorios(self):
        self.frames["RelatoriosFrame"].tkraise()
