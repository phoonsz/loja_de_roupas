import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import vendas_collection, produtos_collection
from bson import ObjectId

class RelatoriosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Abas
        self.tabview.add("Vendas por Período")
        self.tabview.add("Produtividade (Semana/Dia)")
        self.tabview.add("Produtos Mais Vendidos")

        self.criar_aba_vendas_periodo()
        self.criar_aba_produtividade()
        self.criar_aba_produtos_mais_vendidos()


    def criar_aba_vendas_periodo(self):
        frame = self.tabview.tab("Vendas por Período")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # Filtros
        ctk.CTkLabel(frame, text="Data Início:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cal_inicio = DateEntry(frame, width=12, date_pattern='dd/mm/yyyy')
        self.cal_inicio.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Data Fim:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cal_fim = DateEntry(frame, width=12, date_pattern='dd/mm/yyyy')
        self.cal_fim.grid(row=0, column=3, padx=5, pady=5)

        self.btn_gerar = ctk.CTkButton(frame, text="Gerar Gráfico", command=self.gerar_grafico_vendas_periodo)
        self.btn_gerar.grid(row=0, column=4, padx=10, pady=5)

        # Figura matplotlib
        self.fig_vendas, self.ax_vendas = plt.subplots(figsize=(6, 4))
        self.canvas_vendas = FigureCanvasTkAgg(self.fig_vendas, master=frame)
        self.canvas_vendas.get_tk_widget().grid(row=2, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)


    def gerar_grafico_vendas_periodo(self):
        inicio = self.cal_inicio.get_date()
        fim = self.cal_fim.get_date()
        inicio_dt = datetime.combine(inicio, datetime.min.time())
        fim_dt = datetime.combine(fim, datetime.max.time())

        vendas = list(vendas_collection.find({"data": {"$gte": inicio_dt, "$lte": fim_dt}}))
        if not vendas:
            messagebox.showinfo("Sem dados", "Nenhuma venda no período.")
            return

        # Agrupar por dia
        dias = {}
        for v in vendas:
            dia = v["data"].strftime("%Y-%m-%d")
            dias[dia] = dias.get(dia, 0) + v["total"]

        # Ordenar as chaves (datas)
        datas_ordenadas = sorted(dias.keys())
        valores = [dias[d] for d in datas_ordenadas]

        # Converter para objetos datetime para melhor formatação
        datas_dt = [datetime.strptime(d, "%Y-%m-%d") for d in datas_ordenadas]

        # Limpar e desenhar gráfico
        self.ax_vendas.clear()

        # Plotar barras
        self.ax_vendas.bar(datas_dt, valores, width=0.8, color='#3a7ebf')

        # --- MELHORIA: Ajustar rótulos do eixo X ---
        num_dias = len(datas_dt)

        if num_dias <= 15:
            # Mostra todos os dias
            self.ax_vendas.set_xticks(datas_dt)
            self.ax_vendas.set_xticklabels([d.strftime("%d/%m") for d in datas_dt], rotation=45, ha='right')
        elif num_dias <= 60:
            # Mostra a cada 3 dias
            step = max(1, num_dias // 20)  # ~20 rótulos
            indices = range(0, num_dias, step)
            ticks = [datas_dt[i] for i in indices]
            labels = [datas_dt[i].strftime("%d/%m") for i in indices]
            self.ax_vendas.set_xticks(ticks)
            self.ax_vendas.set_xticklabels(labels, rotation=45, ha='right')
        else:
            # Mostra a cada semana (ou a cada 7 dias)
            step = max(7, num_dias // 20)
            indices = range(0, num_dias, step)
            ticks = [datas_dt[i] for i in indices]
            # Para períodos longos, mostrar semana e mês
            labels = [datas_dt[i].strftime("%d/%m") for i in indices]
            self.ax_vendas.set_xticks(ticks)
            self.ax_vendas.set_xticklabels(labels, rotation=45, ha='right')

        # Ajustar margens para não cortar as barras
        self.ax_vendas.margins(x=0.01)

        self.ax_vendas.set_title("Vendas por Dia")
        self.ax_vendas.set_xlabel("Data")
        self.ax_vendas.set_ylabel("Total (R$)")

        self.fig_vendas.tight_layout()
        self.canvas_vendas.draw()
 
 
    def criar_aba_produtividade(self):
        frame = self.tabview.tab("Produtividade (Semana/Dia)")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Comparar semanas (últimas 4):").grid(row=0, column=0, pady=5)
        self.btn_produtividade = ctk.CTkButton(frame, text="Gerar Produtividade", command=self.gerar_produtividade)
        self.btn_produtividade.grid(row=0, column=1, padx=10, pady=5)

        self.fig_prod, self.ax_prod = plt.subplots(figsize=(6, 4))
        self.canvas_prod = FigureCanvasTkAgg(self.fig_prod, master=frame)
        self.canvas_prod.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)


    def gerar_produtividade(self):
        """Gera gráfico de vendas das últimas 4 semanas (segunda a domingo)."""
        hoje = datetime.now()
        
        # Encontrar a segunda-feira mais recente (início da semana atual)
        dias_para_segunda = (hoje.weekday() - 0) % 7  # 0 = segunda
        segunda_mais_recente = hoje - timedelta(days=dias_para_segunda)
        
        semanas = []
        totais = []
        labels = []
        
        # Para cada uma das últimas 4 semanas (da mais antiga para a mais recente)
        for i in range(3, -1, -1):  # i = 3, 2, 1, 0
            inicio_semana = segunda_mais_recente - timedelta(weeks=i)
            fim_semana = inicio_semana + timedelta(days=6)  # domingo
            # Ajustar para o fim do domingo (23:59:59)
            fim_semana = datetime.combine(fim_semana, datetime.max.time())
            
            # Consultar vendas no período
            vendas = list(vendas_collection.find({
                "data": {"$gte": inicio_semana, "$lte": fim_semana}
            }))
            total = sum(v.get("total", 0) for v in vendas)
            totais.append(total)
            
            # Rótulo: "Semana XX/XX" ou algo legível
            label = f"{inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m')}"
            labels.append(label)
        
        # Limpar e desenhar gráfico
        self.ax_prod.clear()
        
        # Escolher cores (mais escura para a semana atual)
        cores = ['#4a7fbf', '#3a7ebf', '#2a7ebf', '#1a7ebf']  # da mais antiga para a mais recente
        bars = self.ax_prod.bar(labels, totais, color=cores)
        
        # Destacar a semana atual (última barra) com cor diferente
        if bars:
            bars[-1].set_color('#e67e22')  # laranja para a semana atual
        
        self.ax_prod.set_title("Vendas por Semana (Últimas 4 Semanas)")
        self.ax_prod.set_ylabel("Total (R$)")
        self.ax_prod.tick_params(axis='x', rotation=45)
        
        # Adicionar valores acima das barras
        for bar, valor in zip(bars, totais):
            if valor > 0:
                self.ax_prod.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                                  f'R${valor:.0f}', ha='center', va='bottom', fontsize=9)
        
        self.fig_prod.tight_layout()
        self.canvas_prod.draw()
 
 
    def criar_aba_produtos_mais_vendidos(self):
        frame = self.tabview.tab("Produtos Mais Vendidos")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Mês (MM/AAAA):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_mes = ctk.CTkEntry(frame, placeholder_text="01/2025")
        self.entry_mes.grid(row=0, column=1, padx=5, pady=5)

        self.btn_mais_vendidos = ctk.CTkButton(frame, text="Gerar", command=self.gerar_mais_vendidos)
        self.btn_mais_vendidos.grid(row=0, column=2, padx=10)

        self.fig_top, self.ax_top = plt.subplots(figsize=(6, 4))
        self.canvas_top = FigureCanvasTkAgg(self.fig_top, master=frame)
        self.canvas_top.get_tk_widget().grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)


    def gerar_mais_vendidos(self):
        mes_input = self.entry_mes.get().strip()
        try:
            mes, ano = map(int, mes_input.split('/'))
        except:
            messagebox.showerror("Erro", "Formato MM/AAAA")
            return
        inicio = datetime(ano, mes, 1)
        if mes == 12:
            fim = datetime(ano+1, 1, 1) - timedelta(seconds=1)
        else:
            fim = datetime(ano, mes+1, 1) - timedelta(seconds=1)

        vendas = list(vendas_collection.find({"data": {"$gte": inicio, "$lte": fim}}))
        contagem = {}
        for v in vendas:
            for item in v.get("itens", []):
                nome = item.get("nome_produto", "Desconhecido")
                qtd = item.get("quantidade", 0)
                contagem[nome] = contagem.get(nome, 0) + qtd

        if not contagem:
            messagebox.showinfo("Sem dados", "Nenhuma venda nesse mês.")
            return

        # Ordenar e pegar top 10
        top = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:10]
        self.ax_top.clear()
        self.ax_top.barh([nome for nome, _ in top], [qtd for _, qtd in top], color='#3a7ebf')
        self.ax_top.set_title("Produtos Mais Vendidos")
        self.ax_top.set_xlabel("Quantidade")
        self.fig_top.tight_layout()
        self.canvas_top.draw()

