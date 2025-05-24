# backend/migrations/env.py
import sys, os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))

from core.database import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    import asyncio
    asyncio.run(run_async_migrations())
