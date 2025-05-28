import customtkinter as ctk
from tkinter import ttk, messagebox
from interface.produtos_frame import ProdutosFrame
from interface.vendas_frame import VendasFrame
from interface.relatorios_frame import RelatoriosFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Janela
        self.title("Sistema de Gestão - Loja de Roupas")
        self.resizable(True, True)
        self.attributes('-alpha', 0.90)
        self.after(0, lambda: self.state('zoomed'))

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Barra lateral
        self.create_sidebar()

        # Telas principais
        self.frames = {}
        for F in (ProdutosFrame, VendasFrame, RelatoriosFrame):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=1, sticky="nsew")

        self.show_frame(ProdutosFrame)

    def create_sidebar(self):
        # Menu lateral
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Loja do phoon :)",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botões de navegação
        self.produtos_btn = ctk.CTkButton(
            self.sidebar,
            text="Produtos",
            command=lambda: self.show_frame(ProdutosFrame)
        )
        self.produtos_btn.grid(row=1, column=0, padx=20, pady=10)

        self.vendas_btn = ctk.CTkButton(
            self.sidebar,
            text="Vendas",
            command=lambda: self.show_frame(VendasFrame)
        )
        self.vendas_btn.grid(row=2, column=0, padx=20, pady=10)

        self.relatorios_btn = ctk.CTkButton(
            self.sidebar,
            text="Relatórios",
            command=lambda: self.show_frame(RelatoriosFrame)
        )
        self.relatorios_btn.grid(row=3, column=0, padx=20, pady=10)

        # Opção de tema
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(0, 20))
        self.appearance_mode_optionemenu.set("Dark")  # Tema padrão

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode.lower())
