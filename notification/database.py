from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import Settings

settings = Settings()

load_dotenv()

database_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@db:{settings.db_port}/{settings.db_name}"  

sync_url = f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@db:{settings.db_port}/{settings.db_name}"  


engine = create_async_engine(
    database_url,
    echo=True
)

sync_engine = create_engine(
    sync_url,
    echo=True
)


async_session = async_sessionmaker(engine, class_= AsyncSession,expire_on_commit=False)
sync_session = sessionmaker(bind = sync_engine)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session

