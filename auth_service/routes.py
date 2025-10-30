from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import logging

from shared.core.security import create_access_token, verify_access_token, oauth2_scheme
from shared.core.configs import settings
from shared.schemas.user import UserCreate, UserLogin, UserRead
from crud import login_user, create_user, get_user_by_id


router = APIRouter(prefix="/auth", tags=["auth"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth-service")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    try:
        user = await create_user(user_create)
        token = create_access_token(user_id=user.id)
        return {"user": user, "token": token}
    except Exception as e:
        logger.warning("There is an error: ", e)
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/login")
async def login(login_form: OAuth2PasswordRequestForm = Depends()) -> dict:
    user_login = UserLogin(email=login_form.username, password=login_form.password)
    try:
        user = await login_user(user_login)
        token = create_access_token(user_id=user.id, expires_delta=timedelta(days=7))
        return {"user": user, "token": token}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user", response_model=UserRead)
async def read_current_user(token: str = Depends(oauth2_scheme)) -> UserRead:
    user_id = verify_access_token(token)
    logger.info(f"Using SECRET_KEY: {settings.SECRET_KEY}...")
    
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


