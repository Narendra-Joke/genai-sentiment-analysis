from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.ingestion import router as ingestion_router
from app.api.sentiment import router as sentiment_router
from app.api.component import router as component_router

from app.core.logging_config import setup_logging
from app.core.exception import GenAIException

from uvicorn import run as app_run 

logger = logging.getLogger(__name__)

# Lifespan (startup + shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Application starting...")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title="GenAI Insights",
    lifespan=lifespan
)

# CORS Middleware
origins = ["*"]  # change this in production

# app = FastAPI(title="GenAI Insights")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(sentiment_router)
app.include_router(component_router)

# Global Exception Handler
@app.exception_handler(GenAIException)
async def genai_exception_handler(request: Request, exc: GenAIException):
    logger.error(f"Handled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "ERROR",
            "message": str(exc),
            "path": request.url.path
        }
    )

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response

# Health Check
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

if __name__=="__main__":
    app_run(app,host="127.0.0.1",port=8000)