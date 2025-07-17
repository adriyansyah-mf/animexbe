from datetime import date
from typing import Optional, Union, List
from enum import Enum
from pydantic import BaseModel
import attrs

class AdminLoginSchema(BaseModel):
    username: str
    password: str


@attrs.define(slots=False)
class AdminMeResponseSchema:
    username: str
    uuid: str
    api_key: str


class SettingsSiteSchema(BaseModel):
    site_name: str
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    site_author: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_robots: Optional[str] = None
    favicon_url: Optional[str] = None
    logo_url: Optional[str] = None
    google_analytics_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None

@attrs.define(slots=False)
class AdminSettingsResponseSchema:
    site_name: str
    site_description: str
    site_keywords: str
    site_author: str
    meta_title: str
    meta_description: str
    meta_robots: str
    favicon_url: str
    logo_url: str
    google_analytics_id: str
    facebook_pixel_id: str

class AddCrawlersSchema(BaseModel):
    ip: str
    status_engine: str
    status_crawlers: str
    last_crawling: int

@attrs.define(slots=False)
class ListingCrawlersSchema:
    ip: str
    status_engine: str
    status_crawlers: str
    last_crawling: int


class AnimeBase(BaseModel):
    title: str
    status: Optional[str] = None
    studio: Optional[str] = None
    released_year: Optional[str] = None
    season: Optional[str] = None
    type: Optional[str] = None
    director: Optional[str] = None
    casts: Optional[str] = None
    posted_by: Optional[str] = None
    released_on: Optional[date] = None
    updated_on: Optional[date] = None
    banner: Optional[str] = None
    sinopsis: Optional[str] = None
    episodes: Optional[Union[List[dict], dict]] = None
    genres: Optional[List[str]] = None


class TypeEnum(str, Enum):
    TV = 'TV'
    Movie = 'Movie'
    Special = 'Special'


class StatusEnum(str, Enum):
    Ongoing = 'Ongoing'
    Completed = 'Completed'

class FilterAnime(BaseModel):
    page: Optional[int] = 1
    per_page: Optional[int] = 5
    status: Optional[StatusEnum] = None
    search: Optional[str] = None
    genre: Optional[str] = None
    type: Optional[TypeEnum] = None




@attrs.define(slots=False)
class ListingAnimeBase:
    id: int
    title: str
    status: Optional[str] = None
    banner: Optional[str] = None
    genres: Optional[List[str]] = None
    released_year: Optional[str] = None

@attrs.define(slots=False)
class GeneralListingResponse:
    page: int
    per_page: int
    total: int
    data: List[ListingAnimeBase]


@attrs.define(slots=False)
class DetailAnimeResponseSchema:
    id: int
    title: str
    status: Optional[str] = None
    studio: Optional[str] = None
    released_year: Optional[str] = None
    season: Optional[str] = None
    type: Optional[str] = None
    posted_by: Optional[str] = None
    updated_on: Optional[date] = None
    banner: Optional[str] = None
    sinopsis: Optional[str] = None
    episodes: Optional[Union[List[dict], dict]] = None
    genres: Optional[List[str]] = None



class AddCrawlerSettingsSchema(BaseModel):
    name: str
    url: str

class CrawlerSettingsResponseSchema(BaseModel):
    id: int
    name: str
    url: str