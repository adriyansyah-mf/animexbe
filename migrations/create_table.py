import asyncio
from core.db import meta, engine
from models.admin import AdminModel
from models.animes import AnimesModel
from models.crawler import CrawlersModel
from models.settings import SiteSettingsModel
from models.users import UserModel
async def main():

    async with engine.begin() as conn:

        #await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all, tables=[
            UserModel,
            #AdminModel,
            #CrawlersModel,
            #AnimesModel,
            #SiteSettingsModel,
        ] )

    #await engine.dispose()
    print("Creating tables...")

if __name__ == '__main__':
    asyncio.run(main())