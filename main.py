import uvicorn
import logging
from src.api.app import app
from src.config import settings

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("green_certification")

if __name__ == "__main__":
    logger.info(f"Starting Green Certification API on port {settings.API_PORT}")
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.UVICORN_LOG_LEVEL.lower(),
    )