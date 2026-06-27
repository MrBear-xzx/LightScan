from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel, Field

from app.auth.jwt import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import get_engine
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session


class LoginRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: int
    tenant_id: str
    username: str
    role: str


class RegisterRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=4)
    role: str = Field(default='analyst', pattern='^(admin|analyst|viewer)$')


class RegisterResponse(BaseModel):
    user_id: int
    tenant_id: str
    username: str
    role: str


class UserInfo(BaseModel):
    user_id: int
    tenant_id: str
    username: str
    role: str


class UserListItem(BaseModel):
    user_id: int
    tenant_id: str
    username: str
    role: str
    is_active: bool = True
    created_at: str = ""


class UserListResponse(BaseModel):
    total: int
    items: list[UserListItem]


router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.get('/users', response_model=UserListResponse)
def list_users(tenant_id: str = Query(default='default', min_length=1)) -> UserListResponse:
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(User).where(User.tenant_id == tenant_id).order_by(User.created_at.desc())
        rows = session.execute(stmt).scalars().all()
        items = [
            UserListItem(
                user_id=u.user_id,
                tenant_id=u.tenant_id,
                username=u.username,
                role=u.role,
                created_at=str(u.created_at.replace(tzinfo=None)) if u.created_at else "",
            )
            for u in rows
        ]
        return UserListResponse(total=len(items), items=items)


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization is None:
        raise HTTPException(status_code=401, detail='??????')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail='??????')
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail='????????')
    return payload


@router.post('/register', response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> RegisterResponse:
    engine = get_engine()
    with Session(engine) as session:
        existing = session.execute(
            select(User).where(User.username == payload.username)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail='??????')

        user = User(
            tenant_id=payload.tenant_id,
            username=payload.username,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return RegisterResponse(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            username=user.username,
            role=user.role,
        )


@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    engine = get_engine()
    with Session(engine) as session:
        user = session.execute(
            select(User).where(
                User.tenant_id == payload.tenant_id,
                User.username == payload.username,
            )
        ).scalar_one_or_none()
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail='账号或密码错误')

        token = create_access_token(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            username=user.username,
            role=user.role,
        )
        return LoginResponse(
            access_token=token,
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            username=user.username,
            role=user.role,
        )


@router.get('/me', response_model=UserInfo)
def me(payload: dict = Depends(get_current_user)) -> UserInfo:
    return UserInfo(
        user_id=int(payload['sub']),
        tenant_id=payload['tenant_id'],
        username=payload['username'],
        role=payload['role'],
    )
