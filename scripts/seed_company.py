import asyncio
from datetime import datetime
from config.database import connect_to_mongo, init_tenant_db, init_metadata_db

from models.company import Company
from models.tenant import Tenant

async def create_test_tenant():
    """Create a test tenant in metadata database"""
    await init_metadata_db()
    
    tenant = Tenant(
        name="TechCorp",
        database_name="tenant_techcorp",
        domain="techcorp.hrms.com",
        subscription_plan="premium",
        status="active"
    )
    await tenant.insert()
    print(f"✅ Created tenant: {tenant.name} -> {tenant.database_name}")
    return tenant

async def seed_companies(tenant_db_name: str):
    """Create test companies in tenant database"""
    await init_tenant_db(tenant_db_name)
    
    # 1. Create Holding Group (Level 0)
    holding = Company(
        name="TechCorp Holdings",
        code="TECH-HOLD",
        parent_company_id=None,
        fallback_parent_company_id=None,
        materialized_path=None,
        depth=0,
        type="holding_group",
        status="active",
        effective_from=datetime(2020, 1, 1)
    )
    await holding.insert()
    print(f"✅ Created: {holding.name} (ID: {holding.id})")
    
    # 2. Create Parent Company (Level 1)
    parent = Company(
        name="TechCorp Global",
        code="TECH-GLB",
        parent_company_id=holding.id,
        fallback_parent_company_id=None,
        materialized_path="001",
        depth=1,
        type="parent",
        status="active",
        effective_from=datetime(2021, 1, 1)
    )
    await parent.insert()
    print(f"✅ Created: {parent.name} (ID: {parent.id})")
    
    # Update holding's children
    holding.child_company_ids.append(parent.id)
    await holding.save()
    
    # 3. Create Subsidiary - India (Level 2)
    india = Company(
        name="TechCorp India",
        code="TECH-IND",
        parent_company_id=parent.id,
        fallback_parent_company_id=holding.id,
        materialized_path="001.001",
        depth=2,
        type="subsidiary",
        status="active",
        effective_from=datetime(2022, 1, 1)
    )
    await india.insert()
    print(f"✅ Created: {india.name} (ID: {india.id})")
    
    # 4. Create Subsidiary - USA (Level 2)
    usa = Company(
        name="TechCorp USA",
        code="TECH-USA",
        parent_company_id=parent.id,
        fallback_parent_company_id=holding.id,
        materialized_path="001.002",
        depth=2,
        type="subsidiary",
        status="active",
        effective_from=datetime(2022, 6, 1)
    )
    await usa.insert()
    print(f"✅ Created: {usa.name} (ID: {usa.id})")
    
    # Update parent's children
    parent.child_company_ids.extend([india.id, usa.id])
    await parent.save()
    
    # 5. Create Sub-subsidiary - Mumbai (Level 3)
    mumbai = Company(
        name="TechCorp Mumbai",
        code="TECH-MUM",
        parent_company_id=india.id,
        fallback_parent_company_id=parent.id,
        materialized_path="001.001.001",
        depth=3,
        type="subsidiary",
        status="active",
        effective_from=datetime(2023, 1, 1)
    )
    await mumbai.insert()
    print(f"✅ Created: {mumbai.name} (ID: {mumbai.id})")
    
    # Update india's children
    india.child_company_ids.append(mumbai.id)
    await india.save()
    
    print("\n📊 Company Hierarchy:")
    print("TechCorp Holdings (holding_group, depth: 0)")
    print("└── TechCorp Global (parent, depth: 1, path: 001)")
    print("    ├── TechCorp India (subsidiary, depth: 2, path: 001.001)")
    print("    │   └── TechCorp Mumbai (subsidiary, depth: 3, path: 001.001.001)")
    print("    └── TechCorp USA (subsidiary, depth: 2, path: 001.002)")

async def verify_data(tenant_db_name: str):
    """Verify inserted data"""
    await init_tenant_db(tenant_db_name)
    
    print("\n🔍 Verifying data...")
    
    # Count companies
    total = await Company.count()
    print(f"Total companies: {total}")
    
    # Find all companies
    companies = await Company.find_all().to_list()
    
    print("\nCompanies by depth:")
    for depth in range(4):
        companies_at_depth = [c for c in companies if c.depth == depth]
        print(f"  Depth {depth}: {len(companies_at_depth)} companies")
        for c in companies_at_depth:
            print(f"    - {c.code}: {c.name}")
    
    # Test hierarchy query
    print("\n📁 Testing hierarchy queries...")
    
    # Find all subsidiaries of TechCorp Global (path starts with 001)
    descendants = await Company.find(
        Company.materialized_path != None,
        Company.materialized_path >= "001",
        Company.materialized_path < "002"
    ).to_list()
    
    print(f"Descendants of TechCorp Global: {len(descendants)}")
    for d in descendants:
        print(f"  - {d.code}: {d.name} (path: {d.materialized_path})")

async def main():
    """Main seed script"""
    await connect_to_mongo()
    
    print("🌱 Starting data seeding...\n")
    
    # Create tenant
    tenant = await create_test_tenant()
    
    print("\n" + "="*50)
    
    # Seed companies for this tenant
    await seed_companies(tenant.database_name)
    
    print("\n" + "="*50)
    
    # Verify data
    await verify_data(tenant.database_name)
    
    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())


## **Project Structure**
'''
hrms/
├── config/
│   ├── __init__.py
│   └── database.py          # Database connection
├── models/
│   ├── __init__.py
│   ├── tenant.py            # Tenant metadata model
│   └── company.py           # Company model
├── scripts/
│   ├── __init__.py
│   └── seed_data.py         # Test data creation
└── requirements.txt
'''