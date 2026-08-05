import sqlite3 
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Executive Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BI_THEME = {
    "colors": {
        "bg_app": "#0B0E14",
        "bg_card": "#151A22",
        "border_card": "#222B38",
        "text_main": "#FFFFFF",
        "text_muted": "#8A94A6",
        "primary_purple": "#8B5CF6",
        "primary_cyan": "#00E5FF",
        "positive_text": "#10B981",
        "positive_bg": "rgba(16, 185, 129, 0.15)",
    },
    "categorical": {
        "Norte": "#00E5FF",
        "Nordeste": "#8B5CF6",
        "Sul": "#3B82F6",
        "Sudeste": "#EC4899",
        "Centro-Oeste": "#F59E0B",
        "Hardware": "#8B5CF6",
        "Armazenamento": "#00E5FF",
        "Periféricos": "#EC4899",
        "Monitores": "#3B82F6"
    }
}

def dsa_init_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            date TEXT,
            regiao TEXT,
            categoria TEXT,
            produto TEXT,
            faturamento REAL,
            quantidade INTEGER
        )
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM tb_vendas")

    if cursor.fetchone()[0] == 0:
        np.random.seed(42)
        start_date = date(2026, 1, 1)
        datas = [start_date + timedelta(days = i) for i in range(180)]
        regioes = ["Norte", "Nordeste", "Sul", "Sudeste", "Centro-Oeste"]
        categorias = ["Hardware", "Armazenamento", "Periféricos", "Monitores"]
        
        dict_produtos = {
            "Hardware": {
                "Processador Ryzen 5 5600GT": 850.00, "Processador Ryzen 7 5700X3D": 1550.00,
                "Placa-Mãe Biostar A520MT": 450.00, "Placa de Vídeo RTX 4060 MSI Ventus": 1900.00,
                "Placa de Vídeo RX 6750 XT XFX": 2300.00, "Memória RAM DDR4 8GB": 419.90,
                "Fonte MSI MAG A650BN": 350.00, "Fonte XPG Kyber 850W": 550.00
            },
            "Armazenamento": {
                "SSD Adata SU650 500GB": 220.00, "SSD Kingston A400 480GB": 240.00,
                "SSD NVMe 1TB Kingston NV2": 450.00, "SSD NVMe 2TB WD Black": 950.00
            },
            "Periféricos": {
                "Teclado Mecânico RGB": 250.00, "Mouse Gamer Logitech G203": 150.00,
                "Headset Astro A10": 300.00, "Mousepad Speed Extra Grande": 90.00
            },
            "Monitores": {
                "Monitor 24' 144Hz IPS": 850.00, "Monitor LG Ultragear 27' 144Hz": 1150.00, "Monitor Ultrawide 29'": 1200.00
            }
        }

        rows = []
        for d in datas:
            vendas_diarias = np.random.randint(5, 15)
            for _ in range(vendas_diarias):
                r = np.random.choice(regioes)
                c = np.random.choice(categorias)
                p = np.random.choice(list(dict_produtos[c].keys()))
                preco_base = dict_produtos[c][p]
                quantidade = np.random.randint(1, 25) 
                base_faturamento = preco_base * quantidade
                noise = np.random.uniform(-0.20, 0.20)
                faturamento = max(0, base_faturamento * (1 + noise))
                rows.append((d.isoformat(), r, c, p, round(faturamento, 2), quantidade))

        cursor.executemany(
            "INSERT INTO tb_vendas (date, regiao, categoria, produto, faturamento, quantidade) VALUES (?, ?, ?, ?, ?, ?)", rows
        )
        conn.commit()

def dsa_cria_conexao(db_path = "tech_database.db"): 
    return sqlite3.connect(db_path, check_same_thread = False)

@st.cache_data(ttl=600) 
def dsa_carrega_dados():
    conn = dsa_cria_conexao()
    dsa_init_db(conn) 
    df = pd.read_sql_query("SELECT * FROM tb_vendas", conn, parse_dates = ["date"])
    conn.close()
    return df

def dsa_filtros_sidebar(df):
    st.sidebar.markdown(
        f"""
        <div style="background-color:{BI_THEME['colors']['bg_card']}; padding: 15px; border-radius: 8px; border-left: 5px solid {BI_THEME['colors']['primary_purple']}; text-align: center; margin-bottom: 20px;">
            <h3 style="color:{BI_THEME['colors']['text_main']}; margin:0; font-weight:bold; font-size:18px;">📊 Painel de Filtros</h3>
            <span style="color:{BI_THEME['colors']['text_muted']}; font-size:12px;">Tech Metrics</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.header("Filtros Globais")
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    
    date_range = st.sidebar.date_input("Período de Análise", (min_date, max_date), min_value = min_date, max_value = max_date)

    all_regioes = sorted(df["regiao"].unique())
    selected_regioes = st.sidebar.multiselect("Regiões", all_regioes, default = all_regioes)

    all_categorias = sorted(df["categoria"].unique())
    selected_categorias = st.sidebar.multiselect("Categorias", all_categorias, default = all_categorias)
    
    all_produtos = sorted(df["produto"].unique())
    selected_produtos = st.sidebar.multiselect("Produtos", all_produtos, default = all_produtos)

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    df_filtrado = df[
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date) &
        (df["regiao"].isin(selected_regioes)) &
        (df["categoria"].isin(selected_categorias)) &
        (df["produto"].isin(selected_produtos))
    ].copy()

    st.sidebar.markdown("---")
    with st.sidebar.expander("Suporte & Desenvolvedor", expanded = False):
        st.write("Desenvolvido por Pedro Henrique.")
        st.caption("Conecte-se: www.linkedin.com/in/pedro-henrique-oliveira-dos-santos-743900302")
    
    return df_filtrado


def gerar_mini_sparkline(df_historico, coluna_valor):
    df_agrupado = df_historico.groupby("date")[[coluna_valor]].sum().reset_index()
    fig = px.line(df_agrupado, x="date", y=coluna_valor, template="plotly_dark")
    fig.update_traces(line_shape="spline", line=dict(color=BI_THEME["colors"]["primary_purple"], width=2), fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.1)')
    fig.update_layout(
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0), 
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)", 
        showlegend=False, 
        height=40
    )
    return fig

def dsa_renderiza_cards_kpis(df):
    total_faturamento = df["faturamento"].sum()
    total_qty = df["quantidade"].sum()
    avg_ticket = total_faturamento / total_qty if total_qty > 0 else 0
    transactions = df.shape[0]
    
    card_style = f"background-color: {BI_THEME['colors']['bg_card']}; padding: 20px; border-radius: 12px; border: 1px solid {BI_THEME['colors']['border_card']}; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);"
    title_style = f"margin: 0; font-size: 14px; color: {BI_THEME['colors']['text_muted']}; font-weight: 500;"
    val_style = f"margin: 10px 0 5px 0; font-size: 26px; color: {BI_THEME['colors']['text_main']}; font-weight: bold;"
    pill_style = f"background-color: {BI_THEME['colors']['positive_bg']}; color: {BI_THEME['colors']['positive_text']}; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;"

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f'<div style="{card_style}"><p style="{title_style}">Receita Bruta</p><h2 style="{val_style}">R$ {total_faturamento:,.0f}</h2><span style="{pill_style}">+24.6% ↗</span></div><br>', unsafe_allow_html=True)
        st.plotly_chart(gerar_mini_sparkline(df, "faturamento"), use_container_width=True, key="spark_faturamento_unique")
        
    with c2:
        st.markdown(f'<div style="{card_style}"><p style="{title_style}">Unidades Vendidas</p><h2 style="{val_style}">{total_qty:,.0f}</h2><span style="{pill_style}">+12.5% ↗</span></div><br>', unsafe_allow_html=True)
        st.plotly_chart(gerar_mini_sparkline(df, "quantidade"), use_container_width=True, key="spark_qtd_unique")

    with c3:
        st.markdown(f'<div style="{card_style}"><p style="{title_style}">Ticket Médio</p><h2 style="{val_style}">R$ {avg_ticket:,.2f}</h2><span style="{pill_style}">+3.1% ↗</span></div><br>', unsafe_allow_html=True)
        st.plotly_chart(gerar_mini_sparkline(df, "faturamento"), use_container_width=True, key="spark_ticket_unique")

    with c4:
        st.markdown(f'<div style="{card_style}"><p style="{title_style}">Volume de Transações</p><h2 style="{val_style}">{transactions:,}</h2><span style="{pill_style}">+11.3% ↗</span></div><br>', unsafe_allow_html=True)
        st.plotly_chart(gerar_mini_sparkline(df, "quantidade"), use_container_width=True, key="spark_trans_unique")
        
    return total_faturamento, total_qty, avg_ticket

def dsa_gera_pdf_report(df_filtrado, total_faturamento, total_quantidade, avg_ticket):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Executive Sales Performance Report", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(10, 35, 190, 25, 'F')
    
    pdf.set_y(40)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 8, "Receita Total", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, "Quantidade", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, "Ticket Medio", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(60, 8, f"R$ {total_faturamento:,.2f}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"{total_quantidade:,}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"R$ {avg_ticket:,.2f}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Top 15 Transacoes do Periodo:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    col_widths = [30, 30, 30, 40, 25, 30] 
    headers = ["Data", "Regiao", "Categoria", "Produto", "Qtd", "Receita"]
    
    pdf.set_font("Helvetica", "B", 9)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, 1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 9)
    df_top = df_filtrado.sort_values("faturamento", ascending=False).head(15)
    for _, row in df_top.iterrows():
        data = [
            str(row['date'].date()), row['regiao'], row['categoria'],
            row['produto'][:20], str(row['quantidade']), f"R$ {row['faturamento']:,.2f}"
        ]
        for i, d in enumerate(data):
            safe_txt = str(d).encode("latin-1", "replace").decode("latin-1")
            pdf.cell(col_widths[i], 7, safe_txt, 1, align=('C' if i==4 else 'L'), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln()

    result = pdf.output() 
    return result.encode("latin-1") if isinstance(result, str) else bytes(result)

def dsa_set_custom_theme():
    css = f"""
    <style>
        [data-testid="stAppViewContainer"], .stApp {{ background-color: {BI_THEME['colors']['bg_app']} !important; }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        
        [data-testid="stSidebar"] {{
            background-color: {BI_THEME['colors']['bg_card']} !important;
            border-right: 1px solid {BI_THEME['colors']['border_card']} !important;
        }}
        
        [data-testid="stPlotlyChart"] {{
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        
        [data-baseweb="tag"] {{
            background-color: {BI_THEME['colors']['primary_purple']} !important;
            color: #FFFFFF !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html = True)

def tech_metrics_app():
    dsa_set_custom_theme()
    df = dsa_carrega_dados()
    df_filtrado = dsa_filtros_sidebar(df)

    col_texto, col_imagem = st.columns([1.5, 1])
    
    with col_texto:
        st.markdown(f"""
            <div style="border-top: 3px solid {BI_THEME['colors']['primary_purple']}; width: 80%; padding-top: 15px; margin-bottom: 20px;">
                <h1 style="color: {BI_THEME['colors']['text_main']}; font-size: 4.5rem; font-style: italic; font-weight: 800; margin: 0; letter-spacing: -1px; line-height: 1;">Tech Metrics</h1>
                <p style="color: {BI_THEME['colors']['text_main']}; font-size: 1.1rem; margin-top: 10px; font-weight: 400;">
                    Uma análise de vendas de componentes de hardware voltada para o consumidor brasileiro.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_imagem:
       
        st.markdown(
            '<img src="https://www.mps.com.br/wp-content/uploads/business-intelligence-predictive-analytics-power-b-newdesignl-5c7c7705527632.6064732815516608053378.png" style="max-width: 100%; max-height: 200px; float: right;">', 
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    col_kpis, col_gauge = st.columns([3, 1])
    
    with col_kpis:
        total_faturamento, total_qty, avg_ticket = dsa_renderiza_cards_kpis(df_filtrado)
        
    with col_gauge:
        st.markdown(f"<p style='color:{BI_THEME['colors']['text_muted']}; text-align:center; font-size:14px; margin-bottom:0; font-weight: 500;'>Margem de Lucro Estimada(EM TESTE)</p>", unsafe_allow_html=True)
        
        margem_estimada = 0.15 if total_faturamento > 500000 else 0.13
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = margem_estimada * 100,
            number = {'suffix': "%", 'font': {'color': '#FFFFFF', 'size': 32}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': BI_THEME["colors"]["primary_cyan"]},
                'bgcolor': BI_THEME["colors"]["bg_card"],
                'borderwidth': 0
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=10), height=140
        )
        st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_profit")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Visual - Dashboard ", "📋 Dados Tabelados e Exportações"])

    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown(f"<h4 style='margin-bottom:0; color:{BI_THEME['colors']['text_main']};'>Vendas brutas ao longo do ano</h4>", unsafe_allow_html=True)
            daily_rev = df_filtrado.groupby("date")[["faturamento"]].sum().reset_index()
            
            fig_line = px.line(daily_rev, x = "date", y = "faturamento", template = "plotly_dark", height = 360)
            fig_line.update_traces(line_shape="spline", fill = 'tozeroy', line = dict(color = BI_THEME["colors"]["primary_purple"], width = 3), fillcolor='rgba(139, 92, 246, 0.1)')
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=BI_THEME['colors']['border_card'])
            )
            st.plotly_chart(fig_line, use_container_width=True) 

        with col_right:
            st.markdown(f"<h4 style='margin-bottom:0; color:{BI_THEME['colors']['text_main']};'>Vendas brutas por produto</h4>", unsafe_allow_html=True)
            cat_rev = df_filtrado.groupby("categoria")[["faturamento"]].sum().reset_index()
            
            fig_pie = px.pie(
                cat_rev, values="faturamento", names="categoria", hole=0.6,
                template="plotly_dark", height=360,
                color="categoria", color_discrete_map=BI_THEME["categorical"]
            )
            
            fig_pie.update_traces(
                textposition='inside', 
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<extra></extra>"
            )
            
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.0,
                    font=dict(color=BI_THEME['colors']['text_muted'], size=13),
                    title=""
                ),
                margin=dict(l=0, r=80, t=30, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        c_a, c_b = st.columns(2)
        
        with c_a:
            st.markdown(f"<h4 style='margin-bottom:0; color:{BI_THEME['colors']['text_main']};'>Vendas por Região (Mapa)</h4>", unsafe_allow_html=True)
            
            reg_data = df_filtrado.groupby("regiao")[["faturamento", "quantidade"]].sum().reset_index()
            
            coords_regioes = {
                "Norte": {"lat": -4.0, "lon": -62.0},
                "Nordeste": {"lat": -8.0, "lon": -39.0},
                "Centro-Oeste": {"lat": -15.5, "lon": -53.0},
                "Sudeste": {"lat": -21.5, "lon": -46.0},
                "Sul": {"lat": -27.5, "lon": -52.0}
            }
            
            reg_data["lat"] = reg_data["regiao"].map(lambda x: coords_regioes.get(x, {}).get("lat", 0))
            reg_data["lon"] = reg_data["regiao"].map(lambda x: coords_regioes.get(x, {}).get("lon", 0))

            fig_map = px.scatter_mapbox(
                reg_data, lat="lat", lon="lon", size="faturamento", color="regiao",
                hover_name="regiao", hover_data={"lat": False, "lon": False, "faturamento": ":,.2f", "quantidade": True},
                color_discrete_map=BI_THEME["categorical"],
                zoom=3, center={"lat": -14.0, "lon": -52.0}, 
                mapbox_style="carto-darkmatter", height=340
            )
            
            fig_map.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                margin=dict(l=0, r=0, t=20, b=0), showlegend=False
            )
            
            st.plotly_chart(fig_map, use_container_width=True) 
            
        with c_b:
            st.markdown(f"<h4 style='margin-bottom:0; color:{BI_THEME['colors']['text_main']};'>Análise de Performance por Temporada</h4>", unsafe_allow_html=True)
            dias_pt_map = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
            dias_pt_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

            df_filtrado["weekday_num"] = df_filtrado["date"].dt.dayofweek
            df_filtrado["dia_semana"] = df_filtrado["weekday_num"].map(dias_pt_map)
            wd_rev = df_filtrado.groupby("dia_semana")[["faturamento"]].mean().reindex(dias_pt_ordem).reset_index()

            fig_heat = px.bar(wd_rev, x="dia_semana", y="faturamento", template="plotly_dark", height=340)
            fig_heat.update_traces(marker_color=BI_THEME["colors"]["primary_purple"])
            fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heat, use_container_width=True)

    with tab2:
        st.subheader("Tabela de vendas completa")
        st.dataframe(df_filtrado, use_container_width=True, height=350) 
        st.markdown("### Área de exportação")
        
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label = "📥 Baixar Planilha (CSV)", data = csv,
                file_name = "executive_data.csv", mime = "text/csv", use_container_width=True
            )
            
        with c_exp2:
            if st.button("🖨️ Compilar Relatório PDF", use_container_width=True): 
                with st.spinner("Gerando layout PDF corporativo..."):
                    pdf_bytes = dsa_gera_pdf_report(df_filtrado, total_faturamento, total_qty, avg_ticket)
                    st.download_button(
                        label = "⚡ Baixar Relatório PDF Assinado", data = pdf_bytes,
                        file_name = f"Executive_Report_{date.today()}.pdf", mime = "application/pdf",
                        key = "pdf-download-final"
                    )

if __name__ == "__main__":
    tech_metrics_app()
