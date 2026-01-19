from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
# from bson import ObjectId # Not needed with Beanie's PydanticObjectId in Pydantic v2
from pydantic import field_validator
import re

class Role(Document):
    """
    Role defines a set of permissions.
    Roles are reusable templates assigned to users via UserAccess.
    by claude
    """
    
    # ==================== IDENTIFICATION ====================
    name: str = Field(..., min_length=1, max_length=100)
    # Role name: "SUPER_ADMIN", "MANAGER", "EMPLOYEE"
    # Should be UPPERCASE by convention
    # Unique
    
    code: str = Field(..., min_length=2, max_length=50)
    # Short code for programmatic use
    # Example: "SUPER_ADMIN", "DEPT_MGR", "EMP"
    # Unique, uppercase
    
    display_name: str = Field(..., max_length=100)
    # Human-readable name for UI
    # Example: "Department Manager", "Employee"
    
    description: Optional[str] = Field(None, max_length=500)
    # What this role is for
    # Example: "Manages department, approves leave, views team data"
    
    # ==================== ROLE HIERARCHY ====================
    level: int = Field(default=0)
    # Hierarchy level for role comparison
    # 0 = Employee (lowest)
    # 1 = Team Lead
    # 2 = Manager
    # 3 = Director
    # 4 = Admin
    # 5 = Super Admin (highest)
    
    inherits_from: Optional[PydanticObjectId] = None
    # Optional: Role inheritance
    # If set, this role inherits all permissions from parent role
    # Example: "SENIOR_MANAGER" inherits from "MANAGER"
    
    # ==================== PERMISSIONS ====================
    permissions: dict = Field(default_factory=dict)
    # Permission flags (boolean)
    # Example:
    # {
    #     # Organization Management
    #     "can_manage_company": False,
    #     "can_manage_departments": False,
    #     "can_manage_branches": False,
    #     
    #     # Employee Management
    #     "can_create_employee": False,
    #     "can_edit_employee": False,
    #     "can_terminate_employee": False,
    #     "can_view_all_employees": False,
    #     
    #     # Sensitive Data
    #     "can_view_salary": False,
    #     "can_edit_salary": False,
    #     "can_view_bank_details": False,
    #     
    #     # Time & Attendance
    #     "can_approve_leave": False,
    #     "can_edit_attendance": False,
    #     "can_view_team_attendance": False,
    #     
    #     # Payroll
    #     "can_process_payroll": False,
    #     "can_view_payroll": False,
    #     
    #     # Reports
    #     "can_view_reports": False,
    #     "can_export_data": False,
    #     
    #     # System Admin
    #     "can_manage_roles": False,
    #     "can_manage_permissions": False,
    #     "can_view_audit_logs": False
    # }
    
    # ==================== METADATA ====================
    is_system_role: bool = Field(default=False)
    # True for built-in roles (cannot be deleted)
    # False for custom roles created by admins
    
    is_active: bool = Field(default=True)
    # Can this role be assigned?
    
    # ==================== USAGE TRACKING ====================
    assigned_count: int = Field(default=0)
    # How many UserAccess records use this role
    # Updated via trigger/scheduled job
    # Helps prevent deletion of in-use roles
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
    
    # ==================== VALIDATORS ====================
    @field_validator("code")
    @classmethod
    def normalize_code(cls, v):
        """Uppercase and trim code"""
        return v.upper().strip()
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v):
        """Uppercase and trim name"""
        return v.upper().strip()
    
    class Settings:
        name = "roles"
        
        indexes = [
            "name",  # Unique
            "code",  # Unique
            "is_system_role",
            "is_active",
            "level",  # For hierarchy queries
        ]