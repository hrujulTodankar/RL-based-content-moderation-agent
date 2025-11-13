#!/usr/bin/env python3
"""
Observability and monitoring system for RL Content Moderation
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import contextmanager
import traceback
import asyncio
from functools import wraps

# Sentry integration
SENTRY_AVAILABLE = False
sentry_sdk = None
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    pass

# PostHog integration
POSTHOG_AVAILABLE = False
Posthog = None
try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)

class ObservabilityConfig:
    """Configuration for observability services"""

    # Sentry Configuration
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    SENTRY_RELEASE = os.getenv("GIT_SHA", "unknown")

    # PostHog Configuration
    POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
    POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://us.posthog.com")

    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))  # seconds

    # Feature Flags
    ENABLE_USER_ANALYTICS = os.getenv("ENABLE_USER_ANALYTICS", "true").lower() == "true"
    ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "true").lower() == "true"

config = ObservabilityConfig()

class SentryManager:
    """Sentry integration for error tracking"""

    def __init__(self):
        self.initialized = False
        self.setup()

    def setup(self):
        """Initialize Sentry"""
        if not SENTRY_AVAILABLE:
            logger.info("Sentry SDK not available")
            return

        if not config.SENTRY_DSN:
            logger.info("Sentry DSN not configured")
            return

        try:
            logging_integration = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )

            sentry_sdk.init(
                dsn=config.SENTRY_DSN,
                environment=config.SENTRY_ENVIRONMENT,
                release=config.SENTRY_RELEASE,
                integrations=[
                    FastApiIntegration(),
                    logging_integration
                ],
                traces_sample_rate=1.0 if config.SENTRY_ENVIRONMENT == "development" else 0.1,
                send_default_pii=False,
                attach_stacktrace=True,
                max_breadcrumbs=50
            )

            sentry_sdk.set_tag("service", "rl-content-moderation")
            sentry_sdk.set_tag("version", config.SENTRY_RELEASE)

            self.initialized = True
            logger.info("Sentry initialized successfully")

        except Exception as e:
            logger.error(f"Sentry initialization failed: {e}")

    def capture_exception(self, error: Exception, extra_data: Dict[str, Any] = None):
        """Capture exception with additional context"""
        if not self.initialized:
            return

        try:
            with sentry_sdk.configure_scope() as scope:
                if extra_data:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)

                sentry_sdk.capture_exception(error)
        except Exception as e:
            logger.error(f"Failed to send exception to Sentry: {e}")

    def capture_message(self, message: str, level: str = "info", extra_data: Dict[str, Any] = None):
        """Capture custom message"""
        if not self.initialized:
            return

        try:
            with sentry_sdk.configure_scope() as scope:
                if extra_data:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)

                sentry_sdk.capture_message(message, level)
        except Exception as e:
            logger.error(f"Failed to send message to Sentry: {e}")

    def set_user_context(self, user_id: str, username: str = None, email: str = None):
        """Set user context for error tracking"""
        if not self.initialized:
            return

        try:
            sentry_sdk.set_user({
                "id": user_id,
                "username": username,
                "email": email
            })
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")

class PostHogManager:
    """PostHog integration for product analytics"""

    def __init__(self):
        self.client = None
        self.initialized = False
        self.setup()

    def setup(self):
        """Initialize PostHog client"""
        if not POSTHOG_AVAILABLE:
            logger.info("PostHog SDK not available")
            return

        if not config.POSTHOG_API_KEY:
            logger.info("PostHog API key not configured")
            return

        try:
            self.client = Posthog(
                project_api_key=config.POSTHOG_API_KEY,
                host=config.POSTHOG_HOST,
                debug=config.SENTRY_ENVIRONMENT == "development"
            )
            self.initialized = True
            logger.info("PostHog initialized successfully")

        except Exception as e:
            logger.error(f"PostHog initialization failed: {e}")

    def track_event(self, user_id: str, event: str, properties: Dict[str, Any] = None):
        """Track user event with properties"""
        if not self.initialized or not config.ENABLE_USER_ANALYTICS:
            return

        try:
            event_properties = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "rl-content-moderation",
                "environment": config.SENTRY_ENVIRONMENT,
                **(properties or {})
            }

            self.client.capture(
                distinct_id=user_id,
                event=event,
                properties=event_properties
            )

        except Exception as e:
            logger.error(f"Failed to track PostHog event: {e}")

    def identify_user(self, user_id: str, traits: Dict[str, Any] = None):
        """Identify user with traits"""
        if not self.initialized:
            return

        try:
            self.client.identify(
                distinct_id=user_id,
                properties={
                    "service": "rl-content-moderation",
                    "identified_at": datetime.utcnow().isoformat(),
                    **(traits or {})
                }
            )

        except Exception as e:
            logger.error(f"Failed to identify user in PostHog: {e}")

    def track_feature_usage(self, user_id: str, feature: str, success: bool = True,
                           duration_ms: int = None, metadata: Dict[str, Any] = None):
        """Track feature usage with success metrics"""
        if not self.initialized:
            return

        properties = {
            "feature": feature,
            "success": success,
            "environment": config.SENTRY_ENVIRONMENT,
            **(metadata or {})
        }

        if duration_ms is not None:
            properties["duration_ms"] = duration_ms

        self.track_event(user_id, "feature_used", properties)

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""

    def __init__(self):
        self.metrics = {}
        self.slow_operations = []
        self.start_time = time.time()

    @contextmanager
    def measure_operation(self, operation_name: str, user_id: str = None):
        """Context manager to measure operation performance"""
        start_time = time.time()
        success = True
        error = None

        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Record metrics
            self._record_performance_metric(operation_name, duration, success, user_id)

            # Track slow operations
            if duration > config.SLOW_QUERY_THRESHOLD * 1000:
                self._record_slow_operation(operation_name, duration, user_id, error)

    def _record_performance_metric(self, operation: str, duration_ms: float,
                                  success: bool, user_id: str = None):
        """Record performance metric"""
        metric_key = f"{operation}_{datetime.now().strftime('%Y%m%d_%H')}"

        if metric_key not in self.metrics:
            self.metrics[metric_key] = {
                "operation": operation,
                "count": 0,
                "total_duration": 0,
                "success_count": 0,
                "error_count": 0,
                "min_duration": float('inf'),
                "max_duration": 0
            }

        metric = self.metrics[metric_key]
        metric["count"] += 1
        metric["total_duration"] += duration_ms
        metric["min_duration"] = min(metric["min_duration"], duration_ms)
        metric["max_duration"] = max(metric["max_duration"], duration_ms)

        if success:
            metric["success_count"] += 1
        else:
            metric["error_count"] += 1

        # Track in PostHog if user_id available
        if user_id and posthog_manager.initialized:
            posthog_manager.track_feature_usage(
                user_id, operation, success, int(duration_ms)
            )

    def _record_slow_operation(self, operation: str, duration_ms: float,
                              user_id: str = None, error: str = None):
        """Record slow operation for investigation"""
        slow_op = {
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "error": error
        }

        self.slow_operations.append(slow_op)

        # Keep only last 100 slow operations
        if len(self.slow_operations) > 100:
            self.slow_operations = self.slow_operations[-100:]

        # Report to Sentry if very slow
        if duration_ms > config.SLOW_QUERY_THRESHOLD * 2000:  # 2x threshold
            sentry_manager.capture_message(
                f"Very slow operation: {operation}",
                level="warning",
                extra_data=slow_op
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        summary = {}

        for metric_key, metric in self.metrics.items():
            if metric["count"] > 0:
                summary[metric["operation"]] = {
                    "count": metric["count"],
                    "avg_duration_ms": metric["total_duration"] / metric["count"],
                    "success_rate": metric["success_count"] / metric["count"],
                    "min_duration_ms": metric["min_duration"],
                    "max_duration_ms": metric["max_duration"]
                }

        return {
            "metrics": summary,
            "slow_operations_count": len(self.slow_operations),
            "recent_slow_operations": self.slow_operations[-5:] if self.slow_operations else []
        }

    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time

class StructuredLogger:
    """Structured logging for better observability"""

    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        """Setup structured logging configuration"""
        # Add custom log levels
        logging.addLevelName(25, "SUCCESS")
        logging.addLevelName(35, "SECURITY")

    def log_api_request(self, method: str, path: str, status_code: int,
                       duration_ms: float, user_id: str = None,
                       request_size: int = None, response_size: int = None):
        """Log API request with structured data"""
        log_data = {
            "event_type": "api_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            log_data["user_id"] = user_id
        if request_size:
            log_data["request_size_bytes"] = request_size
        if response_size:
            log_data["response_size_bytes"] = response_size

        logger.info("API Request", extra=log_data)

    def log_moderation_event(self, content_type: str, flagged: bool, score: float,
                           user_id: str = None, duration_ms: float = None):
        """Log moderation events"""
        log_data = {
            "event_type": "moderation",
            "content_type": content_type,
            "flagged": flagged,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            log_data["user_id"] = user_id
        if duration_ms:
            log_data["duration_ms"] = duration_ms

        logger.info("Moderation Event", extra=log_data)

    def log_security_event(self, event_type: str, client_ip: str, user_id: str = None,
                          details: Dict[str, Any] = None):
        """Log security events"""
        log_data = {
            "event_type": "security_event",
            "security_event": event_type,
            "client_ip": client_ip,
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            log_data["user_id"] = user_id
        if details:
            log_data["details"] = details

        logger.log(35, "Security Event", extra=log_data)

# Simple manager classes
class SimpleSentryManager:
    def __init__(self):
        self.initialized = bool(config.SENTRY_DSN and SENTRY_AVAILABLE)
    def capture_exception(self, *args, **kwargs): pass
    def capture_message(self, *args, **kwargs): pass
    def set_user_context(self, *args, **kwargs): pass

class SimplePostHogManager:
    def __init__(self):
        self.initialized = bool(config.POSTHOG_API_KEY and POSTHOG_AVAILABLE)
    def track_event(self, *args, **kwargs): pass
    def identify_user(self, *args, **kwargs): pass
    def track_feature_usage(self, *args, **kwargs): pass

def initialize_observability():
    """Initialize observability services safely"""
    global sentry_manager, posthog_manager, performance_monitor, structured_logger

    sentry_manager = SimpleSentryManager()
    posthog_manager = SimplePostHogManager()
    performance_monitor = PerformanceMonitor()
    structured_logger = StructuredLogger()

    return sentry_manager, posthog_manager, performance_monitor, structured_logger

# Initialize on import
sentry_manager, posthog_manager, performance_monitor, structured_logger = initialize_observability()

# Decorators for easy integration
def track_performance(operation_name: str):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with performance_monitor.measure_operation(operation_name):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with performance_monitor.measure_operation(operation_name):
                return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def track_user_action(action_name: str):
    """Decorator to track user actions in PostHog"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user_id from function arguments or kwargs
            user_id = kwargs.get('user_id') or getattr(kwargs.get('current_user'), 'user_id', None)

            try:
                result = await func(*args, **kwargs)
                if user_id:
                    posthog_manager.track_event(user_id, action_name, {"success": True})
                return result
            except Exception as e:
                if user_id:
                    posthog_manager.track_event(user_id, action_name, {
                        "success": False,
                        "error": str(e)
                    })
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or getattr(kwargs.get('current_user'), 'user_id', None)

            try:
                result = func(*args, **kwargs)
                if user_id:
                    posthog_manager.track_event(user_id, action_name, {"success": True})
                return result
            except Exception as e:
                if user_id:
                    posthog_manager.track_event(user_id, action_name, {
                        "success": False,
                        "error": str(e)
                    })
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Utility functions
def capture_exception(error: Exception, extra_data: Dict[str, Any] = None):
    """Convenience function to capture exceptions"""
    sentry_manager.capture_exception(error, extra_data)

def track_event(user_id: str, event: str, properties: Dict[str, Any] = None):
    """Convenience function to track events"""
    posthog_manager.track_event(user_id, event, properties)

def set_user_context(user_id: str, username: str = None, email: str = None):
    """Set user context for both Sentry and PostHog"""
    sentry_manager.set_user_context(user_id, username, email)
    if username or email:
        posthog_manager.identify_user(user_id, {
            "username": username,
            "email": email
        })

def get_observability_health() -> Dict[str, Any]:
    """Get health status of observability services"""
    return {
        "sentry": {
            "enabled": sentry_manager.initialized,
            "dsn_configured": bool(config.SENTRY_DSN)
        },
        "posthog": {
            "enabled": posthog_manager.initialized,
            "api_key_configured": bool(config.POSTHOG_API_KEY)
        },
        "performance_monitoring": {
            "enabled": config.ENABLE_PERFORMANCE_MONITORING,
            "slow_query_threshold": config.SLOW_QUERY_THRESHOLD
        }
    }