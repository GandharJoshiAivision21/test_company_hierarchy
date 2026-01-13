from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.company import Company
from models.tenant import Tenant

MONGO_URL = "mongodb://localhost:27017"
METADATA_DB = "tenant_metadata"

client = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(MONGO_URL)
    print(f"✅ Connected to MongoDB")

async def init_tenant_db(tenant_db_name: str):
    """Initialize a tenant's database"""
    if not client:
        await connect_to_mongo()
    
    database = client[tenant_db_name]
    await init_beanie(database=database, document_models=[Company])
    print(f"✅ Initialized: {tenant_db_name}")
    return database

async def init_metadata_db():
    """Initialize metadata database"""
    if not client:
        await connect_to_mongo()
    
    database = client[METADATA_DB]
    await init_beanie(database=database, document_models=[Tenant])
    print(f"✅ Initialized metadata DB")
    return database