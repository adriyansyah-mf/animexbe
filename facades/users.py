import attrs
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from exceptions import UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from helpers.authentication import BasicSalt, PasswordHasher
from helpers.token_maker import TokenMaker
from schemas.users import UserLoginSchema, UserRegisterSchema
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

        
