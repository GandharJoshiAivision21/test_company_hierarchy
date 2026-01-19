# from beanie import Document
# from pydantic import Field, validator
# # from pydantic import field_validator

# from datetime import datetime
# from typing import Optional, List
# # from bson import ObjectId
# from beanie import PydanticObjectId
# import re

# class Company(Document):
#     """Company model - each tenant has separate database"""
    
#     # Core fields (NO tenant_id needed)
#     name: str = Field(..., min_length=1, max_length=200)
#     code: str = Field(..., min_length=1, max_length=50)
    
#     # Hierarchy
#     parent_company_id: Optional[PydanticObjectId] = None
#     fallback_parent_company_id: Optional[PydanticObjectId] = None
#     materialized_path: Optional[str] = None  # "001.002.003"
#     depth: int = Field(default=0, ge=0)
    
#     # Classification
#     type: str = Field(...)  # holding_group, parent, subsidiary
#     status: str = Field(default="active")
    
#     # Denormalized children
#     child_company_ids: List[PydanticObjectId] = Field(default_factory=list)

    
#     # Lifecycle tracking
#     effective_from: datetime = Field(default_factory=datetime.utcnow)
#     effective_to: Optional[datetime] = None
    
#     # Soft delete
#     is_deleted: bool = Field(default=False)
#     deleted_at: Optional[datetime] = None
#     deleted_by: Optional[PydanticObjectId] = None
    
#     # Audit trail
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     created_by: Optional[PydanticObjectId] = None
#     updated_by: Optional[PydanticObjectId] = None
    
#     # Validators
#     @validator('type')
#     def validate_type(cls, v):
#         allowed = ['holding_group', 'parent', 'subsidiary']
#         if v not in allowed:
#             raise ValueError(f'type must be one of {allowed}')
#         return v
    
#     @validator('status')
#     def validate_status(cls, v):
#         allowed = ['active', 'inactive', 'dissolved', 'merged', 'pending']
#         if v not in allowed:
#             raise ValueError(f'status must be one of {allowed}')
#         return v
    
#     @validator('materialized_path')
#     def validate_materialized_path(cls, v):
#         if v is None:
#             return v
#         pattern = r'^(\d{3})(\.(\d{3}))*$'
#         if not re.match(pattern, v):
#             raise ValueError('materialized_path must match pattern: 001.002.003')
#         return v
    
#     @validator('code')
#     def normalize_code(cls, v):
#         return v.upper().strip()
    
#     class Settings:
#         name = "companies"
        
#         # Indexes (NO tenant_id in indexes)
#         indexes = [
#             "code",  # Unique code per database (per tenant)
#             "parent_company_id",
#             "materialized_path",
#             "depth",
#             [("status", 1), ("is_deleted", 1)],
#             "type",
#         ]

# from beanie import Document
# from pydantic import Field, validator
# from datetime import datetime
# from typing import Optional, List
# from beanie import PydanticObjectId
# import re

# class Company(Document):
#     """Company model - each tenant has separate database"""
    
#     # Core fields
#     name: str = Field(..., min_length=1, max_length=200)
#     code: str = Field(..., min_length=1, max_length=50) # The Business ID (e.g., TECH-IND)
    
#     # Hierarchy
#     parent_company_id: Optional[PydanticObjectId] = None
#     materialized_path: Optional[str] = None  # "001.002.003"
#     depth: int = Field(default=0, ge=0)
    
#     # --- ADDED FOR CLARITY ---
#     is_group: bool = Field(default=False) 
#     # Helps UI/Logic know if this company can have subsidiaries or departments
    
#     root_id: Optional[PydanticObjectId] = None 
#     # Links to the top-most ancestor (the 001 node) for fast "entire tree" queries
#     # -------------------------

#     # Classification
#     type: str = Field(...)  # holding_group, parent, subsidiary
#     status: str = Field(default="active")
    
#     # --- REMOVED child_company_ids ---
#     # With Materialized Path, storing IDs in a list is redundant and 
#     # creates "Sync" risks. Use M-Path to find children instead.

#     # Lifecycle & Audit
#     effective_from: datetime = Field(default_factory=datetime.utcnow)
#     effective_to: Optional[datetime] = None
#     is_deleted: bool = Field(default=False)
#     deleted_at: Optional[datetime] = None
#     deleted_by: Optional[PydanticObjectId] = None
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     created_by: Optional[PydanticObjectId] = None
#     updated_by: Optional[PydanticObjectId] = None

#     # Validators
#     @validator('type')
#     def validate_type(cls, v):
#         allowed = ['holding_group', 'parent', 'subsidiary']
#         if v not in allowed:
#             raise ValueError(f'type must be one of {allowed}')
#         return v
    
#     @validator('status')
#     def validate_status(cls, v):
#         allowed = ['active', 'inactive', 'dissolved', 'merged', 'pending']
#         if v not in allowed:
#             raise ValueError(f'status must be one of {allowed}')
#         return v
    
#     @validator('materialized_path')
#     def validate_materialized_path(cls, v):
#         if v is None:
#             return v
#         pattern = r'^(\d{3})(\.(\d{3}))*$'
#         if not re.match(pattern, v):
#             raise ValueError('materialized_path must match pattern: 001.002.003')
#         return v
    
#     @validator('code')
#     def normalize_code(cls, v):
#         return v.upper().strip()

#     class Settings:
#         name = "companies"
#         indexes = [
#             "code",
#             "parent_company_id",
#             "materialized_path",
#             "root_id", # Added for performance
#             "depth",
#             [("status", 1), ("is_deleted", 1)],
#             "type",
#         ]

from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId
import re

class Company(Document):
    """
    Company hierarchy model.
    Each tenant has separate database.
    Supports unlimited depth hierarchy using Materialized Path.
    """
    
    # ==================== CORE IDENTIFICATION ====================
    name: str = Field(..., min_length=1, max_length=200)
    # Full legal company name
    # Example: "TechCorp India Private Limited"
    
    code: str = Field(..., min_length=1, max_length=50)
    # Business identifier/short code
    # Example: "TECH-IND"
    # Unique within tenant (enforced by separate DB)
    
    # ==================== LEGAL/COMPLIANCE (ADD THESE) ====================
    legal_name: Optional[str] = Field(None, max_length=300)
    # Official registered name (if different from display name)
    # Example: "TechCorp India Private Limited"
    
    registration_number: Optional[str] = Field(None, max_length=100)
    # Company registration number
    # Example: "CIN: U72900MH2020PTC123456" (India)
    
    tax_id: Optional[str] = Field(None, max_length=100)
    # Tax identification number
    # Example: "GSTIN: 27AABCT1234F1Z5" (India GST)
    # Or: "EIN: 12-3456789" (US)
    
    incorporation_date: Optional[datetime] = None
    # When company was legally established
    
    # ==================== HIERARCHY ====================
    parent_company_id: Optional[ObjectId] = None
    # Reference to immediate parent company
    # Null for top-level holding companies
    
    materialized_path: Optional[str] = None
    # Full path from root: "001.002.003"
    # Null for root/holding companies
    
    depth: int = Field(default=0, ge=0)
    # Hierarchy depth (0=root, 1=parent, 2+=subsidiary)
    
    is_group: bool = Field(default=False)
    # Can have subsidiaries (True) or is leaf node (False)
    # Controls UI (folder vs file icon)
    
    root_id: Optional[ObjectId] = None
    # Reference to top-most ancestor
    # Points to self if IS the root
    # Enables fast "all in tree" queries
    
    # ==================== CLASSIFICATION ====================
    type: str = Field(...)
    # Company classification
    # Values: "holding_group" | "parent" | "subsidiary"
    
    status: str = Field(default="active")
    # Operational status
    # Values: "active" | "inactive" | "dissolved" | "merged" | "pending"
    
    # ==================== CONTACT INFO (ADD THESE) ====================
    registered_address: Optional[dict] = None
    # Legal registered address
    # {
    #     "line1": "123 Business Park",
    #     "line2": "Suite 100",
    #     "city": "Mumbai",
    #     "state": "Maharashtra",
    #     "country": "India",
    #     "postal_code": "400001"
    # }
    
    operating_address: Optional[dict] = None
    # Actual operating address (if different)
    # Same structure as registered_address
    
    primary_email: Optional[str] = Field(None, max_length=100)
    # Company contact email
    # Example: "contact@techcorp.com"
    
    primary_phone: Optional[str] = Field(None, max_length=20)
    # Company contact number
    
    website: Optional[str] = Field(None, max_length=200)
    # Company website URL
    
    # ==================== BUSINESS INFO (ADD THESE) ====================
    industry: Optional[str] = Field(None, max_length=100)
    # Industry/sector
    # Example: "Information Technology", "Manufacturing"
    
    company_size: Optional[str] = None
    # Employee count category
    # Values: "1-10", "11-50", "51-200", "201-500", "500+"
    
    fiscal_year_start: Optional[int] = Field(None, ge=1, le=12)
    # Fiscal year start month (1-12)
    # Example: 4 (April-March fiscal year in India)
    
    currency: str = Field(default="INR")
    # Primary currency for this company
    # Example: "INR", "USD", "EUR"
    
    timezone: str = Field(default="Asia/Kolkata")
    # Primary timezone
    # Example: "Asia/Kolkata", "America/New_York"
    
    # ==================== LIFECYCLE ====================
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    # When company became operational
    
    effective_to: Optional[datetime] = None
    # When company became inactive (null if still active)
    
    # ==================== SOFT DELETE ====================
    is_deleted: bool = Field(default=False)
    # Soft delete flag
    
    deleted_at: Optional[datetime] = None
    # When record was soft-deleted
    
    deleted_by: Optional[ObjectId] = None
    # User who deleted the record
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[ObjectId] = None
    updated_by: Optional[ObjectId] = None
    
    # ==================== METADATA (ADD THESE) ====================
    logo_url: Optional[str] = None
    # URL to company logo
    
    description: Optional[str] = Field(None, max_length=1000)
    # Company description/about
    
    settings: dict = Field(default_factory=dict)
    # Company-specific settings
    # Example:
    # {
    #     "allow_remote_work": True,
    #     "default_work_hours": 8,
    #     "weekend_days": ["saturday", "sunday"]
    # }
    
    # ==================== VALIDATORS ====================
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
    
    @validator('primary_email')
    def normalize_email(cls, v):
        if v:
            return v.lower().strip()
        return v
    
    # NEW: Validate fiscal year
    @validator('fiscal_year_start')
    def validate_fiscal_year(cls, v):
        if v is not None and (v < 1 or v > 12):
            raise ValueError('fiscal_year_start must be between 1 and 12')
        return v
    
    class Settings:
        name = "companies"
        
        indexes = [
            "code",  # Unique lookups
            "parent_company_id",  # Find children
            "materialized_path",  # Hierarchy queries
            "root_id",  # Tree queries
            "depth",  # Level queries
            "is_group",  # Filter groups vs leaves
            "type",  # Filter by type
            [("status", 1), ("is_deleted", 1)],  # Active companies
            "industry",  # NEW: Industry filtering
        ]