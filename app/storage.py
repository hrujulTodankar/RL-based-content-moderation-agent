#!/usr/bin/env python3
"""
Multi-backend storage system for RL Content Moderation
Supports local filesystem, AWS S3, and Supabase Storage
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StorageConfig:
    """Storage configuration"""

    # Backend selection
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # "local", "s3", "supabase"

    # Local storage
    LOCAL_STORAGE_PATH = Path(os.getenv("LOCAL_STORAGE_PATH", "storage"))

    # AWS S3 Configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "rl-moderation-storage")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "moderation-files")

    # Storage segments
    SEGMENTS = ["moderations", "feedback", "analytics", "logs", "uploads", "temp"]

class StorageBackend:
    """Abstract base class for storage backends"""

    def save_file(self, segment: str, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        raise NotImplementedError

    def save_text(self, segment: str, filename: str, content: str) -> str:
        raise NotImplementedError

    def save_json(self, segment: str, filename: str, data: Dict[str, Any]) -> str:
        raise NotImplementedError

    def get_file(self, segment: str, filename: str) -> Optional[bytes]:
        raise NotImplementedError

    def get_text(self, segment: str, filename: str) -> Optional[str]:
        raise NotImplementedError

    def get_json(self, segment: str, filename: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def list_files(self, segment: str) -> List[str]:
        raise NotImplementedError

    def delete_file(self, segment: str, filename: str) -> bool:
        raise NotImplementedError

    def cleanup_old_files(self, segment: str, max_age_days: int) -> int:
        raise NotImplementedError

class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._init_storage()

    def _init_storage(self):
        """Initialize storage directory structure"""
        for segment in self.config.SEGMENTS:
            (self.config.LOCAL_STORAGE_PATH / segment).mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, segment: str, filename: str) -> Path:
        """Get safe path within storage directory"""
        if segment not in self.config.SEGMENTS:
            raise ValueError(f"Invalid segment: {segment}")

        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")

        path = self.config.LOCAL_STORAGE_PATH / segment / safe_filename

        # Security check: ensure path is within storage directory
        if not str(path.resolve()).startswith(str(self.config.LOCAL_STORAGE_PATH.resolve())):
            raise ValueError("Path outside storage directory")

        return path

    def save_file(self, segment: str, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        path = self._get_safe_path(segment, filename)
        path.write_bytes(content)
        return str(path)

    def save_text(self, segment: str, filename: str, content: str) -> str:
        path = self._get_safe_path(segment, filename)
        path.write_text(content, encoding="utf-8")
        return str(path)

    def save_json(self, segment: str, filename: str, data: Dict[str, Any]) -> str:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return self.save_text(segment, filename, content)

    def get_file(self, segment: str, filename: str) -> Optional[bytes]:
        try:
            path = self._get_safe_path(segment, filename)
            if path.exists():
                return path.read_bytes()
        except Exception as e:
            logger.error(f"Error reading file {segment}/{filename}: {e}")
        return None

    def get_text(self, segment: str, filename: str) -> Optional[str]:
        try:
            path = self._get_safe_path(segment, filename)
            if path.exists():
                return path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading text file {segment}/{filename}: {e}")
        return None

    def get_json(self, segment: str, filename: str) -> Optional[Dict[str, Any]]:
        try:
            text = self.get_text(segment, filename)
            if text:
                return json.loads(text)
        except Exception as e:
            logger.error(f"Error reading JSON file {segment}/{filename}: {e}")
        return None

    def list_files(self, segment: str) -> List[str]:
        try:
            if segment not in self.config.SEGMENTS:
                return []

            segment_path = self.config.LOCAL_STORAGE_PATH / segment
            if segment_path.exists():
                return [f.name for f in segment_path.iterdir() if f.is_file()]
        except Exception as e:
            logger.error(f"Error listing files in {segment}: {e}")
        return []

    def delete_file(self, segment: str, filename: str) -> bool:
        try:
            path = self._get_safe_path(segment, filename)
            if path.exists():
                path.unlink()
                return True
        except Exception as e:
            logger.error(f"Error deleting file {segment}/{filename}: {e}")
        return False

    def cleanup_old_files(self, segment: str, max_age_days: int) -> int:
        try:
            if segment not in self.config.SEGMENTS:
                return 0

            segment_path = self.config.LOCAL_STORAGE_PATH / segment
            if not segment_path.exists():
                return 0

            cutoff_time = time.time() - (max_age_days * 86400)
            cleaned_count = 0

            for file_path in segment_path.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1

            return cleaned_count
        except Exception as e:
            logger.error(f"Error cleaning up old files in {segment}: {e}")
            return 0

class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._s3_client = None

    def _get_s3_client(self):
        if self._s3_client is None:
            try:
                import boto3
                self._s3_client = boto3.client(
                    's3',
                    region_name=self.config.S3_REGION,
                    aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY
                )
            except ImportError:
                raise ImportError("boto3 is required for S3 backend. Install with: pip install boto3")
        return self._s3_client

    def _get_s3_key(self, segment: str, filename: str) -> str:
        if segment not in self.config.SEGMENTS:
            raise ValueError(f"Invalid segment: {segment}")

        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")

        return f"{segment}/{safe_filename}"

    def save_file(self, segment: str, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        s3_key = self._get_s3_key(segment, filename)
        client = self._get_s3_client()

        client.put_object(
            Bucket=self.config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            ContentType=content_type
        )

        return f"s3://{self.config.S3_BUCKET_NAME}/{s3_key}"

    def save_text(self, segment: str, filename: str, content: str) -> str:
        return self.save_file(segment, filename, content.encode('utf-8'), "text/plain")

    def save_json(self, segment: str, filename: str, data: Dict[str, Any]) -> str:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return self.save_file(segment, filename, content.encode('utf-8'), "application/json")

    def get_file(self, segment: str, filename: str) -> Optional[bytes]:
        try:
            s3_key = self._get_s3_key(segment, filename)
            client = self._get_s3_client()

            response = client.get_object(Bucket=self.config.S3_BUCKET_NAME, Key=s3_key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error reading file from S3 {segment}/{filename}: {e}")
            return None

    def get_text(self, segment: str, filename: str) -> Optional[str]:
        try:
            content = self.get_file(segment, filename)
            if content:
                return content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading text from S3 {segment}/{filename}: {e}")
        return None

    def get_json(self, segment: str, filename: str) -> Optional[Dict[str, Any]]:
        try:
            text = self.get_text(segment, filename)
            if text:
                return json.loads(text)
        except Exception as e:
            logger.error(f"Error reading JSON from S3 {segment}/{filename}: {e}")
        return None

    def list_files(self, segment: str) -> List[str]:
        try:
            if segment not in self.config.SEGMENTS:
                return []

            client = self._get_s3_client()
            response = client.list_objects_v2(
                Bucket=self.config.S3_BUCKET_NAME,
                Prefix=f"{segment}/"
            )

            files = []
            for obj in response.get('Contents', []):
                filename = obj['Key'].replace(f"{segment}/", "")
                if filename and '/' not in filename:
                    files.append(filename)

            return files
        except Exception as e:
            logger.error(f"Error listing S3 files in {segment}: {e}")
            return []

    def delete_file(self, segment: str, filename: str) -> bool:
        try:
            s3_key = self._get_s3_key(segment, filename)
            client = self._get_s3_client()

            client.delete_object(Bucket=self.config.S3_BUCKET_NAME, Key=s3_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting S3 file {segment}/{filename}: {e}")
            return False

    def cleanup_old_files(self, segment: str, max_age_days: int) -> int:
        try:
            if segment not in self.config.SEGMENTS:
                return 0

            client = self._get_s3_client()
            response = client.list_objects_v2(
                Bucket=self.config.S3_BUCKET_NAME,
                Prefix=f"{segment}/"
            )

            cutoff_time = time.time() - (max_age_days * 86400)
            cleaned_count = 0

            for obj in response.get('Contents', []):
                if obj['LastModified'].timestamp() < cutoff_time:
                    client.delete_object(Bucket=self.config.S3_BUCKET_NAME, Key=obj['Key'])
                    cleaned_count += 1

            return cleaned_count
        except Exception as e:
            logger.error(f"Error cleaning up S3 files in {segment}: {e}")
            return 0

class SupabaseStorageBackend(StorageBackend):
    """Supabase Storage backend"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._supabase_client = None

    def _get_supabase_client(self):
        if self._supabase_client is None:
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    self.config.SUPABASE_URL,
                    self.config.SUPABASE_KEY
                )
            except ImportError:
                raise ImportError("supabase-py is required for Supabase backend. Install with: pip install supabase")
        return self._supabase_client

    def _get_file_path(self, segment: str, filename: str) -> str:
        if segment not in self.config.SEGMENTS:
            raise ValueError(f"Invalid segment: {segment}")

        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")

        return f"{segment}/{safe_filename}"

    def save_file(self, segment: str, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        file_path = self._get_file_path(segment, filename)
        client = self._get_supabase_client()

        # Upload file to Supabase Storage
        response = client.storage.from_(self.config.SUPABASE_BUCKET_NAME).upload(
            file_path,
            content,
            {"content-type": content_type}
        )

        if response.status_code != 200:
            raise Exception(f"Supabase upload failed: {response.json()}")

        return f"supabase://{self.config.SUPABASE_BUCKET_NAME}/{file_path}"

    def save_text(self, segment: str, filename: str, content: str) -> str:
        return self.save_file(segment, filename, content.encode('utf-8'), "text/plain")

    def save_json(self, segment: str, filename: str, data: Dict[str, Any]) -> str:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return self.save_file(segment, filename, content.encode('utf-8'), "application/json")

    def get_file(self, segment: str, filename: str) -> Optional[bytes]:
        try:
            file_path = self._get_file_path(segment, filename)
            client = self._get_supabase_client()

            response = client.storage.from_(self.config.SUPABASE_BUCKET_NAME).download(file_path)

            if response.status_code == 200:
                return response.content
        except Exception as e:
            logger.error(f"Error reading file from Supabase {segment}/{filename}: {e}")
        return None

    def get_text(self, segment: str, filename: str) -> Optional[str]:
        try:
            content = self.get_file(segment, filename)
            if content:
                return content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading text from Supabase {segment}/{filename}: {e}")
        return None

    def get_json(self, segment: str, filename: str) -> Optional[Dict[str, Any]]:
        try:
            text = self.get_text(segment, filename)
            if text:
                return json.loads(text)
        except Exception as e:
            logger.error(f"Error reading JSON from Supabase {segment}/{filename}: {e}")
        return None

    def list_files(self, segment: str) -> List[str]:
        try:
            if segment not in self.config.SEGMENTS:
                return []

            client = self._get_supabase_client()
            response = client.storage.from_(self.config.SUPABASE_BUCKET_NAME).list(segment)

            if response.status_code == 200:
                files = []
                for item in response.json():
                    if not item['name'].endswith('/'):  # Skip directories
                        files.append(item['name'])
                return files
        except Exception as e:
            logger.error(f"Error listing Supabase files in {segment}: {e}")
        return []

    def delete_file(self, segment: str, filename: str) -> bool:
        try:
            file_path = self._get_file_path(segment, filename)
            client = self._get_supabase_client()

            response = client.storage.from_(self.config.SUPABASE_BUCKET_NAME).remove([file_path])

            if response.status_code == 200:
                return True
        except Exception as e:
            logger.error(f"Error deleting Supabase file {segment}/{filename}: {e}")
        return False

    def cleanup_old_files(self, segment: str, max_age_days: int) -> int:
        # Supabase doesn't provide file modification times in list operations
        # This would need to be implemented differently or skipped
        logger.warning("Cleanup not implemented for Supabase backend")
        return 0

class StorageManager:
    """Main storage manager with multi-backend support"""

    def __init__(self):
        self.config = StorageConfig()
        self.backend = self._create_backend()

    def _create_backend(self) -> StorageBackend:
        """Create the appropriate storage backend"""
        backend_type = self.config.STORAGE_BACKEND.lower()

        if backend_type == "local":
            return LocalStorageBackend(self.config)
        elif backend_type == "s3":
            return S3StorageBackend(self.config)
        elif backend_type == "supabase":
            return SupabaseStorageBackend(self.config)
        else:
            logger.warning(f"Unknown storage backend '{backend_type}', falling back to local")
            return LocalStorageBackend(self.config)

    def save_file(self, segment: str, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        return self.backend.save_file(segment, filename, content, content_type)

    def save_text(self, segment: str, filename: str, content: str) -> str:
        return self.backend.save_text(segment, filename, content)

    def save_json(self, segment: str, filename: str, data: Dict[str, Any]) -> str:
        return self.backend.save_json(segment, filename, data)

    def get_file(self, segment: str, filename: str) -> Optional[bytes]:
        return self.backend.get_file(segment, filename)

    def get_text(self, segment: str, filename: str) -> Optional[str]:
        return self.backend.get_text(segment, filename)

    def get_json(self, segment: str, filename: str) -> Optional[Dict[str, Any]]:
        return self.backend.get_json(segment, filename)

    def list_files(self, segment: str) -> List[str]:
        return self.backend.list_files(segment)

    def delete_file(self, segment: str, filename: str) -> bool:
        return self.backend.delete_file(segment, filename)

    def cleanup_old_files(self, segment: str, max_age_days: int = 30) -> int:
        return self.backend.cleanup_old_files(segment, max_age_days)

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage backend information"""
        return {
            "backend": self.config.STORAGE_BACKEND,
            "segments": self.config.SEGMENTS,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global storage manager instance
storage_manager = StorageManager()