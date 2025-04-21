
from sqlalchemy import Table, Column, BigInteger, Unicode, UUID

from core.db import meta

CrawlersModel = Table(
    'crawlers', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('ip', Unicode(100), nullable=False, unique=True),
    Column('status_engine', Unicode(250), nullable=True),
    Column('status_crawlers', Unicode(250), nullable=True),
    Column('last_crawling', BigInteger, nullable=True),
)
