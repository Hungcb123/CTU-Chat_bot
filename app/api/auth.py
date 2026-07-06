import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Request, Depends
import jwt

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.schema import User
from app.models.pydantic import UserAuth, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Cấu hình bảo mật
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ JWT_SECRET_KEY is not set in environment variables.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 ngày

import bcrypt

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency lấy User hiện tại từ Cookie
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để sử dụng tính năng này")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        
        async with AsyncSessionLocal() as db:
            user = await db.get(User, user_id)
            if user is None:
                raise HTTPException(status_code=401, detail="User không tồn tại")
            return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Lỗi xác thực Token")

@router.post("/register")
async def register(user_data: UserAuth):
    async with AsyncSessionLocal() as db:
        # Kiểm tra trùng username
        existing_user = await db.scalar(select(User).where(User.username == user_data.username))
        if existing_user:
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
            
        hashed_password = get_password_hash(user_data.password)
        new_user = User(username=user_data.username, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {"message": "Đăng ký thành công", "user": {"id": new_user.id, "username": new_user.username}}

@router.post("/login")
async def login(user_data: UserAuth, response: Response):
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.username == user_data.username))
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu")
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        # Nhúng Token vào HTTP-Only Cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False # Set True nếu dùng HTTPS
        )
        return {"message": "Đăng nhập thành công", "user": {"id": user.id, "username": user.username}}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Đã đăng xuất"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, username=current_user.username, role=current_user.role)
