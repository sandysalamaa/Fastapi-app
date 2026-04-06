from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.item import Item
from app.models.audit_log import AuditLog
from app.models.membership import Membership


async def create_item(db: AsyncSession, org_id: int, user, details: dict):
    item = Item(
        org_id=org_id,
        created_by=user.id,
        details=details
    )

    db.add(item)
    await db.flush()

    #  audit log
    log = AuditLog(
        org_id=org_id,
        user_id=user.id,
        action="CREATE_ITEM",
        extra_data={"item_id": item.id}
    )
    db.add(log)

    await db.commit()
    await db.refresh(item)

    return item


async def get_items(db: AsyncSession, org_id: int, user, limit: int, offset: int):
    # get user role
    result = await db.execute(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.org_id == org_id
        )
    )
    membership = result.scalar_one_or_none()

    if not membership:
        return []

    #  role-based filtering
    if membership.role == "admin":
        query = select(Item).where(Item.org_id == org_id)
    else:
        query = select(Item).where(
            Item.org_id == org_id,
            Item.created_by == user.id
        )

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    items = result.scalars().all()

    return items