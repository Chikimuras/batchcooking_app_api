from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
else:
    print("No config file found, logging will not be configured.")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

from app.core.config import settings  # Import your settings module
from app.models import SQLModel  # Import SQLModel for metadata

target_metadata = SQLModel.metadata
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """
    Returns the appropriate SQLAlchemy database connection URL based on the current environment.
    
    Selects the local database URI if the environment is set to "local"; otherwise, returns the default database URI.
    """
    return str(settings.SQLALCHEMY_DATABASE_URI_LOCAL if settings.ENVIRONMENT == "local" else settings.SQLALCHEMY_DATABASE_URI)

print(f"Using database URL: {get_url()}")  # Debugging output to check the URL

def run_migrations_offline() -> None:
    """
    Runs database migrations in offline mode using only the database URL.
    
    Configures the Alembic migration context without requiring a database connection, enabling the generation of SQL migration scripts as output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Executes Alembic migrations in online mode using a live database connection.
    
    Establishes a SQLAlchemy engine with the configured database URL, connects to the database, and applies migrations within a transactional context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
