from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password
from app.core.security import verify_password, create_access_token


async def register_user(db: AsyncSession, email: str, password: str, full_name: str):
    '''
    Register a new user
    
    Args:
        db: AsyncSession
        email: User email
        password: User password
        full_name: User full name
    
    Returns:
        User: Created user
    '''
    # check if user exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise Exception("User already exists")

    # create user
    new_user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name
    )


    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def login_user(db, email: str, password: str):
    '''
    Login user and return access token
    
    Args:
        db: AsyncSession
        email: User email
        password: User password
    
    Returns:
        str: Access token
    '''
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise Exception("Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise Exception("Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return token