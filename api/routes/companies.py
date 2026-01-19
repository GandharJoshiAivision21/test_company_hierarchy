# ============================================================
# FILE: api/routes/companies.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from bson import ObjectId

from app.models.company import Company
from app.models.department import Department
from app.models.branch import Branch
from api.dependencies import get_current_user

router = APIRouter()

def build_tree(items: List[Company]) -> List[Dict[str, Any]]:
    """Build hierarchical tree from flat list"""
    # Create lookup dict
    item_dict = {str(item.id): {
        "id": str(item.id),
        "name": item.name,
        "code": item.code,
        "type": item.type,
        "path": item.materialized_path,
        "depth": item.depth,
        "currency": item.currency,
        "status": item.status,
        "children": []
    } for item in items}
    
    # Build tree
    tree = []
    for item in items:
        item_data = item_dict[str(item.id)]
        if item.parent_company_id is None:
            # Root node
            tree.append(item_data)
        else:
            # Child node - add to parent
            parent_id = str(item.parent_company_id)
            if parent_id in item_dict:
                item_dict[parent_id]["children"].append(item_data)
    
    return tree

@router.get("/hierarchy", response_model=List[Dict[str, Any]])
async def get_company_hierarchy(current_user = Depends(get_current_user)):
    """Get complete company hierarchy as tree"""
    
    # Get all companies
    companies = await Company.find(
        Company.is_deleted == False
    ).sort("+depth", "+materialized_path").to_list()
    
    if not companies:
        return []
    
    # Build tree
    tree = build_tree(companies)
    
    return tree

@router.get("/", response_model=List[Dict[str, Any]])
async def list_companies(current_user = Depends(get_current_user)):
    """List all companies (flat)"""
    
    companies = await Company.find(
        Company.is_deleted == False
    ).sort("+depth", "+materialized_path").to_list()
    
    result = []
    for company in companies:
        # Get parent name if exists
        parent_name = None
        if company.parent_company_id:
            parent = await Company.get(company.parent_company_id)
            if parent:
                parent_name = parent.name
        
        result.append({
            "id": str(company.id),
            "name": company.name,
            "code": company.code,
            "type": company.type,
            "path": company.materialized_path,
            "depth": company.depth,
            "parent_name": parent_name,
            "status": company.status,
            "currency": company.currency
        })
    
    return result

@router.get("/{company_id}")
async def get_company(
    company_id: str,
    current_user = Depends(get_current_user)
):
    """Get single company details"""
    
    try:
        company = await Company.get(ObjectId(company_id))
    except:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get parent if exists
    parent = None
    if company.parent_company_id:
        parent_company = await Company.get(company.parent_company_id)
        if parent_company:
            parent = {
                "id": str(parent_company.id),
                "name": parent_company.name,
                "code": parent_company.code
            }
    
    # Get children
    children = await Company.find(
        Company.parent_company_id == company.id,
        Company.is_deleted == False
    ).to_list()
    
    children_list = [{
        "id": str(child.id),
        "name": child.name,
        "code": child.code,
        "type": child.type,
        "path": child.materialized_path
    } for child in children]
    
    # Count departments and branches
    dept_count = await Department.find(
        Department.company_id == company.id,
        Department.is_deleted == False
    ).count()
    
    branch_count = await Branch.find(
        Branch.company_id == company.id,
        Branch.is_deleted == False
    ).count()
    
    return {
        "id": str(company.id),
        "name": company.name,
        "code": company.code,
        "type": company.type,
        "status": company.status,
        "materialized_path": company.materialized_path,
        "depth": company.depth,
        "is_group": company.is_group,
        "currency": company.currency,
        "timezone": company.timezone,
        "parent": parent,
        "children": children_list,
        "stats": {
            "departments": dept_count,
            "branches": branch_count
        }
    }


# @router.get("/{company_id}/hierarchy", response_model=Dict[str, Any])
# async def get_company_subtree(
#     company_id: str,
#     current_user = Depends(get_current_user)
# ):
#     """Get hierarchy starting from a specific company"""

#     try:
#         root_company = await Company.get(ObjectId(company_id))
#     except:
#         raise HTTPException(status_code=404, detail="Company not found")

#     if not root_company or root_company.is_deleted:
#         raise HTTPException(status_code=404, detail="Company not found")

#     # Fetch all descendants using materialized path
#     companies = await Company.find(
#         # Company.materialized_path.startswith(root_company.materialized_path),
#         {"materialized_path": {"$regex": f"^{root_company.materialized_path}"}},
#         Company.is_deleted == False
#     ).to_list() #sort("+depth", "+materialized_path").

#     if not companies:
#         return {}

#     # Build full tree
#     full_tree = build_tree(companies)

#     # Find the root node inside the tree
#     def find_root(tree):
#         for node in tree:
#             if node["id"] == str(root_company.id):
#                 return node
#             child_result = find_root(node["children"])
#             if child_result:
#                 return child_result
#         return None

#     subtree = find_root(full_tree)

#     return subtree


@router.get("/{company_id}/hierarchy", response_model=Dict[str, Any])
async def get_company_subtree(
    company_id: str,
    current_user = Depends(get_current_user)
):
    """Get hierarchy starting from a specific company"""

    try:
        root_company = await Company.get(ObjectId(company_id))
    except:
        raise HTTPException(status_code=404, detail="Company not found")

    if not root_company or root_company.is_deleted:
        raise HTTPException(status_code=404, detail="Company not found")

    # Fetch descendants
    if root_company.materialized_path:
        companies = await Company.find(
            {
                "materialized_path": {
                    "$regex": f"^{root_company.materialized_path}"
                }
            },
            Company.is_deleted == False
        ).sort("+depth", "+materialized_path").to_list()
    else:
        companies = await Company.find(
            Company.is_deleted == False
        ).sort("+depth", "+materialized_path").to_list()

    if not companies:
        return {}

    # Build node map
    node_map = {}
    for item in companies:
        node_map[str(item.id)] = {
            "id": str(item.id),
            "name": item.name,
            "code": item.code,
            "type": item.type,
            "path": item.materialized_path,
            "depth": item.depth,
            "currency": item.currency,
            "status": item.status,
            "children": []
        }

    # Attach children
    for item in companies:
        if item.parent_company_id:
            pid = str(item.parent_company_id)
            if pid in node_map:
                node_map[pid]["children"].append(node_map[str(item.id)])

    # Return subtree root
    return node_map.get(str(root_company.id), {})
