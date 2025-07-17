from typing import Tuple

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from core.db import engine
from exceptions import UserNotFoundError
from facades.users import User
from helpers.token_maker import TokenMaker

user_login_schema = OAuth2PasswordBearer(
    tokenUrl="/user/login", scheme_name="User", auto_error=True
)

async def get_connection() -> AsyncConnection:
    """
    Method to get database connection
    """
    async with engine.begin() as conn:
        yield conn

async def get_user_id(
    token: str = Depends(user_login_schema),
    conn: AsyncConnection = Depends(get_connection)
) -> Tuple[str, AsyncConnection]:
    """
    Get user UUID from JWT token
    """
    try:
        token_maker = TokenMaker()
        decoded = token_maker.verify_token(token, cfg.password.token_key)
        uuid = decoded.get("uuid")
        
        if not uuid:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user exists
        user_facade = User(conn)
        user = await user_facade.get_user_by_uuid(uuid)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return uuid, conn
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed") 