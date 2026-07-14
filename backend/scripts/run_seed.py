import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from scripts.seeders.seeder_identity import seed_identity_org
from scripts.seeders.seeder_asset import seed_asset_inventory
from scripts.seeders.seeder_maintenance import seed_maintenance
from scripts.seeders.seeder_procurement import seed_procurement_finance
from scripts.seeders.seeder_ai import seed_ai_analytics

async def main():
    print("Starting Enterprise Data Seeding...")
    async with AsyncSessionLocal() as session:
        try:
            await seed_identity_org(session)
            await seed_asset_inventory(session)
            await seed_maintenance(session)
            await seed_procurement_finance(session)
            await seed_ai_analytics(session)
            print("Seeding Complete!")
        except Exception as e:
            print(f"Error during seeding: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(main())
