import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from app.core.config import settings

# Initialize tracing
def setup_tracing():
    """Setup OpenTelemetry tracing"""
    
    # Create resource
    resource = Resource.create({
        "service.name": "dristhi-backend",
        "service.version": settings.VERSION,
        "deployment.environment": "development" if settings.DEBUG else "production"
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add span processors
    if settings.DEBUG:
        # Console exporter for development
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Jaeger exporter for distributed tracing
    if hasattr(settings, 'JAEGER_HOST') and settings.JAEGER_HOST:
        jaeger_exporter = JaegerExporter(
            agent_host_name=settings.JAEGER_HOST,
            agent_port=settings.JAEGER_PORT or 6831,
        )
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # OTLP exporter for production monitoring
    if hasattr(settings, 'OTLP_ENDPOINT') and settings.OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTLP_ENDPOINT,
            insecure=settings.DEBUG
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    return provider

def get_tracer(name: str):
    """Get a tracer instance for a specific module"""
    return trace.get_tracer(name)

# Tracing decorators and utilities
def trace_function(span_name: str = None):
    """Decorator to trace function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer(func.__module__)
            span_name_final = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name_final) as span:
                # Add function attributes to span
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

def trace_database_operation(operation: str, table: str = None):
    """Decorator to trace database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer("database")
            span_name = f"db.{operation}"
            
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("db.operation", operation)
                if table:
                    span.set_attribute("db.table", table)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

def trace_ai_operation(operation_type: str, model: str = None):
    """Decorator to trace AI operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer("ai_service")
            span_name = f"ai.{operation_type}"
            
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("ai.operation_type", operation_type)
                if model:
                    span.set_attribute("ai.model", model)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

def trace_external_api_call(service: str, endpoint: str):
    """Decorator to trace external API calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer("external_api")
            span_name = f"api.{service}.{endpoint}"
            
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("http.service", service)
                span.set_attribute("http.endpoint", endpoint)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

# Context managers for manual tracing
class TraceContext:
    """Context manager for manual tracing"""
    
    def __init__(self, tracer_name: str, span_name: str, attributes: dict = None):
        self.tracer = get_tracer(tracer_name)
        self.span_name = span_name
        self.attributes = attributes or {}
        self.span = None
    
    def __enter__(self):
        self.span = self.tracer.start_as_current_span(self.span_name)
        
        # Set attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc_val)))
            self.span.record_exception(exc_val)
        else:
            self.span.set_status(trace.Status(trace.StatusCode.OK))
        
        self.span.end()

# Utility functions for adding context to spans
def add_user_context(span, user_id: int):
    """Add user context to a span"""
    span.set_attribute("user.id", user_id)

def add_request_context(span, method: str, path: str, status_code: int = None):
    """Add HTTP request context to a span"""
    span.set_attribute("http.method", method)
    span.set_attribute("http.path", path)
    if status_code:
        span.set_attribute("http.status_code", status_code)

def add_performance_metrics(span, duration: float, memory_usage: float = None):
    """Add performance metrics to a span"""
    span.set_attribute("performance.duration_ms", duration * 1000)
    if memory_usage:
        span.set_attribute("performance.memory_mb", memory_usage)

# Initialize tracing
setup_tracing()
