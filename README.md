# 🛡️ Plataforma de Visão Computacional Multi-Sensor e No-Code

Sistema modular de monitoramento e auditoria com IA generativa de visão, arquitetado com suporte a múltiplos hardwares de entrada (Wi-Fi ao vivo, barramento USB e decodificação local).

## 🚀 Como Executar o Ecossistema

### 🧪 1. Executando o Ambiente de Teste Isolado (Simulador)
```bash
cd 2_AMBIENTE_DE_TESTE_ISOLADO
python -m pip install -r requirements-test.txt
python engine_simulada/criar_infraestrutura_teste.py
python engine_simulada/mock_engine_teste.py
# Em outro terminal:
python -m streamlit run interface_usuario_teste/dashboard_teste.py
```

### ⚙️ 2. Executando o Sistema Integral (Produção Real)
```bash
cd 1_SISTEMA_INTEGRAL_PRODUCAO
python -m pip install -r requirements.txt
python engine_core/criar_infraestrutura.py
python engine_core/app_engine.py
# Em outro terminal:
python -m streamlit run interface_usuario/dashboard.py
```
