import secrets

from api.config import cfg
from core.db import engine
from models.admin import AdminModel
from helpers.authentication import PasswordHasher, BasicSalt
from helpers.general import generate_uuid_from_username
import asyncio

async def main():
    async with engine.begin() as conn:
        hasher = PasswordHasher(BasicSalt(cfg.password.salt))
        password_hash = hasher.hash('admin')
        uuid = generate_uuid_from_username('admin')
        query =  AdminModel.insert().values(
            name='admin',
            password=password_hash,
            uuid=uuid,
            api_key=secrets.token_urlsafe(32)
        )

        return await conn.execute(query)

if __name__ == '__main__':
    asyncio.run(main())