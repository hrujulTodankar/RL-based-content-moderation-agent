import logging
import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

logger = logging.getLogger(__name__)

class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging
    Tracks metrics, errors, and performance
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Metrics tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
    
    async def dispatch(self, request: Request, call_next):
        """Process each request and log details"""
        start_time = time.time()
        self.request_count += 1
        
        # Extract request info
        request_id = f"req_{int(start_time * 1000)}"
        client_host = request.client.host if request.client else "unknown"
        
        # Log request
        request_log = {
            "request_id": request_id,
            "timestamp": start_time,
            "method": request.method,
            "path": request.url.path,
            "client": client_host,
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        logger.info(f"Request: {request.method} {request.url.path} from {client_host}")
        
        try:
            # Skip auth check for demo endpoints
            if request.url.path.startswith("/api/moderate") or request.url.path.startswith("/api/feedback"):
                # Allow demo access
                pass

            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            self.total_response_time += process_time
            
            # Log response
            response_log = {
                **request_log,
                "status_code": response.status_code,
                "process_time": process_time,
                "success": response.status_code < 400
            }
            
            # Add custom header
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log to file
            self._write_log(response_log)
            
            logger.info(
                f"Response: {response.status_code} for {request.url.path} "
                f"in {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            self.error_count += 1
            process_time = time.time() - start_time
            
            # Log error
            error_log = {
                **request_log,
                "status_code": 500,
                "process_time": process_time,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            
            self._write_log(error_log)
            
            logger.error(
                f"Error processing {request.url.path}: {str(e)}",
                exc_info=True
            )
            
            # Re-raise to let FastAPI handle it
            raise
    
    def _write_log(self, log_data: dict):
        """Write log entry to file"""
        try:
            log_file = os.path.join(self.log_dir, "requests.jsonl")
            with open(log_file, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            logger.error(f"Error writing request log: {str(e)}")
    
    def get_metrics(self) -> dict:
        """Get middleware metrics"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "avg_response_time": avg_response_time
        }