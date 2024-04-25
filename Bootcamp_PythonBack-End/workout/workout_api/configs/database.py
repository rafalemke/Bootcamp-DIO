from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


DB_URL: str = ('sqlite+aiosqlite:///C:/Users/Rafa_/Documents' +
               '/GitHub/Bootcamp-DIO/Bootcamp_PythonBack-End/workout/workout.db')
engine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def get_session() -> AsyncGenerator:
    async with async_session() as session:  # type: ignore
        yield session
