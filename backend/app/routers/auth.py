"""Authentication endpoints: signup, login, current user."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import User, get_db
from ..schemas import UserCreate, UserLogin, TokenResponse, UserOut
from ..services import auth

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=auth.hash_password(payload.password),
        plan="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = auth.create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserOut(**auth.user_to_dict(user)))


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = auth.create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserOut(**auth.user_to_dict(user)))


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def token_login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """OAuth2 password flow (used by Swagger 'Authorize')."""
    user = await db.scalar(select(User).where(User.email == form.username))
    if not user or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserOut(**auth.user_to_dict(user)))


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(auth.get_current_user)):
    return UserOut(**auth.user_to_dict(current))


@router.post("/upgrade", response_model=UserOut)
async def upgrade(
    current: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)
):
    """Demo: flip the user to premium (no real payment integration)."""
    current.plan = "premium"
    await db.commit()
    await db.refresh(current)
    return UserOut(**auth.user_to_dict(current))
