import os
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

os.environ["ANONYMIZED_TELEMETRY"] = "False"

ROOT_DIR = Path(__file__).parent.parent.parent
PDF_PATH = ROOT_DIR/ "data"/ "raw_pdfs"/ "dengue.pdf"
CHROMA_DIR = ROOT_DIR/  "data"/ "chroma_db"

print("iniciando pipeline de ingestão...")

print(f"Lendo o documento: {PDF_PATH.name}")

try:
    loader = PyMuPDFLoader(str(PDF_PATH))
    documentos = loader.load()
    print(f"documento carregado com sucesso.\ntamanho total: {len(documentos)}")
except Exception as e:
    print(f" Erro ao ler o PDF: {e}")
    exit(1)


#iniciando o processo de Chunking do PDF

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size = 800,
    chunk_overlap = 100,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = text_spliter.split_documents(documentos)
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