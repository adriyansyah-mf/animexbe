from typing import List
import attrs
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from exceptions import UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from helpers.authentication import BasicSalt, PasswordHasher
from helpers.token_maker import TokenMaker
from schemas.users import BookmarkResponseSchema, AddBookmarkSchema, UserLoginSchema, UserRegisterSchema
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

        
