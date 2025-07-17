from pydantic import BaseModel
from typing import Optional


class UserRegisterSchema(BaseModel):
    email: str
    password: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserUpdateSchema(BaseModel):
    uuid: str
    email: str
    password: str


class UserProfileSchema(BaseModel):
    id: int
    email: str
    uuid: str
    created_at: int


class UserUpdateProfileSchema(BaseModel):
    email: str


class UserChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str


class AddBookmarkSchema(BaseModel):
    content_id: int
    url: str


class ListingBookmarksSchema(BaseModel):
    id: int
    url: str
    content_id: int
    created_at: int


class BookmarkResponseSchema(BaseModel):
    id: int
    url: str
    content_id: int
    created_at: int
    anime_title: Optional[str] = None
    anime_banner: Optional[str] = None
    anime_status: Optional[str] = None