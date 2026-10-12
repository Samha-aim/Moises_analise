import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página do Streamlit (deve ser o primeiro comando do Streamlit)
st.set_page_config(
    page_title="Dashboard - Canal do Moises",
    page_icon="📊",
    layout="wide",
)


# Função para carregar os dados do banco SQLite com cache para otimizar performance
@st.cache_data
def carregar_dados():
  conexao = sqlite3.connect("data/canal_moisas.db")
  df = pd.read_sql_query("SELECT * FROM tb_videos_canal", conexao)
  conexao.close()
  # Converte a coluna de data para o formato datetime do Pandas
  df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
  return df


df = carregar_dados()

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard Analítico - Canal do Moises")
st.markdown(
    "Este painel interativo consome os dados extraídos da YouTube Data API"
    " armazenados no banco SQLite."
)

if df.empty:
  st.warning(
      "⚠️ Nenhum dado encontrado no banco. Execute o pipeline `main.py` primeiro!"
  )
else:
  # --- BARRA LATERAL (Filtros) ---
  st.sidebar.header("🔍 Filtros de Análise")

  anos_disponiveis = sorted(df["ano_publicacao"].dropna().unique())
  ano_selecionado = st.sidebar.selectbox(
      "Selecione o Ano", options=["Todos"] + list(anos_disponiveis)
  )

  if ano_selecionado != "Todos":
    df_filtrado = df[df["ano_publicacao"] == ano_selecionado]
  else:
    df_filtrado = df

  # --- CARDS DE MÉTRICAS (KPIs) ---
  st.markdown("### 📌 Visão Geral do Canal")
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.metric("Total de Vídeos", len(df_filtrado))
  with col2:
    st.metric(
        "Total de Visualizações", f"{df_filtrado['visualizacoes'].sum():,}"
    )
  with col3:
    st.metric("Total de Curtidas", f"{df_filtrado['curtidas'].sum():,}")
  with col4:
    media_engajamento = (
        df_filtrado["taxa_engajamento_%"].mean()
        if not df_filtrado.empty
        else 0
    )
    st.metric("Média de Engajamento", f"{media_engajamento:.2f}%")

  st.markdown("---")

  # --- GRÁFICOS INTERATIVOS ---
  col_graf1, col_graf2 = st.columns(2)

  with col_graf1:
    st.markdown("#### 🏆 Top 10 Vídeos Mais Visualizados")
    top_vistos = df_filtrado.nlargest(10, "visualizacoes")
    fig_top = px.bar(
        top_vistos,
        x="visualizacoes",
        y="titulo",
        orientation="h",
        text="visualizacoes",
        color="visualizacoes"
    )
    fig_top.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Visualizações",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig_top, use_container_width=True)

  with col_graf2:
    st.markdown("#### 📈 Relação: Visualizações vs Engajamento")
    fig_scatter = px.scatter(
        df_filtrado,
        x="visualizacoes",
        y="taxa_engajamento_%",
        hover_data=["titulo"],
        color="curtidas",
        labels={
            "visualizacoes": "Visualizações",
            "taxa_engajamento_%": "Taxa de Engajamento (%)",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

  # --- TABELA DE DADOS DETALHADA ---
  st.markdown("---")
  st.markdown("### 📋 Tabela Completa de Vídeos")

  # Caixa de pesquisa interativa
  busca = st.text_input("🔍 Filtrar vídeos por título:")
  if busca:
    df_exibicao = df_filtrado[
        df_filtrado["titulo"].str.contains(busca, case=False, na=False)
    ]
  else:
    df_exibicao = df_filtrado

  st.dataframe(
      df_exibicao[
          [
              "titulo",
              "data_publicacao",
              "visualizacoes",
              "curtidas",
              "comentarios",
              "taxa_engajamento_%",
          ]
      ],
      use_container_width=True,
  )
  