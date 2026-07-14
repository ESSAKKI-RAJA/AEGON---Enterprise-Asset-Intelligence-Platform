import random
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

fake = Faker()
Faker.seed(42)
random.seed(42)

async def check_table_empty(session: AsyncSession, model) -> bool:
    """Returns True if the table has 0 rows, False otherwise."""
    result = await session.execute(select(func.count(model.id)))
    count = result.scalar()
    return count == 0

def random_past_date(days_back=365):
    return fake.date_time_between(start_date=f'-{days_back}d', end_date='now')

def random_future_date(days_forward=365):
    return fake.date_time_between(start_date='now', end_date=f'+{days_forward}d')
