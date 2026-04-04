#!/usr/bin/env python3
"""
🔧 UUID SERVICE - Centralized UUID Handling

Fixes PostgreSQL UUID vs varchar mismatches across the application.
"""

import uuid
from fastapi import HTTPException
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)

class UUIDService:
    """Centralized UUID handling service"""
    
    @staticmethod
    def safe_convert(device_id: Union[str, uuid.UUID, None]) -> Optional[uuid.UUID]:
        """Convert string to UUID safely"""
        if device_id is None:
            return None
        if isinstance(device_id, uuid.UUID):
            return device_id
        try:
            return uuid.UUID(str(device_id))
        except ValueError:
            # Smart log-level: test/debug IDs use DEBUG (invisible in prod), others use WARNING
            device_id_str = str(device_id).lower()
            if any(p in device_id_str for p in ("test-", "debug-", "manual-", "temp-")):
                logger.debug(f"Rejected test/debug device_id (non-UUID): {device_id}")
            else:
                logger.warning(f"Invalid device_id format (not a UUID): {device_id}")
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid device_id format. Expected UUID, got: {device_id}"
            )
    
    @staticmethod
    def safe_convert_list(device_ids: List[Union[str, uuid.UUID]]) -> List[uuid.UUID]:
        """Convert list of string UUIDs to UUID objects"""
        uuids = []
        for device_id in device_ids:
            try:
                uuids.append(uuid.UUID(str(device_id)))
            except ValueError:
                logger.warning(f"Skipping invalid UUID in list: {device_id}")
                continue  # Skip invalid UUIDs
        return uuids
    
    @staticmethod
    def validate_uuid_string(device_id: str) -> bool:
        """Check if string is valid UUID format"""
        try:
            uuid.UUID(str(device_id))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def convert_or_none(device_id: Union[str, uuid.UUID, None]) -> Optional[uuid.UUID]:
        """Convert string to UUID, return None if invalid (no exception)"""
        if device_id is None:
            return None
        if isinstance(device_id, uuid.UUID):
            return device_id
        try:
            return uuid.UUID(str(device_id))
        except ValueError:
            logger.warning(f"Invalid UUID format, returning None: {device_id}")
            return None

# Global convenience functions
def safe_uuid(device_id: Union[str, uuid.UUID, None]) -> Optional[uuid.UUID]:
    """Convenience function for UUID conversion"""
    return UUIDService.safe_convert(device_id)

def safe_uuid_list(device_ids: List[Union[str, uuid.UUID]]) -> List[uuid.UUID]:
    """Convenience function for UUID list conversion"""
    return UUIDService.safe_convert_list(device_ids)
