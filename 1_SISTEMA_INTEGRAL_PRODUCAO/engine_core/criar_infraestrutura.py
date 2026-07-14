import sqlite3
import os

def inicializar_banco_producao():
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(raiz, "database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analises_ativas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_analise TEXT,
        classes_obrigatorias TEXT,
        fonte_video TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS log_infracoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        analise_origem TEXT,
        detalhes_inconformidade TEXT,
        hash_lacre_sha256 TEXT,
        caminho_corte TEXT
    )""")

    cursor.execute("SELECT COUNT(*) FROM analises_ativas")
    if cursor.fetchone() == 0:
        cursor.execute("""
        INSERT INTO analises_ativas (nome_analise, classes_obrigatorias, fonte_video) 
        VALUES ('Hardware Producao - Principal', 'person', '0')
        """)

    conn.commit()
    conn.close()
    print("✅ Banco de DADOS DE PRODUÇÃO real inicializado!")

if __name__ == "__main__":
    inicializar_banco_producao()