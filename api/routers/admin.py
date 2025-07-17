from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from api.depends.admin import get_id
from core.db import engine
from exceptions import AdminPasswordError, AdminIsNotLoginError
from facades.admin import Admin
from helpers.authentication import BasicSalt, PasswordHasher
from schemas.admin import AddCrawlerSettingsSchema, AdminLoginSchema, CrawlerSettingsResponseSchema, SettingsSiteSchema, AddCrawlersSchema, AnimeBase

router = APIRouter(prefix='/admin', tags=["Admin"])

@router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    """
    Route For Admin Login
    :param data:
    :return:
    """
    salt = BasicSalt(cfg.password.salt)
    hash_ = PasswordHasher(salt)
    async with engine.begin() as conn:
        try:
            return await Admin(
                conn
            ).login(
                AdminLoginSchema(
                    username=data.username,
                    password=data.password
                ), hash_
            )
        except AdminPasswordError:
            raise HTTPException(401, detail="Login Failed")

@router.get("/me")
async def get_me(admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    try:
        return await Admin(conn).me(admin_id)
    except AdminIsNotLoginError:
        raise HTTPException(401, detail="Admin is not login")


@router.post("/site-setting")
async def get_me(data: SettingsSiteSchema, admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    try:
        return await Admin(conn).site_settings(data)
    except AdminIsNotLoginError:
        raise HTTPException(401, detail="Admin is not login")


@router.get("/settings")
async def get_settings():
    async with engine.begin() as conn:
        return await Admin(conn).read_settings(1)


@router.post("/add-crawler")
async def add_crawler(api_key: str, data: AddCrawlersSchema):
    async with engine.begin() as conn:
        try:
            return await Admin(conn).add_crawler(api_key, data)
        except AdminIsNotLoginError:
            raise HTTPException(401, detail="Admin is not login")

@router.get("/listing-crawler")
async def listing_crawler(admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn

    return await Admin(conn).listing_crawler()


@router.post("/add-anime")
async def add_or_update_anime(api_key: str, data: AnimeBase):
    async with engine.begin() as conn:
        try:
            return await Admin(conn).add_or_update_anime(api_key, data)
        except AdminIsNotLoginError:
            raise HTTPException(401, detail="Admin is not login")
        
@router.post("/add-crawler-settings")
async def add_crawler_settings(data: AddCrawlerSettingsSchema, admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    try:
        return await Admin(conn).add_crawler_settings(data)
    except AdminIsNotLoginError:
        raise HTTPException(401, detail="Admin is not login")
    
@router.get("/listing-crawler-settings")
async def listing_crawler_settings(admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    return await Admin(conn).listing_crawler_settings()

@router.patch("/update-crawler-settings")
async def update_crawler_settings(data: CrawlerSettingsResponseSchema, admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    return await Admin(conn).update_crawler_settings(data)

@router.get("/get-url-for-crawler")
async def get_url_for_crawler(apikey:str, crawler_name: str):
    async with engine.begin() as conn:
        return await Admin(conn).get_url_for_crawler(apikey, crawler_name)
    
@router.delete("/delete-crawler-settings")
async def delete_crawler_settings(crawler_id: int, admin_conn: Tuple[int, AsyncConnection] = Depends(get_id)):
    admin_id, conn = admin_conn
    return await Admin(conn).delete_crawler_settings(crawler_id)







