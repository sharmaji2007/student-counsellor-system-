import asyncio
import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime

from app.core.config import settings

class StorageService:
    def __init__(self):
        self.minio_client = None
        self.s3_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize storage clients"""
        # Initialize MinIO client for local development
        try:
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            
            # Create bucket if it doesn't exist
            if not self.minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
                print(f"Created MinIO bucket: {settings.MINIO_BUCKET_NAME}")
                
        except Exception as e:
            print(f"Warning: Could not initialize MinIO client: {e}")
        
        # Initialize AWS S3 client for production
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                print(f"Warning: Could not initialize S3 client: {e}")
    
    async def upload_file(
        self, 
        file_content: bytes, 
        file_name: str, 
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to storage and return file path"""
        # Generate unique file path
        timestamp = datetime.now().strftime("%Y/%m/%d")
        unique_name = f"{uuid.uuid4()}_{file_name}"
        file_path = f"uploads/{timestamp}/{unique_name}"
        
        if settings.ENVIRONMENT == "production" and self.s3_client and settings.AWS_S3_BUCKET:
            # Use S3 in production
            return await self._upload_to_s3(file_content, file_path, content_type)
        else:
            # Use MinIO for development
            return await self._upload_to_minio(file_content, file_path, content_type)
    
    async def _upload_to_minio(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """Upload file to MinIO"""
        if not self.minio_client:
            # Fallback: save to local filesystem
            return await self._save_to_local_filesystem(file_content, file_path)
        
        try:
            # Run MinIO upload in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.minio_client.put_object(
                    settings.MINIO_BUCKET_NAME,
                    file_path,
                    data=asyncio.BytesIO(file_content),
                    length=len(file_content),
                    content_type=content_type
                )
            )
            
            return f"minio://{settings.MINIO_BUCKET_NAME}/{file_path}"
            
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            return await self._save_to_local_filesystem(file_content, file_path)
    
    async def _upload_to_s3(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """Upload file to AWS S3"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    Key=file_path,
                    Body=file_content,
                    ContentType=content_type
                )
            )
            
            return f"s3://{settings.AWS_S3_BUCKET}/{file_path}"
            
        except ClientError as e:
            print(f"S3 upload error: {e}")
            return await self._save_to_local_filesystem(file_content, file_path)
    
    async def _save_to_local_filesystem(self, file_content: bytes, file_path: str) -> str:
        """Fallback: save file to local filesystem"""
        local_path = f"uploads/{file_path}"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Write file
        with open(local_path, 'wb') as f:
            f.write(file_content)
        
        return f"file://{local_path}"
    
    async def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file from storage"""
        if file_path.startswith("minio://"):
            return await self._download_from_minio(file_path)
        elif file_path.startswith("s3://"):
            return await self._download_from_s3(file_path)
        elif file_path.startswith("file://"):
            return await self._download_from_local(file_path)
        else:
            print(f"Unknown file path format: {file_path}")
            return None
    
    async def _download_from_minio(self, file_path: str) -> Optional[bytes]:
        """Download file from MinIO"""
        if not self.minio_client:
            return None
        
        try:
            # Extract bucket and object name from path
            path_parts = file_path.replace("minio://", "").split("/", 1)
            bucket_name = path_parts[0]
            object_name = path_parts[1]
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.minio_client.get_object(bucket_name, object_name)
            )
            
            return response.read()
            
        except S3Error as e:
            print(f"MinIO download error: {e}")
            return None
    
    async def _download_from_s3(self, file_path: str) -> Optional[bytes]:
        """Download file from AWS S3"""
        if not self.s3_client:
            return None
        
        try:
            # Extract bucket and key from path
            path_parts = file_path.replace("s3://", "").split("/", 1)
            bucket_name = path_parts[0]
            key = path_parts[1]
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=bucket_name, Key=key)
            )
            
            return response['Body'].read()
            
        except ClientError as e:
            print(f"S3 download error: {e}")
            return None
    
    async def _download_from_local(self, file_path: str) -> Optional[bytes]:
        """Download file from local filesystem"""
        try:
            local_path = file_path.replace("file://", "")
            
            if os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    return f.read()
            else:
                print(f"Local file not found: {local_path}")
                return None
                
        except Exception as e:
            print(f"Local file read error: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        if file_path.startswith("minio://"):
            return await self._delete_from_minio(file_path)
        elif file_path.startswith("s3://"):
            return await self._delete_from_s3(file_path)
        elif file_path.startswith("file://"):
            return await self._delete_from_local(file_path)
        else:
            return False
    
    async def _delete_from_minio(self, file_path: str) -> bool:
        """Delete file from MinIO"""
        if not self.minio_client:
            return False
        
        try:
            path_parts = file_path.replace("minio://", "").split("/", 1)
            bucket_name = path_parts[0]
            object_name = path_parts[1]
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.minio_client.remove_object(bucket_name, object_name)
            )
            
            return True
            
        except S3Error as e:
            print(f"MinIO delete error: {e}")
            return False
    
    async def _delete_from_s3(self, file_path: str) -> bool:
        """Delete file from AWS S3"""
        if not self.s3_client:
            return False
        
        try:
            path_parts = file_path.replace("s3://", "").split("/", 1)
            bucket_name = path_parts[0]
            key = path_parts[1]
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            )
            
            return True
            
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
    
    async def _delete_from_local(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            local_path = file_path.replace("file://", "")
            
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Local file delete error: {e}")
            return False