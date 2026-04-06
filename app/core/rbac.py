from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.dependency import get_db
from app.models.membership import Membership
from app.core.dependencies import get_current_user


def require_role(required_role: str):
    '''
    To require a specific role for a route
    '''
    async def role_checker(
        org_id: int,
        user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        result = await db.execute(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.org_id == org_id
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not part of organization")

        if membership.role != required_role:
            raise HTTPException(status_code=403, detail="Not authorized")

        return user

    return role_checker


'''
check roles
'''
def require_membership():
    async def checker(
        org_id: int,
        user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        result = await db.execute(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.org_id == org_id
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Not part of organization")

        return user

    return checker
