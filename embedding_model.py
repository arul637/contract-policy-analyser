from typing import List
from langchain_ollama.embeddings import OllamaEmbeddings
import chromadb


class EmbeddingModel:
    def __init__(self, embedding_model: str = 'qwen3-embedding:8b', vector_database_path: str = 'chroma-db'):
        self.client = chromadb.PersistentClient(path=vector_database_path)
        self.collection_name = 'business-policy-aggregator'

        try:
            self.database_collection = self.client.get_collection(self.collection_name)
        except:
            self.database_collection = self.client.create_collection(self.collection_name)

        self.model = OllamaEmbeddings(
            model=embedding_model,
            temperature=0.5
        )
    
    def embed(self, text: str) -> List:
        return self.model.embed_query(text)

    def vector_store(self, structured_policy):
        for clause in structured_policy:
            vector = self.embed(text=clause['content'])

            self.database_collection.add(
                ids=[clause['clause_id']],
                embeddings=[vector],
                documents=[clause['content']],
                metadatas=[{
                    'category': clause['category'],
                    'severity': clause['severity']
                }]
            )


obj = EmbeddingModel()
structured_policy = [{'clause_id': 'clause-BP22', 'content': 'This policy serves as a guiding framework for contract-based employment and may be updated at the discretion of the company with prior notice.', 'category': 'optional', 'severity': 'low'}]

obj.vector_store(structured_policy)
