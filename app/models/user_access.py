from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
from bson import ObjectId
from pydantic import field_validator
import re

class UserAccess(Document):
    """
    Links a User to a Role within a specific Scope.
    One user can have multiple UserAccess records (different roles in different places).
    by claude
    """
    
    # ==================== LINKING ====================
    user_id: PydanticObjectId = Field(...)
    # Which user has this access
    # Links to User._id
    # Required
    
    role_id: PydanticObjectId = Field(...)
    # Which role (permission template)
    # Links to Role._id
    # Required
    
    # ==================== SCOPE (WHERE) ====================
    scope_type: str = Field(...)
    # Where does this role apply?
    # Values: "COMPANY", "DEPARTMENT", "BRANCH", "GLOBAL"
    # Required
    
    path_limit: str = Field(...)
    # Materialized path boundary
    # Examples:
    #   "001" - entire company
    #   "001.002" - engineering dept
    #   "005" - mumbai branch
    # All descendants of this path are included
    # Required
    
    # ==================== SCOPE DEPTH LIMIT ====================
    depth_limit: Optional[int] = None
    # Optional: Limit how deep the scope goes
    # Example:
    #   path_limit: "001.002", depth_limit: 1
    #   → Can manage 001.002.xxx (direct children only)
    #   → Cannot manage 001.002.xxx.yyy (grandchildren)
    # Null = unlimited depth (default)
    
    # ==================== OVERRIDES ====================
    overrides: dict = Field(default_factory=dict)
    # User-specific permission exceptions
    # Overrides the role's default permissions
    # Example:
    # {
    #     "can_view_salary": True,  # Override role default
    #     "can_approve_leave": False  # Remove role permission
    # }
    # Usually empty - only for special cases
    
    # ==================== RESTRICTIONS ====================
    restrictions: dict = Field(default_factory=dict)
    # Additional constraints beyond permissions
    # Example:
    # {
    #     "max_salary_approval": 100000,  # Can't approve >1L
    #     "max_leave_days": 5,  # Can approve max 5 days
    #     "allowed_departments": ["001.002", "001.003"]  # Specific depts
    # }
    
    # ==================== VALIDITY ====================
    is_active: bool = Field(default=True)
    # Is this access grant currently active?
    # False = temporarily disabled
    
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    # When does this access start?
    # Allows: Schedule future access
    
    valid_until: Optional[datetime] = None
    # When does this access expire?
    # Null = never expires
    # Allows: Temporary access (contractors, projects)
    
    # ==================== APPROVAL/AUDIT ====================
    granted_by: Optional[PydanticObjectId] = None
    # Who gave this access?
    # Links to User._id of admin
    # For audit trail
    
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    # When was this access granted?
    
    reason: Optional[str] = Field(None, max_length=500)
    # Why was this access granted?
    # Example: "Temporary access for Q4 audit"
    
    revoked_by: Optional[PydanticObjectId] = None
    # Who revoked this access?
    # Set when is_active = False
    
    revoked_at: Optional[datetime] = None
    # When was access revoked?
    
    revoke_reason: Optional[str] = Field(None, max_length=500)
    # Why was access revoked?
    
    # ==================== METADATA ====================
    last_used_at: Optional[datetime] = None
    # Last time this access was actually used
    # Helps identify unused access grants
    
    usage_count: int = Field(default=0)
    # How many times this access was used
    # Incremented on permission checks
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
    
    # ==================== VALIDATORS ====================
    @field_validator("scope_type")
    @classmethod
    def validate_scope_type(cls, v):
        """Ensure valid scope type"""
        allowed = ['COMPANY', 'DEPARTMENT', 'BRANCH', 'GLOBAL']
        if v not in allowed:
            raise ValueError(f'scope_type must be one of {allowed}')
        return v
    
    @field_validator("path_limit")
    @classmethod
    def validate_path_limit(cls, v):
        """Validate materialized path format"""
        if v == "*":  # Global scope
            return v
        # Should match: 001 or 001.002 or 001.002.003
        import re
        pattern = r'^(\d{3})(\.(\d{3}))*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid path_limit format. Expected: 001.002.003')
        return v
    
    class Settings:
        name = "user_access"
        
        indexes = [
            "user_id",  # Find all access for a user
            "role_id",  # Find all users with a role
            "scope_type",
            "path_limit",
            [("user_id", 1), ("is_active", 1)],  # Active access for user
            [("user_id", 1), ("scope_type", 1), ("path_limit", 1)],  # Unique combo
            [("valid_from", 1), ("valid_until", 1)],  # Time-based queries
            [("is_active", 1), ("valid_until", 1)],  # Find expiring access
        ]