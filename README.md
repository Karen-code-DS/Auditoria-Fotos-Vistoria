# 📸 Verificação de Registro Fotográfico

Aplicação Desktop em Python desenvolvida para realizar a auditoria, contagem e verificação da organização de imagens das vistorias de campo salvas em servidor de rede.

---

## 📌 Visão Geral

Diferente da auditoria de documentos (PDFs), esta ferramenta foca na validação da documentação visual das vistorias. Ela varre as estruturas de pastas dos corpos hídricos em busca de registros fotográficos, organizando os dados por datas de captura e gerando relatórios de cobertura fotográfica.

---

## 🚀 Funcionalidades Principais

- **Mapeamento de Mídias:** Suporte automático para múltiplos formatos de imagem (`.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`).
- **Agrupamento Temporal:** Identificação e contagem de fotos organizadas por pastas de datas (ex: `2026.08.19`).
- **Nomenclatura Flexível:** Busca inteligente por variações de pastas de imagens (`Fotos`, `Foto`, `Fotografias`).
- **Filtro por Tipo de Vistoria:** Suporte a vistorias do tipo **Manual** e **Mecânico**.
- **Painel de Detalhamento Diário:** Exibição da quantidade exata de capturas por dia para cada corpo hídrico selecionado.
- **Relatórios Gerenciais:** Exportação dos dados consolidados para planilhas do Excel (`.xlsx`).

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.x](https://www.python.org/)**
- **[Tkinter](https://docs.python.org/3/library/tkinter.html):** Interface gráfica e visualização em tabela.
- **[Pandas](https://pandas.pydata.org/):** Consolidação dos registros e contagens.
- **[OpenPyXL](https://openpyxl.readthedocs.io/):** Manipulação e exportação para `.xlsx`.

---

## 📋 Pré-requisitos

- Ter o Python 3.8+ instalado.
- Acesso à unidade de rede configurada (Mapeamento padrão: M:\001 - Vistorias de Campo).

---


## 📂 Estrutura do Repositório

```text
verificacao-fotos-vistoria/
│
├── src/
│   └── verificacao_fotos.py    # Script principal da aplicação de fotos
│
├── .gitignore                  # Filtro de arquivos temporários
├── README.md                   # Documentação do projeto
└── requirements.txt            # Dependências (pandas, openpyxl)
