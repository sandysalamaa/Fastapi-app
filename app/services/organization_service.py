from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.membership import Membership
from app.models.audit_log import AuditLog
from sqlalchemy import select,func
from app.models.user import User
from fastapi import HTTPException



async def create_organization(db: AsyncSession, user, org_name: str):
    # 1. Create organization
    org = Organization(
        name=org_name,
        created_by=user.id
    )

    db.add(org)
    await db.flush()  # get org.id

    # 2. Create admin membership
    membership = Membership(
        user_id=user.id,
        org_id=org.id,
        role="admin"
    )
    db.add(membership)

    # 3. Create audit log
    log = AuditLog(
        org_id=org.id,
        user_id=user.id,
        action="CREATE_ORGANIZATION",
        extra_data={"org_name": org_name}
    )
    db.add(log)

    await db.commit()
    await db.refresh(org)

    return org





async def add_user_to_org(db, org_id: int, email: str, role: str, current_user):
    # 1. find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. check if already member 
    result = await db.execute(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.org_id == org_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already added to this organization"
        )

    # 3. create membership
    membership = Membership(
        user_id=user.id,
        org_id=org_id,
        role=role
    )
    db.add(membership)

    # 4. audit log
    log = AuditLog(
        org_id=org_id,
        user_id=current_user.id,
        action="ADD_USER",
        extra_data={
            "added_user": email,
            "role": role
        }
    )
    db.add(log)

    await db.commit()

    return {"message": "User added successfully"}



async def get_org_users(db, org_id: int, limit: int, offset: int):
    query = (
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.org_id == org_id)
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    users = result.scalars().all()

    return users



async def search_users(db, org_id: int, query_str: str):
    query = (
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .where(
            Membership.org_id == org_id,
            func.to_tsvector('english', User.email + ' ' + User.full_name)
            .match(query_str)
        )
    )

    result = await db.execute(query)
    users = result.scalars().all()

    return users