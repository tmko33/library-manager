"""Seed the database with demo data from the command line."""

import asyncio

from app.db.session import AsyncSessionLocal
from app.demo_data import seed_demo_data


async def main() -> None:
    async with AsyncSessionLocal() as session:
        created = await seed_demo_data(session)
    if created:
        print("Demo data created.")
    else:
        print("Database already seeded, nothing to do.")


if __name__ == "__main__":
    asyncio.run(main())
