import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit_authenticator as stauth
import plotly.express as px
from datetime import datetime

# Usuários e senhas (senha já com hash bcrypt)
users = {
    "usernames": {
        "emerson": {
            "name": "Emerson",
            "password": "$2b$12$hPqBcgOtAknHYzGx3kPtBObvOx5JYbVDpMaS1r6eEOo9tpZ6ns7ju"  # senha: 12345
        }
    }
}

# Configuração do autenticador
authenticator = stauth.Authenticate(
    users,
    "dashboard_vendas_cookie",
    "dashboard_vendas_signature",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
    st.title(f"📊 Dashboard de Vendas em Tempo Real - {name}")

    CAMINHO_PASTA = Path(r"H:\Outros computadores\Meu computador\BOT\bot vendas\relatorios")

    if not CAMINHO_PASTA.exists():
        st.error(f"Pasta não encontrada: {CAMINHO_PASTA}")
    else:
        arquivos_xls = [
            CAMINHO_PASTA / f
            for f in os.listdir(CAMINHO_PASTA)
            if f.lower().endswith(".xls")
        ]

        if arquivos_xls:
            arquivos_xls.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            arquivo_mais_recente = arquivos_xls[0]

            st.info(f"Arquivo carregado: `{arquivo_mais_recente.name}`")

            try:
                df = pd.read_excel(arquivo_mais_recente)

                # Ajustes
                df.columns = df.columns.str.strip()
                df["Numero notas"] = pd.to_numeric(df["Numero notas"], errors="coerce")
                df["Valor notas"] = df["Valor notas"].astype(str).str.replace(",", ".")
                df["Valor notas"] = pd.to_numeric(df["Valor notas"], errors="coerce")
                df = df.dropna(subset=["Portador", "Numero notas", "Valor notas"])

                # KPIs
                total_notas = int(df["Numero notas"].sum())
                total_valor = df["Valor notas"].sum()
                ticket_medio = total_valor / total_notas if total_notas else 0

                col1, col2, col3 = st.columns(3)
                col1.metric("🧾 Total de Notas", f"{total_notas}")
                col2.metric("💰 Total Vendido", f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                # Data e hora da última modificação do arquivo
                timestamp = arquivo_mais_recente.stat().st_mtime
                data_hora = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
                st.markdown(f"**Última atualização:** {data_hora}")

                st.markdown("---")

                fig = px.pie(
                    df,
                    values="Valor notas",
                    names="Portador",
                    title="Distribuição de Vendas por Forma de Pagamento",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")
        else:
            st.warning("Nenhum arquivo .xls encontrado na pasta.")

    authenticator.logout("Logout", "sidebar")

elif authentication_status is False:
    st.error("Usuário ou senha incorretos")
elif authentication_status is None:
    st.info("Por favor, faça login para acessar o dashboard")
