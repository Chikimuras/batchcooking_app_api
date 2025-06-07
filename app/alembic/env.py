from app.core.config import settings  # Import your settings module
from app.models import SQLModel  # Import SQLModel for metadata
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

target_metadata = SQLModel.metadata
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """
    Returns the appropriate database connection URL based on the current environment.
    
    Selects the local database URI if the environment is set to "local"; otherwise, returns the production database URI.
    """
    return str(settings.SQLALCHEMY_DATABASE_URI_LOCAL if settings.ENVIRONMENT == "local" else settings.SQLALCHEMY_DATABASE_URI)

print(f"Using database URL: {get_url()}")  # Debugging output to check the URL

def run_migrations_offline() -> None:
    """
    Configures and runs Alembic migrations in offline mode, emitting SQL scripts without connecting to the database.
    
    This function sets up the Alembic context using the database URL and model metadata, enabling literal value binding and type comparison for accurate migration script generation. Migrations are output as SQL statements rather than being executed directly.
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
    Runs Alembic migrations directly against the database using a live connection.
    
    Creates a SQLAlchemy engine with the selected database URL, establishes a connection, and applies migrations to the database in an online mode.
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
