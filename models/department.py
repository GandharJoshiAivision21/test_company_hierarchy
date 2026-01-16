from beanie import Document, PydanticObjectId
from pydantic import Field, validator
from typing import Optional
from datetime import datetime
import re

class Department(Document):
    """
    Department Hierarchy (Functional Structure).
    Independent of Branch (Location).
    """
    
    # 1. Identity & Display
    name: str = Field(..., min_length=1, max_length=100)  # e.g., "Engineering"
    code: str = Field(..., min_length=1, max_length=50)   # e.g., "DEPT-ENG"
    
    # 2. The Link to the Parent Entity
    # A Department MUST belong to a specific Company.
    company_id: PydanticObjectId = Field(...) 
    
    # 3. Hierarchy (The Tree Logic)
    # Just like Company, we use M-Path for sub-departments.
    parent_department_id: Optional[PydanticObjectId] = Field(None)
    materialized_path: Optional[str] = Field(None) # e.g., "001.002"
    depth: int = Field(default=0, ge=0)
    is_group: bool = Field(default=False) # True if it has sub-departments
    
    # 4. Status & Audit
    status: str = Field(default="active")
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- VALIDATORS (Same rules as Company) ---
    
    @validator('code')
    def normalize_code(cls, v):
        return v.upper().strip()

    @validator('materialized_path')
    def validate_materialized_path(cls, v):
        if v is None: return v
        # Enforces the "001.001" format
        pattern = r'^(\d{3})(\.(\d{3}))*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid path format. Use 001.001')
        return v

    class Settings:
        name = "departments"
        indexes = [
            "company_id",           # Find all depts in a company
            "materialized_path",    # Find entire sub-tree
            "parent_department_id", # Find direct children
            "code"
        ]