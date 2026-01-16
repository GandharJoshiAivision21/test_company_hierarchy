# import asyncio
# from datetime import datetime
# from config.database import connect_to_mongo, init_tenant_db, init_metadata_db

# from models.company import Company
# from models.tenant import Tenant

# async def create_test_tenant():
#     """Create a test tenant in metadata database"""
#     await init_metadata_db()
    
#     tenant = Tenant(
#         name="TechCorp",
#         database_name="tenant_techcorp",
#         domain="techcorp.hrms.com",
#         subscription_plan="premium",
#         status="active"
#     )
#     await tenant.insert()
#     print(f"✅ Created tenant: {tenant.name} -> {tenant.database_name}")
#     return tenant

# async def seed_companies(tenant_db_name: str):
#     """Create test companies in tenant database"""
#     await init_tenant_db(tenant_db_name)
    
#     # 1. Create Holding Group (Level 0)
#     holding = Company(
#         name="TechCorp Holdings",
#         code="TECH-HOLD",
#         parent_company_id=None,
#         fallback_parent_company_id=None,
#         materialized_path=None,
#         depth=0,
#         type="holding_group",
#         status="active",
#         effective_from=datetime(2020, 1, 1)
#     )
#     await holding.insert()
#     print(f"✅ Created: {holding.name} (ID: {holding.id})")
    
#     # 2. Create Parent Company (Level 1)
#     parent = Company(
#         name="TechCorp Global",
#         code="TECH-GLB",
#         parent_company_id=holding.id,
#         fallback_parent_company_id=None,
#         materialized_path="001",
#         depth=1,
#         type="parent",
#         status="active",
#         effective_from=datetime(2021, 1, 1)
#     )
#     await parent.insert()
#     print(f"✅ Created: {parent.name} (ID: {parent.id})")
    
#     # Update holding's children
#     holding.child_company_ids.append(parent.id)
#     await holding.save()
    
#     # 3. Create Subsidiary - India (Level 2)
#     india = Company(
#         name="TechCorp India",
#         code="TECH-IND",
#         parent_company_id=parent.id,
#         fallback_parent_company_id=holding.id,
#         materialized_path="001.001",
#         depth=2,
#         type="subsidiary",
#         status="active",
#         effective_from=datetime(2022, 1, 1)
#     )
#     await india.insert()
#     print(f"✅ Created: {india.name} (ID: {india.id})")
    
#     # 4. Create Subsidiary - USA (Level 2)
#     usa = Company(
#         name="TechCorp USA",
#         code="TECH-USA",
#         parent_company_id=parent.id,
#         fallback_parent_company_id=holding.id,
#         materialized_path="001.002",
#         depth=2,
#         type="subsidiary",
#         status="active",
#         effective_from=datetime(2022, 6, 1)
#     )
#     await usa.insert()
#     print(f"✅ Created: {usa.name} (ID: {usa.id})")
    
#     # Update parent's children
#     parent.child_company_ids.extend([india.id, usa.id])
#     await parent.save()
    
#     # 5. Create Sub-subsidiary - Mumbai (Level 3)
#     mumbai = Company(
#         name="TechCorp Mumbai",
#         code="TECH-MUM",
#         parent_company_id=india.id,
#         fallback_parent_company_id=parent.id,
#         materialized_path="001.001.001",
#         depth=3,
#         type="subsidiary",
#         status="active",
#         effective_from=datetime(2023, 1, 1)
#     )
#     await mumbai.insert()
#     print(f"✅ Created: {mumbai.name} (ID: {mumbai.id})")
    
#     # Update india's children
#     india.child_company_ids.append(mumbai.id)
#     await india.save()
    
#     print("\n📊 Company Hierarchy:")
#     print("TechCorp Holdings (holding_group, depth: 0)")
#     print("└── TechCorp Global (parent, depth: 1, path: 001)")
#     print("    ├── TechCorp India (subsidiary, depth: 2, path: 001.001)")
#     print("    │   └── TechCorp Mumbai (subsidiary, depth: 3, path: 001.001.001)")
#     print("    └── TechCorp USA (subsidiary, depth: 2, path: 001.002)")

# async def verify_data(tenant_db_name: str):
#     """Verify inserted data"""
#     await init_tenant_db(tenant_db_name)
    
#     print("\n🔍 Verifying data...")
    
#     # Count companies
#     total = await Company.count()
#     print(f"Total companies: {total}")
    
#     # Find all companies
#     companies = await Company.find_all().to_list()
    
#     print("\nCompanies by depth:")
#     for depth in range(4):
#         companies_at_depth = [c for c in companies if c.depth == depth]
#         print(f"  Depth {depth}: {len(companies_at_depth)} companies")
#         for c in companies_at_depth:
#             print(f"    - {c.code}: {c.name}")
    
#     # Test hierarchy query
#     print("\n📁 Testing hierarchy queries...")
    
#     # Find all subsidiaries of TechCorp Global (path starts with 001)
#     descendants = await Company.find(
#         Company.materialized_path != None,
#         Company.materialized_path >= "001",
#         Company.materialized_path < "002"
#     ).to_list()
    
#     print(f"Descendants of TechCorp Global: {len(descendants)}")
#     for d in descendants:
#         print(f"  - {d.code}: {d.name} (path: {d.materialized_path})")

# async def main():
#     """Main seed script"""
#     await connect_to_mongo()
    
#     print("🌱 Starting data seeding...\n")
    
#     # Create tenant
#     tenant = await create_test_tenant()
    
#     print("\n" + "="*50)
    
#     # Seed companies for this tenant
#     await seed_companies(tenant.database_name)
    
#     print("\n" + "="*50)
    
#     # Verify data
#     await verify_data(tenant.database_name)
    
#     print("\n✨ Seeding complete!")

# if __name__ == "__main__":
#     asyncio.run(main())


# ## **Project Structure**
# '''
# hrms/
# ├── config/
# │   ├── __init__.py
# │   └── database.py          # Database connection
# ├── models/
# │   ├── __init__.py
# │   ├── tenant.py            # Tenant metadata model
# │   └── company.py           # Company model
# ├── scripts/
# │   ├── __init__.py
# │   └── seed_data.py         # Test data creation
# └── requirements.txt
# '''


# import asyncio
# from datetime import datetime
# from config.database import connect_to_mongo, init_tenant_db, init_metadata_db
# from models.company import Company
# from models.tenant import Tenant

# async def create_tenant():
#     """Create test tenant"""
#     await init_metadata_db()
    
#     tenant = Tenant(
#         name="TechCorp",
#         database_name="tenant_techcorp",
#         domain="techcorp.hrms.com"
#     )
#     await tenant.insert()
#     print(f"✅ Created tenant: {tenant.name} -> {tenant.database_name}")
#     return tenant

# async def seed_companies(db_name: str):
#     """Seed company hierarchy"""
#     await init_tenant_db(db_name)
    
#     print("\n📊 Creating company hierarchy...")
    
#     # Level 0: Holding Group
#     holding = Company(
#         name="TechCorp Holdings",
#         code="TECH-HOLD",
#         parent_company_id=None,
#         materialized_path=None,
#         depth=0,
#         type="holding_group",
#         status="active",
#         is_group=True,  # Will have children
#         root_id=None,  # Is its own root
#         effective_from=datetime(2020, 1, 1)
#     )
#     await holding.insert()
#     holding.root_id = holding.id  # Point to itself
#     await holding.save()
#     print(f"  ✅ {holding.name} (depth: 0, is_group: {holding.is_group})")
    
#     # Level 1: Parent Company
#     parent = Company(
#         name="TechCorp Global",
#         code="TECH-GLB",
#         parent_company_id=holding.id,
#         materialized_path="001",
#         depth=1,
#         type="parent",
#         status="active",
#         is_group=True,  # Will have children
#         root_id=holding.id,  # Points to holding
#         effective_from=datetime(2021, 1, 1)
#     )
#     await parent.insert()
#     print(f"  ✅ {parent.name} (depth: 1, path: 001, is_group: {parent.is_group})")
    
#     # Level 2: India Subsidiary
#     india = Company(
#         name="TechCorp India",
#         code="TECH-IND",
#         parent_company_id=parent.id,
#         materialized_path="001.001",
#         depth=2,
#         type="subsidiary",
#         status="active",
#         is_group=True,  # Will have children
#         root_id=holding.id,
#         effective_from=datetime(2022, 1, 1)
#     )
#     await india.insert()
#     print(f"  ✅ {india.name} (depth: 2, path: 001.001, is_group: {india.is_group})")
    
#     # Level 2: USA Subsidiary
#     usa = Company(
#         name="TechCorp USA",
#         code="TECH-USA",
#         parent_company_id=parent.id,
#         materialized_path="001.002",
#         depth=2,
#         type="subsidiary",
#         status="active",
#         is_group=False,  # Leaf node, no children
#         root_id=holding.id,
#         effective_from=datetime(2022, 6, 1)
#     )
#     await usa.insert()
#     print(f"  ✅ {usa.name} (depth: 2, path: 001.002, is_group: {usa.is_group})")
    
#     # Level 3: Mumbai Office
#     mumbai = Company(
#         name="TechCorp Mumbai",
#         code="TECH-MUM",
#         parent_company_id=india.id,
#         materialized_path="001.001.001",
#         depth=3,
#         type="subsidiary",
#         status="active",
#         is_group=False,  # Leaf node
#         root_id=holding.id,
#         effective_from=datetime(2023, 1, 1)
#     )
#     await mumbai.insert()
#     print(f"  ✅ {mumbai.name} (depth: 3, path: 001.001.001, is_group: {mumbai.is_group})")
    
#     print("\n✨ Company hierarchy created!")

# async def test_queries(db_name: str):
#     """Test and validate data"""
#     await init_tenant_db(db_name)
    
#     print("\n🔍 VALIDATION TESTS")
#     print("=" * 50)
    
#     # Test 1: Count companies
#     total = await Company.count()
#     print(f"\n1️⃣ Total companies: {total}")
#     assert total == 5, f"Expected 5 companies, got {total}"
#     print("   ✅ PASS")
    
#     # Test 2: Find by is_group
#     print(f"\n2️⃣ Group vs Leaf companies:")
#     groups = await Company.find(Company.is_group == True).to_list()
#     leaves = await Company.find(Company.is_group == False).to_list()
#     print(f"   Groups (can have children): {len(groups)}")
#     for g in groups:
#         print(f"      - {g.code}: {g.name}")
#     print(f"   Leaves (no children): {len(leaves)}")
#     for l in leaves:
#         print(f"      - {l.code}: {l.name}")
#     print("   ✅ PASS")
    
#     # Test 3: Find by root_id
#     print(f"\n3️⃣ Find all in TechCorp Holdings tree:")
#     holding = await Company.find_one(Company.type == "holding_group")
#     tree = await Company.find(Company.root_id == holding.id).to_list()
#     print(f"   Found {len(tree)} companies:")
#     for c in tree:
#         print(f"      - {c.code}: {c.name} (depth: {c.depth})")
#     assert len(tree) == 5  # All companies
#     print("   ✅ PASS")
    
#     # Test 4: Find children using M-Path (no child_ids array needed)
#     print(f"\n4️⃣ Find children of TechCorp Global (using M-Path):")
#     children = await Company.find(
#         Company.materialized_path != None,
#         Company.materialized_path >= "001",
#         Company.materialized_path < "002",
#         Company.depth == 2  # Direct children only
#     ).to_list()
#     print(f"   Direct children: {len(children)}")
#     for c in children:
#         print(f"      - {c.code}: {c.name}")
#     assert len(children) == 2  # India and USA
#     print("   ✅ PASS")
    
#     # Test 5: Find ALL descendants (including grandchildren)
#     print(f"\n5️⃣ Find ALL descendants of TechCorp Global:")
#     descendants = await Company.find(
#         Company.materialized_path != None,
#         Company.materialized_path >= "001.",  # Note the dot!
#         Company.materialized_path < "002"
#     ).to_list()
#     print(f"   Total descendants: {len(descendants)}")
#     for d in descendants:
#         print(f"      - {d.code}: {d.name} (path: {d.materialized_path})")
#     assert len(descendants) == 3  # India, USA, Mumbai
#     print("   ✅ PASS")
    
#     # Test 6: Verify root_id points correctly
#     print(f"\n6️⃣ Verify root_id points to holding:")
#     mumbai = await Company.find_one(Company.code == "TECH-MUM")
#     root = await Company.get(mumbai.root_id)
#     print(f"   Mumbai's root: {root.name}")
#     assert root.type == "holding_group"
#     print("   ✅ PASS")
    
#     print("\n" + "=" * 50)
#     print("🎉 ALL VALIDATION TESTS PASSED!")

# async def main():
#     """Main execution"""
#     await connect_to_mongo()
    
#     print("🌱 STARTING COMPANY STRUCTURE SETUP\n")
#     print("=" * 50)
    
#     # Create tenant
#     tenant = await create_tenant()
    
#     print("\n" + "=" * 50)
    
#     # Seed companies
#     await seed_companies(tenant.database_name)
    
#     print("\n" + "=" * 50)
    
#     # Test and validate
#     await test_queries(tenant.database_name)
    
#     print("\n✅ SETUP COMPLETE!")

# if __name__ == "__main__":
#     asyncio.run(main())

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
    
    print("\n📊 Creating company hierarchy...")
    
    # 1. Create Holding Group (Level 0)
    holding = Company(
        name="TechCorp Holdings",
        code="TECH-HOLD",
        parent_company_id=None,
        materialized_path=None,
        depth=0,
        type="holding_group",
        status="active",
        is_group=True,  # Has children
        root_id=None,  # Will be set to itself
        effective_from=datetime(2020, 1, 1)
    )
    await holding.insert()
    
    # Set root_id to itself (it's the root)
    holding.root_id = holding.id
    await holding.save()
    
    print(f"  ✅ {holding.name} (depth: 0, is_group: {holding.is_group})")
    
    # 2. Create Parent Company (Level 1)
    parent = Company(
        name="TechCorp Global",
        code="TECH-GLB",
        parent_company_id=holding.id,
        materialized_path="001",
        depth=1,
        type="parent",
        status="active",
        is_group=True,  # Has children
        root_id=holding.id,
        effective_from=datetime(2021, 1, 1)
    )
    await parent.insert()
    print(f"  ✅ {parent.name} (depth: 1, path: 001, is_group: {parent.is_group})")
    
    # 3. Create Subsidiary - India (Level 2)
    india = Company(
        name="TechCorp India",
        code="TECH-IND",
        parent_company_id=parent.id,
        materialized_path="001.001",
        depth=2,
        type="subsidiary",
        status="active",
        is_group=True,  # Has children
        root_id=holding.id,
        effective_from=datetime(2022, 1, 1)
    )
    await india.insert()
    print(f"  ✅ {india.name} (depth: 2, path: 001.001, is_group: {india.is_group})")
    
    # 4. Create Subsidiary - USA (Level 2)
    usa = Company(
        name="TechCorp USA",
        code="TECH-USA",
        parent_company_id=parent.id,
        materialized_path="001.002",
        depth=2,
        type="subsidiary",
        status="active",
        is_group=False,  # Leaf node - no children
        root_id=holding.id,
        effective_from=datetime(2022, 6, 1)
    )
    await usa.insert()
    print(f"  ✅ {usa.name} (depth: 2, path: 001.002, is_group: {usa.is_group})")
    
    # 5. Create Sub-subsidiary - Mumbai (Level 3)
    mumbai = Company(
        name="TechCorp Mumbai",
        code="TECH-MUM",
        parent_company_id=india.id,
        materialized_path="001.001.001",
        depth=3,
        type="subsidiary",
        status="active",
        is_group=False,  # Leaf node - no children
        root_id=holding.id,
        effective_from=datetime(2023, 1, 1)
    )
    await mumbai.insert()
    print(f"  ✅ {mumbai.name} (depth: 3, path: 001.001.001, is_group: {mumbai.is_group})")
    
    print("\n📊 Company Hierarchy:")
    print("TechCorp Holdings (holding_group, depth: 0, is_group: True)")
    print("└── TechCorp Global (parent, depth: 1, path: 001, is_group: True)")
    print("    ├── TechCorp India (subsidiary, depth: 2, path: 001.001, is_group: True)")
    print("    │   └── TechCorp Mumbai (subsidiary, depth: 3, path: 001.001.001, is_group: False)")
    print("    └── TechCorp USA (subsidiary, depth: 2, path: 001.002, is_group: False)")

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
            print(f"    - {c.code}: {c.name} (is_group: {c.is_group})")
    
    # Test: Find by is_group
    print("\n📁 Companies by is_group flag:")
    groups = await Company.find(Company.is_group == True).to_list()
    leaves = await Company.find(Company.is_group == False).to_list()
    print(f"  Group companies (can have children): {len(groups)}")
    for g in groups:
        print(f"    - {g.code}: {g.name}")
    print(f"  Leaf companies (no children): {len(leaves)}")
    for l in leaves:
        print(f"    - {l.code}: {l.name}")
    
    # Test hierarchy query using M-Path
    print("\n📁 Testing M-Path hierarchy queries...")
    
    # Find all descendants of TechCorp Global (including itself)
    descendants = await Company.find(
        Company.materialized_path != None,
        Company.materialized_path >= "001",
        Company.materialized_path < "002"
    ).to_list()
    
    print(f"Descendants of TechCorp Global (including self): {len(descendants)}")
    for d in descendants:
        print(f"  - {d.code}: {d.name} (path: {d.materialized_path})")
    
    # Test: Find direct children only (depth 2)
    print("\n👶 Direct children of TechCorp Global:")
    children = await Company.find(
        Company.parent_company_id == parent.id
    ).to_list() if (parent := await Company.find_one(Company.code == "TECH-GLB")) else []
    for c in children:
        print(f"  - {c.code}: {c.name}")
    
    # Test: Find by root_id
    print("\n🌳 All companies in TechCorp Holdings tree (using root_id):")
    holding = await Company.find_one(Company.code == "TECH-HOLD")
    if holding:
        tree = await Company.find(Company.root_id == holding.id).to_list()
        print(f"  Found {len(tree)} companies in tree")
        for c in sorted(tree, key=lambda x: x.depth):
            indent = "  " * c.depth
            print(f"{indent}- {c.code}: {c.name} (depth: {c.depth})")

async def main():
    """Main seed script"""
    await connect_to_mongo()
    
    print("🌱 Starting data seeding...\n")
    print("=" * 50)
    
    # Create tenant
    tenant = await create_test_tenant()
    
    print("\n" + "=" * 50)
    
    # Seed companies for this tenant
    await seed_companies(tenant.database_name)
    
    print("\n" + "=" * 50)
    
    # Verify data
    await verify_data(tenant.database_name)
    
    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())