# # ============================================================
# # FILE: seed_data.py
# # ============================================================
# """
# Seed database with demo data
# Run: python seed_data.py
# """
# import asyncio
# from datetime import datetime
# from bson import ObjectId
# import bcrypt

# from config.database import Database
# from app.models.tenant import Tenant
# from app.models.company import Company
# from app.models.department import Department
# from app.models.branch import Branch
# from app.models.employee import Employee
# from app.models.user import User
# from app.models.role import Role
# from app.models.user_access import UserAccess

# async def hash_password(password: str) -> str:
#     """Hash password"""
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# async def seed_all():
#     """Seed complete demo data"""
    
#     print("🌱 Starting database seeding...")
    
#     # Connect to database
#     await Database.connect_db()
    
#     # ===== 1. CREATE TENANT =====
#     print("\n📦 Creating Tenant...")
#     tenant = Tenant(
#         name="TechCorp",
#         tenant_id="techcorp",
#         database_name="tenant_techcorp",
#         domain="techcorp.hrms.local",
#         subscription_plan="enterprise",
#         status="active",
#         settings={
#             "allow_multi_root": False,
#             "timezone": "Asia/Kolkata"
#         }
#     )
#     await tenant.insert()
#     print(f"✅ Tenant created: {tenant.name}")
    
#     # Initialize tenant database
#     await Database.init_tenant_db(tenant.database_name)
    
#     # ===== 2. CREATE COMPANY =====
#     print("\n🏢 Creating Company...")
#     company = Company(
#         name="TechCorp India",
#         code="TECH-IND",
#         type="holding_group",
#         status="active",
#         materialized_path=None,  # Root company
#         depth=0,
#         is_group=True,
#         root_id=None,  # Will set to self after insert
#         currency="INR",
#         timezone="Asia/Kolkata"
#     )
#     await company.insert()
#     company.root_id = company.id
#     await company.save()
#     print(f"✅ Company created: {company.name} (Path: {company.id})")
    
#     # ===== 3. CREATE DEPARTMENTS =====
#     print("\n📁 Creating Departments...")
    
#     # Engineering Department
#     dept_eng = Department(
#         name="Engineering",
#         code="ENG",
#         company_id=company.id,
#         materialized_path="001",
#         depth=0,
#         is_group=True,
#         root_id=None,  # Will set to self
#         type="functional",
#         status="active",
#         parent_department_id=None
#     )
#     await dept_eng.insert()
#     dept_eng.root_id = dept_eng.id
#     await dept_eng.save()
#     print(f"  ✅ Engineering (Path: 001)")
    
#     # Sales Department
#     dept_sales = Department(
#         name="Sales",
#         code="SALES",
#         company_id=company.id,
#         materialized_path="002",
#         depth=0,
#         is_group=False,
#         root_id=None,
#         type="functional",
#         status="active",
#         parent_department_id=None
#     )
#     await dept_sales.insert()
#     dept_sales.root_id = dept_sales.id
#     await dept_sales.save()
#     print(f"  ✅ Sales (Path: 002)")
    
#     # ===== 4. CREATE BRANCH =====
#     print("\n🏪 Creating Branch...")
#     branch = Branch(
#         name="Mumbai HQ",
#         code="MUM-HQ",
#         company_id=company.id,
#         materialized_path="001",
#         depth=0,
#         is_group=False,
#         root_id=None,
#         type="headquarters",
#         status="active",
#         is_headquarters=True,
#         address={
#             "line1": "Tech Park, Andheri East",
#             "city": "Mumbai",
#             "state": "Maharashtra",
#             "country": "India",
#             "postal_code": "400069"
#         },
#         timezone="Asia/Kolkata"
#     )
#     await branch.insert()
#     branch.root_id = branch.id
#     await branch.save()
#     print(f"✅ Branch created: {branch.name}")
    
#     # ===== 5. CREATE ROLES =====
#     print("\n👔 Creating Roles...")
    
#     role_super_admin = Role(
#         name="SUPER_ADMIN",
#         code="SUPER_ADMIN",
#         display_name="Super Administrator",
#         level=5,
#         is_system_role=True,
#         permissions={
#             "can_manage_company": True,
#             "can_manage_departments": True,
#             "can_manage_branches": True,
#             "can_create_employee": True,
#             "can_edit_employee": True,
#             "can_terminate_employee": True,
#             "can_view_all_employees": True,
#             "can_view_salary": True,
#             "can_edit_salary": True,
#             "can_approve_leave": True,
#             "can_view_reports": True,
#             "can_manage_roles": True,
#         }
#     )
#     await role_super_admin.insert()
#     print(f"  ✅ {role_super_admin.display_name}")
    
#     role_dept_manager = Role(
#         name="DEPT_MANAGER",
#         code="DEPT_MGR",
#         display_name="Department Manager",
#         level=2,
#         is_system_role=True,
#         permissions={
#             "can_create_employee": True,
#             "can_edit_employee": True,
#             "can_view_all_employees": False,
#             "can_approve_leave": True,
#             "can_view_reports": True,
#         }
#     )
#     await role_dept_manager.insert()
#     print(f"  ✅ {role_dept_manager.display_name}")
    
#     role_employee = Role(
#         name="EMPLOYEE",
#         code="EMP",
#         display_name="Employee",
#         level=0,
#         is_system_role=True,
#         permissions={
#             "can_view_own_data": True,
#         }
#     )
#     await role_employee.insert()
#     print(f"  ✅ {role_employee.display_name}")
    
#     # ===== 6. CREATE EMPLOYEES & USERS =====
#     print("\n👥 Creating Employees & Users...")
    
#     # John - Super Admin
#     emp_john = Employee(
#         employee_code="EMP001",
#         first_name="John",
#         last_name="Doe",
#         display_name="John Doe",
#         work_email="john@techcorp.com",
#         mobile_number="+91-9876543210",
#         company_id=company.id,
#         department_id=dept_eng.id,
#         department_path="001",
#         branch_id=branch.id,
#         branch_path="001",
#         job_title_id=None,
#         employment_type="full_time",
#         employment_status="active",
#         joining_date=datetime(2020, 1, 1)
#     )
#     await emp_john.insert()
    
#     user_john = User(
#         email="john@techcorp.com",
#         password_hash=await hash_password("password123"),
#         full_name="John Doe",
#         employee_id=emp_john.id,
#         is_active=True,
#         is_verified=True
#     )
#     await user_john.insert()
#     emp_john.user_id = user_john.id
#     await emp_john.save()
    
#     # Grant Super Admin access
#     access_john = UserAccess(
#         user_id=user_john.id,
#         role_id=role_super_admin.id,
#         scope_type="COMPANY",
#         path_limit="*",  # Entire company
#         is_active=True
#     )
#     await access_john.insert()
#     print(f"  ✅ John Doe (Super Admin)")
    
#     # Alice - Engineering Manager
#     emp_alice = Employee(
#         employee_code="EMP002",
#         first_name="Alice",
#         last_name="Smith",
#         display_name="Alice Smith",
#         work_email="alice@techcorp.com",
#         mobile_number="+91-9876543211",
#         company_id=company.id,
#         department_id=dept_eng.id,
#         department_path="001",
#         branch_id=branch.id,
#         branch_path="001",
#         employment_type="full_time",
#         employment_status="active",
#         joining_date=datetime(2021, 3, 15)
#     )
#     await emp_alice.insert()
    
#     user_alice = User(
#         email="alice@techcorp.com",
#         password_hash=await hash_password("password123"),
#         full_name="Alice Smith",
#         employee_id=emp_alice.id,
#         is_active=True,
#         is_verified=True
#     )
#     await user_alice.insert()
#     emp_alice.user_id = user_alice.id
#     await emp_alice.save()
    
#     # Grant Engineering Manager access
#     access_alice = UserAccess(
#         user_id=user_alice.id,
#         role_id=role_dept_manager.id,
#         scope_type="DEPARTMENT",
#         path_limit="001",  # Engineering only
#         is_active=True
#     )
#     await access_alice.insert()
#     print(f"  ✅ Alice Smith (Engineering Manager)")
    
#     # Bob - Multi-role (Engineering + Sales)
#     emp_bob = Employee(
#         employee_code="EMP003",
#         first_name="Bob",
#         last_name="Johnson",
#         display_name="Bob Johnson",
#         work_email="bob@techcorp.com",
#         mobile_number="+91-9876543212",
#         company_id=company.id,
#         department_id=dept_sales.id,
#         department_path="002",
#         branch_id=branch.id,
#         branch_path="001",
#         employment_type="full_time",
#         employment_status="active",
#         joining_date=datetime(2021, 6, 1)
#     )
#     await emp_bob.insert()
    
#     user_bob = User(
#         email="bob@techcorp.com",
#         password_hash=await hash_password("password123"),
#         full_name="Bob Johnson",
#         employee_id=emp_bob.id,
#         is_active=True,
#         is_verified=True
#     )
#     await user_bob.insert()
#     emp_bob.user_id = user_bob.id
#     await emp_bob.save()
    
#     # Grant multi-role access
#     access_bob_eng = UserAccess(
#         user_id=user_bob.id,
#         role_id=role_dept_manager.id,
#         scope_type="DEPARTMENT",
#         path_limit="001",  # Engineering
#         is_active=True
#     )
#     await access_bob_eng.insert()
    
#     access_bob_sales = UserAccess(
#         user_id=user_bob.id,
#         role_id=role_dept_manager.id,
#         scope_type="DEPARTMENT",
#         path_limit="002",  # Sales
#         is_active=True
#     )
#     await access_bob_sales.insert()
#     print(f"  ✅ Bob Johnson (Multi-role Manager)")
    
#     # Charlie - Regular Employee (reports to Alice)
#     emp_charlie = Employee(
#         employee_code="EMP004",
#         first_name="Charlie",
#         last_name="Brown",
#         display_name="Charlie Brown",
#         work_email="charlie@techcorp.com",
#         mobile_number="+91-9876543213",
#         company_id=company.id,
#         department_id=dept_eng.id,
#         department_path="001",
#         branch_id=branch.id,
#         branch_path="001",
#         employment_type="full_time",
#         employment_status="active",
#         joining_date=datetime(2022, 1, 10),
#         reporting_lines=[{
#             "manager_id": emp_alice.id,
#             "type": "DIRECT",
#             "is_primary": True,
#             "effective_from": datetime(2022, 1, 10)
#         }]
#     )
#     await emp_charlie.insert()
    
#     user_charlie = User(
#         email="charlie@techcorp.com",
#         password_hash=await hash_password("password123"),
#         full_name="Charlie Brown",
#         employee_id=emp_charlie.id,
#         is_active=True,
#         is_verified=True
#     )
#     await user_charlie.insert()
#     emp_charlie.user_id = user_charlie.id
#     await emp_charlie.save()
    
#     # Grant basic employee access
#     access_charlie = UserAccess(
#         user_id=user_charlie.id,
#         role_id=role_employee.id,
#         scope_type="DEPARTMENT",
#         path_limit="001",
#         is_active=True
#     )
#     await access_charlie.insert()
#     print(f"  ✅ Charlie Brown (Employee, reports to Alice)")
    
#     print("\n" + "="*60)
#     print("✅ SEEDING COMPLETE!")
#     print("="*60)
#     print("\n📊 Summary:")
#     print(f"  • 1 Tenant: {tenant.name}")
#     print(f"  • 1 Company: {company.name}")
#     print(f"  • 2 Departments: Engineering, Sales")
#     print(f"  • 1 Branch: Mumbai HQ")
#     print(f"  • 3 Roles: Super Admin, Dept Manager, Employee")
#     print(f"  • 4 Users:")
#     print(f"      - john@techcorp.com (password123) - Super Admin")
#     print(f"      - alice@techcorp.com (password123) - Engineering Manager")
#     print(f"      - bob@techcorp.com (password123) - Multi-role Manager")
#     print(f"      - charlie@techcorp.com (password123) - Employee")
#     print("\n🚀 Ready to test APIs!")
    
#     await Database.close_db()

# if __name__ == "__main__":
#     asyncio.run(seed_all())


# ============================================================
# FILE: seed_data.py
# ============================================================
"""
Seed database with demo data
Run: python seed_data.py
"""
import asyncio
from datetime import datetime
from bson import ObjectId
import bcrypt

from config.database import Database
from app.models.tenant import Tenant
from app.models.company import Company
from app.models.department import Department
from app.models.branch import Branch
from app.models.employee import Employee
from app.models.user import User
from app.models.role import Role
from app.models.user_access import UserAccess

async def hash_password(password: str) -> str:
    """Hash password"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def seed_all():
    """Seed complete demo data"""
    
    print("🌱 Starting database seeding...")
    
    # Connect to database
    await Database.connect_db()
    
    # ===== 1. CREATE TENANT =====
    print("\n📦 Creating Tenant...")
    tenant = Tenant(
        name="TechCorp",
        tenant_id="techcorp",
        database_name="tenant_techcorp",
        domain="techcorp.hrms.local",
        subscription_plan="enterprise",
        status="active",
        settings={
            "allow_multi_root": False,
            "timezone": "Asia/Kolkata"
        }
    )
    await tenant.insert()
    print(f"✅ Tenant created: {tenant.name}")
    
    # Initialize tenant database
    await Database.init_tenant_db(tenant.database_name)
    
    # ===== 2. CREATE COMPANIES (Multi-level Hierarchy) =====
    print("\n🏢 Creating Company Hierarchy...")
    
    # Root Company (Level 0)
    company_root = Company(
        name="TechCorp Global Holdings",
        code="TECH-GLOBAL",
        type="holding_group",
        status="active",
        materialized_path=None,  # Root company
        depth=0,
        is_group=True,
        root_id=None,  # Will set to self after insert
        currency="USD",
        timezone="America/New_York"
    )
    await company_root.insert()
    company_root.root_id = company_root.id
    await company_root.save()
    print(f"✅ Level 0 (Root): {company_root.name} (ID: {company_root.id})")
    
    # Level 1 Companies (Regional)
    company_india = Company(
        name="TechCorp India",
        code="TECH-IND",
        type="parent",
        status="active",
        parent_company_id=company_root.id,
        materialized_path="001",
        depth=1,
        is_group=True,
        root_id=company_root.id,
        currency="INR",
        timezone="Asia/Kolkata"
    )
    await company_india.insert()
    print(f"  ✅ Level 1: {company_india.name} (Path: 001)")
    
    company_usa = Company(
        name="TechCorp USA",
        code="TECH-USA",
        type="parent",
        status="active",
        parent_company_id=company_root.id,
        materialized_path="002",
        depth=1,
        is_group=True,
        root_id=company_root.id,
        currency="USD",
        timezone="America/Los_Angeles"
    )
    await company_usa.insert()
    print(f"  ✅ Level 1: {company_usa.name} (Path: 002)")
    
    # Level 2 Companies (Subsidiaries under India)
    company_ind_services = Company(
        name="TechCorp India Services Pvt Ltd",
        code="TECH-IND-SVC",
        type="subsidiary",
        status="active",
        parent_company_id=company_india.id,
        materialized_path="001.001",
        depth=2,
        is_group=False,
        root_id=company_root.id,
        currency="INR",
        timezone="Asia/Kolkata"
    )
    await company_ind_services.insert()
    print(f"    ✅ Level 2: {company_ind_services.name} (Path: 001.001)")
    
    company_ind_products = Company(
        name="TechCorp India Products Pvt Ltd",
        code="TECH-IND-PRD",
        type="subsidiary",
        status="active",
        parent_company_id=company_india.id,
        materialized_path="001.002",
        depth=2,
        is_group=False,
        root_id=company_root.id,
        currency="INR",
        timezone="Asia/Kolkata"
    )
    await company_ind_products.insert()
    print(f"    ✅ Level 2: {company_ind_products.name} (Path: 001.002)")
    
    # Level 2 Companies (Subsidiaries under USA)
    company_usa_west = Company(
        name="TechCorp West Coast LLC",
        code="TECH-USA-WC",
        type="subsidiary",
        status="active",
        parent_company_id=company_usa.id,
        materialized_path="002.001",
        depth=2,
        is_group=False,
        root_id=company_root.id,
        currency="USD",
        timezone="America/Los_Angeles"
    )
    await company_usa_west.insert()
    print(f"    ✅ Level 2: {company_usa_west.name} (Path: 002.001)")
    
    print(f"\n📊 Company Hierarchy:")
    print(f"  TechCorp Global Holdings (Root)")
    print(f"  ├── TechCorp India (001)")
    print(f"  │   ├── TechCorp India Services (001.001)")
    print(f"  │   └── TechCorp India Products (001.002)")
    print(f"  └── TechCorp USA (002)")
    print(f"      └── TechCorp West Coast (002.001)")
    
    # Use India Services as the main company for employees
    company = company_ind_services
    
    # ===== 3. CREATE DEPARTMENTS =====
    print("\n📁 Creating Departments...")
    
    # Engineering Department
    dept_eng = Department(
        name="Engineering",
        code="ENG",
        company_id=company.id,
        materialized_path="001",
        depth=0,
        is_group=True,
        root_id=None,  # Will set to self
        type="functional",
        status="active",
        parent_department_id=None
    )
    await dept_eng.insert()
    dept_eng.root_id = dept_eng.id
    await dept_eng.save()
    print(f"  ✅ Engineering (Path: 001)")
    
    # Sales Department
    dept_sales = Department(
        name="Sales",
        code="SALES",
        company_id=company.id,
        materialized_path="002",
        depth=0,
        is_group=False,
        root_id=None,
        type="functional",
        status="active",
        parent_department_id=None
    )
    await dept_sales.insert()
    dept_sales.root_id = dept_sales.id
    await dept_sales.save()
    print(f"  ✅ Sales (Path: 002)")
    
    # ===== 4. CREATE BRANCH =====
    print("\n🏪 Creating Branch...")
    branch = Branch(
        name="Mumbai HQ",
        code="MUM-HQ",
        company_id=company.id,
        materialized_path="001",
        depth=0,
        is_group=False,
        root_id=None,
        type="headquarters",
        status="active",
        is_headquarters=True,
        address={
            "line1": "Tech Park, Andheri East",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "postal_code": "400069"
        },
        timezone="Asia/Kolkata"
    )
    await branch.insert()
    branch.root_id = branch.id
    await branch.save()
    print(f"✅ Branch created: {branch.name}")
    
    # ===== 5. CREATE ROLES =====
    print("\n👔 Creating Roles...")
    
    role_super_admin = Role(
        name="SUPER_ADMIN",
        code="SUPER_ADMIN",
        display_name="Super Administrator",
        level=5,
        is_system_role=True,
        permissions={
            "can_manage_company": True,
            "can_manage_departments": True,
            "can_manage_branches": True,
            "can_create_employee": True,
            "can_edit_employee": True,
            "can_terminate_employee": True,
            "can_view_all_employees": True,
            "can_view_salary": True,
            "can_edit_salary": True,
            "can_approve_leave": True,
            "can_view_reports": True,
            "can_manage_roles": True,
        }
    )
    await role_super_admin.insert()
    print(f"  ✅ {role_super_admin.display_name}")
    
    role_dept_manager = Role(
        name="DEPT_MANAGER",
        code="DEPT_MGR",
        display_name="Department Manager",
        level=2,
        is_system_role=True,
        permissions={
            "can_create_employee": True,
            "can_edit_employee": True,
            "can_view_all_employees": False,
            "can_approve_leave": True,
            "can_view_reports": True,
        }
    )
    await role_dept_manager.insert()
    print(f"  ✅ {role_dept_manager.display_name}")
    
    role_employee = Role(
        name="EMPLOYEE",
        code="EMP",
        display_name="Employee",
        level=0,
        is_system_role=True,
        permissions={
            "can_view_own_data": True,
        }
    )
    await role_employee.insert()
    print(f"  ✅ {role_employee.display_name}")
    
    # ===== 6. CREATE EMPLOYEES & USERS =====
    print("\n👥 Creating Employees & Users...")
    
    # John - Super Admin
    emp_john = Employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        display_name="John Doe",
        work_email="john@techcorp.com",
        mobile_number="+91-9876543210",
        company_id=company.id,
        department_id=dept_eng.id,
        department_path="001",
        branch_id=branch.id,
        branch_path="001",
        job_title_id=None,
        employment_type="full_time",
        employment_status="active",
        joining_date=datetime(2020, 1, 1)
    )
    await emp_john.insert()
    
    user_john = User(
        email="john@techcorp.com",
        password_hash=await hash_password("password123"),
        full_name="John Doe",
        employee_id=emp_john.id,
        is_active=True,
        is_verified=True
    )
    await user_john.insert()
    emp_john.user_id = user_john.id
    await emp_john.save()
    
    # Grant Super Admin access
    access_john = UserAccess(
        user_id=user_john.id,
        role_id=role_super_admin.id,
        scope_type="COMPANY",
        path_limit="*",  # Entire company
        is_active=True
    )
    await access_john.insert()
    print(f"  ✅ John Doe (Super Admin)")
    
    # Alice - Engineering Manager
    emp_alice = Employee(
        employee_code="EMP002",
        first_name="Alice",
        last_name="Smith",
        display_name="Alice Smith",
        work_email="alice@techcorp.com",
        mobile_number="+91-9876543211",
        company_id=company.id,
        department_id=dept_eng.id,
        department_path="001",
        branch_id=branch.id,
        branch_path="001",
        employment_type="full_time",
        employment_status="active",
        joining_date=datetime(2021, 3, 15)
    )
    await emp_alice.insert()
    
    user_alice = User(
        email="alice@techcorp.com",
        password_hash=await hash_password("password123"),
        full_name="Alice Smith",
        employee_id=emp_alice.id,
        is_active=True,
        is_verified=True
    )
    await user_alice.insert()
    emp_alice.user_id = user_alice.id
    await emp_alice.save()
    
    # Grant Engineering Manager access
    access_alice = UserAccess(
        user_id=user_alice.id,
        role_id=role_dept_manager.id,
        scope_type="DEPARTMENT",
        path_limit="001",  # Engineering only
        is_active=True
    )
    await access_alice.insert()
    print(f"  ✅ Alice Smith (Engineering Manager)")
    
    # Bob - Multi-role (Engineering + Sales)
    emp_bob = Employee(
        employee_code="EMP003",
        first_name="Bob",
        last_name="Johnson",
        display_name="Bob Johnson",
        work_email="bob@techcorp.com",
        mobile_number="+91-9876543212",
        company_id=company.id,
        department_id=dept_sales.id,
        department_path="002",
        branch_id=branch.id,
        branch_path="001",
        employment_type="full_time",
        employment_status="active",
        joining_date=datetime(2021, 6, 1)
    )
    await emp_bob.insert()
    
    user_bob = User(
        email="bob@techcorp.com",
        password_hash=await hash_password("password123"),
        full_name="Bob Johnson",
        employee_id=emp_bob.id,
        is_active=True,
        is_verified=True
    )
    await user_bob.insert()
    emp_bob.user_id = user_bob.id
    await emp_bob.save()
    
    # Grant multi-role access
    access_bob_eng = UserAccess(
        user_id=user_bob.id,
        role_id=role_dept_manager.id,
        scope_type="DEPARTMENT",
        path_limit="001",  # Engineering
        is_active=True
    )
    await access_bob_eng.insert()
    
    access_bob_sales = UserAccess(
        user_id=user_bob.id,
        role_id=role_dept_manager.id,
        scope_type="DEPARTMENT",
        path_limit="002",  # Sales
        is_active=True
    )
    await access_bob_sales.insert()
    print(f"  ✅ Bob Johnson (Multi-role Manager)")
    
    # Charlie - Regular Employee (reports to Alice)
    emp_charlie = Employee(
        employee_code="EMP004",
        first_name="Charlie",
        last_name="Brown",
        display_name="Charlie Brown",
        work_email="charlie@techcorp.com",
        mobile_number="+91-9876543213",
        company_id=company.id,
        department_id=dept_eng.id,
        department_path="001",
        branch_id=branch.id,
        branch_path="001",
        employment_type="full_time",
        employment_status="active",
        joining_date=datetime(2022, 1, 10),
        reporting_lines=[{
            "manager_id": emp_alice.id,
            "type": "DIRECT",
            "is_primary": True,
            "effective_from": datetime(2022, 1, 10)
        }]
    )
    await emp_charlie.insert()
    
    user_charlie = User(
        email="charlie@techcorp.com",
        password_hash=await hash_password("password123"),
        full_name="Charlie Brown",
        employee_id=emp_charlie.id,
        is_active=True,
        is_verified=True
    )
    await user_charlie.insert()
    emp_charlie.user_id = user_charlie.id
    await emp_charlie.save()
    
    # Grant basic employee access
    access_charlie = UserAccess(
        user_id=user_charlie.id,
        role_id=role_employee.id,
        scope_type="DEPARTMENT",
        path_limit="001",
        is_active=True
    )
    await access_charlie.insert()
    print(f"  ✅ Charlie Brown (Employee, reports to Alice)")
    
    print("\n" + "="*60)
    print("✅ SEEDING COMPLETE!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"  • 1 Tenant: {tenant.name}")
    print(f"  • 6 Companies:")
    print(f"      - TechCorp Global Holdings (Root)")
    print(f"      - TechCorp India (001)")
    print(f"      - TechCorp India Services (001.001)")
    print(f"      - TechCorp India Products (001.002)")
    print(f"      - TechCorp USA (002)")
    print(f"      - TechCorp West Coast (002.001)")
    print(f"  • 2 Departments: Engineering, Sales")
    print(f"  • 1 Branch: Mumbai HQ")
    print(f"  • 3 Roles: Super Admin, Dept Manager, Employee")
    print(f"  • 4 Users:")
    print(f"      - john@techcorp.com (password123) - Super Admin")
    print(f"      - alice@techcorp.com (password123) - Engineering Manager")
    print(f"      - bob@techcorp.com (password123) - Multi-role Manager")
    print(f"      - charlie@techcorp.com (password123) - Employee")
    print("\n🚀 Ready to test APIs!")
    
    await Database.close_db()

if __name__ == "__main__":
    asyncio.run(seed_all())