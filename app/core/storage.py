"""Storage utilities for model artifacts."""

import logging
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_s3_client = None


def get_s3_client():
    """Get or create S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name=settings.aws_region)
    return _s3_client


def save_model(model_path: Path, s3_key: str) -> None:
    """Save model to S3 if configured, otherwise use local storage."""
    if settings.use_local_storage:
        logger.debug(f"Using local storage for {model_path}")
        return
    
    if not settings.s3_bucket_name:
        logger.warning("S3 bucket not configured, using local storage")
        return
    
    try:
        s3_client = get_s3_client()
        s3_client.upload_file(str(model_path), settings.s3_bucket_name, s3_key)
        logger.info(f"Model saved to S3: s3://{settings.s3_bucket_name}/{s3_key}")
    except ClientError as e:
        logger.error(f"Failed to save model to S3: {e}")
        raise


def load_model(s3_key: str, local_path: Path) -> None:
    """Load model from S3 if configured, otherwise use local storage."""
    if settings.use_local_storage:
        if not local_path.exists():
            raise FileNotFoundError(f"Model not found: {local_path}")
        logger.debug(f"Using local storage for {local_path}")
        return
    
    if not settings.s3_bucket_name:
        logger.warning("S3 bucket not configured, using local storage")
        return
    
    try:
        s3_client = get_s3_client()
        s3_client.download_file(settings.s3_bucket_name, s3_key, str(local_path))
        logger.info(f"Model loaded from S3: s3://{settings.s3_bucket_name}/{s3_key}")
    except ClientError as e:
        logger.error(f"Failed to load model from S3: {e}")
        raise


def delete_model(s3_key: str) -> None:
    """Delete model from S3 if configured."""
    if not settings.s3_bucket_name:
        return
    
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
        logger.info(f"Model deleted from S3: s3://{settings.s3_bucket_name}/{s3_key}")
    except ClientError as e:
        logger.error(f"Failed to delete model from S3: {e}")

