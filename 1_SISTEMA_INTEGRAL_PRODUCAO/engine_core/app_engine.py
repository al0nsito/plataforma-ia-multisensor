import os
import cv2
import numpy as np
import sqlite3
import time
import queue
import threading
import hashlib
from datetime import datetime
from ultralytics import YOLO

PROCESS_FPS = 30

def worker_captura(fonte, buffer_q, stop_e):
    origem = int(fonte) if str(fonte).isdigit() else fonte
    while not stop_e.is_set():
        cap = cv2.VideoCapture(origem)
        while not stop_e.is_set():
            ret, frame = cap.read()
            if not ret: break
            if buffer_q.qsize() < 30: buffer_q.put(frame)
            time.sleep(1.0 / PROCESS_FPS)
        cap.release()

def rodar_engine_real():
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(raiz, "database.db")
    pasta_cortes = os.path.join(raiz, "evidencias_recortes")
    os.makedirs(pasta_cortes, exist_ok=True)

    print("[IA CORE] Carregando Rede Neural YOLO real para Produção...")
    modelo_ia = YOLO("yolov8n.pt")
    
    threads, buffers, stop_events = {}, {}, {}
    frame_id = 0

    try:
        while True:
            frame_id += 1
            time.sleep(1.0 / PROCESS_FPS)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_analise, fonte_video FROM analises_ativas WHERE id = 1")
            analise = cursor.fetchone()
            if not analise: 
                conn.close()
                continue
            id_r, nome_canal, fonte = analise

            if id_r not in threads:
                buffers[id_r] = queue.Queue()
                stop_events[id_r] = threading.Event()
                t = threading.Thread(target=worker_captura, args=(fonte, buffers[id_r], stop_events[id_r]), daemon=True)
                t.start()
                threads[id_r] = t
                print(f"📡 [HARDWARE REAL ATIVO] Conectado na interface: {fonte}")

            q = buffers[id_r]
            if q.empty() or frame_id % PROCESS_FPS != 0:
                conn.close()
                continue
                
            frame_bruto = q.get()
            resultados = modelo_ia.track(frame_bruto, classes=[0], persist=True, verbose=False)
            
            if resultados and len(resultados) > 0 and resultados[0].boxes is not None and resultados[0].boxes.id is not None:
                boxes = resultados[0].boxes.xyxy.cpu().numpy().astype(int)
                ids_p = resultados[0].boxes.id.cpu().numpy().astype(int)
                
                for box, id_p in zip(boxes, ids_p):
                    x1, y1, x2, y2 = box
                    y1, y2 = max(0, y1), min(frame_bruto.shape[0], y2)
                    x1, x2 = max(0, x1), min(frame_bruto.shape[1], x2)
                    
                    recorte = frame_bruto[y1:y2, x1:x2]
                    if recorte.size == 0: continue
                    
                    if id_p % 2 == 0:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        nome_img = f"real_id_{id_p}_{int(time.time())}.jpg"
                        cv2.imwrite(os.path.join(pasta_cortes, nome_img), recorte)
                        
                        lacre = hashlib.sha256(recorte.tobytes()).hexdigest()
                        caminho_rel = f"evidencias_recortes/{nome_img}"
                        
                        cursor.execute("""
                            INSERT INTO log_infracoes (timestamp, analise_origem, detalhes_inconformidade, hash_lacre_sha256, caminho_corte)
                            VALUES (?, ?, ?, ?, ?)
                        """, (timestamp, nome_canal, f"Registro de Pessoa Rastreada ID #{id_p}", lacre, caminho_rel))
                        conn.commit()
                        print(f"⚖️ [PRODUÇÃO] Quadro arquivado para a Pessoa ID #{id_p}")

            cv2.imshow("Monitor de Hardware Real (Producao)", cv2.resize(frame_bruto, (480, 360)))
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            conn.close()
    finally:
        for ev in stop_events.values(): ev.set()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    rodar_engine_real()
