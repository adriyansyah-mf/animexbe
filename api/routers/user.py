from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.util import await_only

from api.config import cfg
from api.depends.admin import get_id
from core.db import engine
from exceptions import AdminPasswordError, AdminIsNotLoginError, UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from facades.admin import Admin
from facades.users import User
from helpers.authentication import BasicSalt, PasswordHasher
from schemas.admin import AdminLoginSchema, SettingsSiteSchema, AddCrawlersSchema, AnimeBase, FilterAnime
from facades.admin import AdminCRUD
from schemas.users import UserLoginSchema, UserRegisterSchema

router = APIRouter(prefix='/user', tags=["User"])


@router.get('/list-anime')
async def listing_anime(data: FilterAnime = Depends()):
    async with engine.begin() as conn:
        return await AdminCRUD(conn).listing_anime(data)


@router.get('/anime/{anime_id}')
async def get_anime(anime_id: int ):
    async with engine.begin() as conn:
        return await AdminCRUD(conn).detail_anime(anime_id)
    

@router.post('/register')
async def register(user: UserRegisterSchema):
    async with engine.begin() as conn:
        try:
            return await User(conn).register(user)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail="User already exists")
    
@router.post('/login')
async def login(user: UserLoginSchema):
    async with engine.begin() as conn:
        try:
            return await User(conn).login(user)
        except UserPasswordError as e:
            raise HTTPException(status_code=400, detail="User not found")


