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
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004451.png", width=100) 
    st.title("🩺 Assistente RAG")
    
    st.warning("⚠️ **Aviso Legal:** Este é um assistente de IA baseado em protocolos do Ministério da Saúde. O conteúdo gerado tem caráter puramente informativo e acadêmico. Nunca substitua uma consulta médica profissional.")
    
    st.markdown("---")
    st.markdown("### 📚 Protocolos Disponíveis")
    
    # Mostra os mais buscados ou populares abertos
    st.markdown("- Dengue\n- Obesidade\n- TDAH\n- HPV\n- COVID-19")
    
    # O Expander mágico que vai abrir o resto da lista!
    with st.expander("Ver todas as condições cadastradas"):
        st.markdown("""
        - Alzheimer
        - Artrite Reumatoide
        - Blinatumomabe
        - Câncer de Mama
        - Depressão
        - Diabetes (e Gestacional)
        - Dislipidemia
        - Doença Celíaca
        - Doença de Chagas
        - Doença de Crohn
        - Dor Crônica
        - Epilepsia
        - Esquizofrenia
        - Hanseníase
        - Infarto
        - Influenza
        - Lúpus Eritematoso Sistêmico
        - Osteoporose
        - Parkinson
        - Raquitismo
        - Tabagismo
        """)
    
    st.markdown("---")
    # Botão para limpar a memória do bot
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.rerun()

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