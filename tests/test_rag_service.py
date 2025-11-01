# tests/test_rag_service.py
import unittest
from unittest.mock import MagicMock, patch
from core.rag_service import RAGService

class TestRAGService(unittest.TestCase):

    @patch('core.rag_service.OllamaLLM') # Mock the LLM
    def test_answer_query_uses_retriever(self, mock_ollama):
        # Arrange
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        # The mock retriever will return a predictable result
        mock_retriever.get_relevant_documents.return_value = ["fake context"]
        mock_vector_store.as_retriever.return_value = mock_retriever

        # Mock the entire RetrievalQA chain
        mock_rag_chain = MagicMock()
        mock_rag_chain.run.return_value = "This is the mocked LLM answer."

        # Act
        # We need to patch the chain creation within the RAGService's scope
        with patch('core.rag_service.RetrievalQA.from_chain_type', return_value=mock_rag_chain):
            rag_service = RAGService(vector_store=mock_vector_store)
            result = rag_service.answer_query("test query")

        # Assert
        # Was the chain executed with our query?
        mock_rag_chain.run.assert_called_once_with("test query")
        # Did we get the expected response?
        self.assertEqual(result, "This is the mocked LLM answer.")
        # Was the retriever created from our vector store?
        mock_vector_store.as_retriever.assert_called_once()