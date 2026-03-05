"""
SmartLead API - Main Application
================================
FastAPI application for AI-Powered Lead Scoring System

Endpoints:
- /score-lead: Single lead scoring
- /batch-score: Batch lead scoring
- /health: Health check
- /metrics: Prometheus metrics

Spec-Driven Development: Generated from SmartLead/context-spec.json
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, generate_latest

from src.api.config import Settings
from src.api.models import LeadData, LeadScoreResponse, BatchScoreRequest, BatchScoreResponse
from src.ml.predictor import LeadPredictor
from src.ml.features import FeatureExtractor
from src.utils.resilience import circuit_breaker, retry_with_backoff
from src.utils.observability import setup_logging, setup_metrics

# Initialize settings
settings = Settings()

# Configure logging
logger = setup_logging(settings)

# Setup metrics
REQUEST_COUNT = Counter(
    'smartlead_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)
REQUEST_LATENCY = Histogram(
    'smartlead_api_request_latency_seconds',
    'API request latency',
    ['endpoint']
)
PREDICTION_COUNT = Counter(
    'lead_score_predictions_total',
    'Total lead score predictions',
    ['model_version']
)

# Initialize ML components
predictor = LeadPredictor(settings)
feature_extractor = FeatureExtractor(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting SmartLead API...")
    
    # Initialize ML model
    await predictor.load_model()
    
    # Initialize feature store
    await feature_extractor.initialize()
    
    logger.info("SmartLead API started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down SmartLead API...")
    await predictor.cleanup()


# Create FastAPI application
app = FastAPI(
    title="SmartLead - AI-Powered Lead Scoring",
    description="Machine learning system for lead conversion prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for metrics and logging
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware for collecting metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
    
    return response


# ================== API Endpoints ==================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status of the API and its dependencies
    """
    health_status = {
        "status": "healthy",
        "service": "smartlead-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }
    
    # Check dependencies
    try:
        # Check model loaded
        if predictor.is_ready():
            health_status["model"] = "ready"
        else:
            health_status["model"] = "not_ready"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["model"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint
    
    Returns:
        Readiness status for Kubernetes probes
    """
    ready = predictor.is_ready() and feature_extractor.is_ready()
    
    if not ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    
    return {"status": "ready"}


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint
    
    Returns:
        Prometheus metrics in text format
    """
    return JSONResponse(
        content=generate_latest(),
        media_type="text/plain"
    )


@app.post("/score-lead", response_model=LeadScoreResponse, tags=["Predictions"])
@retry_with_backoff(max_attempts=3)
@circuit_breaker(failure_threshold=5, timeout=30)
async def score_lead(lead_data: LeadData, request: Request) -> LeadScoreResponse:
    """
    Score a single lead for conversion probability
    
    Args:
        lead_data: Lead information including email, company details, etc.
    
    Returns:
        Lead score with probability and grade
    """
    start_time = time.time()
    
    try:
        # Extract features
        features = await feature_extractor.extract_features(lead_data)
        
        # Get prediction
        prediction = await predictor.predict(features)
        
        # Record prediction count
        PREDICTION_COUNT.labels(
            model_version=predictor.model_version
        ).inc()
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return LeadScoreResponse(
            lead_id=lead_data.lead_id,
            conversion_probability=prediction["probability"],
            lead_grade=prediction["grade"],
            confidence_score=prediction["confidence"],
            model_version=predictor.model_version,
            shap_explanation=prediction.get("shap_values", {}),
            processing_time_ms=processing_time * 1000
        )
        
    except Exception as e:
        logger.error(f"Error scoring lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring lead: {str(e)}"
        )


@app.post("/batch-score", response_model=BatchScoreResponse, tags=["Predictions"])
@retry_with_backoff(max_attempts=3)
@circuit_breaker(failure_threshold=5, timeout=60)
async def batch_score_leads(batch_request: BatchScoreRequest, request: Request) -> BatchScoreResponse:
    """
    Score multiple leads in batch
    
    Args:
        batch_request: List of leads to score
    
    Returns:
        Batch prediction results
    """
    start_time = time.time()
    
    try:
        results = []
        
        for lead_data in batch_request.leads:
            # Extract features
            features = await feature_extractor.extract_features(lead_data)
            
            # Get prediction
            prediction = await predictor.predict(features)
            
            results.append({
                "lead_id": lead_data.lead_id,
                "conversion_probability": prediction["probability"],
                "lead_grade": prediction["grade"],
                "confidence_score": prediction["confidence"],
                "model_version": predictor.model_version
            })
        
        # Record batch prediction count
        PREDICTION_COUNT.labels(
            model_version=predictor.model_version
        ).inc(len(batch_request.leads))
        
        processing_time = time.time() - start_time
        
        return BatchScoreResponse(
            total_leads=len(batch_request.leads),
            scored_leads=len(results),
            results=results,
            processing_time_ms=processing_time * 1000
        )
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch scoring: {str(e)}"
        )


# ================== Error Handlers ==================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP error handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
