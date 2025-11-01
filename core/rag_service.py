# core/rag_service.py
from langchain_ollama.llms import OllamaLLM
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from data_access.vector_store import VectorStore
from core.config import config

class RAGService:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self._llm = OllamaLLM(
            model=config.generation_llm.model,
            temperature=config.generation_llm.temperature,
            num_predict=config.generation_llm.max_tokens,
        )
        
        prompt_template = """
        You are a precise and knowledgeable assistant.
        Use ONLY the provided context to answer, and if you don't know, say "I don’t know."
        Keep answers concise and factual.

        Context:
        {context}

        Question:
        {question}

        Answer:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self._llm,
            retriever=self._vector_store.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def answer_query(self, query: str) -> dict:
        response = self.rag_chain.invoke(query)

        sources = []
        for doc in response.get("source_documents", []):
            source_data = doc.metadata.copy() # Get metadata
            source_data["content"] = doc.page_content # Add the actual text
            sources.append(source_data)

        return {
            "answer": response.get("result", "No answer found."),
            "sources": sources
        }
        # response = self.rag_chain.run(query)
        # return response