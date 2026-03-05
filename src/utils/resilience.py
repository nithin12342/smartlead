"""
SmartLead Resilience Utilities
=============================
Circuit breaker and retry decorators for resilience

Spec-Driven: Generated from SmartLead/harness.json resilience_harness
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance
    
    Prevents cascading failures by stopping requests to failing services
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 30,
        half_open_max_requests: int = 3,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_requests = half_open_max_requests
        self.name = name
        
        self._failure_count = 0
        self._last_failure_time = 0
        self._state = "closed"  # closed, open, half-open
        self._half_open_requests = 0
    
    @property
    def state(self) -> str:
        """Get current circuit breaker state"""
        if self._state == "open":
            # Check if timeout has passed
            if time.time() - self._last_failure_time > self.timeout:
                self._state = "half-open"
                self._half_open_requests = 0
                logger.info(f"Circuit breaker {self.name} moved to half-open")
        
        return self._state
    
    def record_success(self) -> None:
        """Record a successful call"""
        if self._state == "half-open":
            self._half_open_requests += 1
            if self._half_open_requests >= self.half_open_max_requests:
                self._state = "closed"
                self._failure_count = 0
                logger.info(f"Circuit breaker {self.name} closed")
        elif self._state == "closed":
            self._failure_count = max(0, self._failure_count - 1)
    
    def record_failure(self) -> None:
        """Record a failed call"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == "half-open":
            self._state = "open"
            logger.warning(f"Circuit breaker {self.name} opened after half-open failure")
        elif self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(f"Circuit breaker {self.name} opened after {self._failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        return self.state != "open"


# Global circuit breaker instances
_circuit_breakers = {}


def circuit_breaker(
    failure_threshold: int = 5,
    timeout: int = 30,
    half_open_max_requests: int = 3,
    service_name: Optional[str] = None
):
    """
    Circuit breaker decorator
    
    Args:
        failure_threshold: Number of failures before opening circuit
        timeout: Time in seconds before trying again
        half_open_max_requests: Max requests in half-open state
        service_name: Name of the service (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = service_name or func.__name__
            
            if name not in _circuit_breakers:
                _circuit_breakers[name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    timeout=timeout,
                    half_open_max_requests=half_open_max_requests,
                    name=name
                )
            
            breaker = _circuit_breakers[name]
            
            if not breaker.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker {name} is open")
            
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = service_name or func.__name__
            
            if name not in _circuit_breakers:
                _circuit_breakers[name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    timeout=timeout,
                    half_open_max_requests=half_open_max_requests,
                    name=name
                )
            
            breaker = _circuit_breakers[name]
            
            if not breaker.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker {name} is open")
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def retry_with_backoff(
    max_attempts: int = 3,
    initial_interval: int = 1000,
    max_interval: int = 30000,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_interval: Initial wait time in milliseconds
        max_interval: Maximum wait time in milliseconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        # Calculate wait time
                        wait_time = min(
                            initial_interval * (exponential_base ** attempt),
                            max_interval
                        )
                        
                        if jitter:
                            import random
                            wait_time = wait_time * (0.5 + random.random())
                        
                        wait_time_seconds = wait_time / 1000
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {wait_time_seconds:.2f}s"
                        )
                        await asyncio.sleep(wait_time_seconds)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        # Calculate wait time
                        wait_time = min(
                            initial_interval * (exponential_base ** attempt),
                            max_interval
                        )
                        
                        if jitter:
                            import random
                            wait_time = wait_time * (0.5 + random.random())
                        
                        wait_time_seconds = wait_time / 1000
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {wait_time_seconds:.2f}s"
                        )
                        time.sleep(wait_time_seconds)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class Bulkhead:
    """
    Bulkhead pattern implementation for resource isolation
    """
    
    def __init__(self, max_concurrent: int = 100, max_waiting: int = 50):
        self.max_concurrent = max_concurrent
        self.max_waiting = max_waiting
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._waiting_queue = asyncio.Queue(maxsize=max_waiting)
    
    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with bulkhead isolation"""
        async with self._semaphore:
            return await func(*args, **kwargs)
