from sqlalchemy import Table, Column, BigInteger, Unicode, String, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from core.db import meta

AnimesModel = Table(
    'animes', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('uuid', UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False),

    Column('title', Unicode(255), nullable=False),
    Column('status', String(50), nullable=True),
    Column('studio', Unicode(100), nullable=True),
    Column('released_year', String(100), nullable=True),
    Column('season', Unicode(50), nullable=True),
    Column('type', String(20), nullable=True),
    Column('director', Text, nullable=True),
    Column('casts', Text, nullable=True),
    Column('posted_by', Unicode(100), nullable=True),
    Column('released_on', Date, nullable=True),
    Column('updated_on', Date, nullable=True),
    Column('banner', String(255), nullable=True),
    Column('sinopsis', Text, nullable=True),
    Column('episodes', JSONB, nullable=True),
    Column('genres', JSONB, nullable=True),
    Column('created_at', BigInteger, default=lambda: int(datetime.utcnow().timestamp())),
    Column('updated_at', BigInteger, default=lambda: int(datetime.utcnow().timestamp())),
)
