# Tech Metrics - Dashboard Interativo de Sales Analytics para Hardware

Este é um projeto de Data App interativo desenvolvido em Python com **Streamlit** para análise de dados de vendas (Sales Analytics) focado no mercado de hardware, componentes de PC e periféricos. 

O painel foi populado com métricas baseadas nas tendências de consumo do mercado brasileiro atual, cobrindo componentes populares de alta demanda como processadores AMD Ryzen, placas de vídeo NVIDIA RTX, armazenamento NVMe e periféricos.

## Funcionalidades   

- **Análise Macroeconômica:** Visualização de Receita Total, Total de Transações e Margem Média através de cartões de métricas dinâmicos.
- **Mix de Categorias:** Gráfico interativo (Donut Chart) mapeando a distribuição de vendas por categorias (Hardware, Armazenamento, Periféricos e Monitores).
- **Evolução Diária:** Gráfico de linhas mostrando a tendência de faturamento ao longo do tempo.
- **Performance Regional & Temporal:** Análises segmentadas por regiões e dias da semana para identificação de picos de faturamento.
- **Filtros Avançados:** Barra lateral responsiva com filtros dinâmicos por período de data, região e seleção específica de componentes.
- **Exportação de Relatórios:** Funcionalidade integrada para geração e download de relatórios analíticos em PDF e planilhas CSV em tempo real.

## Stack Tecnológica

- **Linguagem:** Python 3.13+
- **Interface & Front-end:** Streamlit
- **Manipulação de Dados:** Pandas & NumPy
- **Visualização Gráfica:** Plotly Express (Dark Theme)
- **Banco de Dados:** SQLite (Engine de persistência local)
- **Engine de Relatórios:** FPDF

## Como Executar o Projeto Localmente

Abra o terminal na pasta do projeto e execute a sequência de comandos abaixo para criar o ambiente isolado, instalar as dependências e rodar a aplicação:

```bash
# 1. Criar o ambiente virtual com Conda
conda create --name tech_env python=3.13 -y

# 2. Ativar o ambiente
conda activate tech_env

# 3. Instalar as dependências necessárias
conda install pip -y
pip install -r requirements.txt

# 4. Executar a aplicação
streamlit run app.py
