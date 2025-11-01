# api/endpoints/query.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import QueryRequest, QueryResponse
from core.rag_service import RAGService
from api.dependencies import get_rag_service

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Answers a query based on the ingested documents.
    """
    try:
        response = rag_service.answer_query(request.query)
        print(response)
        return QueryResponse(answer=response["answer"], sources=response["sources"])
    except Exception as e:
        # Graceful error handling for the API user [cite: 33]
        raise HTTPException(status_code=500, detail=f"Failed to process query: {e}")