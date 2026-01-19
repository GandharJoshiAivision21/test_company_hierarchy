# from beanie import Document, PydanticObjectId
# from pydantic import Field, validator
# from typing import Optional
# from datetime import datetime
# import re

# class Department(Document):
#     """
#     Department Hierarchy (Functional Structure).
#     Independent of Branch (Location).
#     """
    
#     # 1. Identity & Display
#     name: str = Field(..., min_length=1, max_length=100)  # e.g., "Engineering"
#     code: str = Field(..., min_length=1, max_length=50)   # e.g., "DEPT-ENG"
    
#     # 2. The Link to the Parent Entity
#     # A Department MUST belong to a specific Company.
#     company_id: PydanticObjectId = Field(...) 
    
#     # 3. Hierarchy (The Tree Logic)
#     # Just like Company, we use M-Path for sub-departments.
#     parent_department_id: Optional[PydanticObjectId] = Field(None)
#     materialized_path: Optional[str] = Field(None) # e.g., "001.002"
#     depth: int = Field(default=0, ge=0)
#     is_group: bool = Field(default=False) # True if it has sub-departments
    
#     # 4. Status & Audit
#     status: str = Field(default="active")
#     is_deleted: bool = Field(default=False)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)

#     # --- VALIDATORS (Same rules as Company) ---
    
#     @validator('code')
#     def normalize_code(cls, v):
#         return v.upper().strip()

#     @validator('materialized_path')
#     def validate_materialized_path(cls, v):
#         if v is None: return v
#         # Enforces the "001.001" format
#         pattern = r'^(\d{3})(\.(\d{3}))*$'
#         if not re.match(pattern, v):
#             raise ValueError('Invalid path format. Use 001.001')
#         return v

#     class Settings:
#         name = "departments"
#         indexes = [
#             "company_id",           # Find all depts in a company
#             "materialized_path",    # Find entire sub-tree
#             "parent_department_id", # Find direct children
#             "code"
#         ]

from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
# from bson import ObjectId # Not needed with Beanie's PydanticObjectId in Pydantic v2
from beanie import PydanticObjectId
from pydantic import field_validator
import re

class Department(Document):
    """
    Department hierarchy model.
    Represents organizational structure (reporting lines, functional areas).
    Supports unlimited depth using Materialized Path.
    Parallel to Branch (location) hierarchy.
    """
    
    # ==================== CORE IDENTIFICATION ====================
    name: str = Field(..., min_length=1, max_length=200)
    # Department name
    # Example: "Engineering", "Human Resources", "Backend Team"
    
    code: str = Field(..., min_length=1, max_length=50)
    # Short code for identification
    # Example: "ENG", "HR", "ENG-BE"
    # Unique within company
    
    # ==================== COMPANY LINKAGE ====================
    company_id: PydanticObjectId = Field(...)
    # Which company this department belongs to
    # Required - departments are company-specific
    # Links to Company._id
    
    # ==================== HIERARCHY ====================
    parent_department_id: Optional[PydanticObjectId] = None
    # Reference to immediate parent department
    # Null for top-level departments (e.g., "Engineering", "Sales")
    
    materialized_path: Optional[str] = None
    # Full path from root: "001.002.003"
    # Null for root departments
    # Used for: Fast subtree queries, hierarchy display
    
    depth: int = Field(default=0, ge=0)
    # Hierarchy depth (0=root, 1=child, 2=grandchild, etc.)
    # Root departments (Engineering, HR) = 0
    # Sub-departments (Backend, Frontend) = 1
    
    is_group: bool = Field(default=False)
    # Can have sub-departments (True) or is leaf node (False)
    # Controls UI: folder icon vs file icon
    # Example: "Engineering" (True) vs "DevOps Team" (False)
    
    root_id: Optional[PydanticObjectId] = None
    # Reference to top-most ancestor department
    # Points to self if IS the root
    # Enables fast "all departments in division" queries
    
    # ==================== DEPARTMENT INFO ====================
    type: str = Field(default="functional")
    # Department classification
    # Values: 
    #   "functional" - Standard dept (HR, Finance, Engineering)
    #   "division" - Large business unit
    #   "team" - Small working group
    #   "project" - Temporary project-based
    #   "cost_center" - For accounting purposes
    
    description: Optional[str] = Field(None, max_length=1000)
    # What this department does
    # Example: "Responsible for all software development and technical infrastructure"
    
    function: Optional[str] = Field(None, max_length=100)
    # Primary function/responsibility
    # Example: "Product Development", "Customer Support", "Finance & Accounting"
    
    # ==================== LEADERSHIP ====================
    head_employee_id: Optional[PydanticObjectId] = None
    # Department head/manager
    # Links to Employee._id
    # Example: "VP of Engineering", "HR Director"
    
    deputy_head_employee_id: Optional[PydanticObjectId] = None
    # Second-in-command
    # Links to Employee._id
    # Optional
    
    # ==================== METRICS & TRACKING ====================
    headcount: int = Field(default=0)
    # Current number of employees
    # Updated via trigger/scheduled job
    # Denormalized for performance
    
    headcount_limit: Optional[int] = None
    # Maximum allowed employees
    # Null = no limit
    # Used for: Budget planning, hiring approvals
    
    budget_code: Optional[str] = Field(None, max_length=50)
    # For financial tracking
    # Example: "CC-ENG-001"
    # Links to finance system
    
    cost_center_code: Optional[str] = Field(None, max_length=50)
    # Accounting cost center
    # Example: "1000-2000"
    
    # ==================== LOCATION (OPTIONAL) ====================
    primary_branch_id: Optional[PydanticObjectId] = None
    # Main physical location for this department
    # Links to Branch._id
    # Example: Engineering might be primarily in Bangalore
    # Note: Employees can be in different branches
    
    office_location: Optional[str] = Field(None, max_length=200)
    # Specific office area/floor
    # Example: "Building A, Floor 3, East Wing"
    
    # ==================== CONTACT INFO ====================
    email: Optional[str] = Field(None, max_length=100)
    # Department contact email
    # Example: "engineering@company.com", "support@company.com"
    
    phone: Optional[str] = Field(None, max_length=20)
    # Department contact number
    
    # ==================== OPERATIONAL STATUS ====================
    status: str = Field(default="active")
    # Operational status
    # Values: "active", "inactive", "dissolved", "merged", "planned"
    
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    # When department became operational
    
    effective_to: Optional[datetime] = None
    # When department was closed/merged
    # Null if still active
    
    # ==================== APPROVAL & WORKFLOW ====================
    requires_approval_for_hire: bool = Field(default=True)
    # Do hires need special approval?
    # Higher management approval required
    
    approval_chain: List[PydanticObjectId] = Field(default_factory=list)
    # Escalation path for approvals
    # [immediate_manager_id, dept_head_id, vp_id, ...]
    # Used for: Leave approvals, expense approvals
    
    # ==================== SETTINGS & POLICIES ====================
    settings: dict = Field(default_factory=dict)
    # Department-specific settings
    # Example:
    # {
    #     "work_from_home_allowed": True,
    #     "flexible_hours": True,
    #     "probation_period_months": 6,
    #     "default_leave_balance": 24,
    #     "weekend_days": ["saturday", "sunday"]
    # }
    
    policies: dict = Field(default_factory=dict)
    # Department-specific policies
    # Example:
    # {
    #     "code_review_required": True,
    #     "on_call_rotation": True,
    #     "travel_approval_limit": 50000
    # }
    
    # ==================== TAGS & METADATA ====================
    tags: List[str] = Field(default_factory=list)
    # For filtering/grouping
    # Example: ["revenue_generating", "customer_facing", "core_function"]
    
    custom_fields: dict = Field(default_factory=dict)
    # Tenant-specific additional fields
    # Flexible schema extension
    
    # ==================== SOFT DELETE ====================
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[PydanticObjectId] = None
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
    # ==================== VALIDATORS ====================
    @field_validator("code")
    @classmethod
    def normalize_code(cls, v):
        """Uppercase and trim"""
        return v.upper().strip()
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        """Lowercase and trim"""
        if v:
            return v.lower().strip()
        return v
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed = ['functional', 'division', 'team', 'project', 'cost_center']
        if v not in allowed:
            raise ValueError(f'type must be one of {allowed}')
        return v
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ['active', 'inactive', 'dissolved', 'merged', 'planned']
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v
    
    @field_validator("materialized_path")
    @classmethod
    def validate_materialized_path(cls, v):
        if v is None:
            return v
        pattern = r'^(\d{3})(\.(\d{3}))*$'
        if not re.match(pattern, v):
            raise ValueError('materialized_path must match pattern: 001.002.003')
        return v
    
    class Settings:
        name = "departments"
        
        indexes = [
            "company_id",  # Filter by company (CRITICAL)
            [("company_id", 1), ("code", 1)],  # Unique within company
            "parent_department_id",  # Find children
            "materialized_path",  # Hierarchy queries
            "root_id",  # Tree queries
            "depth",  # Level queries
            "is_group",  # Filter groups vs leaves
            "type",  # Filter by type
            "head_employee_id",  # Find departments by manager
            [("company_id", 1), ("status", 1), ("is_deleted", 1)],  # Active departments
            [("company_id", 1), ("materialized_path", 1)],  # Hierarchy within company
            "primary_branch_id",  # Departments at a location
        ]