import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_cohere import CohereRerank
from langchain_classic.retrievers import ContextualCompressionRetriever

ROOT_DIR = Path(__file__).parent.parent.parent
CHROMA_DIR = ROOT_DIR/ "data"/ "chroma_db"

load_dotenv(ROOT_DIR/'.env')
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Erro ao localizar a chave API GROQ, verifique o arquivo .env")
    sys.exit(1)

cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    print("Erro ao localizar a chave da Cohere no .env")
    sys.exit(1)



model = HuggingFaceEmbeddings(model_name="neuralmind/bert-base-portuguese-cased")
chroma_db = Chroma(
    persist_directory= str(CHROMA_DIR),
    embedding_function= model,
    collection_name= "documentos_medicos"
)



#configurando o banco local para buscar 10 textos 
# Pescamos 50 chunks, filtramos os 30 mais diversos, e mandamos para a Cohere
buscador_base = chroma_db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 30, "fetch_k": 50}
)
#instanciando o Cohere Rerank usando um modelo multiidiomas
#vai ler os 10 textos e retornas os 3 mais relevantes
compressor = CohereRerank(
    model= "rerank-multilingual-v3.0",
    top_n= 3,
    cohere_api_key= cohere_api_key
)

#criando o pipeline que une o buscador local com a IA da Cohere

buscador_inteligente = ContextualCompressionRetriever(
    base_compressor = compressor,
    base_retriever = buscador_base
)
llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature= 0.1,
)

def buscar_resposta_medica(pergunta_usuario, historico_mensagens):
    try:
        historico_texto = ""

        for msg in historico_mensagens[-4:]:
            quem = "Usuário" if msg['role'] == "user" else "IA"
            historico_texto += f"{quem}: {msg['content']}\n"

        prompt_memoria = f"""
        Você é um especialista em analisar conversas. 
        Leia o histórico do chat abaixo e a nova pergunta do usuário.
        
        Histórico:
        {historico_texto}
        
        Nova Pergunta: "{pergunta_usuario}"
        
        Sua tarefa: Reescreva a Nova Pergunta para que ela faça sentido sozinha, sem precisar do histórico. 
        Se a palavra "isso", "ele" ou "ela" estiver na pergunta, troque pelo assunto real da conversa.
        Se a Nova Pergunta já for clara sozinha, apenas repita ela.
        NÃO RESPONDA a pergunta. APENAS escreva a pergunta reescrita.
        """

        pergunta_reescrita = llm.invoke(prompt_memoria).content.strip()
        print(f"\n🧠 Pergunta Original: {pergunta_usuario}")
        print(f"🎯 Pergunta Reescrita: {pergunta_reescrita}\n")

    


        resultados = buscador_inteligente.invoke(pergunta_reescrita)

        textos_extraidos = []

        for doc in resultados:
            fonte = Path(doc.metadata["source"]).name
            pagina = doc.metadata["page"]
            textos_extraidos.append(f"[Fonte: {fonte} | Página: {pagina}]\n{doc.page_content}")
        
        contexto_final = "\n\n".join(textos_extraidos)

        prompt_sistema = f'''Você é um assistente médico especialista. 
        Responda à pergunta do usuário usando APENAS o contexto abaixo.
        Se não souber, diga que não há informações suficientes. Seja educado e cordial.

        REGRA OBRIGATÓRIA: 
        Ao final da sua resposta, você DEVE citar a fonte e a página exata de onde tirou a informação, usando os dados [Fonte: ... | Página: ...] fornecidos no contexto.

        CONTEXTO:
        {contexto_final}
        '''
        
        mensagens = [
            SystemMessage(content=prompt_sistema),
            HumanMessage(content=pergunta_reescrita)
        ]
        
        resposta = llm.invoke(mensagens)
        return resposta.content
    except Exception as e:
        return f"ocorreu um erro ao consultar os protocolos: {e}"