# ============================================================
# FILE: api/routes/auth.py
# ============================================================
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import bcrypt

from app.models.user import User
from app.models.employee import Employee
from app.models.user_access import UserAccess
from app.models.role import Role
from api.dependencies import create_access_token, get_current_user, get_current_employee

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    # Find user
    user = await User.find_one(User.email == request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Get employee info if exists
    employee = None
    if user.employee_id:
        employee = await Employee.get(user.employee_id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "employee_code": employee.employee_code if employee else None
        }
    }

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    current_employee: Employee = Depends(get_current_employee)
):
    """Get current user info with permissions"""
    
    # Get all access grants
    access_grants = await UserAccess.find(
        UserAccess.user_id == current_user.id,
        UserAccess.is_active == True
    ).to_list()
    
    # Get roles
    roles_info = []
    all_permissions = {}
    
    for access in access_grants:
        role = await Role.get(access.role_id)
        if role:
            roles_info.append({
                "role": role.display_name,
                "scope_type": access.scope_type,
                "path_limit": access.path_limit
            })
            
            # Merge permissions
            for perm, value in role.permissions.items():
                if perm not in all_permissions:
                    all_permissions[perm] = value
                else:
                    all_permissions[perm] = all_permissions[perm] or value
    
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name
        },
        "employee": {
            "id": str(current_employee.id),
            "employee_code": current_employee.employee_code,
            "display_name": current_employee.display_name,
            "department_path": current_employee.department_path,
            "branch_path": current_employee.branch_path
        },
        "roles": roles_info,
        "permissions": all_permissions
    }
