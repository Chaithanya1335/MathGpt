from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams
from langchain_experimental.text_splitter import SemanticChunker
from src.utils import get_embedding_model, get_qdrant_client
from src.data_loader.data_loader import DataLoader
from uuid import uuid4

class VectorDB:
    def __init__(self, initialize=False):
        self.embedding_model = get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.qclient = get_qdrant_client()
        self.collection_name = "Maths Data"
        self.vector_store = None

        if initialize:
            self._create_vector_store()
        else:
            # Just connect to existing collection
            self.vector_store = QdrantVectorStore(
                client=self.qclient,
                collection_name=self.collection_name,
                embedding=self.embedding_model
            )

    def _create_vector_store(self):
        print("Checking for existing collections...")
        existing_collections = [c.name for c in self.qclient.get_collections().collections]

        if self.collection_name not in existing_collections:
            print("No existing collection found — creating new one...")
            self.qclient.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

        # Only proceed if the collection is empty
        count_info = self.qclient.count(collection_name=self.collection_name)
        if count_info.count > 0:
            print("Collection already populated. Skipping ingestion.")
            return

        print("Loading and chunking documents...")
        docs = DataLoader(directory_path="Data").get_documents()
        text_splitter = SemanticChunker(
            embeddings=self.embedding_model,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=80
        )
        chunks = text_splitter.split_documents(docs)

        self.vector_store = QdrantVectorStore(
            client=self.qclient,
            collection_name=self.collection_name,
            embedding=self.embedding_model
        )

        ids = [str(uuid4()) for _ in range(len(chunks))]
        BATCH_SIZE = 100
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_docs = chunks[i:i+BATCH_SIZE]
            batch_ids = ids[i:i+BATCH_SIZE]
            print(f"Upserting batch {i//BATCH_SIZE + 1}")
            self.vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        print("Documents successfully added to the vector store.")

    def get_retriever(self, search_type="mmr", k=5):
        print(f"Creating retriever (type={search_type}, k={k})...")
        if not self.vector_store:
            self.vector_store = QdrantVectorStore(
                client=self.qclient,
                collection_name=self.collection_name,
                embedding=self.embedding_model
            )
        return self.vector_store.as_retriever(search_type=search_type, search_kwargs={"k": k})




if __name__ == "__main__":
    retriever = VectorDB(initialize=True).get_retriever()
    results = retriever.get_relevant_documents("Why is the Pythagorean theorem true?")
    print("\nFetched Results:\n" + "="*60)
    for i, doc in enumerate(results):
        print(f"\n--- Document {i+1} ---")
        print(doc.page_content[:500])
