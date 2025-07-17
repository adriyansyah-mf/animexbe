import secrets

from api.config import cfg
from core.db import engine
from models.admin import AdminModel
from helpers.authentication import PasswordHasher, BasicSalt
from helpers.general import generate_uuid_from_username
import asyncio
from sqlalchemy import select

async def main():
    async with engine.begin() as conn:
        # Check if admin already exists
        check_query = select(AdminModel).where(AdminModel.c.name == 'admin')
        result = await conn.execute(check_query)
        existing_admin = result.fetchone()
        
        if existing_admin:
            print("Admin user already exists, skipping creation...")
            return
        
        # Create admin if it doesn't exist
        hasher = PasswordHasher(BasicSalt(cfg.password.salt))
        password_hash = hasher.hash('admin')
        uuid = generate_uuid_from_username('admin')
        query = AdminModel.insert().values(
            name='admin',
            password=password_hash,
            uuid=uuid,
            api_key=secrets.token_urlsafe(32)
        )

        await conn.execute(query)
        print("Admin user created successfully!")

if __name__ == '__main__':
    asyncio.run(main())