import streamlit as st
import sqlite3
import pandas as pd
import os
import time

st.set_page_config(page_title="Painel Industrial Real", layout="wide")
st.title("⚙️ SISTEMA INDUSTRIAL - Linha de Produção Real")

raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(raiz, "database.db")

def query_real(q, params=(), commit=False):
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

t_monitor, t_cfg = st.tabs(["📺 Fluxo Real em Tempo Real", "🔧 Interfaces de Rede/USB"])

with t_cfg:
    st.subheader("Configurações das Interfaces de Integração Física")
    hardware = query_real("SELECT nome_analise, fonte_video FROM analises_ativas WHERE id=1")
    if hardware:
        nome_h, fonte_h = hardware
        with st.form("form_cfg_real"):
            n_disp = st.text_input("Identificação do Dispositivo:", value=nome_h)
            n_fonte = st.text_input("Interface (0 para USB, IP do Celular Wi-Fi, ou MP4):", value=fonte_h)
            if st.form_submit_button("💾 Salvar e Reiniciar Barramento"):
                query_real("UPDATE analises_ativas SET nome_analise=?, fonte_video=? WHERE id=1", (n_disp, n_fonte), commit=True)
                st.success("Barramento de hardware alterado!")

with t_monitor:
    bloco = st.empty()
    while True:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM log_infracoes ORDER BY id DESC", conn)
            conn.close()
        else: df = pd.DataFrame()
        
        with bloco.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Logs de Eventos Reais (Visão Computacional)**")
                if df.empty: st.info("Aguardando detecção de pessoas na câmera...")
                else: st.dataframe(df[["id", "timestamp", "analise_origem", "detalhes_inconformidade", "hash_lacre_sha256"]], use_container_width=True)
            with col2:
                st.markdown("**Corte de Frame (Fatiamento NumPy Real)**")
                if not df.empty:
                    img_abs = os.path.join(raiz, df["caminho_corte"].iloc[0])
                    if os.path.exists(img_abs): st.image(img_abs, use_container_width=True, caption="Recorte de Pessoa")
        time.sleep(2)
