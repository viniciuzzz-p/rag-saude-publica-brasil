import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR/ '.env')

print("Iniciando Teste de Conexão com a Groq...\n")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Erro ao localizar a chave API, verifique o arquivo .env")
    sys.exit(1)


try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1, 
    )
    pergunta = "Qual é o protocolo básico de hidratação para suspeita de dengue em adultos? Responda em apenas um parágrafo."
    print(f"Pergunta: {pergunta}")
    print("Aguardando resposta do Llama 3.3 (via Groq)...")

    mensagem = [HumanMessage(content= pergunta)]
    resposta = llm.invoke(mensagem)
    print("\n✅ Resposta recebida com sucesso:\n")
    print("-" * 60)
    print(resposta.content)
    print("-" * 60)

except  Exception as e:
    print(f"\n Falha ao conectar com o Groq: {e}")
