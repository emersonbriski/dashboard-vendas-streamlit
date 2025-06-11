import streamlit as st
import pandas as pd
import os
from pathlib import Path
import plotly.express as px
from datetime import datetime

# Usuário e senha fixos (você pode mudar aqui)
USUARIO = "admin"
SENHA = "1234"

def carregar_dados():
    CAMINHO_PASTA = Path(".")

    if not CAMINHO_PASTA.exists():
        st.error(f"Pasta não encontrada: {CAMINHO_PASTA}")
        return None, None

    arquivos_xls = [CAMINHO_PASTA / f for f in os.listdir(CAMINHO_PASTA) if f.lower().endswith(".xls")]
    if not arquivos_xls:
        st.warning("Nenhum arquivo .xls encontrado na pasta.")
        return None, None

    arquivos_xls.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    arquivo_mais_recente = arquivos_xls[0]

    try:
        df = pd.read_excel(arquivo_mais_recente)
        # Corrige nomes de colunas
        df.columns = df.columns.str.strip()
        # Converte colunas numéricas
        df["Numero notas"] = pd.to_numeric(df["Numero notas"], errors="coerce")
        df["Valor notas"] = df["Valor notas"].astype(str).str.replace(",", ".")
        df["Valor notas"] = pd.to_numeric(df["Valor notas"], errors="coerce")
        df = df.dropna(subset=["Portador", "Numero notas", "Valor notas"])
        return df, arquivo_mais_recente.stat().st_mtime
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None, None

def dashboard(df, ultima_atualizacao_timestamp):
    st.title("📊 Dashboard de Vendas em Tempo Real")

    if ultima_atualizacao_timestamp:
        datahora = datetime.fromtimestamp(ultima_atualizacao_timestamp).strftime("%d/%m/%Y %H:%M:%S")
        st.markdown(
            f"<p style='color:#00FF00; font-weight: bold; font-size: 16px;'>🕒 Última atualização: {datahora}</p>",
            unsafe_allow_html=True
        )

    total_notas = int(df["Numero notas"].sum())
    total_valor = df["Valor notas"].sum()
    ticket_medio = total_valor / total_notas if total_notas else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("🧾 Total de Notas", f"{total_notas}")
    col2.metric("💰 Total Vendido", f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    fig = px.pie(
        df,
        values="Valor notas",
        names="Portador",
        title="Distribuição de Vendas por Forma de Pagamento",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    if 'login' not in st.session_state:
        st.session_state.login = False

    if not st.session_state.login:
        st.markdown("## 🔐 Acesso ao Dashboard")
        st.markdown("Informe suas credenciais para visualizar os dados de vendas.")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://img.icons8.com/fluency/96/login-rounded-right.png", width=70)
        with col2:
            usuario_input = st.text_input("👤 Usuário")
            senha_input = st.text_input("🔑 Senha", type="password")

        if st.button("🚪 Entrar"):
            if usuario_input == USUARIO and senha_input == SENHA:
                st.session_state.login = True
                st.rerun()

            else:
                st.error("Usuário ou senha incorretos.")
    else:
        df, ultima_atualizacao = carregar_dados()
        if df is not None:
            dashboard(df, ultima_atualizacao)

        st.markdown("---")
        if st.button("🔓 Sair"):
            st.session_state.login = False
            st.rerun()



if __name__ == "__main__":
    main()
