from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependency import get_db
from app.core.dependencies import get_current_user
from app.services.item_service import create_item, get_items
from app.core.rbac import require_membership

router = APIRouter(prefix="/organizations/{org_id}/item", tags=["Items"])


@router.post("")
async def create_item_api(
    org_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_membership())
):
    item = await create_item(db, org_id, user, data["item_details"])

    return {"item_id": item.id}



@router.get("")
async def get_items_api(
    org_id: int,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_membership())
):
    items = await get_items(db, org_id, user, limit, offset)

    return [
        {
            "id": i.id,
            "details": i.details,
            "created_by": i.created_by
        }
        for i in items
    ]