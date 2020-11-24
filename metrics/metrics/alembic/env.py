import os

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from metrics.models import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

target_metadata = Base.metadata  # pylint: disable=invalid-name


def get_url():
    def _get_value(name):
        if name not in os.environ:
            raise Exception(f'Environment variable {name} not set')
        return os.environ[name]

    url = 'mysql+pymysql://{}:{}@{}:{}/metrics'
    suffixes = ('USER', 'PASSWORD', 'HOST', 'PORT')
    values = [_get_value(f'MYSQL_{i}') for i in suffixes]
    return url.format(*values)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    url = get_url()
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
