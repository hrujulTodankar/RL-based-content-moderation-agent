from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth_middleware import get_current_user
from app.storage import storage_manager
from app.observability import track_performance, structured_logger, set_user_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storage", tags=["Storage Management"])

@router.get("/info")
@track_performance("storage_info")
async def get_storage_info(current_user: Dict = Depends(get_current_user)):
    """Get storage backend information"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        info = storage_manager.get_storage_info()
        info["user_id"] = user_id

        return info

    except Exception as e:
        logger.error(f"Error getting storage info for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storage information")

@router.get("/files/{segment}")
@track_performance("list_storage_files")
async def list_storage_files(
    segment: str,
    current_user: Dict = Depends(get_current_user)
):
    """List files in a storage segment"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Validate segment access (users can only access their own files)
        allowed_segments = ["uploads", "temp"]  # Restrict to user-accessible segments

        if segment not in allowed_segments:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to segment '{segment}'"
            )

        files = storage_manager.list_files(segment)

        structured_logger.log_security_event(
            "storage_list_access",
            "127.0.0.1",
            user_id,
            {"segment": segment, "file_count": len(files)}
        )

        return {
            "segment": segment,
            "files": files,
            "count": len(files),
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files in segment {segment} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")

@router.post("/upload/{segment}")
@track_performance("storage_file_upload")
async def upload_file(
    segment: str,
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Upload a file to storage"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Validate segment access
        allowed_segments = ["uploads", "temp"]

        if segment not in allowed_segments:
            raise HTTPException(
                status_code=403,
                detail=f"Upload not allowed to segment '{segment}'"
            )

        # Read file content
        content = await file.read()

        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File too large (max 100MB)"
            )

        # Generate unique filename with user prefix
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = f"{user_id}_{timestamp}_{file.filename}"

        # Determine content type
        content_type = file.content_type or "application/octet-stream"

        # Save file
        file_path = storage_manager.save_file(segment, safe_filename, content, content_type)

        structured_logger.log_security_event(
            "storage_file_upload",
            "127.0.0.1",
            user_id,
            {
                "segment": segment,
                "filename": safe_filename,
                "original_filename": file.filename,
                "content_type": content_type,
                "size_bytes": len(content)
            }
        )

        return {
            "message": "File uploaded successfully",
            "segment": segment,
            "filename": safe_filename,
            "original_filename": file.filename,
            "path": file_path,
            "size_bytes": len(content),
            "content_type": content_type,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file to segment {segment} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@router.get("/download/{segment}/{filename}")
@track_performance("storage_file_download")
async def download_file(
    segment: str,
    filename: str,
    current_user: Dict = Depends(get_current_user)
):
    """Download a file from storage"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Validate segment access
        allowed_segments = ["uploads", "temp"]

        if segment not in allowed_segments:
            raise HTTPException(
                status_code=403,
                detail=f"Download not allowed from segment '{segment}'"
            )

        # Security check: ensure user can only access their own files
        if not filename.startswith(f"{user_id}_"):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this file"
            )

        # Get file content
        content = storage_manager.get_file(segment, filename)

        if content is None:
            raise HTTPException(status_code=404, detail="File not found")

        structured_logger.log_security_event(
            "storage_file_download",
            "127.0.0.1",
            user_id,
            {
                "segment": segment,
                "filename": filename,
                "size_bytes": len(content)
            }
        )

        # Return file content with appropriate headers
        from fastapi.responses import Response

        # Try to determine content type from filename
        content_type = "application/octet-stream"
        if filename.lower().endswith('.json'):
            content_type = "application/json"
        elif filename.lower().endswith('.txt'):
            content_type = "text/plain"
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            content_type = "image/jpeg"
        elif filename.lower().endswith('.png'):
            content_type = "image/png"
        elif filename.lower().endswith('.pdf'):
            content_type = "application/pdf"

        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {segment}/{filename} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@router.delete("/files/{segment}/{filename}")
@track_performance("storage_file_delete")
async def delete_file(
    segment: str,
    filename: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete a file from storage"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Validate segment access
        allowed_segments = ["uploads", "temp"]

        if segment not in allowed_segments:
            raise HTTPException(
                status_code=403,
                detail=f"Delete not allowed in segment '{segment}'"
            )

        # Security check: ensure user can only delete their own files
        if not filename.startswith(f"{user_id}_"):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this file"
            )

        # Delete file
        success = storage_manager.delete_file(segment, filename)

        if not success:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")

        structured_logger.log_security_event(
            "storage_file_delete",
            "127.0.0.1",
            user_id,
            {
                "segment": segment,
                "filename": filename
            }
        )

        return {
            "message": "File deleted successfully",
            "segment": segment,
            "filename": filename,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {segment}/{filename} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

@router.post("/cleanup/{segment}")
@track_performance("storage_cleanup")
async def cleanup_old_files(
    segment: str,
    max_age_days: int = 30,
    current_user: Dict = Depends(get_current_user)
):
    """Clean up old files in a storage segment (admin only)"""
    user_id = current_user["user_id"]

    try:
        set_user_context(user_id, current_user.get("username"))

        # Check if user has admin role (simplified check)
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required for cleanup operations"
            )

        # Validate segment
        allowed_segments = ["temp", "logs", "uploads"]

        if segment not in allowed_segments:
            raise HTTPException(
                status_code=400,
                detail=f"Cleanup not allowed for segment '{segment}'"
            )

        # Perform cleanup
        cleaned_count = storage_manager.cleanup_old_files(segment, max_age_days)

        structured_logger.log_security_event(
            "storage_cleanup",
            "127.0.0.1",
            user_id,
            {
                "segment": segment,
                "max_age_days": max_age_days,
                "cleaned_count": cleaned_count
            }
        )

        return {
            "message": f"Cleanup completed for segment '{segment}'",
            "segment": segment,
            "max_age_days": max_age_days,
            "files_cleaned": cleaned_count,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up files in segment {segment} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup files")