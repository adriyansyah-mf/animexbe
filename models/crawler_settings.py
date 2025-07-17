
from sqlalchemy import Table, Column, BigInteger, Unicode, UUID

from core.db import meta

CrawelerSetting = Table(
    'crawler_settings', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('name', Unicode(255), nullable=False, unique=True),
    Column('url', Unicode(255), nullable=False),
)
