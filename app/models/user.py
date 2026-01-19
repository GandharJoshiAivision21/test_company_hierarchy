from beanie import Document
from pydantic import Field, EmailStr, validator
from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from bson import ObjectId
from pydantic import field_validator

class User(Document):
    """
    User account for authentication and authorization.
    Represents the login identity.
    by claude
    """
    
    # ==================== AUTHENTICATION ====================
    email: EmailStr = Field(..., unique=True)
    # Primary login identifier
    # Must be unique across system
    # Validated email format
    
    password_hash: str = Field(...)
    # NEVER store plain password
    # Use bcrypt/argon2 for hashing
    # Example: "$2b$12$KIXqMxGz..."
    
    # ==================== IDENTITY ====================
    username: Optional[str] = Field(None, max_length=50)
    # Optional: Alternative login (if not using email)
    # Unique if provided
    
    full_name: str = Field(..., min_length=1, max_length=200)
    # Display name in UI
    # Example: "John Doe"
    
    # ==================== LINKING ====================
    employee_id: Optional[PydanticObjectId] = None
    # Link to Employee record (1:1 in most cases)
    # Null if: System user, consultant, external auditor
    
    # ==================== ACCOUNT STATUS ====================
    is_active: bool = Field(default=True)
    # Can this user login?
    # False = account disabled/locked
    
    is_verified: bool = Field(default=False)
    # Email verification status
    # True after clicking verification link
    
    is_locked: bool = Field(default=False)
    # Locked due to too many failed login attempts
    
    failed_login_attempts: int = Field(default=0)
    # Counter for security (lock after 5 attempts)
    
    locked_until: Optional[datetime] = None
    # Auto-unlock timestamp
    # Example: Lock for 30 minutes after 5 failed attempts
    
    # ==================== SECURITY ====================
    last_login_at: Optional[datetime] = None
    # Track last successful login
    # Used for: Security audits, inactive account cleanup
    
    last_login_ip: Optional[str] = None
    # IP address of last login
    # Security tracking
    
    password_changed_at: Optional[datetime] = None
    # Track password changes
    # Used for: Force password reset after X days
    
    mfa_enabled: bool = Field(default=False)
    # Multi-factor authentication enabled?
    # Future: OTP, Authenticator app
    
    mfa_secret: Optional[str] = None
    # TOTP secret for MFA
    # Encrypted storage recommended
    
    # ==================== SESSION MANAGEMENT ====================
    active_sessions: list[dict] = Field(default_factory=list)
    # Track active login sessions
    # Example: [{"token": "abc...", "device": "Chrome", "expires": "..."}]
    # Allows: Force logout from all devices
    
    # ==================== PASSWORD RESET ====================
    reset_token: Optional[str] = None
    # One-time token for password reset
    # Expires after use or 1 hour
    
    reset_token_expires: Optional[datetime] = None
    # Token expiration timestamp
    
    # ==================== PREFERENCES ====================
    preferred_language: str = Field(default="en")
    # UI language preference
    # Values: "en", "hi", "es", etc.
    
    timezone: str = Field(default="Asia/Kolkata")
    # User's timezone for datetime display
    # Example: "Asia/Kolkata", "America/New_York"
    
    theme: str = Field(default="light")
    # UI theme preference
    # Values: "light", "dark", "auto"
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PydanticObjectId] = None  # Admin who created account
    updated_by: Optional[PydanticObjectId] = None
    
    deleted_at: Optional[datetime] = None  # Soft delete
    is_deleted: bool = Field(default=False)
    
    # ==================== VALIDATORS ====================
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        """Lowercase and trim email"""
        return v.lower().strip()
    
    @field_validator("username")
    @classmethod
    def normalize_username(cls, v):
        """Lowercase and trim username"""
        if v:
            return v.lower().strip()
        return v
    
    class Settings:
        name = "users"
        
        indexes = [
            "email",  # Unique index for login
            "username",  # Unique if provided
            "employee_id",  # Quick employee lookup
            "is_active",  # Filter active users
            [("is_deleted", 1), ("is_active", 1)],  # Compound
        ]