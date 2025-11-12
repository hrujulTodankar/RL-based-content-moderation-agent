from fastapi import APIRouter, HTTPException, File, UploadFile, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import uuid
import io

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available - image dimension analysis disabled")

from ..moderation_agent import ModerationAgent
from ..feedback_handler import FeedbackHandler
from ..event_queue import EventQueue

logger = logging.getLogger(__name__)

# Initialize components
moderation_agent = ModerationAgent()
feedback_handler = FeedbackHandler()
event_queue = EventQueue()

def extract_image_metadata(content: bytes, filename: str) -> Dict[str, Any]:
    """Extract detailed metadata from image files"""
    metadata = {}

    if not PIL_AVAILABLE:
        return metadata

    try:
        # Open image with PIL
        image = Image.open(io.BytesIO(content))

        # Basic dimensions
        metadata["width"] = image.width
        metadata["height"] = image.height
        metadata["format"] = image.format
        metadata["mode"] = image.mode

        # Calculate aspect ratio
        if image.height > 0:
            metadata["aspect_ratio"] = image.width / image.height

        # Color analysis
        if image.mode in ['RGB', 'RGBA', 'P']:
            # Get color statistics
            colors = image.getcolors(maxcolors=256)
            if colors:
                metadata["color_count"] = len(colors)
                # Find dominant color
                dominant_color = max(colors, key=lambda x: x[0])
                metadata["dominant_color"] = dominant_color[1] if len(dominant_color) > 1 else None

        # File size efficiency (pixels per byte)
        total_pixels = image.width * image.height
        metadata["pixels_per_byte"] = total_pixels / len(content) if len(content) > 0 else 0

        # Image quality indicators
        metadata["is_animated"] = getattr(image, 'is_animated', False)
        metadata["frame_count"] = getattr(image, 'n_frames', 1)

        # Check for transparency
        metadata["has_transparency"] = image.mode in ['RGBA', 'LA', 'P'] and 'A' in image.mode

        # EXIF data (if available)
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            if exif:
                metadata["has_exif"] = True
                # Extract basic EXIF info
                exif_info = {}
                exif_tags = {
                    271: "Make",      # Camera make
                    272: "Model",     # Camera model
                    306: "DateTime",  # Date/time
                    274: "Orientation" # Image orientation
                }
                for tag, name in exif_tags.items():
                    if tag in exif:
                        exif_info[name] = str(exif[tag])
                if exif_info:
                    metadata["exif"] = exif_info
            else:
                metadata["has_exif"] = False
        else:
            metadata["has_exif"] = False

        image.close()

    except Exception as e:
        logger.warning(f"Failed to extract image metadata: {str(e)}")
        metadata["extraction_error"] = str(e)

    return metadata

router = APIRouter()

class ModerationResponse(BaseModel):
    moderation_id: str
    flagged: bool
    score: float
    confidence: float
    content_type: str
    reasons: list[str]
    timestamp: str

@router.post("/moderate/file")
async def moderate_file(
    file: UploadFile = File(...),
    content_type: str = Form(...),
    mcp_metadata: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Moderate uploaded files (images, audio, video)
    Handles large files asynchronously with proper error handling
    """
    # For demo purposes, skip authentication
    """
    Moderate uploaded files (images, audio, video)
    Handles large files asynchronously with proper error handling
    """
    try:
        moderation_id = str(uuid.uuid4())

        # Validate file size (10MB limit for images)
        MAX_SIZE = 10 * 1024 * 1024
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_SIZE} bytes (10MB)"
            )

        # Validate content type
        valid_types = ["image", "audio", "video"]
        if content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content_type for file. Must be one of: {valid_types}"
            )

        # Parse MCP metadata if provided
        mcp_meta = None
        if mcp_metadata:
            import json
            mcp_meta = json.loads(mcp_metadata)

        # Process file content and extract metadata
        file_metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        }

        # Extract detailed image metadata if it's an image
        if content_type == "image" and PIL_AVAILABLE:
            image_metadata = extract_image_metadata(content, file.filename)
            file_metadata.update(image_metadata)

        # Run moderation
        result = await moderation_agent.moderate(
            content=content,
            content_type=content_type,
            metadata={"file": file_metadata, "mcp_metadata": mcp_meta}
        )

        moderation_record = {
            "moderation_id": moderation_id,
            "content_type": content_type,
            "flagged": result["flagged"],
            "score": result["score"],
            "confidence": result["confidence"],
            "reasons": result["reasons"],
            "timestamp": datetime.utcnow().isoformat()
        }

        await feedback_handler.store_moderation(moderation_record)

        background_tasks.add_task(
            event_queue.emit,
            "file_moderation_completed",
            moderation_record
        )

        return ModerationResponse(**moderation_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File moderation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="File processing error")