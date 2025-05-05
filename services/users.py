import attrs
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select
from core.db import engine
from api.config import cfg
from exceptions import UserAlreadyExistsError, UserNotFoundError, UserPasswordError
from helpers.authentication import BasicSalt, PasswordHasher
from models.users import UserModel
from schemas.users import UserLoginSchema, UserRegisterSchema, UserUpdateSchema
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
                UserModel.c.email == user.email
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
    