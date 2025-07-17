
import time
import uuid as uuid_module
from sqlalchemy import Table, Column, BigInteger, Unicode, DateTime, ForeignKey, Text, Boolean, UUID, String

from core.db import meta

UserModel = Table(
    'users', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('email', Unicode(100), nullable=False, unique=True),
    Column('password', Unicode(250), nullable=False),
    Column('uuid', UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False),
    Column('created_at', BigInteger, nullable=False, default=int(time.time())), #epoch time
    
)
