from beanie import Document
from pydantic import Field
from datetime import datetime

class Tenant(Document):
    """Tenant metadata - stored in central metadata database"""
    
    name: str = Field(..., max_length=200)
    database_name: str = Field(..., max_length=100)  # e.g., "tenant_techcorp"
    domain: str = Field(..., max_length=100)  # e.g., "techcorp.hrms.com"
    subscription_plan: str = Field(default="basic")
    status: str = Field(default="active")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "tenants"
        indexes = ["database_name", "domain"]