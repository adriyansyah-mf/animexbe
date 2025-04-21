from sqlalchemy import Table, Column, BigInteger, Unicode, String, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.db import meta

SiteSettingsModel = Table(
    'site_settings', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('uuid', UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False),
    Column('site_name', Unicode(100), nullable=False),
    Column('site_description', Text, nullable=True),
    Column('site_keywords', Text, nullable=True),
    Column('site_author', Unicode(100), nullable=True),
    Column('meta_title', Unicode(255), nullable=True),
    Column('meta_description', Text, nullable=True),
    Column('meta_robots', String(50), nullable=True),
    Column('favicon_url', String(255), nullable=True),
    Column('logo_url', String(255), nullable=True),
    Column('google_analytics_id', String(100), nullable=True),
    Column('facebook_pixel_id', String(100), nullable=True),
    Column('created_at', BigInteger, default=lambda: int(datetime.utcnow().timestamp())),
    Column('updated_at', BigInteger, default=lambda: int(datetime.utcnow().timestamp())),
)
