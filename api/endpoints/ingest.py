# api/endpoints/ingest.py
from fastapi import APIRouter, Depends, BackgroundTasks
from api.schemas import IngestResponse
from core.ingestion_service import IngestionService
from api.dependencies import get_ingestion_service
from core.config import config

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Triggers the ingestion of documents from the configured directory.
    Runs as a background task.
    """
    background_tasks.add_task(ingestion_service.ingest_directory, config.persist_files_directory)
    
    return IngestResponse(
        status="success",
        message=f"Ingestion started in the background from '{config.persist_files_directory}'."
    )