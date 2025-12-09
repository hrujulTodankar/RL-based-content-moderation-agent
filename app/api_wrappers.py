#!/usr/bin/env python3
"""
API Response Wrappers and Error Handling
========================================

Standardized response wrappers for inconsistent API endpoints.
Provides unified error handling and response formatting across all endpoints.

Author: Content Moderation System
Version: 1.0.0
"""

import logging
import uuid
import traceback
from typing import Any, Dict, Optional, Union, Callable, Awaitable
from functools import wraps
from datetime import datetime

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from .schemas import StandardResponse, ErrorResponse, PaginatedResponse

logger = logging.getLogger(__name__)

class APIErrorCodes:
    """Standardized error codes for consistent error handling"""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_VALUE = "INVALID_VALUE"
    
    # Authentication/Authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_DELETED = "RESOURCE_DELETED"
    
    # Service errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"

class APIException(Exception):
    """Custom API exception with standardized error handling"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str, 
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.request_id = request_id
        super().__init__(self.message)

class APIResponseWrapper:
    """Wrapper for standardizing API responses"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "Request processed successfully",
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> StandardResponse:
        """Create standardized success response"""
        return StandardResponse(
            success=True,
            message=message,
            data=data,
            meta=meta,
            request_id=request_id or str(uuid.uuid4())
        )
    
    @staticmethod
    def error(
        message: str,
        error_code: str = APIErrorCodes.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> ErrorResponse:
        """Create standardized error response"""
        return ErrorResponse(
            message=message,
            error_code=error_code,
            details=details,
            request_id=request_id or str(uuid.uuid4())
        )
    
    @staticmethod
    def paginated(
        data: list,
        page: int,
        page_size: int,
        total_items: int,
        message: str = "Data retrieved successfully",
        request_id: Optional[str] = None
    ) -> PaginatedResponse:
        """Create standardized paginated response"""
        total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        
        return PaginatedResponse(
            data=data,
            meta={
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            request_id=request_id or str(uuid.uuid4())
        )
    
    @staticmethod
    def to_json_response(response: Union[StandardResponse, ErrorResponse, PaginatedResponse]) -> JSONResponse:
        """Convert standardized response to FastAPI JSONResponse"""
        return JSONResponse(
            content=response.dict(),
            status_code=getattr(response, 'status_code', 200)
        )

def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator for automatic error handling in API endpoints.
    Converts exceptions to standardized error responses.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        request_id = str(uuid.uuid4())
        
        try:
            # Extract request from args if available
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Handle different return types
            if isinstance(result, (StandardResponse, ErrorResponse, PaginatedResponse)):
                return APIResponseWrapper.to_json_response(result)
            elif isinstance(result, dict) and "success" in result:
                # Already a response dict, convert to StandardResponse
                response = StandardResponse(**result)
                response.request_id = request_id
                return APIResponseWrapper.to_json_response(response)
            else:
                # Raw data, wrap in success response
                response = APIResponseWrapper.success(
                    data=result,
                    request_id=request_id
                )
                return APIResponseWrapper.to_json_response(response)
                
        except HTTPException as e:
            # Re-raise HTTP exceptions as-is (FastAPI handles these)
            logger.error(f"HTTP exception in {func.__name__}: {e.detail}")
            raise
        except APIException as e:
            # Handle custom API exceptions
            logger.error(f"API exception in {func.__name__}: {e.message}")
            error_response = APIResponseWrapper.error(
                message=e.message,
                error_code=e.error_code,
                status_code=e.status_code,
                details=e.details,
                request_id=e.request_id or request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            error_response = APIResponseWrapper.error(
                message=str(e),
                error_code=APIErrorCodes.VALIDATION_ERROR,
                status_code=400,
                request_id=request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            error_response = APIResponseWrapper.error(
                message="An unexpected error occurred",
                error_code=APIErrorCodes.INTERNAL_ERROR,
                status_code=500,
                details={"original_error": str(e)} if logger.isEnabledFor(logging.DEBUG) else None,
                request_id=request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        request_id = str(uuid.uuid4())
        
        try:
            # Extract request from args if available
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Call the original function
            result = func(*args, **kwargs)
            
            # Handle different return types
            if isinstance(result, (StandardResponse, ErrorResponse, PaginatedResponse)):
                return APIResponseWrapper.to_json_response(result)
            elif isinstance(result, dict) and "success" in result:
                # Already a response dict, convert to StandardResponse
                response = StandardResponse(**result)
                response.request_id = request_id
                return APIResponseWrapper.to_json_response(response)
            else:
                # Raw data, wrap in success response
                response = APIResponseWrapper.success(
                    data=result,
                    request_id=request_id
                )
                return APIResponseWrapper.to_json_response(response)
                
        except HTTPException as e:
            # Re-raise HTTP exceptions as-is
            logger.error(f"HTTP exception in {func.__name__}: {e.detail}")
            raise
        except APIException as e:
            # Handle custom API exceptions
            logger.error(f"API exception in {func.__name__}: {e.message}")
            error_response = APIResponseWrapper.error(
                message=e.message,
                error_code=e.error_code,
                status_code=e.status_code,
                details=e.details,
                request_id=e.request_id or request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            error_response = APIResponseWrapper.error(
                message=str(e),
                error_code=APIErrorCodes.VALIDATION_ERROR,
                status_code=400,
                request_id=request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            error_response = APIResponseWrapper.error(
                message="An unexpected error occurred",
                error_code=APIErrorCodes.INTERNAL_ERROR,
                status_code=500,
                details={"original_error": str(e)} if logger.isEnabledFor(logging.DEBUG) else None,
                request_id=request_id
            )
            return APIResponseWrapper.to_json_response(error_response)
    
    # Return async wrapper if function is async, sync wrapper otherwise
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that all required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise APIException(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            error_code=APIErrorCodes.MISSING_REQUIRED_FIELD,
            status_code=400,
            details={"missing_fields": missing_fields}
        )

def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> None:
    """Validate that fields have expected types"""
    for field_name, expected_type in field_types.items():
        if field_name in data and data[field_name] is not None:
            if not isinstance(data[field_name], expected_type):
                raise APIException(
                    message=f"Field '{field_name}' must be of type {expected_type.__name__}",
                    error_code=APIErrorCodes.INVALID_FORMAT,
                    status_code=400,
                    details={
                        "field": field_name,
                        "expected_type": expected_type.__name__,
                        "actual_type": type(data[field_name]).__name__
                    }
                )

def validate_enum_values(data: Dict[str, Any], field_enums: Dict[str, list]) -> None:
    """Validate that enum fields have allowed values"""
    for field_name, allowed_values in field_enums.items():
        if field_name in data and data[field_name] is not None:
            if data[field_name] not in allowed_values:
                raise APIException(
                    message=f"Field '{field_name}' must be one of: {', '.join(map(str, allowed_values))}",
                    error_code=APIErrorCodes.INVALID_VALUE,
                    status_code=400,
                    details={
                        "field": field_name,
                        "allowed_values": allowed_values,
                        "actual_value": data[field_name]
                    }
                )

# Global wrapper instance
api_wrapper = APIResponseWrapper()

# Convenience functions
def success_response(data: Any = None, message: str = "Success", meta: Optional[Dict] = None) -> StandardResponse:
    """Create standardized success response"""
    return api_wrapper.success(data, message, meta)

def error_response(message: str, error_code: str = APIErrorCodes.INTERNAL_ERROR, 
                  status_code: int = 500, details: Optional[Dict] = None) -> ErrorResponse:
    """Create standardized error response"""
    return api_wrapper.error(message, error_code, status_code, details)

def paginated_response(data: list, page: int, page_size: int, 
                      total_items: int) -> PaginatedResponse:
    """Create standardized paginated response"""
    return api_wrapper.paginated(data, page, page_size, total_items)