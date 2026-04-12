import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embed_model = HuggingFaceEmbeddings(model_name="neuralmind/bert-base-portuguese-cased")
db = Chroma(persist_directory="data/chroma_db",
            embedding_function=embed_model,
            collection_name="documentos_medicos")

# Teste de busca
resultado = db.similarity_search("quais são os sintomas da dengue?", k=3)
for i, doc in enumerate(resultado):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content[:300])
    print(f"Fonte: {doc.metadata}")