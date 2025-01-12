from typing import List
import openai
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from document_processor import DocumentProcessor
from config import OPENAI_MODEL

class RAGSystem:
    def __init__(self, api_key: str):
        self.document_processor = DocumentProcessor()
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.vector_store = None
        openai.api_key = api_key

    def ingest_documents(self, file_paths: List[str]):
        all_chunks = []
        for file_path in file_paths:
            chunks = self.document_processor.process_document(file_path)
            all_chunks.extend(chunks)

        self.vector_store = FAISS.from_texts(
            all_chunks,
            self.embeddings
        )

    def generate_response(self, query: str, k: int = 3) -> str:
        if not self.vector_store:
            raise ValueError("No documents have been ingested yet.")

        # Retrieve relevant chunks
        relevant_chunks = self.vector_store.similarity_search(query, k=k)
        context = "\n".join([doc.page_content for doc in relevant_chunks])

        # Generate response using OpenAI
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes documents and helps fill out forms based on the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
            ]
        )

        return response.choices[0].message.content 

    def validate_file(self, file_path: str) -> bool:
        ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx'}
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

        try:
            # Check file extension
            if not any(file_path.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                raise ValueError(f"Unsupported file type. Allowed types: {ALLOWED_EXTENSIONS}")

            # Check file size
            import os
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB")

            return True
        except Exception as e:
            raise ValueError(f"File validation failed: {str(e)}") 