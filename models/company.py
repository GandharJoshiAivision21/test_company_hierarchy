from beanie import Document
from pydantic import Field, validator
# from pydantic import field_validator

from datetime import datetime
from typing import Optional, List
# from bson import ObjectId
from beanie import PydanticObjectId
import re

class Company(Document):
    """Company model - each tenant has separate database"""
    
    # Core fields (NO tenant_id needed)
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    
    # Hierarchy
    parent_company_id: Optional[PydanticObjectId] = None
    fallback_parent_company_id: Optional[PydanticObjectId] = None
    materialized_path: Optional[str] = None  # "001.002.003"
    depth: int = Field(default=0, ge=0)
    
    # Classification
    type: str = Field(...)  # holding_group, parent, subsidiary
    status: str = Field(default="active")
    
    # Denormalized children
    child_company_ids: List[PydanticObjectId] = Field(default_factory=list)

    
    # Lifecycle tracking
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    effective_to: Optional[datetime] = None
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[PydanticObjectId] = None
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
    
    # Validators
    @validator('type')
    def validate_type(cls, v):
        allowed = ['holding_group', 'parent', 'subsidiary']
        if v not in allowed:
            raise ValueError(f'type must be one of {allowed}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ['active', 'inactive', 'dissolved', 'merged', 'pending']
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v
    
    @validator('materialized_path')
    def validate_materialized_path(cls, v):
        if v is None:
            return v
        pattern = r'^(\d{3})(\.(\d{3}))*$'
        if not re.match(pattern, v):
            raise ValueError('materialized_path must match pattern: 001.002.003')
        return v
    
    @validator('code')
    def normalize_code(cls, v):
        return v.upper().strip()
    
    class Settings:
        name = "companies"
        
        # Indexes (NO tenant_id in indexes)
        indexes = [
            "code",  # Unique code per database (per tenant)
            "parent_company_id",
            "materialized_path",
            "depth",
            [("status", 1), ("is_deleted", 1)],
            "type",
        ]