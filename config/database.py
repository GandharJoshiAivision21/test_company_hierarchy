# from motor.motor_asyncio import AsyncIOMotorClient
# from beanie import init_beanie
# from models.company import Company
# from models.tenant import Tenant

# MONGO_URL = "mongodb://localhost:27017"
# METADATA_DB = "tenant_metadata"

# client = None

# async def connect_to_mongo():
#     global client
#     client = AsyncIOMotorClient(MONGO_URL)
#     print(f"✅ Connected to MongoDB")

# async def init_tenant_db(tenant_db_name: str):
#     """Initialize a tenant's database"""
#     if not client:
#         await connect_to_mongo()
    
#     database = client[tenant_db_name]
#     await init_beanie(database=database, document_models=[Company])
#     print(f"✅ Initialized: {tenant_db_name}")
#     return database

# async def init_metadata_db():
#     """Initialize metadata database"""
#     if not client:
#         await connect_to_mongo()
    
#     database = client[METADATA_DB]
#     await init_beanie(database=database, document_models=[Tenant])
#     print(f"✅ Initialized metadata DB")
#     return database


# ============================================================
# FILE: config/database.py
# ============================================================
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
import os

# Import all your models
from app.models.tenant import Tenant
from app.models.company import Company
from app.models.department import Department
from app.models.branch import Branch
from app.models.employee import Employee
from app.models.user import User
from app.models.role import Role
from app.models.user_access import UserAccess

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
METADATA_DB = "hrms_metadata"

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        
        # Initialize metadata database (for tenants)
        await init_beanie(
            database=cls.client[METADATA_DB],
            document_models=[Tenant]
        )
        
        print(f"✅ Connected to MongoDB: {MONGODB_URL}")
    
    @classmethod
    async def init_tenant_db(cls, database_name: str):
        """Initialize a specific tenant database"""
        await init_beanie(
            database=cls.client[database_name],
            document_models=[
                Company,
                Department,
                Branch,
                Employee,
                User,
                Role,
                UserAccess
            ]
        )
        print(f"✅ Initialized tenant database: {database_name}")
    
    @classmethod
    async def close_db(cls):
        """Close database connection"""
        cls.client.close()
        print("✅ Database connection closed")

