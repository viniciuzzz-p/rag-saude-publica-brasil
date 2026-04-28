import streamlit as st
import sys
from pathlib import Path

# Isso ensina o Streamlit a achar a pasta 'src' no seu computador
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

# IMPORTANDO O SEU CÉREBRO RAG!
from src.query.retriever import buscar_resposta_medica

st.set_page_config(page_title="Assistente Médico RAG", page_icon="🩺", layout="centered")

st.title("🩺 Assistente Médico IA")
st.markdown("Faça perguntas sobre protocolos médicos e tratamentos baseados no Ministério da Saúde.")
st.divider()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "assistant", "content": "Olá! Sou o seu assistente médico virtual. Como posso ajudar hoje?"}
    ]

# ... (seus imports e st.title)

# Defina o caminho da imagem logo no início
CAMINHO_DESENHO = Path(__file__).parent / "assets" / "medico.png"

# ... (inicialização do session_state.mensagens continua igual)

# 1. ATUALIZANDO O HISTÓRICO DE MENSAGENS:
for msg in st.session_state.mensagens:
    # Lógica: Se for a IA, usa o seu desenho. Se for o usuário, usa um emoji ou deixa vazio.
    icone = CAMINHO_DESENHO if msg["role"] == "assistant" else "👤"
    
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])

# --- O CHAT ---
if pergunta_usuario := st.chat_input("Digite sua dúvida médica aqui..."):
    
    # 2. ATUALIZANDO A MENSAGEM NOVA DO USUÁRIO
    with st.chat_message("user", avatar="👤"):
        st.markdown(pergunta_usuario)
    st.session_state.mensagens.append({"role": "user", "content": pergunta_usuario})
    
    # 3. A MÁGICA: A MENSAGEM NOVA DA IA COM O SEU DESENHO
    with st.chat_message("assistant", avatar=CAMINHO_DESENHO):
        with st.spinner("Consultando protocolos e diretrizes médicas... ⏳"):
            resposta_ia = buscar_resposta_medica(pergunta_usuario, st.session_state.mensagens[:-1])
            
        st.markdown(resposta_ia)
        
    st.session_state.mensagens.append({"role": "assistant", "content": resposta_ia})