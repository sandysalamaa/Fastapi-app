
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from app.db.dependency import get_db
from app.schemas.auth import LoginRequest
from app.services.auth_service import login_user
from app.core.rbac import require_role



router = APIRouter(prefix="/auth", tags=["Auth"])


# @router.get("/")
# async def test_auth():
#     return {"message": "Auth is working"}


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, data.email, data.password, data.full_name)
        return {
            "message": "User created successfully",
            "user_id": user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await login_user(db, data.email, data.password)

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

from app.core.dependencies import get_current_user


@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }



@router.get("/test-admin/{org_id}")
async def test_admin(
    org_id: int,
    user = Depends(require_role("admin"))
):
    return {"message": "You are admin"}