from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependency import get_db
from app.core.dependencies import get_current_user
from app.services.organization_service import create_organization , add_user_to_org, get_org_users , search_users
from app.core.rbac import require_role

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("")
async def create_org(
    data: dict,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    org = await create_organization(db, user, data["org_name"])

    return {
        "org_id": org.id
    }




@router.post("/{org_id}/user")
async def add_user(
    org_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role("admin"))
):
    return await add_user_to_org(
        db,
        org_id,
        data["email"],
        data["role"],
        user
    )



@router.get("/{org_id}/users")
async def get_users(
    org_id: int,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role("admin"))
):
    users = await get_org_users(db, org_id, limit, offset)

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
        for user in users
    ]


@router.get("/{org_id}/users/search")
async def search_users_api(
    org_id: int,
    q: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role("admin"))
):
    users = await search_users(db, org_id, q)

    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name
        }
        for u in users
    ]