import asyncio
from core.db import meta, engine
from models.admin import AdminModel
from models.animes import AnimesModel
from models.crawler import CrawlersModel
from models.settings import SiteSettingsModel
from models.users import UserModel
from models.crawler_settings import CrawelerSetting
from models.bookmarks import BookmarksModel

async def main():

    async with engine.begin() as conn:

        # Drop all existing tables first to fix schema issues
        await conn.run_sync(meta.drop_all)
        
        # Create all tables in the correct order
        await conn.run_sync(meta.create_all, tables=[
            UserModel,
            AdminModel,
            CrawlersModel,
            AnimesModel,
            SiteSettingsModel,
            CrawelerSetting,
            BookmarksModel
        ])

    #await engine.dispose()
    print("Creating tables...")

if __name__ == '__main__':
    asyncio.run(main())