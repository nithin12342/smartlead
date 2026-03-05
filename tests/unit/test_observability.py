"""
SmartLead Unit Tests - Observability
====================================
Test logging, metrics, and tracing setup

Spec-Driven: Generated from SmartLead/harness.json testing_harness
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import logging
import sys

from src.utils.observability import (
    setup_logging,
    setup_metrics,
    setup_tracing,
    get_prometheus_metrics,
    StructuredLogger
)


class TestSetupLogging:
    """Tests for setup_logging function"""
    
    def test_logger_creation_with_info_level(self):
        """Test logger created with INFO level"""
        settings = Mock(log_level="INFO")
        logger = setup_logging(settings)
        
        assert logger.name == "smartlead"
        assert logger.level == logging.INFO
    
    def test_logger_creation_with_debug_level(self):
        """Test logger created with DEBUG level"""
        settings = Mock(log_level="DEBUG")
        logger = setup_logging(settings)
        assert logger.level == logging.DEBUG
    
    def test_logger_creation_with_warning_level(self):
        """Test logger created with WARNING level"""
        settings = Mock(log_level="WARNING")
        logger = setup_logging(settings)
        assert logger.level == logging.WARNING
    
    def test_logger_creation_with_error_level(self):
        """Test logger created with ERROR level"""
        settings = Mock(log_level="ERROR")
        logger = setup_logging(settings)
        assert logger.level == logging.ERROR
    
    def test_logger_default_level_on_invalid(self):
        """Test logger defaults to INFO on invalid level"""
        settings = Mock(log_level="INVALID")
        logger = setup_logging(settings)
        assert logger.level == logging.INFO
    
    def test_logger_has_console_handler(self):
        """Test logger has console handler configured"""
        settings = Mock(log_level="INFO")
        logger = setup_logging(settings)
        
        assert len(logger.handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    
    def test_logger_formatter_configured(self):
        """Test logger formatter is properly configured"""
        settings = Mock(log_level="INFO")
        logger = setup_logging(settings)
        
        handler = logger.handlers[0]
        assert handler.formatter is not None
        assert "%(asctime)s" in handler.formatter._fmt
        assert "%(levelname)s" in handler.formatter._fmt
    
    def test_third_party_loggers_set_to_warning(self):
        """Test uvicorn and fastapi loggers set to WARNING"""
        settings = Mock(log_level="DEBUG")
        setup_logging(settings)
        
        assert logging.getLogger("uvicorn").level == logging.WARNING
        assert logging.getLogger("fastapi").level == logging.WARNING
    
    def test_lowercase_log_level(self):
        """Test lowercase log level is converted"""
        settings = Mock(log_level="info")
        logger = setup_logging(settings)
        assert logger.level == logging.INFO


class TestSetupMetrics:
    """Tests for setup_metrics function"""
    
    @patch('src.utils.observability.CollectorRegistry')
    @patch('src.utils.observability.Counter', return_value=Mock())
    @patch('src.utils.observability.Histogram', return_value=Mock())
    @patch('src.utils.observability.Gauge', return_value=Mock())
    def test_metrics_registry_created(self, mock_gauge, mock_histogram, mock_counter, mock_registry):
        """Test metrics registry is created"""
        settings = Mock()
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance
        
        result = setup_metrics(settings)
        
        assert result == mock_registry_instance
        mock_registry.assert_called_once()
    
    @patch('src.utils.observability.CollectorRegistry')
    @patch('src.utils.observability.Counter', return_value=Mock())
    @patch('src.utils.observability.Histogram', return_value=Mock())
    @patch('src.utils.observability.Gauge', return_value=Mock())
    def test_all_metrics_created(self, mock_gauge, mock_histogram, mock_counter, mock_registry):
        """Test all metrics are created"""
        settings = Mock()
        setup_metrics(settings)
        
        assert mock_counter.call_count >= 6
        assert mock_histogram.call_count >= 3
        assert mock_gauge.call_count >= 1


class TestSetupTracing:
    """Tests for setup_tracing function"""
    
    @patch('src.utils.observability.trace')
    @patch('src.utils.observability.Resource')
    @patch('src.utils.observability.TracerProvider')
    @patch('src.utils.observability.BatchSpanProcessor')
    @patch('src.utils.observability.ConsoleSpanExporter')
    def test_tracing_setup_success(self, mock_exporter, mock_processor, mock_provider_class, 
                                   mock_resource, mock_trace):
        """Test successful tracing setup"""
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        
        result = setup_tracing("test-service")
        
        assert result == mock_tracer
        mock_resource.create.assert_called_once()
        mock_provider_class.assert_called_once()
    
    @patch('src.utils.observability.trace')
    @patch('src.utils.observability.Resource')
    @patch('src.utils.observability.TracerProvider')
    def test_tracing_exception_handling(self, mock_provider_class, mock_resource, mock_trace):
        """Test exception handling in tracing setup"""
        mock_resource.create.side_effect = Exception("Test error")
        
        result = setup_tracing("test-service")
        
        assert result is None


class TestGetPrometheusMetrics:
    """Tests for get_prometheus_metrics function"""
    
    @patch('src.utils.observability.generate_latest')
    def test_get_metrics_success(self, mock_generate):
        """Test getting metrics successfully"""
        mock_generate.return_value = b"# HELP test_metric\n"
        
        result = get_prometheus_metrics()
        
        assert result == b"# HELP test_metric\n"
        mock_generate.assert_called_once()


class TestStructuredLogger:
    """Tests for StructuredLogger class"""
    
    def test_logger_initialization(self):
        """Test logger initialization"""
        logger = StructuredLogger("test-logger")
        assert logger.logger.name == "test-logger"
    
    @patch('logging.Logger.log')
    def test_log_method(self, mock_log):
        """Test generic log method"""
        logger = StructuredLogger("test")
        logger.log("INFO", "test message", key="value")
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == logging.INFO
        assert args[1] == "test message"
        assert kwargs['extra']['structured'] is True
        assert kwargs['extra']['key'] == "value"
    
    @patch('logging.Logger.log')
    def test_info_method(self, mock_log):
        """Test info logging"""
        logger = StructuredLogger("test")
        logger.info("info message", user_id=123)
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == logging.INFO
        assert kwargs['extra']['user_id'] == 123
    
    @patch('logging.Logger.log')
    def test_warning_method(self, mock_log):
        """Test warning logging"""
        logger = StructuredLogger("test")
        logger.warning("warning message", code=400)
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == logging.WARNING
        assert kwargs['extra']['code'] == 400
    
    @patch('logging.Logger.log')
    def test_error_method(self, mock_log):
        """Test error logging"""
        logger = StructuredLogger("test")
        logger.error("error message", error_code=500)
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == logging.ERROR
        assert kwargs['extra']['error_code'] == 500
    
    @patch('logging.Logger.log')
    def test_debug_method(self, mock_log):
        """Test debug logging"""
        logger = StructuredLogger("test")
        logger.debug("debug message", trace_id="abc123")
        
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == logging.DEBUG
        assert kwargs['extra']['trace_id'] == "abc123"
