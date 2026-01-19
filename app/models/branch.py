from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
# from bson import ObjectId # Not needed with Beanie's PydanticObjectId in Pydantic v2
from beanie import PydanticObjectId
from pydantic import field_validator
import re

class Branch(Document):
    """
    Branch/Location hierarchy model.
    Represents physical office locations and geographic presence.
    Supports unlimited depth using Materialized Path.
    Parallel to Department (organizational) hierarchy.
    """
    
    # ==================== CORE IDENTIFICATION ====================
    name: str = Field(..., min_length=1, max_length=200)
    # Branch/location name
    # Example: "Mumbai HQ", "Bangalore Tech Center", "Delhi Sales Office"
    
    code: str = Field(..., min_length=1, max_length=50)
    # Short code for identification
    # Example: "MUM-HQ", "BLR-TC", "DEL-SO"
    # Unique within company
    
    # ==================== COMPANY LINKAGE ====================
    company_id: PydanticObjectId = Field(...)
    # Which company this branch belongs to
    # Required - branches are company-specific
    # Links to Company._id
    
    # ==================== HIERARCHY ====================
    parent_branch_id: Optional[PydanticObjectId] = None
    # Reference to immediate parent branch
    # Null for top-level branches (Regional HQ, Country Office)
    # Example: "Mumbai - Andheri" parent is "Mumbai Region"
    
    materialized_path: Optional[str] = None
    # Full path from root: "001.002.003"
    # Null for root branches
    # Used for: Fast subtree queries, regional rollups
    
    depth: int = Field(default=0, ge=0)
    # Hierarchy depth (0=root, 1=child, 2=grandchild, etc.)
    # Regional HQ = 0
    # City Office = 1
    # Satellite Office = 2
    
    is_group: bool = Field(default=False)
    # Can have sub-branches (True) or is leaf location (False)
    # Controls UI: folder icon vs file icon
    # Example: "India Region" (True) vs "Pune Office" (False)
    
    root_id: Optional[PydanticObjectId] = None
    # Reference to top-most ancestor branch
    # Points to self if IS the root
    # Enables fast "all branches in region" queries
    
    # ==================== BRANCH TYPE ====================
    type: str = Field(default="office")
    # Branch classification
    # Values:
    #   "headquarters" - Main corporate office
    #   "regional_office" - Regional HQ
    #   "office" - Standard office
    #   "branch" - Smaller branch office
    #   "warehouse" - Storage/logistics
    #   "factory" - Manufacturing plant
    #   "store" - Retail location
    #   "remote" - Virtual/remote office
    
    category: Optional[str] = Field(None, max_length=50)
    # Additional categorization
    # Example: "production", "sales", "support", "r_and_d"
    
    description: Optional[str] = Field(None, max_length=1000)
    # What happens at this location
    # Example: "Primary software development center with 500+ engineers"
    
    # ==================== LOCATION DETAILS ====================
    address: dict = Field(default_factory=dict)
    # Physical address
    # {
    #     "line1": "Tech Park, Phase 2",
    #     "line2": "Whitefield Road",
    #     "city": "Bangalore",
    #     "state": "Karnataka",
    #     "country": "India",
    #     "postal_code": "560066",
    #     "landmark": "Near Metro Station"
    # }
    
    coordinates: Optional[dict] = None
    # GPS coordinates for mapping
    # {
    #     "latitude": 12.9716,
    #     "longitude": 77.5946
    # }
    
    timezone: str = Field(default="Asia/Kolkata")
    # Local timezone
    # Example: "Asia/Kolkata", "America/New_York", "Europe/London"
    # Used for: Attendance tracking, shift scheduling
    
    # ==================== CONTACT INFO ====================
    email: Optional[str] = Field(None, max_length=100)
    # Branch contact email
    # Example: "bangalore@company.com"
    
    phone: Optional[str] = Field(None, max_length=20)
    # Main reception/contact number
    
    fax: Optional[str] = Field(None, max_length=20)
    # Fax number (if still used)
    
    website: Optional[str] = Field(None, max_length=200)
    # Branch-specific website/page
    
    # ==================== LEADERSHIP ====================
    branch_manager_id: Optional[PydanticObjectId] = None
    # Person in charge of this location
    # Links to Employee._id
    # Example: "Site Manager", "Branch Head"
    
    admin_contact_id: Optional[PydanticObjectId] = None
    # Administrative contact person
    # Links to Employee._id
    # Example: Office manager, receptionist
    
    hr_contact_id: Optional[PydanticObjectId] = None
    # HR representative at this location
    # Links to Employee._id
    
    # ==================== FACILITIES & CAPACITY ====================
    total_area_sqft: Optional[float] = None
    # Total area in square feet
    # For: Space planning, cost allocation
    
    seating_capacity: Optional[int] = None
    # How many people can work here
    # For: Capacity planning, hot-desking
    
    current_occupancy: int = Field(default=0)
    # Current number of employees
    # Updated via trigger/scheduled job
    # Denormalized for performance
    
    parking_spaces: Optional[int] = None
    # Available parking spots
    
    facilities: List[str] = Field(default_factory=list)
    # Available amenities
    # Example: ["cafeteria", "gym", "daycare", "medical_room", "library"]
    
    # ==================== WORKING HOURS ====================
    working_hours: dict = Field(default_factory=dict)
    # Standard working hours for this location
    # {
    #     "monday": {"start": "09:00", "end": "18:00"},
    #     "tuesday": {"start": "09:00", "end": "18:00"},
    #     ...
    #     "saturday": null,  # Closed
    #     "sunday": null     # Closed
    # }
    
    is_24x7: bool = Field(default=False)
    # Is this location operational 24/7?
    # Example: Data centers, customer support centers
    
    # ==================== COMPLIANCE & LEGAL ====================
    registration_number: Optional[str] = Field(None, max_length=100)
    # Local business registration
    # Example: "GSTIN", "VAT Number", "Local business license"
    
    tax_jurisdiction: Optional[str] = Field(None, max_length=100)
    # Tax jurisdiction for this location
    # Example: "Maharashtra, India", "California, USA"
    
    labor_laws: Optional[str] = Field(None, max_length=100)
    # Applicable labor law jurisdiction
    # Different regions have different rules
    
    # ==================== FINANCIAL TRACKING ====================
    cost_center_code: Optional[str] = Field(None, max_length=50)
    # Accounting cost center
    # For: Expense allocation
    
    budget_code: Optional[str] = Field(None, max_length=50)
    # Budget tracking code
    
    currency: str = Field(default="INR")
    # Local currency
    # Example: "INR", "USD", "EUR"
    
    # ==================== OPERATIONAL STATUS ====================
    status: str = Field(default="active")
    # Operational status
    # Values: "active", "inactive", "under_construction", "closed", "planned"
    
    is_headquarters: bool = Field(default=False)
    # Is this the main HQ?
    # Only one branch per company should be True
    
    opened_date: Optional[datetime] = None
    # When branch started operations
    
    closed_date: Optional[datetime] = None
    # When branch ceased operations
    # Null if still active
    
    # ==================== SECURITY & ACCESS ====================
    access_control_system: Optional[str] = None
    # Type of access control
    # Example: "biometric", "card_based", "manual"
    
    security_level: Optional[str] = None
    # Security classification
    # Values: "low", "medium", "high", "critical"
    # Example: Data centers = "critical"
    
    requires_security_clearance: bool = Field(default=False)
    # Do employees need clearance to access?
    
    # ==================== IT INFRASTRUCTURE ====================
    it_infrastructure: dict = Field(default_factory=dict)
    # IT setup details
    # {
    #     "internet_provider": "Airtel",
    #     "bandwidth_mbps": 1000,
    #     "backup_power": True,
    #     "network_type": "fiber",
    #     "server_room": True
    # }
    
    # ==================== SETTINGS & POLICIES ====================
    settings: dict = Field(default_factory=dict)
    # Branch-specific settings
    # Example:
    # {
    #     "allow_visitors": True,
    #     "visitor_approval_required": True,
    #     "remote_work_allowed": False,
    #     "hot_desking": True
    # }
    
    policies: dict = Field(default_factory=dict)
    # Branch-specific policies
    # Example:
    # {
    #     "dress_code": "business_casual",
    #     "food_policy": "cafeteria_only",
    #     "smoking_allowed": False
    # }
    
    # ==================== TAGS & METADATA ====================
    tags: List[str] = Field(default_factory=list)
    # For filtering/grouping
    # Example: ["tech_hub", "customer_facing", "production", "tier_1_city"]
    
    custom_fields: dict = Field(default_factory=dict)
    # Tenant-specific additional fields
    
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
        allowed = ['headquarters', 'regional_office', 'office', 'branch', 
                   'warehouse', 'factory', 'store', 'remote']
        if v not in allowed:
            raise ValueError(f'type must be one of {allowed}')
        return v
    
    @field_validator("satus")
    @classmethod
    def validate_status(cls, v):
        allowed = ['active', 'inactive', 'under_construction', 'closed', 'planned']
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
    
    @field_validator("security_level")
    @classmethod
    def validate_security_level(cls, v):
        if v is not None:
            allowed = ['low', 'medium', 'high', 'critical']
            if v not in allowed:
                raise ValueError(f'security_level must be one of {allowed}')
        return v
    
    class Settings:
        name = "branches"
        
        indexes = [
            "company_id",  # Filter by company (CRITICAL)
            [("company_id", 1), ("code", 1)],  # Unique within company
            "parent_branch_id",  # Find children
            "materialized_path",  # Hierarchy queries
            "root_id",  # Tree queries
            "depth",  # Level queries
            "is_group",  # Filter groups vs leaves
            "type",  # Filter by type
            "branch_manager_id",  # Find branches by manager
            [("company_id", 1), ("status", 1), ("is_deleted", 1)],  # Active branches
            [("company_id", 1), ("materialized_path", 1)],  # Hierarchy within company
            "is_headquarters",  # Quick HQ lookup
            [("address.city", 1), ("address.state", 1)],  # Location queries
            "timezone",  # Timezone-based queries
        ]