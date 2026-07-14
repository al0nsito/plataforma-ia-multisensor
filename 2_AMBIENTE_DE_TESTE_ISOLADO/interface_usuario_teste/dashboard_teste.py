import streamlit as st
import sqlite3
import pandas as pd
import os
import time
import plotly.express as px

st.set_page_config(page_title="Painel Simulador Testes", layout="wide")
st.title("🧪 AMBIENTE DE TESTE ISOLADO - Painel de Validação")

raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(raiz, "database_teste.db")

def query_teste(q, params=(), commit=False):
    if not os.path.exists(db_path): return None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(q, params)
    if commit:
        conn.commit()
        res = None
    else:
        res = cursor.fetchall()
    conn.close()
    return res

t_live, t_bi, t_cfg = st.tabs(["📺 Monitoramento de Teste", "📊 Gráficos de Teste", "⚙️ Mudar Alvos de Teste"])

with t_cfg:
    st.subheader("Configurações do Simulador Alheio")
    hardware = query_teste("SELECT nome_analise, classes_obrigatorias, fonte_video FROM analises_ativas WHERE id=1")
    if hardware:
        nome_h, classes_h, fonte_h = hardware
        with st.form("form_cfg_teste"):
            n_disp = st.text_input("Nome do Dispositivo Simulado:", value=nome_h)
            a_ia = st.text_input("Objetos Gerados pela Simulação (separe por vírgula):", value=classes_h)
            if st.form_submit_button("🔥 Atualizar Alvos Fictícios"):
                query_teste("UPDATE analises_ativas SET nome_analise=?, classes_obrigatorias=? WHERE id=1", (n_disp, a_ia), commit=True)
                st.success("Simulador atualizado!")

with t_bi:
    st.subheader("Métricas Estatísticas Simuladas")
    if st.button("🔄 Atualizar Gráficos de Teste"):
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM log_infracoes", conn)
            conn.close()
            if not df.empty:
                contagem = df['detalhes_inconformidade'].value_counts().reset_index()
                contagem.columns = ['Desvio', 'Total']
                st.plotly_chart(px.bar(contagem, x='Desvio', y='Total', color='Desvio'), use_container_width=True)
            else: st.warning("Sem dados na simulação.")

with t_live:
    bloco = st.empty()
    while True:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df_logs = pd.read_sql_query("SELECT * FROM log_infracoes ORDER BY id DESC", conn)
            conn.close()
        else: df_logs = pd.DataFrame()
        
        with bloco.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Logs de Teste (Banco de Dados Isolado)**")
                if df_logs.empty: st.info("Aguardando motor simulado...")
                else: st.dataframe(df_logs[["id", "timestamp", "analise_origem", "detalhes_inconformidade", "hash_lacre_sha256"]], use_container_width=True)
            with col2:
                st.markdown("**Imagem do Frame Gerado Sinteticamente**")
                if not df_logs.empty:
                    img_abs = os.path.join(raiz, df_logs["caminho_corte"].iloc[0])
                    if os.path.exists(img_abs): st.image(img_abs, use_container_width=True)
        time.sleep(2)
