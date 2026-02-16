import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# import sys
# sys.path.append(".")  # it can be imported by nobarrier

from nobarrier.database.session import Base
from nobarrier.core.settings import settings

# Alembic config object
config = context.config

# Logging
fileConfig(config.config_file_name)

# target_metadata for autogenerate
target_metadata = Base.metadata

# Migration functions
def run_migrations_offline():
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        url=settings.database_url,
        poolclass=pool.NullPool,
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# Main run
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
