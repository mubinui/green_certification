from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ..config import settings
from ..database.session import get_db
from .routes import upload_router, analysis_router, certification_router

app = FastAPI(
    title="Green Certification API",
    description="API for tree analysis and certification system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Include routers
app.include_router(upload_router, prefix="/api/v1", tags=["Uploads"])
app.include_router(analysis_router, prefix="/api/v1", tags=["Analysis"])
app.include_router(certification_router, prefix="/api/v1", tags=["Certification"])