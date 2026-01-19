from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
from enum import Enum
from pydantic import BaseModel, EmailStr
from bson import ObjectId
import re



class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    RETIRED = "retired"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class ReportingLine(BaseModel):
    """Reporting structure"""
    manager_id: ObjectId
    # Which employee is the manager
    
    type: str
    # "DIRECT", "FUNCTIONAL", "PROJECT", "DOTTED_LINE", "MENTOR"
    
    is_primary: bool = False
    # Is this the main reporting line?
    # Only one should be primary
    
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    effective_to: Optional[datetime] = None
    # Reporting line validity period

class Employee(Document):
    """
    Employee master data.
    Contains all business and HR information about an employee.
    """
    
    # ==================== LINKING ====================
    user_id: Optional[ObjectId] = None
    # Link to User account (1:1 usually)
    # Null if: Employee hasn't been given system access yet
    
    # ==================== BASIC INFORMATION ====================
    employee_code: str = Field(..., unique=True, max_length=50)
    # Unique employee identifier
    # Example: "EMP001", "TC-2024-001"
    # Used in: Reports, payslips, ID cards
    
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    
    display_name: str = Field(..., max_length=200)
    # How name appears in UI
    # Example: "John Doe", "Dr. Jane Smith"
    
    preferred_name: Optional[str] = Field(None, max_length=100)
    # Nickname or preferred name
    # Example: "Johnny" instead of "Jonathan"
    
    # ==================== PERSONAL INFORMATION ====================
    date_of_birth: Optional[datetime] = None
    # For: Age calculation, birthday reminders
    
    gender: Optional[Gender] = None
    # For: Diversity reports
    
    marital_status: Optional[MaritalStatus] = None
    
    nationality: Optional[str] = Field(None, max_length=100)
    # Country of citizenship
    
    blood_group: Optional[str] = Field(None, max_length=10)
    # For: Emergency situations
    # Example: "A+", "O-"
    
    # ==================== CONTACT INFORMATION ====================
    personal_email: Optional[EmailStr] = None
    # Personal email (different from work email)
    
    work_email: EmailStr = Field(...)
    # Official company email
    # Unique
    
    mobile_number: str = Field(..., max_length=20)
    # Primary contact number
    
    alternate_mobile: Optional[str] = Field(None, max_length=20)
    # Secondary contact
    
    # ==================== ADDRESS ====================
    current_address: Optional[dict] = None
    # {
    #     "line1": "123 Main St",
    #     "line2": "Apt 4B",
    #     "city": "Mumbai",
    #     "state": "Maharashtra",
    #     "country": "India",
    #     "postal_code": "400001"
    # }
    
    permanent_address: Optional[dict] = None
    # Same structure as current_address
    
    is_address_same: bool = Field(default=False)
    # Is current address same as permanent?
    
    # ==================== EMERGENCY CONTACT ====================
    emergency_contacts: List[dict] = Field(default_factory=list)
    # [
    #     {
    #         "name": "Jane Doe",
    #         "relationship": "Spouse",
    #         "mobile": "+91-9876543210",
    #         "is_primary": True
    #     }
    # ]
    
    # ==================== ORGANIZATION PLACEMENT ====================
    company_id: ObjectId = Field(...)
    # Which company (required)
    # Links to Company._id
    
    department_id: Optional[ObjectId] = None
    # Which department
    # Links to Department._id
    
    department_path: Optional[str] = None
    # Materialized path for quick queries
    # Example: "001.002.003"
    # Denormalized from Department
    
    branch_id: Optional[ObjectId] = None
    # Which branch/location
    # Links to Branch._id
    
    branch_path: Optional[str] = None
    # Materialized path for branch
    # Example: "005.001"
    
    # ==================== JOB INFORMATION ====================
    job_title_id: Optional[ObjectId] = None
    # Links to JobTitle master
    # Example: "Software Engineer", "HR Manager"
    
    position_id: Optional[ObjectId] = None
    # Links to Position (specific seat/role)
    # Example: "Senior Backend Engineer - Payments Team"
    
    level: Optional[str] = Field(None, max_length=20)
    # Career level
    # Example: "L1", "L2", "L3", "L4"
    # Or: "Junior", "Mid", "Senior", "Principal"
    
    grade: Optional[str] = Field(None, max_length=20)
    # Salary grade
    # Example: "A", "B", "C"
    # Links to compensation structure
    
    # ==================== EMPLOYMENT DETAILS ====================
    employment_type: str = Field(default="full_time")
    # "full_time", "part_time", "contract", "intern", "consultant"
    
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.ACTIVE)
    
    joining_date: datetime = Field(...)
    # When employee started
    # Required
    
    confirmation_date: Optional[datetime] = None
    # When probation ended
    # Null if still in probation
    
    probation_period_months: int = Field(default=3)
    # Length of probation
    # Usually 3 or 6 months
    
    resignation_date: Optional[datetime] = None
    # Date resignation submitted
    
    last_working_date: Optional[datetime] = None
    # Final day at company
    # Exit date
    
    termination_date: Optional[datetime] = None
    # If terminated
    
    termination_reason: Optional[str] = Field(None, max_length=500)
    # Why terminated
    # For: Exit analysis
    
    # ==================== REPORTING STRUCTURE ====================
    reporting_lines: List[ReportingLine] = Field(default_factory=list)
    # Who this employee reports to
    # Can have multiple (matrix organization)
    # Example:
    # [
    #     {
    #         "manager_id": ObjectId("..."),
    #         "type": "DIRECT",
    #         "is_primary": True
    #     },
    #     {
    #         "manager_id": ObjectId("..."),
    #         "type": "FUNCTIONAL",
    #         "is_primary": False
    #     }
    # ]
    
    # ==================== COMPENSATION (SENSITIVE!) ====================
    salary: Optional[float] = None
    # Current base salary
    # HIGHLY SENSITIVE
    
    currency: str = Field(default="INR")
    # Salary currency
    # Example: "INR", "USD", "EUR"
    
    salary_effective_from: Optional[datetime] = None
    # When current salary became effective
    
    payment_frequency: str = Field(default="monthly")
    # "monthly", "bi_weekly", "weekly"
    
    bank_name: Optional[str] = Field(None, max_length=100)
    # For: Salary payment
    
    bank_account_number: Optional[str] = Field(None, max_length=50)
    # SENSITIVE - encrypt in production
    
    bank_ifsc_code: Optional[str] = Field(None, max_length=20)
    # India specific
    
    pan_number: Optional[str] = Field(None, max_length=20)
    # Tax ID (India)
    # SENSITIVE
    
    aadhaar_number: Optional[str] = Field(None, max_length=20)
    # National ID (India)
    # SENSITIVE - encrypt
    
    # ==================== WORK ARRANGEMENT ====================
    work_mode: str = Field(default="office")
    # "office", "remote", "hybrid"
    
    work_location: Optional[str] = Field(None, max_length=200)
    # If remote/hybrid, where do they work from?
    
    desk_number: Optional[str] = Field(None, max_length=50)
    # Physical desk location in office
    
    # ==================== DOCUMENTS ====================
    profile_photo_url: Optional[str] = None
    # URL to profile picture
    
    documents: List[dict] = Field(default_factory=list)
    # [
    #     {
    #         "type": "resume",
    #         "file_url": "https://...",
    #         "uploaded_at": "...",
    #         "verified": True
    #     },
    #     {
    #         "type": "offer_letter",
    #         "file_url": "https://...",
    #         "uploaded_at": "..."
    #     }
    # ]
    
    # ==================== SKILLS & CERTIFICATIONS ====================
    skills: List[str] = Field(default_factory=list)
    # ["Python", "React", "MongoDB", "Team Leadership"]
    
    certifications: List[dict] = Field(default_factory=list)
    # [
    #     {
    #         "name": "AWS Certified Solutions Architect",
    #         "issued_by": "Amazon",
    #         "issued_date": "2023-01-15",
    #         "expiry_date": "2026-01-15",
    #         "credential_id": "ABC123"
    #     }
    # ]
    
    # ==================== ATTENDANCE & LEAVE ====================
    work_schedule_id: Optional[ObjectId] = None
    # Links to WorkSchedule
    # Defines working hours, days
    
    shift_id: Optional[ObjectId] = None
    # Current shift (if shift-based work)
    
    annual_leave_balance: float = Field(default=0.0)
    # Current leave balance
    # In days
    
    # ==================== PERFORMANCE ====================
    last_appraisal_date: Optional[datetime] = None
    # Last performance review date
    
    next_appraisal_date: Optional[datetime] = None
    # Scheduled next review
    
    performance_rating: Optional[str] = None
    # Last rating: "Excellent", "Good", "Needs Improvement"
    
    # ==================== INTERNAL NOTES ====================
    notes: Optional[str] = Field(None, max_length=2000)
    # Internal HR notes
    # Not visible to employee
    
    tags: List[str] = Field(default_factory=list)
    # For: Filtering, grouping
    # Example: ["high_performer", "flight_risk", "key_talent"]
    
    # ==================== AUDIT ====================
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[ObjectId] = None
    updated_by: Optional[ObjectId] = None
    
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[ObjectId] = None
    
    # ==================== VALIDATORS ====================
    @validator('employee_code')
    def normalize_employee_code(cls, v):
        """Uppercase and trim"""
        return v.upper().strip()
    
    @validator('work_email')
    def normalize_work_email(cls, v):
        """Lowercase and trim"""
        return v.lower().strip()
    
    @validator('display_name', pre=True, always=True)
    def generate_display_name(cls, v, values):
        """Auto-generate if not provided"""
        if not v and 'first_name' in values and 'last_name' in values:
            return f"{values['first_name']} {values['last_name']}"
        return v
    
    class Settings:
        name = "employees"
        
        indexes = [
            "employee_code",  # Unique
            "work_email",  # Unique
            "user_id",  # Quick user lookup
            "company_id",  # Filter by company
            "department_id",
            "department_path",  # Hierarchy queries
            "branch_id",
            "branch_path",
            "employment_status",  # Filter active employees
            [("company_id", 1), ("employment_status", 1)],  # Active in company
            [("is_deleted", 1), ("employment_status", 1)],  # Active, non-deleted
            "joining_date",  # Seniority queries
            "last_name",  # Name search
            # For reporting queries:
            [("department_path", 1), ("employment_status", 1)],
            [("branch_path", 1), ("employment_status", 1)],
        ]