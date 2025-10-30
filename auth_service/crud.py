from shared.models.user import User
from shared.core.security import hash_password, verify_password
from shared.schemas.user import UserCreate, UserLogin, UserRead
from datetime import datetime


async def create_user(user_create: UserCreate) -> UserRead:
    hashed_pw = hash_password(user_create.password)
    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_pw,
        created_at=datetime.now()
    )
    await user.insert()
    return UserRead(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat()
    )


async def login_user(user_login: UserLogin) -> UserRead:
    user = await User.find_one(User.email == user_login.email)
    if user and verify_password(user_login.password, user.hashed_password):
        return UserRead(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    else:
        raise ValueError("Invalid email or password")
    

async def get_user_by_id(user_id: str) -> UserRead | None:
    user = await User.get(user_id)
    if user:
        return UserRead(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    return None