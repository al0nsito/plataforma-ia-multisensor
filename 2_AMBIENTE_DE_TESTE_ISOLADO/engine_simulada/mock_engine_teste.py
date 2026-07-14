import os
import sqlite3
import time
import random
import hashlib
import numpy as np
import cv2
from datetime import datetime

def rodar_simulador_teste():
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(raiz, "database_teste.db")
    pasta_cortes = os.path.join(raiz, "evidencias_simuladas")
    os.makedirs(pasta_cortes, exist_ok=True)

    print("🚀 [TESTE] Motor de IA Simulado ativo. Gravando dados fictícios...")

    try:
        while True:
            time.sleep(random.randint(3, 5))
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nome_analise, classes_obrigatorias FROM analises_ativas WHERE id = 1")
            dados = cursor.fetchone()
            
            if dados:
                nome_canal, classes_str = dados
                lista_classes = [c.strip() for c in classes_str.split(",") if c.strip()]
                
                if lista_classes:
                    item_esquecido = random.choice(lista_classes)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    img_teste = np.zeros((300, 200, 3), dtype=np.uint8)
                    cv2.putText(img_teste, f"ID: {random.randint(10,99)}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    nome_arq = f"teste_recorte_{int(time.time())}.jpg"
                    cv2.imwrite(os.path.join(pasta_cortes, nome_arq), img_teste)
                    
                    lacre_sha = hashlib.sha256(img_teste.tobytes()).hexdigest()
                    caminho_relativo = f"evidencias_simuladas/{nome_arq}"
                    
                    cursor.execute("""
                        INSERT INTO log_infracoes (timestamp, analise_origem, detalhes_inconformidade, hash_lacre_sha256, caminho_corte)
                        VALUES (?, ?, ?, ?, ?)
                    """, (timestamp, nome_canal, f"Ausencia de: {item_esquecido} (TESTE)", lacre_sha, caminho_relativo))
                    conn.commit()
                    print(f"📡 [TESTE] Evento gerado com sucesso para o item '{item_esquecido}'")
            conn.close()
    except KeyboardInterrupt:
        print("\n🛑 Simulador de Teste Encerrado.")

if __name__ == "__main__":
    rodar_simulador_teste()
