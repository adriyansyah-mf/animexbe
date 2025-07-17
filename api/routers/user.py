from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.util import await_only

from api.config import cfg
from api.depends.user import get_user_id
from core.db import engine
from exceptions import AdminPasswordError, AdminIsNotLoginError, UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from facades.admin import Admin
from facades.users import User
from helpers.authentication import BasicSalt, PasswordHasher
from schemas.admin import AdminLoginSchema, SettingsSiteSchema, AddCrawlersSchema, AnimeBase, FilterAnime
from facades.admin import AdminCRUD
from schemas.users import UserLoginSchema, UserRegisterSchema, AddBookmarkSchema, BookmarkResponseSchema, UserProfileSchema, UserUpdateProfileSchema, UserChangePasswordSchema

router = APIRouter(prefix='/user', tags=["User"])


@router.get('/list-anime')
async def listing_anime(data: FilterAnime = Depends()):
    """Get list of anime with filtering options"""
    async with engine.begin() as conn:
        return await AdminCRUD(conn).listing_anime(data)


@router.get('/anime/{anime_id}')
async def get_anime(anime_id: int):
    """Get detailed information about a specific anime"""
    async with engine.begin() as conn:
        return await AdminCRUD(conn).detail_anime(anime_id)
    

@router.post('/register')
async def register(user: UserRegisterSchema):
    """Register a new user account"""
    async with engine.begin() as conn:
        try:
            return await User(conn).register(user)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail="User already exists")
    
@router.post('/login')
async def login(user: OAuth2PasswordRequestForm = Depends()):
    """User login endpoint"""
    async with engine.begin() as conn:
        try:
            return await User(conn).login(user)
        except (UserPasswordError, UserNotFoundError) as e:
            raise HTTPException(status_code=400, detail="Invalid credentials")


# User Profile Endpoints
@router.get('/me', response_model=UserProfileSchema)
async def get_user_profile(
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Get current user's profile information"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = await User(conn).get_user_profile(user.id)
        return profile
        
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@router.put('/me', response_model=dict)
async def update_user_profile(
    profile_data: UserUpdateProfileSchema,
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Update current user's profile information"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email is already taken by another user
        existing_user = await User(conn).get_user_by_email(profile_data.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="Email already taken")
        
        success = await User(conn).update_user_profile(user.id, profile_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return {
            "message": "Profile updated successfully",
            "email": profile_data.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.put('/me/password', response_model=dict)
async def change_user_password(
    password_data: UserChangePasswordSchema,
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Change current user's password"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await User(conn).change_user_password(user.id, password_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid current password")
        
        return {
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to change password")


# Bookmark Endpoints
@router.post('/bookmarks', response_model=dict)
async def add_bookmark(
    bookmark_data: AddBookmarkSchema,
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Add an anime to user's bookmarks"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bookmark_id = await User(conn).add_bookmark(user.id, bookmark_data)
        
        return {
            "message": "Bookmark added successfully",
            "bookmark_id": bookmark_id,
            "content_id": bookmark_data.content_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add bookmark")


@router.delete('/bookmarks/{content_id}')
async def remove_bookmark(
    content_id: int,
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Remove an anime from user's bookmarks"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        removed = await User(conn).remove_bookmark(user.id, content_id)
        
        if not removed:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        return {
            "message": "Bookmark removed successfully",
            "content_id": content_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to remove bookmark")


@router.get('/bookmarks', response_model=list[BookmarkResponseSchema])
async def get_user_bookmarks(
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Get all bookmarks for the authenticated user"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bookmarks = await User(conn).get_bookmarks(user.id)
        return bookmarks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get bookmarks")


@router.get('/bookmarks/check/{content_id}')
async def check_bookmark_status(
    content_id: int,
    user_auth: Tuple[str, AsyncConnection] = Depends(get_user_id)
):
    """Check if a specific anime is bookmarked by the user"""
    user_uuid, conn = user_auth
    
    try:
        # Get user details
        user = await User(conn).get_user_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        is_bookmarked = await User(conn).check_bookmark_exists(user.id, content_id)
        
        return {
            "content_id": content_id,
            "is_bookmarked": is_bookmarked
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check bookmark status")
        



