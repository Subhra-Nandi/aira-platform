

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class VectorStore:

    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.db = Chroma(
            collection_name="aira_memory",
            embedding_function=self.embedding,
            persist_directory="./vector_db"
        )

    def add_document(self, text: str):

        self.db.add_texts([text])
        self.db.persist()

        return {"status": "stored"}

    def search(self, query: str):

        results = self.db.similarity_search(query, k=3)

        return [doc.page_content for doc in results]