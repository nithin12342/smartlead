"""
SmartLead Observability Utilities
=================================
Logging, metrics, and tracing setup

Spec-Driven: Generated from SmartLead/harness.json monitoring_harness
"""

import logging
import sys
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest


def setup_logging(settings) -> logging.Logger:
    """
    Configure structured logging for the application
    
    Args:
        settings: Application settings
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("smartlead")
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    return logger


def setup_metrics(settings) -> Optional[object]:
    """
    Setup Prometheus metrics
    
    Args:
        settings: Application settings
    
    Returns:
        Prometheus registry or None
    """
    # Create registry
    registry = CollectorRegistry()
    
    # Define custom metrics
    # These will be used throughout the application
    metrics = {
        # Request metrics
        "requests_total": Counter(
            "smartlead_api_requests_total",
            "Total API requests",
            ["endpoint", "method", "status"],
            registry=registry
        ),
        "request_duration": Histogram(
            "smartlead_api_request_duration_seconds",
            "API request duration",
            ["endpoint"],
            registry=registry
        ),
        
        # ML metrics
        "predictions_total": Counter(
            "smartlead_lead_score_predictions_total",
            "Total lead score predictions",
            ["model_version", "lead_grade"],
            registry=registry
        ),
        "model_inference_duration": Histogram(
            "smartlead_model_inference_duration_seconds",
            "Model inference duration",
            ["model_version"],
            registry=registry
        ),
        
        # Feature store metrics
        "feature_store_fetch_duration": Histogram(
            "smartlead_feature_store_fetch_duration_seconds",
            "Feature store fetch duration",
            registry=registry
        ),
        "feature_store_cache_hits": Counter(
            "smartlead_feature_store_cache_hits_total",
            "Feature store cache hits",
            registry=registry
        ),
        "feature_store_cache_misses": Counter(
            "smartlead_feature_store_cache_misses_total",
            "Feature store cache misses",
            registry=registry
        ),
        
        # Resilience metrics
        "circuit_breaker_state": Gauge(
            "smartlead_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["service"],
            registry=registry
        ),
        "retry_attempts_total": Counter(
            "smartlead_retry_attempts_total",
            "Total retry attempts",
            ["service", "attempt_number"],
            registry=registry
        ),
        
        # Business metrics
        "lead_scores_by_grade": Counter(
            "smartlead_lead_scores_by_grade_total",
            "Lead scores by grade",
            ["grade"],
            registry=registry
        ),
    }
    
    return registry


def setup_tracing(service_name: str, tracing_endpoint: Optional[str] = None):
    """
    Setup OpenTelemetry tracing
    
    Args:
        service_name: Name of the service
        tracing_endpoint: OTLP endpoint for exporting traces
    
    Returns:
        Configured tracer or None
    """
    try:
        # Create resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0"
        })
        
        # Create tracer provider
        provider = TracerProvider(resource=resource)
        
        # Add console exporter for development
        provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
        
        # Set provider
        trace.set_tracer_provider(provider)
        
        # Get tracer
        tracer = trace.get_tracer(__name__)
        
        return tracer
    except Exception as e:
        logging.warning(f"Failed to setup tracing: {e}")
        return None


def get_prometheus_metrics() -> bytes:
    """
    Get Prometheus metrics in text format
    
    Returns:
        Prometheus metrics
    """
    return generate_latest()


class StructuredLogger:
    """
    Structured logger for JSON logging
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        extra = {
            "structured": True,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            message,
            extra=extra
        )
    
    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log("debug", message, **kwargs)
