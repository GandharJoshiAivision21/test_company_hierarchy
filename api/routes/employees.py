# ============================================================
# FILE: api/routes/employees.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId

from app.models.employee import Employee
from app.models.user_access import UserAccess
from app.models.role import Role
from app.models.department import Department
from api.dependencies import get_current_user, get_current_employee

router = APIRouter()

async def check_permission(user_id: ObjectId, permission: str, resource_path: str) -> bool:
    """Check if user has permission for resource"""
    access_grants = await UserAccess.find(
        UserAccess.user_id == user_id,
        UserAccess.is_active == True
    ).to_list()
    
    for access in access_grants:
        role = await Role.get(access.role_id)
        if not role or not role.permissions.get(permission):
            continue
        
        # Check if resource is within scope
        if access.path_limit == "*":
            return True
        
        if resource_path.startswith(access.path_limit):
            return True
    
    return False

# @router.get("/", response_model=List[dict])
# async def list_employees(
#     current_user = Depends(get_current_user),
#     current_employee = Depends(get_current_employee)
# ):
#     """List employees based on user's access"""
    
#     # Get user's access grants
#     access_grants = await UserAccess.find(
#         UserAccess.user_id == current_user.id,
#         UserAccess.is_active == True
#     ).to_list()
    
#     # Check if user can view all employees
#     can_view_all = False
#     accessible_paths = []
    
#     for access in access_grants:
#         role = await Role.get(access.role_id)
#         if role and role.permissions.get("can_view_all_employees"):
#             can_view_all = True
        
#         if access.path_limit == "*":
#             can_view_all = True
#         else:
#             accessible_paths.append(access.path_limit)
    
#     # Build query
#     if can_view_all:
#         employees = await Employee.find(
#             Employee.employment_status == "active",
#             Employee.is_deleted == False
#         ).to_list()
#     elif accessible_paths:
#         # Find employees in accessible departments
#         employees = []
#         for path in accessible_paths:
#             dept_employees = await Employee.find(
#                 Employee.department_path == path,
#                 Employee.employment_status == "active",
#                 Employee.is_deleted == False
#             ).to_list()
#             employees.extend(dept_employees)
#     else:
#         # Can only see self
#         employees = [current_employee]
    
#     # Format response
#     result = []
#     for emp in employees:
#         # Get department name
#         dept_name = "N/A"
#         if emp.department_id:
#             dept = await Department.get(emp.department_id)
#             if dept:
#                 dept_name = dept.name
        
#         result.append({
#             "id": str(emp.id),
#             "employee_code": emp.employee_code,
#             "display_name": emp.display_name,
#             "work_email": emp.work_email,
#             "department": dept_name,
#             "department_path": emp.department_path,
#             "employment_status": emp.employment_status,
#             "joining_date": emp.joining_date.isoformat() if emp.joining_date else None
#         })
    
#     return result

# @router.get("/", response_model=List[dict])
# async def list_employees(
#     current_user = Depends(get_current_user),
#     current_employee = Depends(get_current_employee)
# ):
#     """List employees based on user's access"""

#     access_grants = await UserAccess.find(
#         UserAccess.user_id == current_user.id,
#         UserAccess.is_active == True
#     ).to_list()

#     can_view_all = False
#     accessible_paths = set()  # use set to avoid duplicates

#     for access in access_grants:
#         role = await Role.get(access.role_id)
#         if not role:
#             continue

#         # Role decides global access
#         if role.permissions.get("can_view_all_employees"):
#             can_view_all = True
#             break

#         # Otherwise, path-based access
#         if access.path_limit and access.path_limit != "*":
#             accessible_paths.add(access.path_limit)

#     # -----------------------
#     # Query logic
#     # -----------------------

#     if can_view_all:
#         employees = await Employee.find(
#             Employee.employment_status == "active",
#             Employee.is_deleted == False
#         ).to_list()

#     elif accessible_paths:
#         employees = []
#         for path in accessible_paths:
#             dept_employees = await Employee.find(
#                 Employee.department_path == path,
#                 Employee.employment_status == "active",
#                 Employee.is_deleted == False
#             ).to_list()
#             employees.extend(dept_employees)

#         # Deduplicate employees by ID
#         unique = {}
#         for emp in employees:
#             unique[str(emp.id)] = emp
#         employees = list(unique.values())

#     else:
#         # Only self
#         employees = [current_employee]

#     # -----------------------
#     # Format response
#     # -----------------------

#     result = []

#     for emp in employees:
#         dept_name = "N/A"
#         if emp.department_id:
#             dept = await Department.get(emp.department_id)
#             if dept:
#                 dept_name = dept.name

#         result.append({
#             "id": str(emp.id),
#             "employee_code": emp.employee_code,
#             "display_name": emp.display_name,
#             "work_email": emp.work_email,
#             "department": dept_name,
#             "department_path": emp.department_path,
#             "employment_status": emp.employment_status,
#             "joining_date": emp.joining_date.isoformat() if emp.joining_date else None
#         })

#     return result


@router.get("/", response_model=List[dict])
async def list_employees(
    current_user = Depends(get_current_user),
    current_employee = Depends(get_current_employee)
):
    """List employees based on user's access"""

    access_grants = await UserAccess.find(
        UserAccess.user_id == current_user.id,
        UserAccess.is_active == True
    ).to_list()

    if not access_grants:
        return [current_employee]

    can_view_all = False
    can_view_department = False
    can_view_own = False

    accessible_paths = []

    for access in access_grants:
        role = await Role.get(access.role_id)
        if not role:
            continue

        perms = role.permissions or {}

        if perms.get("can_view_all_employees"):
            can_view_all = True

        if perms.get("can_view_department_employees"):
            can_view_department = True

        if perms.get("can_view_own_data"):
            can_view_own = True

        if can_view_department:
            accessible_paths.append(access.path_limit)

    # ---- Enforce permission rules ----

    if can_view_all:
        employees = await Employee.find(
            Employee.employment_status == "active",
            Employee.is_deleted == False
        ).to_list()

    elif can_view_department and accessible_paths:
        employees = []
        for path in accessible_paths:
            dept_employees = await Employee.find(
                Employee.department_path.startswith(path),
                Employee.employment_status == "active",
                Employee.is_deleted == False
            ).to_list()
            employees.extend(dept_employees)

    elif can_view_own:
        employees = [current_employee]

    else:
        raise HTTPException(status_code=403, detail="Access denied")

    # ---- Format response ----

    result = []
    for emp in employees:
        dept_name = "N/A"
        if emp.department_id:
            dept = await Department.get(emp.department_id)
            if dept:
                dept_name = dept.name

        result.append({
            "id": str(emp.id),
            "employee_code": emp.employee_code,
            "display_name": emp.display_name,
            "work_email": emp.work_email,
            "department": dept_name,
            "department_path": emp.department_path,
            "employment_status": emp.employment_status,
            "joining_date": emp.joining_date.isoformat() if emp.joining_date else None
        })

    return result



@router.get("/reporting-to-me", response_model=List[dict])
async def get_my_reports(current_employee = Depends(get_current_employee)):
    """Get employees reporting to current user"""
    
    # Find employees where current employee is their manager
    reports = await Employee.find(
        Employee.employment_status == "active",
        Employee.is_deleted == False
    ).to_list()
    
    # Filter those who report to current user
    my_reports = []
    for emp in reports:
        for reporting_line in emp.reporting_lines:
            if reporting_line.manager_id == current_employee.id and reporting_line.is_primary:
                # Get department
                dept_name = "N/A"
                if emp.department_id:
                    dept = await Department.get(emp.department_id)
                    if dept:
                        dept_name = dept.name
                
                my_reports.append({
                    "id": str(emp.id),
                    "employee_code": emp.employee_code,
                    "display_name": emp.display_name,
                    "work_email": emp.work_email,
                    "department": dept_name,
                    "joining_date": emp.joining_date.isoformat() if emp.joining_date else None
                })
                break
    
    return my_reports

@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    current_user = Depends(get_current_user),
    current_employee = Depends(get_current_employee)
):
    """Get employee details"""
    
    # Get employee
    try:
        emp = await Employee.get(ObjectId(employee_id))
    except:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check permission
    can_view = await check_permission(
        current_user.id,
        "can_view_all_employees",
        emp.department_path or ""
    )
    
    # Can always view self
    if emp.id == current_employee.id:
        can_view = True
    
    if not can_view:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get department
    dept_name = "N/A"
    if emp.department_id:
        dept = await Department.get(emp.department_id)
        if dept:
            dept_name = dept.name
    
    return {
        "id": str(emp.id),
        "employee_code": emp.employee_code,
        "display_name": emp.display_name,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "work_email": emp.work_email,
        "mobile_number": emp.mobile_number,
        "department": dept_name,
        "department_path": emp.department_path,
        "employment_type": emp.employment_type,
        "employment_status": emp.employment_status,
        "joining_date": emp.joining_date.isoformat() if emp.joining_date else None
    }