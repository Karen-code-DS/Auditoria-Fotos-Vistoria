import os
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- CAMINHO RAIZ DA REDE ---
CAMINHO_RAIZ_REDE = r"M:\001 - Vistorias de Campo"
EXTENSOES_FOTOS = ('.jpg', '.jpeg', '.png', '.heic', '.webp')

# Correção ortográfica
vistorias = {
    "manual"   : "Manual"  ,
    "mecânico" : "Mecânico",
    "mecanico" : "Mecânico",
}



def listar_rhs_disponiveis(caminho_base):
    if not os.path.exists(caminho_base):
        return []
    rhs = []
    try:
        with os.scandir(caminho_base) as entradas:
            for entrada in entradas:
                if entrada.is_dir():
                    rhs.append(entrada.name)
    except Exception:
        pass
    return sorted(rhs)

def obter_periodo_mais_recente(caminho_rh):
    padrao_data = re.compile(r'\d{2}\.\d{2}\.\d{4} a (\d{2}\.\d{2}\.\d{4})')
    periodos = []
    try:
        with os.scandir(caminho_rh) as entradas:
            for entrada in entradas:
                if entrada.is_dir():
                    match = padrao_data.search(entrada.name)
                    if match:
                        data_fim = datetime.strptime(match.group(1), "%d.%m.%Y")
                        periodos.append((data_fim, entrada.name))
    except Exception:
        return None

    if not periodos:
        return None

    periodos.sort(key=lambda item: item[0], reverse=True)
    return periodos[0][1]

def buscar_pasta_fotos(caminho_corpo_hidrico):
    """Localiza a subpasta de fotos (ex: 'Fotos', 'Foto', 'Fotografias')."""
    termos_aceitos = ["foto", "fotos", "fotografia", "fotografias"]
    try:
        with os.scandir(caminho_corpo_hidrico) as sub_entradas:
            for item in sub_entradas:
                if item.is_dir():
                    if any(termo in item.name.lower() for termo in termos_aceitos):
                        return item.path
    except Exception:
        pass
    return None

def Mapear_fotos_por_data(pasta_fotos):
    """
    Varre as subpastas dentro de 'Fotos'.
    Procura por pastas com nomes no formato de data (ex: 2026.08.19) e conta as imagens.
    """
    resumo_datas = {}
    total_geral = 0

    try:
        with os.scandir(pasta_fotos) as subpastas:
            for item in subpastas:
                if item.is_dir():
                    nome_pasta = item.name.strip()
                    
                    qtd_fotos_dia = 0
                    with os.scandir(item.path) as arquivos:
                        for arq in arquivos:
                            if arq.is_file() and arq.name.lower().endswith(EXTENSOES_FOTOS):
                                qtd_fotos_dia += 1

                    resumo_datas[nome_pasta] = qtd_fotos_dia
                    total_geral += qtd_fotos_dia

    except Exception as e:
        print(f"Erro ao ler pasta de fotos: {e}")

    return resumo_datas, total_geral

def escanear_fotos_rede(caminho_base, pasta_rh_nome, tipo_vistoria):
    caminho_rh = os.path.join(caminho_base, pasta_rh_nome)
    if not os.path.exists(caminho_rh):
        return None, f"Pasta da RH '{pasta_rh_nome}' não foi encontrada.", None

    periodo = obter_periodo_mais_recente(caminho_rh)
    if not periodo:
        return None, f"Nenhum período de vistoria encontrado em '{pasta_rh_nome}'.", None

    caminho_periodo = Path(caminho_rh) / periodo
    
    caminho_alvo =None
    tipo_normalizado = vistorias.get(tipo_vistoria.lower(), tipo_vistoria)  # Padrão "Mecânico")
    
    if caminho_periodo.exists():
        for subpasta in caminho_periodo.iterdir():
            if subpasta.is_dir():
                if vistorias.get(subpasta.name.lower()) == tipo_normalizado:
                    caminho_alvo = subpasta
                    break
    if not caminho_alvo or not caminho_alvo.exists():
        return (
            None,
            (
                f"Caminho da vistoria '{tipo_vistoria}' não existe em:\n"
                f"{caminho_periodo}"
            ),
            periodo,)
    
    resultados = []

    with os.scandir(caminho_alvo) as entradas:
        for entrada in entradas:
            if entrada.is_dir() and " - " in entrada.name:
                municipio, corpo_hidrico = entrada.name.split(" - ", 1)
                pasta_fotos = buscar_pasta_fotos(entrada.path)
                
                detalhe_datas = {}
                total_fotos = 0

                if pasta_fotos and os.path.exists(pasta_fotos):
                    detalhe_datas, total_fotos = Mapear_fotos_por_data(pasta_fotos)

                if detalhe_datas:
                    resumo_str = " | ".join([f"{data} ({qtd} fotos)" for data, qtd in sorted(detalhe_datas.items())])
                else:
                    resumo_str = "Nenhuma pasta de data / foto encontrada"

                resultados.append({
                    "RH": pasta_rh_nome,
                    "Tipo de Vistoria": tipo_vistoria,
                    "Município": municipio.strip(),
                    "Corpo Hídrico": corpo_hidrico.strip(),
                    "Qt Datas": len(detalhe_datas),
                    "Detalhamento por Data": resumo_str,
                    "_dados_brutos": detalhe_datas
                })

    return pd.DataFrame(resultados), None, periodo


class AplicacaoVerificacaoFotos:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificação de Registro Fotográfico (Fotos)")
        self.root.geometry("1150x700")

        self.df_atual = None

        # --- SELEÇÕES ---
        frame_controles = ttk.LabelFrame(self.root, text=" ⚙️ Opções de Seleção ")
        frame_controles.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_controles, text="RH:", font=("Calibri", 10, "bold")).grid(row=0, column=0, padx=8, pady=10, sticky=tk.W)
        self.cb_rh = ttk.Combobox(frame_controles, state="readonly", width=30)
        self.cb_rh.grid(row=0, column=1, padx=8, pady=10)

        ttk.Label(frame_controles, text="Tipo de Vistoria:", font=("Calibri", 10, "bold")).grid(row=0, column=2, padx=8, pady=10, sticky=tk.W)
        self.cb_vistoria = ttk.Combobox(frame_controles, values=["Manual", "Mecânico"], state="readonly", width=15)
        self.cb_vistoria.set("Manual")
        self.cb_vistoria.grid(row=0, column=3, padx=8, pady=10)

        btn_buscar = ttk.Button(frame_controles, text="🔍 Consultar Fotos", command=self.executar_consulta)
        btn_buscar.grid(row=0, column=4, padx=15, pady=10)

        self.lbl_periodo = ttk.Label(frame_controles, text="Período: -", font=("Calibri", 10, "italic"))
        self.lbl_periodo.grid(row=0, column=5, padx=10, pady=10, sticky=tk.W)

        self.carregar_rhs()

        # --- TABELA E PAINEL ---
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame_tabela = ttk.Frame(paned)
        paned.add(frame_tabela, weight=3)

        scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)

        self.colunas_exibir = ["RH", "Tipo de Vistoria", "Município", "Corpo Hídrico", "Qt Datas", "Detalhamento por Data"]
        self.tabela = ttk.Treeview(
            frame_tabela, 
            columns=self.colunas_exibir, 
            show="headings", 
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tabela.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.config(command=self.tabela.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabela.pack(fill=tk.BOTH, expand=True)

        larguras = {"RH": 120, "Tipo de Vistoria": 110, "Município": 140, "Corpo Hídrico": 170, "Qt Datas": 80, "Detalhamento por Data": 500}
        for col in self.colunas_exibir:
            self.tabela.heading(col, text=col)
            alinhamento = tk.CENTER if col in ["Qt Datas", "RH", "Tipo de Vistoria"] else tk.W
            self.tabela.column(col, width=larguras.get(col, 150), anchor=alinhamento)

        # Painel Inferior de Detalhes
        frame_detalhes = ttk.LabelFrame(paned, text=" 📸 Contagem de Fotos por Data do Local Selecionado ")
        paned.add(frame_detalhes, weight=2)

        scroll_txt = ttk.Scrollbar(frame_detalhes, orient=tk.VERTICAL)
        self.txt_detalhes = tk.Text(frame_detalhes, yscrollcommand=scroll_txt.set, wrap=tk.WORD, font=("Consolas", 10))
        scroll_txt.config(command=self.txt_detalhes.yview)
        scroll_txt.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_detalhes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.txt_detalhes.insert(tk.END, "Selecione as opções e clique em 'Consultar Fotos'...")

        self.tabela.bind("<<TreeviewSelect>>", self.ao_selecionar_linha)

        # Botão de Exportação
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        btn_exportar = ttk.Button(btn_frame, text="📊 Exportar Relatório de Fotos (Excel)", command=self.exportar_excel)
        btn_exportar.pack(side=tk.RIGHT)

    def carregar_rhs(self):
        rhs = listar_rhs_disponiveis(CAMINHO_RAIZ_REDE)
        if rhs:
            self.cb_rh['values'] = rhs
            self.cb_rh.set(rhs[0])

    def executar_consulta(self):
        rh = self.cb_rh.get()
        tipo = self.cb_vistoria.get()

        if not rh:
            messagebox.showwarning("Aviso", "Selecione uma RH válida.")
            return

        df_res, erro, periodo = escanear_fotos_rede(CAMINHO_RAIZ_REDE, rh, tipo)

        if erro:
            messagebox.showerror("Erro", erro)
            return

        self.lbl_periodo.config(text=f"Período: {periodo}")
        self.df_atual = df_res

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for _, linha in df_res.iterrows():
            valores = [linha[col] for col in self.colunas_exibir]
            self.tabela.insert("", tk.END, values=valores)

        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.insert(tk.END, "Clique em uma linha para ver o detalhamento diário de fotos...")

    def ao_selecionar_linha(self, event):
        item = self.tabela.selection()
        if not item:
            return

        valores = self.tabela.item(item[0], "values")
        municipio, corpo_hidrico = valores[2], valores[3]

        linha_df = self.df_atual[(self.df_atual["Município"] == municipio) & (self.df_atual["Corpo Hídrico"] == corpo_hidrico)]
        
        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.insert(tk.END, f"MUNICÍPIO: {municipio} | CORPO HÍDRICO: {corpo_hidrico}\n")
        self.txt_detalhes.insert(tk.END, "=" * 80 + "\n\n")

        if not linha_df.empty:
            dados_brutos = linha_df.iloc[0]["_dados_brutos"]
            if dados_brutos:
                for data, qtd in sorted(dados_brutos.items()):
                    self.txt_detalhes.insert(tk.END, f" 📂 Pasta [{data}]  --->  {qtd} foto(s) \n")
            else:
                self.txt_detalhes.insert(tk.END, "Nenhuma subpasta de data/foto encontrada nesta localização.")

    def exportar_excel(self):
        if self.df_atual is None or self.df_atual.empty:
            messagebox.showwarning("Aviso", "Sem dados para exportar.")
            return

        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha do Excel", "*.xlsx")],
            title="Salvar como Excel"
        )
        if caminho_salvar:
            df_export = self.df_atual[self.colunas_exibir]
            df_export.to_excel(caminho_salvar, index=False)
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{caminho_salvar}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoVerificacaoFotos(root)
    root.mainloop()
