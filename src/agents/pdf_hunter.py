import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import create_react_agent

ROOT_DIR = Path(__file__).parent.parent.parent
PASTA_BASE = ROOT_DIR / "data" / "raw_pdfs"
load_dotenv(ROOT_DIR / '.env')

ferramenta_busca = DuckDuckGoSearchResults()

@tool
def baixar_e_organizar_pdf(url: str, tema: str, nome_arquivo: str) -> str:
    """
    Usa esta ferramenta para baixar um PDF e guardá-lo na pasta correta.
    - url: O link direto do .pdf
    - tema: O nome da doença (ex: 'dengue', 'covid'). Isso criará uma pasta.
    - nome_arquivo: Um nome curto para o arquivo (ex: 'protocolo_2024').
    """
    try:
        pasta_do_tema = PASTA_BASE / tema.lower().replace(" ", "_")
        pasta_do_tema.mkdir(parents=True, exist_ok=True)
        caminho_final = pasta_do_tema / f"{nome_arquivo}.pdf"

        if caminho_final.exists():
            return f"Pulei! O arquivo {nome_arquivo} já existe na pasta {tema}."

        resposta = requests.get(url, stream=True, timeout=15)
        resposta.raise_for_status()

        with open(caminho_final, 'wb') as arquivo:
            for pedaco in resposta.iter_content(chunk_size=8192):
                arquivo.write(pedaco)

        return f"Sucesso! Arquivo salvo em {caminho_final}"
    except Exception as e:
        return f"Erro ao baixar: {str(e)}"

ferramentas = [ferramenta_busca, baixar_e_organizar_pdf]

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)

SYSTEM_PROMPT = """Você é um assistente focado em encontrar PDFs do Ministério da Saúde.
1. Para cada tema, busque no DuckDuckGo usando termos como: 'site:gov.br filetype:pdf [TEMA]'.
2. Encontre 1 link válido que termine em .pdf.
3. Use a ferramenta 'baixar_e_organizar_pdf' para salvar o arquivo."""

# ✅ Substituição do AgentExecutor + create_tool_calling_agent
agente_executor = create_react_agent(
    model=llm,
    tools=ferramentas,
    prompt=SYSTEM_PROMPT
)

if __name__ == "__main__":
    doencas_para_pesquisar = ["dengue", "diabetes", "obesidade"]

    for doenca in doencas_para_pesquisar:
        print(f"\nIniciando caçada para: {doenca.upper()}")
        missao = f"Encontre e baixe 1 protocolo oficial do Ministério da Saúde sobre {doenca}."
        try:
            # ✅ LangGraph usa "messages" no lugar de "input"
            resultado = agente_executor.invoke({
                "messages": [("human", missao)]
            })
            # Pega a última mensagem da resposta
            print(resultado["messages"][-1].content)

            print("Pausando por 5 segundos para esfriar as APIs...")
            time.sleep(5)
        except Exception as e:
            print(f"Erro crítico ao processar {doenca}: {e}")
            continue

    print("\nTodas as missões foram concluídas!")