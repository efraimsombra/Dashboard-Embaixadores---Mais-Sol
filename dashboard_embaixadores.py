import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# Configuração da página
# ------------------------------
st.set_page_config(
    page_title="Dashboard Embaixadores - Mais Sol",
    page_icon="🌞",
    layout="wide",
)

# ------------------------------
# Carregamento e tratamento dos dados
# ------------------------------
@st.cache_data
def load_data(path: str = "embaixadores_resumo.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # Mapear nomes de colunas que podem vir diferentes
    col_map = {
        "Nome": "Nome",
        "Telefone": "Telefone",
        "Email": "Email",
        "E-mail": "Email",
        "Leads indicados (total)": "Leads indicados (total)",
        "Leads indicados": "Leads indicados (total)",
        "N° de Leads Fechados": "Leads fechados",
        "Leads fechados": "Leads fechados",
        "Taxa de conversão dos indicados (%)": "Taxa conversão (%)",
        "Taxa conversão (%)": "Taxa conversão (%)",
        "Data da Ultima Indicação": "Data última indicação",
        "Data Ultima indicacao": "Data última indicação",
        "Data última indicação": "Data última indicação",
        "Soma do Benefício": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Benefício ": "Soma Benefício",
        "Soma do Beneficio ": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Benefício": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
        "Soma do Beneficio": "Soma Benefício",
    }

    # renomear o que bater com o map
    df = df.rename(columns={c: col_map.get(c, c) for c in df.columns})

    # garantir colunas principais
    for c in [
        "Nome",
        "Telefone",
        "Email",
        "Leads indicados (total)",
        "Leads fechados",
        "Soma Benefício",
        "Data última indicação",
    ]:
        if c not in df.columns:
            df[c] = None

    # numéricas
    num_cols = ["Leads indicados (total)", "Leads fechados", "Soma Benefício"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # datas
    df["Data última indicação"] = pd.to_datetime(
        df["Data última indicação"], errors="coerce"
    )

    # ---------------- KPIs ----------------

    # Taxa de conversão
    df["Taxa conversão (%)"] = (
        df["Leads fechados"] / df["Leads indicados (total)"]
    ) * 100
    df.loc[df["Leads indicados (total)"] == 0, "Taxa conversão (%)"] = None

    # Valor médio por indicação
    df["Valor médio por indicação"] = (
        df["Soma Benefício"] / df["Leads indicados (total)"]
    )
    df.loc[df["Leads indicados (total)"] == 0, "Valor médio por indicação"] = None

    # Dias desde a última indicação
    today = pd.to_datetime(datetime.now().date())
    df["Dias desde última indicação"] = (today - df["Data última indicação"]).dt.days

    # Status 90 dias
    def status_90(dias):
        if pd.isna(dias):
            return "Sem indicações"
        return "Ativo (≤90d)" if dias <= 90 else "Inativo (>90d)"

    df["Status 90 dias"] = df["Dias desde última indicação"].apply(status_90)

    # ROI – só se existir coluna de receita
    if "Receita Gerada" in df.columns:
        df["Receita Gerada"] = pd.to_numeric(df["Receita Gerada"], errors="coerce")
        df["ROI"] = df["Receita Gerada"] / df["Soma Benefício"]
    else:
        df["ROI"] = None

    # Velocidade de indicação (leads/dia)
    df["Velocidade indicação (leads/dia)"] = df.apply(
        lambda row: row["Leads indicados (total)"] / row["Dias desde última indicação"]
        if pd.notna(row["Dias desde última indicação"])
        and row["Dias desde última indicação"] > 0
        else None,
        axis=1,
    )

    # Score e Rank
    df["Leads indicados (total)"].fillna(0, inplace=True)
    df["Leads fechados"].fillna(0, inplace=True)
    df["Soma Benefício"].fillna(0, inplace=True)
    df["Taxa conversão (%)"].fillna(0, inplace=True)

    max_beneficio = df["Soma Benefício"].max()
    if pd.isna(max_beneficio) or max_beneficio <= 0:
        beneficio_norm = 0
    else:
        beneficio_norm = df["Soma Benefício"] / max_beneficio

    df["Score"] = (
        df["Leads fechados"] * 3
        + df["Leads indicados (total)"] * 1
        + beneficio_norm * 2
        + (df["Taxa conversão (%)"] / 25)
    )

    df = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1

    return df


df = load_data()

# ------------------------------
# Filtros - Sidebar
# ------------------------------
st.sidebar.header("🔍 Filtros")

status_options = ["Todos"] + sorted(df["Status 90 dias"].dropna().unique().tolist())
selected_status = st.sidebar.selectbox("Status nos últimos 90 dias", status_options)

# slider só se tiver algum lead
max_leads_raw = df["Leads indicados (total)"].max()
if pd.isna(max_leads_raw) or max_leads_raw <= 0:
    st.sidebar.write("Nenhum lead indicado registrado ainda.")
    min_leads = 0
else:
    max_leads = int(max_leads_raw)
    min_leads = st.sidebar.slider(
        "Mínimo de leads indicados",
        min_value=0,
        max_value=max_leads,
        value=0,
    )

nome_busca = st.sidebar.text_input("Buscar embaixador por nome")

filtered_df = df.copy()

if selected_status != "Todos":
    filtered_df = filtered_df[filtered_df["Status 90 dias"] == selected_status]

filtered_df = filtered_df[filtered_df["Leads indicados (total)"] >= min_leads]

if nome_busca:
    filtered_df = filtered_df[
        filtered_df["Nome"].fillna("").str.contains(nome_busca, case=False, na=False)
    ]

# ------------------------------
# Cabeçalho
# ------------------------------
st.title("🌞 Dashboard de Embaixadores - Mais Sol")
st.markdown(
    "Acompanhe o desempenho dos embaixadores, volume de indicações, fechamento e benefícios pagos."
)

# ------------------------------
# KPIs gerais
# ------------------------------
total_embaixadores = df["Nome"].nunique()
total_leads = int(df["Leads indicados (total)"].sum())
total_fechados = int(df["Leads fechados"].sum())
taxa_media_conv = (total_fechados / total_leads * 100) if total_leads > 0 else 0
total_beneficio = df["Soma Benefício"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Embaixadores únicos", total_embaixadores)
col2.metric("Leads indicados (total)", total_leads)
col3.metric("Leads fechados (total)", total_fechados)
col4.metric("Taxa média de conversão (%)", f"{taxa_media_conv:.1f}")

col5, col6 = st.columns(2)
col5.metric(
    "Benefício total pago (R$)",
    f"{total_beneficio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
)

ativos_90 = (df["Status 90 dias"] == "Ativo (≤90d)").sum()
col6.metric("Embaixadores ativos (≤90 dias)", int(ativos_90))

st.markdown("---")

# ------------------------------
# Ranking
# ------------------------------
st.subheader("🏆 Ranking de Embaixadores (por Score)")

cols_rank = [
    "Rank",
    "Nome",
    "Leads indicados (total)",
    "Leads fechados",
    "Taxa conversão (%)",
    "Soma Benefício",
    "Valor médio por indicação",
    "Status 90 dias",
]
ranking_df = filtered_df[cols_rank].copy()
st.dataframe(ranking_df, use_container_width=True)

# ------------------------------
# Gráficos
# ------------------------------
st.markdown("### 📈 Visualizações")

# Top 10 por benefício
if not filtered_df.empty:
    top_beneficio = filtered_df.nlargest(10, "Soma Benefício")
    fig_beneficio = px.bar(
        top_beneficio,
        x="Nome",
        y="Soma Benefício",
        title="Top 10 Embaixadores por Benefício Recebido",
        text_auto=".2s",
    )
    fig_beneficio.update_layout(
        xaxis_title="Embaixador",
        yaxis_title="Benefício (R$)",
    )
    st.plotly_chart(fig_beneficio, use_container_width=True)

    # Top 10 por taxa de conversão (mín. 3 leads)
    df_conv = filtered_df[filtered_df["Leads indicados (total)"] >= 3].copy()
    df_conv = df_conv.sort_values("Taxa conversão (%)", ascending=False).head(10)
    if not df_conv.empty:
        fig_conv = px.bar(
            df_conv,
            x="Nome",
            y="Taxa conversão (%)",
            title="Top 10 por Taxa de Conversão (mín. 3 leads)",
            text_auto=".1f",
        )
        fig_conv.update_layout(
            xaxis_title="Embaixador",
            yaxis_title="Taxa de conversão (%)",
        )
        st.plotly_chart(fig_conv, use_container_width=True)

    # Pizza status 90 dias
    st.markdown("### ⏱ Status nos últimos 90 dias")
    status_counts = filtered_df["Status 90 dias"].value_counts().reset_index()
    status_counts.columns = ["Status 90 dias", "Quantidade"]
    fig_status = px.pie(
        status_counts,
        values="Quantidade",
        names="Status 90 dias",
        title="Distribuição de Atividade (90 dias)",
        hole=0.4,
    )
    st.plotly_chart(fig_status, use_container_width=True)
else:
    st.info("Nenhum embaixador atende aos filtros selecionados no momento.")

# ------------------------------
# Tabela detalhada
# ------------------------------
st.markdown("### 📋 Dados detalhados (com cálculos)")
st.dataframe(filtered_df, use_container_width=True)
