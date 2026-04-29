import os
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

os.environ["ANONYMIZED_TELEMETRY"] = "False"

ROOT_DIR = Path(__file__).parent.parent.parent
PASTA_BASE = ROOT_DIR / "data" / "raw_pdfs"
CHROMA_DIR = ROOT_DIR / "data" / "chroma_db"

print("🚀 Iniciando pipeline de ingestão em lote...")

todos_documentos = []
print("iniciando pipeline de ingestão...")

for arquivo_pdf in PASTA_BASE.rglob("*.pdf"):
    nome_doenca = arquivo_pdf.parent.name 
    
    print(f"Lendo o documento: {nome_doenca.upper()} -> {arquivo_pdf.name}")
    
    try:
        loader = PyMuPDFLoader(str(arquivo_pdf))
        documentos_extraidos = loader.load()
        
        for doc in documentos_extraidos:
            doc.metadata["doenca"] = nome_doenca
            
        todos_documentos.extend(documentos_extraidos)
        
    except Exception as e:
        print(f"❌ Erro ao ler o PDF {arquivo_pdf.name}: {e}")
        continue

print(f"\n✅ Leitura concluída! Total de páginas carregadas no sistema: {len(todos_documentos)}")
text_spliter = RecursiveCharacterTextSplitter(
    chunk_size = 800,
    chunk_overlap = 100,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = text_spliter.split_documents(todos_documentos)
print(f"✅ Texto dividido em {len(chunks)} chunks.")

# 4. Gerar Embeddings e Salvar no ChromaDB
print("preparando modelo de IA para gerar embeddings...")
embed_model = HuggingFaceEmbeddings(model_name="neuralmind/bert-base-portuguese-cased")

print("💾 Calculando vetores e salvando no ChromaDB (disco local)...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embed_model,
    persist_directory=str(CHROMA_DIR),
    collection_name="documentos_medicos"
)

print("\nIngestão concluída com sucesso! Os dados estão salvos no seu banco vetorial.")