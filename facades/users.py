from typing import List
import attrs
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from exceptions import UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from helpers.authentication import BasicSalt, PasswordHasher
from helpers.token_maker import TokenMaker
from schemas.users import BookmarkResponseSchema, AddBookmarkSchema, UserLoginSchema, UserRegisterSchema, UserProfileSchema, UserUpdateProfileSchema, UserChangePasswordSchema
from services.users import UserService



@attrs.define
class User:
    conn: AsyncConnection

    async def register(self, user: UserRegisterSchema) -> int:
        return await UserService(self.conn).register(user)
    
    async def login(self, user: UserLoginSchema) -> str:
        try:
            check_login = await UserService(self.conn).login(user)
            token = TokenMaker()

            return token.return_token(
                cfg.password.token_key, check_login
            )
        except UserPasswordError as e:
            raise UserPasswordError
    
    async def get_user_by_uuid(self, uuid: str) -> int:
        return await UserService(self.conn).get_user_by_uuid(uuid)
    
    async def get_user_by_email(self, email: str):
        """Get user by email"""
        return await UserService(self.conn).get_user_by_email(email)
    
    async def get_user_profile(self, user_id: int) -> UserProfileSchema:
        """Get user profile by ID"""
        user = await UserService(self.conn).get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError
        
        return UserProfileSchema(
            id=user.id,
            email=user.email,
            uuid=str(user.uuid),
            created_at=user.created_at
        )
    
    async def update_user_profile(self, user_id: int, profile_data: UserUpdateProfileSchema) -> bool:
        """Update user profile information"""
        return await UserService(self.conn).update_user_profile(user_id, profile_data.email)
    
    async def change_user_password(self, user_id: int, password_data: UserChangePasswordSchema) -> bool:
        """Change user password with verification"""
        return await UserService(self.conn).change_user_password(
            user_id, 
            password_data.current_password, 
            password_data.new_password
        )
    
    async def add_bookmark(self, user_id: int, bookmark_data: AddBookmarkSchema) -> int:
        return await UserService(self.conn).add_bookmark(
            user_id, 
            bookmark_data.url, 
            bookmark_data.content_id
        )
    
    async def remove_bookmark(self, user_id: int, content_id: int) -> bool:
        return await UserService(self.conn).remove_bookmark(user_id, content_id)
    
    async def get_bookmarks(self, user_id: int) -> List[BookmarkResponseSchema]:
        return await UserService(self.conn).get_bookmarks(user_id)
    
    async def check_bookmark_exists(self, user_id: int, content_id: int) -> bool:
        return await UserService(self.conn).check_bookmark_exists(user_id, content_id)

        
