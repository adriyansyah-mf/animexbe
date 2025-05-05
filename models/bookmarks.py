
import time
from sqlalchemy import Table, Column, BigInteger, Unicode, DateTime, ForeignKey, Text, Boolean, UUID, String

from core.db import meta

BookmarksModel = Table(
    'bookmarks', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('user_id', BigInteger, ForeignKey('users.id'), nullable=False),
    Column('url', Unicode(250), nullable=False),
    Column('content_id', BigInteger, ForeignKey('animes.id'), nullable=False),
    Column('created_at', BigInteger, nullable=False, default=int(time.time())), #epoch time
    
)