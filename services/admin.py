import secrets
import uuid
from datetime import datetime
from typing import List

import attrs
from sqlalchemy import select, func, desc, or_
from sqlalchemy.engine import row
from sqlalchemy.ext.asyncio import AsyncConnection

from exceptions import AdminPasswordError, AdminIsNotLoginError
from helpers.authentication import PasswordHasher
from models.admin import AdminModel
from models.animes import AnimesModel
from models.crawler import CrawlersModel
from schemas.admin import AdminLoginSchema, AdminMeResponseSchema, SettingsSiteSchema, AdminSettingsResponseSchema, \
    AddCrawlersSchema, ListingCrawlersSchema, AnimeBase, GeneralListingResponse, FilterAnime, ListingAnimeBase, \
    DetailAnimeResponseSchema
from models.settings import SiteSettingsModel

@attrs.define
class AdminCRUD:

    conn: AsyncConnection


    async def _check_apikey(self, api_key: str) -> bool:
        query = (
            select(
                AdminModel
            ).select_from(
                AdminModel
            ).where(
                AdminModel.c.api_key == api_key
            )
        )

        result = (await self.conn.execute(query)).first()

        if result is None:
            return False

        return True

    async def login(self, data: AdminLoginSchema, hasher: PasswordHasher) -> str:
        """
        Method for login
        :param data:
        :param hasher:
        :return:
        """
        username = data.username
        password = data.password
        query = (
            select(
                AdminModel.c.password,
                AdminModel.c.name,
                AdminModel.c.uuid
            ).select_from(
                AdminModel
            )
        ).where(
            AdminModel.c.name == username
        )

        result = (await self.conn.execute(query)).first()

        if not hasher.verify(password, result.password):
            raise AdminPasswordError

        return str(result.uuid)

    async def generate_apikey(self, admin_id: int) -> str:
        """
        Generates a new API key asynchronously.

        This method generates a new API key securely, ensuring that the resulting
        key conforms to the required format and length. An API key is typically
        used to authenticate requests and grant access to specific operations
        or resources in your system. The key generation process is implemented
        asynchronously to allow for non-blocking operations in the application.

        :raises RuntimeError: If the key generation fails due to an internal
            error or other unexpected issues.

        :return: A newly generated API key which is a string.
        :rtype: str
        """
        try:
            apikey = secrets.token_urlsafe(32)
            query = AdminModel.update().where(AdminModel.c.id == admin_id).values(api_key=apikey)

            await self.conn.execute(query)

            return apikey
        except Exception as e:
            raise RuntimeError(f"Failed to generate API key: {e}")

    async def me(self, admin_id: int) -> AdminMeResponseSchema:
        query = (
            select(
                AdminModel.c.uuid,
                AdminModel.c.name,
                AdminModel.c.api_key,
            ).select_from(
                AdminModel
            ).where(
                AdminModel.c.id == admin_id
            )
        )

        result = (await self.conn.execute(query)).first()

        return AdminMeResponseSchema(result.name, result.uuid,  result.api_key)

    async def read_by_name(self, name: str):
        """
        Method for read by name
        :param name:
        :return:
        """
        query = (
            select(
                AdminModel.c.id
            ).select_from(AdminModel)
        ).where(
            AdminModel.c.uuid == name
        )

        return (await self.conn.execute(query)).first()


    async def create_setting(self, data: SettingsSiteSchema) -> bool:

        query = SiteSettingsModel.insert().values(
            site_name=data.site_name,
            site_description=data.site_description,
            site_keywords=data.site_keywords,
            site_author=data.site_author,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            meta_robots=data.meta_robots,
            favicon_url=data.favicon_url,
            logo_url=data.logo_url,
            google_analytics_id=data.google_analytics_id,
            facebook_pixel_id=data.facebook_pixel_id,
        )

        return (await self.conn.execute(query)).inserted_primary_key[0]


    async def read_setting(self, setting_id: int) -> AdminSettingsResponseSchema:
        query = select(
            SiteSettingsModel
        ).select_from(
            SiteSettingsModel
        ).where(
            SiteSettingsModel.c.id == setting_id
        )

        data = (await self.conn.execute(query)).first()
        return AdminSettingsResponseSchema(
            site_name=data.site_name,
            site_description=data.site_description,
            site_keywords=data.site_keywords,
            site_author=data.site_author,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            meta_robots=data.meta_robots,
            favicon_url=data.favicon_url,
            logo_url=data.logo_url,
            google_analytics_id=data.google_analytics_id,
            facebook_pixel_id=data.facebook_pixel_id,
        )


    async def add_crawler(self, api_key: str, data: AddCrawlersSchema) -> bool:

        if await self._check_apikey(api_key):
            query = (
                select(
                    CrawlersModel.c.id
                ).select_from(
                    CrawlersModel
                ).where(
                    CrawlersModel.c.ip == data.ip
                )
            )

            existing = (await self.conn.execute(query)).first()
            if existing:
                query = (
                    CrawlersModel.update()
                    .where(CrawlersModel.c.ip == data.ip)
                    .values(
                        status_engine=data.status_engine,
                        status_crawlers=data.status_crawlers,
                        last_crawling=data.last_crawling,
                    )
                )
                await self.conn.execute(query)
            else:
                query = CrawlersModel.insert().values(
                    status_engine=data.status_engine,
                    status_crawlers=data.status_crawlers,
                    last_crawling=data.last_crawling,
                    ip=data.ip,
                )

                await self.conn.execute(query)
        else:
            raise AdminIsNotLoginError

        return True

    async def listing_crawler(self) -> List[ListingCrawlersSchema]:

        query = (
            select(
                CrawlersModel.c.id,
                CrawlersModel.c.ip,
                CrawlersModel.c.status_engine,
                CrawlersModel.c.status_crawlers,
                CrawlersModel.c.last_crawling,
            ).select_from(
                CrawlersModel
            )
        )

        result = (await self.conn.execute(query)).fetchall()

        return [
            ListingCrawlersSchema(
                ip=row.ip,
                status_engine=row.status_engine,
                status_crawlers=row.status_crawlers,
                last_crawling=row.last_crawling,

            ) for row in result
        ]

    async def add_or_update_anime(self,api_key: str, data: AnimeBase) -> bool:
        if not await self._check_apikey(api_key):
            raise AdminIsNotLoginError
        # Cek apakah anime dengan title ini sudah ada
        query = (
            select(AnimesModel.c.id)
            .where(AnimesModel.c.title == data.title)
        )
        existing = await self.conn.execute(query)
        anime = existing.first()

        values = {
            "title": data.title,
            "status": data.status,
            "studio": data.studio,
            "released_year": data.released_year,
            "season": data.season,
            "type": data.type,
            "director": data.director,
            "casts": data.casts,
            "posted_by": data.posted_by,
            "released_on": data.released_on,
            "updated_on": data.updated_on if data.updated_on else data.released_on,
            "banner": data.banner,
            "sinopsis": data.sinopsis,
            "episodes": data.episodes,
            "genres": data.genres,
            "updated_at": int(datetime.utcnow().timestamp())
        }

        if anime:
            # Kalau sudah ada, update
            update_query = (
                AnimesModel.update()
                .where(AnimesModel.c.id == anime.id)
                .values(**values)
            )
            await self.conn.execute(update_query)
        else:
            # Kalau belum ada, insert
            values["uuid"] = uuid.uuid4()
            values["created_at"] = int(datetime.utcnow().timestamp())
            insert_query = AnimesModel.insert().values(**values)
            await self.conn.execute(insert_query)

        return True

    async def listing_anime(self, data: FilterAnime) -> GeneralListingResponse:
        """
        Listing Animex
        :param data:
        :return:
        """

        query = (
            select(
                AnimesModel.c.id,
                AnimesModel.c.title,
                AnimesModel.c.status,
                AnimesModel.c.banner,
                AnimesModel.c.genres,
                AnimesModel.c.released_year
            ).select_from(
                AnimesModel
            )
        )

        if data.status:
            query = query.where(AnimesModel.c.status == data.status)

        if data.genre:
            query = query.where(AnimesModel.c.genres.op('?')(data.genre))

        if data.type:
            query = query.where(AnimesModel.c.type == data.type)

        if data.search:
            query = query.where(AnimesModel.c.title.ilike(f"%{data.search}%"))

        query_total = select(
            func.count(
                AnimesModel.c.id,
            )
        )

        query = query.order_by(
            desc(func.to_date(AnimesModel.c.released_year, 'Month DD, YYYY'))
        )

        total = (await self.conn.execute(query_total)).scalar()

        query = query.limit(data.per_page).offset((data.page - 1) * data.per_page)

        res = (await self.conn.execute(query)).fetchall()

        return GeneralListingResponse(
            total=total,
            page=data.page,
            per_page=data.per_page,
            data=[
                ListingAnimeBase(
                    id=row.id,
                    title=row.title,
                    status=row.status,
                    banner=row.banner,
                    genres=row.genres,
                    released_year=row.released_year,
                ) for row in res
            ]
        )

    async def detail_anime(self, anime_id: int) -> DetailAnimeResponseSchema:
        """
        Animex Detail
        :param anime_id:
        :return:
        """
        query = (
            select(
                AnimesModel.c.id,
                AnimesModel.c.title,
                AnimesModel.c.status,
                AnimesModel.c.studio,
                AnimesModel.c.released_year,
                AnimesModel.c.season,
                AnimesModel.c.type,
                AnimesModel.c.posted_by,
                AnimesModel.c.updated_on,
                AnimesModel.c.banner,
                AnimesModel.c.sinopsis,
                AnimesModel.c.episodes,
                AnimesModel.c.genres,

            )
        ).select_from(
            AnimesModel
        ).where(AnimesModel.c.id == anime_id)


        data = (await self.conn.execute(query)).first()

        return DetailAnimeResponseSchema(
            id=data.id,
            title=data.title,
            status=data.status,
            studio=data.studio,
            released_year=data.released_year,
            season=data.season,
            type=data.type,
            posted_by=data.posted_by,
            updated_on=data.updated_on,
            genres=data.genres,
            episodes=data.episodes,
            banner=data.banner,
            sinopsis=data.sinopsis,
        )













