# api/main.py
from fastapi import FastAPI
from api.endpoints import ingest, query

app = FastAPI(
    title="RAG Q&A System",
    description="An API for document ingestion and retrieval-augmented generation.",
    version="1.0.0"
)

# Include the routers from the endpoints
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(query.router, tags=["Query"])

@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok"}