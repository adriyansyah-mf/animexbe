from typing import List
import attrs
from sqlalchemy.ext.asyncio import AsyncConnection

from api.config import cfg
from exceptions import AdminPasswordError
from helpers.authentication import PasswordHasher
from helpers.token_maker import TokenMaker
from schemas.admin import AddCrawlerSettingsSchema, AdminLoginSchema, AdminMeResponseSchema, CrawlerSettingsResponseSchema, SettingsSiteSchema, AddCrawlersSchema, AnimeBase, \
    FilterAnime
from services.admin import AdminCRUD



@attrs.define
class Admin:

    conn: AsyncConnection

    async def login(self, data: AdminLoginSchema, hasher: PasswordHasher) -> str:
        try:
            check_login = await AdminCRUD(self.conn).login(data, hasher)
            token = TokenMaker()

            return token.return_token(
                cfg.password.token_key, check_login
            )
        except AdminPasswordError as e:
            raise AdminPasswordError

    async def me(self, admin_id: int) -> AdminMeResponseSchema:
        return await AdminCRUD(self.conn).me(admin_id)

    async def read_by_name(self, name: str):
        """
        Asynchronously retrieves an item by its name.

        This function is used to fetch a specific item from a data source using its name
        as a unique identifier. It returns the item if found, or an appropriate result
        if the item does not exist. This operation follows asynchronous patterns ensuring
        non-blocking behavior in runtime environments that support async programming.

        :param name: The unique identifier of the target item to be retrieved.
        :type name: str
        :return: The item corresponding to the provided name, or appropriate data if not
                 found.
        :rtype: Any
        """


        return await AdminCRUD(self.conn).read_by_name(name)


    async def site_settings(self, data: SettingsSiteSchema):

        return await AdminCRUD(self.conn).create_setting(data)


    async def read_settings(self, settings_id: int = 1):
        return await AdminCRUD(self.conn).read_setting(settings_id)

    async def add_crawler(self, api_key: str, data: AddCrawlersSchema):
        return await AdminCRUD(self.conn).add_crawler(api_key, data)


    async def listing_crawler(self):
        return await AdminCRUD(self.conn).listing_crawler()

    async def add_or_update_anime(self, api_key: str, data: AnimeBase) -> bool:
        return await AdminCRUD(self.conn).add_or_update_anime(api_key, data)

    async def listing_anime(self, data: FilterAnime):
        return await AdminCRUD(self.conn).listing_anime(data)

    async def detail_anime(self, anime_id: int ):
        return await AdminCRUD(self.conn).detail_anime(anime_id)
    
    async def add_crawler_settings(self, data: AddCrawlerSettingsSchema) -> bool:
        return await AdminCRUD(self.conn).add_crawler_settings(data)
    
    async def listing_crawler_settings(self) -> List[CrawlerSettingsResponseSchema]:
        return await AdminCRUD(self.conn).listing_crawler_settings()
    
    async def update_crawler_settings(self, data: CrawlerSettingsResponseSchema) -> bool:
        return await AdminCRUD(self.conn).update_crawler_settings(data)
    
    async def get_url_for_crawler(self, apikey: str, crawler_name: str) -> str:
        return await AdminCRUD(self.conn).get_url_for_crawler(apikey, crawler_name)
    
    async def delete_crawler_settings(self, crawler_id: int) -> bool:
        return await AdminCRUD(self.conn).delete_crawler_settings(crawler_id)