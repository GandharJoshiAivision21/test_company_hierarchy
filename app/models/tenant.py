# from beanie import Document
# from pydantic import Field
# from datetime import datetime

# class Tenant(Document):
#     """Tenant metadata - stored in central metadata database"""
    
#     name: str = Field(..., max_length=200)
#     database_name: str = Field(..., max_length=100)  # e.g., "tenant_techcorp"
#     domain: str = Field(..., max_length=100)  # e.g., "techcorp.hrms.com"
#     subscription_plan: str = Field(default="basic")
#     status: str = Field(default="active")
    
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
    
#     class Settings:
#         name = "tenants"
#         indexes = ["database_name", "domain"]

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class Tenant(Document):
    """Tenant metadata - stored in central metadata database"""
    
    # Identifier for routing
    name: str = Field(..., max_length=200)
    tenant_id: str = Field(..., max_length=50, unique=True) # e.g., "techcorp"
    
    # Database Routing
    database_name: str = Field(..., max_length=100)  # e.g., "tenant_techcorp"
    domain: str = Field(..., max_length=100)  # e.g., "techcorp.hrms.com"
    
    # Management
    subscription_plan: str = Field(default="basic")
    status: str = Field(default="active")
    schema_version: int = Field(default=1) # Tracks DB migrations
    
    # Settings for Hierarchy behavior
    # Allows you to turn "Multi-root" on/off for specific clients
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "allow_multi_root": False,
        "timezone": "UTC"
    })
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "tenants"
        indexes = [
            "tenant_id",
            "database_name", 
            "domain",
            "status"
        ]