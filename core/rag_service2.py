# core/rag_service2.py
from langchain_ollama.llms import OllamaLLM
from langchain_classic.prompts import PromptTemplate
from data_access.vector_store import VectorStore
from core.config import Settings
from langchain.chains.llm import LLMChain
import torch
from sentence_transformers import CrossEncoder # <-- Import the reranker

class RAGService:
    def __init__(self, vector_store: VectorStore, settings: Settings):
        self._vector_store = vector_store
        self._settings = settings
        self._llm = OllamaLLM(
            model=self._settings.generation_llm.model,
            temperature=self._settings.generation_llm.temperature,
            num_predict=self._settings.generation_llm.max_tokens,
        )
        
        # Check for M1 Mac GPU (MPS) and set device
        # This is crucial for running the model efficiently on your hardware
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        print(f"Loading reranker model '{settings.reranker_model}' on device: {device}")
        
        # Load the reranker model
        self._reranker = CrossEncoder(
            self._settings.reranker_model, 
            max_length=512, 
            device=device
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

        # Store the prompt template for use in the query method
        self._prompt_template = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

    def query(self, query_text: str) -> dict:
        """
        Performs a RAG query:
        1. Retrieves documents with vector search (fast retrieval).
        2. Reranks the results with a CrossEncoder (smart reranking).
        3. Formats the prompt and calls the LLM.
        """
        
        # 1. Retrieve documents with scores (initial fast retrieval)
        # We fetch *more* documents than we need (top_k_retrieval, e.g., 10)
        retrieved_docs_with_scores = self._vector_store.similarity_search_with_score(
            query_text, 
            k=self._settings.top_k_retrieval 
        )
        
        if not retrieved_docs_with_scores:
            print("No documents found by vector store.")
            return {"answer": "I don't know.", "sources": []}

        # 2. Rerank the results
        # Create pairs of [query, passage] for the reranker
        pairs = [(query_text, doc.page_content) for doc, score in retrieved_docs_with_scores]
        
        # Run the reranker model. This is computationally more expensive but more accurate.
        print(f"Reranking {len(pairs)} documents...")
        rerank_scores = self._reranker.predict(pairs, show_progress_bar=False)
        
        # Combine new scores with original documents
        # (rerank_score, (original_doc, original_vector_score))
        reranked_docs = list(zip(rerank_scores, retrieved_docs_with_scores))
        
        # Sort by the new reranker score (highest first)
        reranked_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Filter down to the final top_k_ranking (e.g., top 5)
        final_docs_with_scores = reranked_docs[:self._settings.top_k_ranking]
        
        # 3. Format the context for the LLM
        # We now use the *best* 5 documents as context
        context = "\n\n".join([doc.page_content for rerank_score, (doc, vector_score) in final_docs_with_scores])
        
        # 4. Create the LLM chain and run it
        llm_chain = LLMChain(prompt=self._prompt_template, llm=self._llm)
        answer = llm_chain.invoke({"context": context, "question": query_text})

        # 5. Format the output sources, including both scores
        sources = []
        for rerank_score, (doc, vector_score) in final_docs_with_scores:
            source_data = doc.metadata.copy() # Get metadata
            source_data["chunk_text"] = doc.page_content # Add the actual text
            source_data["vector_similarity_score"] = vector_score # The original score
            # .item() converts numpy/torch number to a plain python float for JSON
            source_data["relevance_score"] = rerank_score.item() 
            sources.append(source_data)
            
        return {
            "answer": answer.get("text", "No answer found.").strip(),
            "sources": sources
        }

