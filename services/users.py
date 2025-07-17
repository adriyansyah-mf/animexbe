import time
from typing import List
import attrs
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select
from core.db import engine
from api.config import cfg
from exceptions import UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from helpers.authentication import BasicSalt, PasswordHasher
from models.bookmarks import BookmarksModel
from models.animes import AnimesModel
from models.users import UserModel
from schemas.users import ListingBookmarksSchema, BookmarkResponseSchema, UserLoginSchema, UserRegisterSchema, UserUpdateSchema
import uuid

@attrs.define
class UserService:
    conn: AsyncConnection

    async def register(self, user: UserRegisterSchema) -> int:

        query = (
            select(
                UserModel
            ).where(
                UserModel.c.email == user.email
            )
        )

        result = (await self.conn.execute(query)).first()

        if result is not None:
            raise UserAlreadyExistsError

        hasher = PasswordHasher(BasicSalt(cfg.password.salt))
        password_hash = hasher.hash(user.password)

        query = UserModel.insert().values(
            email=user.email,
            password=password_hash,
            uuid=uuid.uuid4()
        )

        result = (await self.conn.execute(query)).inserted_primary_key[0]

        return result
    
    async def login(self, user: UserLoginSchema) -> int:

        hasher = PasswordHasher(BasicSalt(cfg.password.salt))

        query = (
            select(
                UserModel
            ).where(
                UserModel.c.email == user.username
            )
        )

        result = (await self.conn.execute(query)).first()

        if result is None:
            raise UserNotFoundError
        
        if not hasher.verify(user.password, result.password):
            raise UserPasswordError
        
        return str(result.uuid)
    
    async def get_user_by_uuid(self, uuid: str) -> int:
        query = (
            select(
                UserModel
            ).where(
                UserModel.c.uuid == uuid
            )
        )

        result = (await self.conn.execute(query)).first()

        return result
    
    async def get_user_by_id(self, user_id: int):
        """Get user profile by ID"""
        query = (
            select(
                UserModel
            ).where(
                UserModel.c.id == user_id
            )
        )

        result = (await self.conn.execute(query)).first()

        return result
    
    async def update_user_profile(self, user_id: int, email: str) -> bool:
        """Update user profile information"""
        query = UserModel.update().values(
            email=email
        ).where(
            UserModel.c.id == user_id
        )

        result = (await self.conn.execute(query)).rowcount

        return result > 0
    
    async def change_user_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with verification"""
        # First get current user data
        user_query = (
            select(UserModel)
            .where(UserModel.c.id == user_id)
        )
        
        user = (await self.conn.execute(user_query)).first()
        if not user:
            return False
        
        # Verify current password
        hasher = PasswordHasher(BasicSalt(cfg.password.salt))
        if not hasher.verify(current_password, user.password):
            return False
        
        # Hash new password
        new_password_hash = hasher.hash(new_password)
        
        # Update password
        update_query = UserModel.update().values(
            password=new_password_hash
        ).where(
            UserModel.c.id == user_id
        )

        result = (await self.conn.execute(update_query)).rowcount

        return result > 0
    
    async def get_user_by_email(self, email: str) -> int:
        query = (
            select(
                UserModel
            ).where(
                UserModel.c.email == email
            )
        )

        result = (await self.conn.execute(query)).first()

        return result
    
    async def update_user(self, user: UserUpdateSchema) -> int:
        query = UserModel.update().values(
            email=user.email,
            password=user.password
        ).where(
            UserModel.c.uuid == user.uuid
        )

        result = (await self.conn.execute(query)).rowcount

        return result
    
    async def delete_user(self, uuid: str) -> int:
        query = UserModel.delete().where(
            UserModel.c.uuid == uuid
        )

        result = (await self.conn.execute(query)).rowcount

        return result
    
    async def add_bookmark(self, user_id: int, url: str, content_id: int) -> int:
        # Check if bookmark already exists
        check_query = (
            select(BookmarksModel.c.id)
            .where(
                (BookmarksModel.c.user_id == user_id) & 
                (BookmarksModel.c.content_id == content_id)
            )
        )
        
        existing = (await self.conn.execute(check_query)).first()
        if existing:
            return existing.id
        
        query = BookmarksModel.insert().values(
            user_id=user_id,
            url=url,
            content_id=content_id,
            created_at=int(time.time())
        )

        result = (await self.conn.execute(query)).inserted_primary_key[0]

        return result
    
    async def remove_bookmark(self, user_id: int, content_id: int) -> bool:
        query = BookmarksModel.delete().where(
            (BookmarksModel.c.user_id == user_id) & 
            (BookmarksModel.c.content_id == content_id)
        )
        
        result = (await self.conn.execute(query)).rowcount
        return result > 0
    
    async def get_bookmarks(self, user_id: int) -> List[BookmarkResponseSchema]:
        """Get user bookmarks with anime information"""
        query = (
            select(
                BookmarksModel.c.id,
                BookmarksModel.c.url,
                BookmarksModel.c.content_id,
                BookmarksModel.c.created_at,
                AnimesModel.c.title,
                AnimesModel.c.banner,
                AnimesModel.c.status
            )
            .select_from(
                BookmarksModel.join(
                    AnimesModel, 
                    BookmarksModel.c.content_id == AnimesModel.c.id
                )
            )
            .where(BookmarksModel.c.user_id == user_id)
            .order_by(BookmarksModel.c.created_at.desc())
        )

        result = (await self.conn.execute(query)).fetchall()

        return [
            BookmarkResponseSchema(
                id=row.id,
                url=row.url,
                content_id=row.content_id,
                created_at=row.created_at,
                anime_title=row.title,
                anime_banner=row.banner,
                anime_status=row.status
            ) for row in result
        ]
    
    async def check_bookmark_exists(self, user_id: int, content_id: int) -> bool:
        """Check if user has bookmarked this anime"""
        query = (
            select(BookmarksModel.c.id)
            .where(
                (BookmarksModel.c.user_id == user_id) & 
                (BookmarksModel.c.content_id == content_id)
            )
        )
        
        result = (await self.conn.execute(query)).first()
        return result is not None
    