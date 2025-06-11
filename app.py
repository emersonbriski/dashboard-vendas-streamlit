import streamlit as st
import pandas as pd
import os
from pathlib import Path
import plotly.express as px  # Import aqui, no topo

# Configuração da página
st.set_page_config(page_title="Vendas Benjamin", layout="wide")
st.title("📊 Quitanda Benjamin")

# 🔧 Caminho da pasta sincronizada do Google Drive (ajuste aqui!)
CAMINHO_PASTA = Path(r"H:\Outros computadores\Meu computador\BOT\bot vendas\relatorios")

# Verifica se a pasta existe
if not CAMINHO_PASTA.exists():
    st.error(f"Pasta não encontrada: {CAMINHO_PASTA}")
else:
    # Lista todos os arquivos .xls na pasta
    arquivos_xls = [
        CAMINHO_PASTA / f
        for f in os.listdir(CAMINHO_PASTA)
        if f.lower().endswith(".xls")
    ]

    if arquivos_xls:
        # Ordena pela data de modificação (mais recente primeiro)
        arquivos_xls.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        arquivo_mais_recente = arquivos_xls[0]

        # st.info(f"Arquivo carregado: `{arquivo_mais_recente.name}`")

                # Mostrar data/hora da última atualização
        import datetime
        timestamp = arquivo_mais_recente.stat().st_mtime
        data_modificacao = datetime.datetime.fromtimestamp(timestamp)
        data_formatada = data_modificacao.strftime("%d/%m/%Y %H:%M:%S")
        st.markdown(
            f'<p style="font-size:18px; color:green;">Última atualização: <strong>{data_formatada}</strong></p>',
            unsafe_allow_html=True
        )    

        # Lê o conteúdo do Excel
        try:
            df = pd.read_excel(arquivo_mais_recente)

            # Corrige nomes de colunas se necessário
            df.columns = df.columns.str.strip()

            # Converte colunas numéricas
            df["Numero notas"] = pd.to_numeric(df["Numero notas"], errors="coerce")
            df["Valor notas"] = df["Valor notas"].astype(str).str.replace(",", ".")
            df["Valor notas"] = pd.to_numeric(df["Valor notas"], errors="coerce")

            # Remove linhas vazias
            df = df.dropna(subset=["Portador", "Numero notas", "Valor notas"])

            # Calcula totais
            total_notas = int(df["Numero notas"].sum())
            total_valor = df["Valor notas"].sum()
            ticket_medio = total_valor / total_notas if total_notas else 0

            # KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("🧾 Total de Notas", f"{total_notas}")
            col2.metric("💰 Total Vendido", f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.markdown("---")

            # Gráfico de pizza
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
