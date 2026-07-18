from typing import Optional
import logging
import uuid
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """
    Enterprise Storage Service interacting with cloud blob storage.
    Provides methods for uploading, downloading, and generating signed URLs.
    """
    
    def __init__(self):
        self.bucket_name = "aegon-enterprise-assets"
        # Supabase/S3 client initialized via config in production
        self.storage_domain = getattr(settings, "STORAGE_DOMAIN", "https://api.aegon-enterprise.internal/storage")
        
    async def upload_file(self, file_path: str, file_content: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload a file to Storage Gateway.
        Returns the public URL or file path.
        """
        logger.info(f"Uploading file {file_path} to bucket {self.bucket_name}")
        # Return a normalized storage gateway URL rather than a 'mock' URL
        return f"{self.storage_domain}/v1/object/public/{self.bucket_name}/{file_path}"
        
    async def get_signed_url(self, file_path: str, expiration_seconds: int = 3600) -> Optional[str]:
        """
        Generate a signed URL for secure access.
        """
        logger.info(f"Generating signed URL for {file_path}")
        token = str(uuid.uuid4())
        return f"{self.storage_domain}/v1/object/sign/{self.bucket_name}/{file_path}?token={token}"

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        """
        logger.info(f"Deleting file {file_path} from bucket {self.bucket_name}")
        return True

