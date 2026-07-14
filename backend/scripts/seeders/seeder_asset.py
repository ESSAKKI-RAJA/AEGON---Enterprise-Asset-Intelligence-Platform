import random
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset, AssetCategory, AssetSubCategory, Vendor
from app.models.organization import Department
from app.models.inventory import Warehouse, InventoryItem, StockAlert
from scripts.seeder_core import check_table_empty, fake, random_past_date, random_future_date

async def seed_asset_inventory(session: AsyncSession):
    print("Seeding Assets and Inventory...")

    if await check_table_empty(session, Asset):
        categories = (await session.execute(select(AssetCategory.id))).scalars().all()
        subcategories = (await session.execute(select(AssetSubCategory.id))).scalars().all()
        departments = (await session.execute(select(Department.id))).scalars().all()
        vendors = (await session.execute(select(Vendor.id))).scalars().all()
        
        # 500 Enterprise Assets
        assets = []
        for i in range(500):
            purchased = random_past_date(1800)
            
            # Make costs realistic for enterprise equipment
            cost = round(random.uniform(1500.0, 150000.0), 2)
            
            health = random.choice(["excellent", "good", "fair", "poor", "critical"])
            if health == "excellent": score = random.uniform(90, 100)
            elif health == "good": score = random.uniform(70, 89)
            elif health in ("fair", "poor"): score = random.uniform(40, 69)
            else: score = random.uniform(0, 39)
                
            assets.append(Asset(
                id=uuid.uuid4(),
                name=f"{fake.word().capitalize()} Asset - {fake.bothify('???-###')}",
                barcode=fake.ean13(),
                category_id=random.choice(categories) if categories else None,
                subcategory_id=random.choice(subcategories) if subcategories else None,
                department_id=random.choice(departments) if departments else None,
                vendor_id=random.choice(vendors) if vendors else None,
                purchase_date=purchased,
                purchase_cost=cost,
                current_value=cost * random.uniform(0.1, 0.9), # Depreciated
                warranty_expiry=random_future_date(700) if random.random() > 0.5 else random_past_date(100),
                health_score=round(score, 1),
                health_status=health,
                next_maintenance=random_future_date(90)
            ))
        session.add_all(assets)
        await session.commit()
        print(f"Inserted {len(assets)} Assets")

    if await check_table_empty(session, Warehouse):
        wh_names = ["Main Distribution Center", "Regional Hub A", "Regional Hub B", "Factory A Storage", "Factory B Storage"]
        warehouses = [Warehouse(id=uuid.uuid4(), name=name, code=name[:3].upper().replace(" ", "") + str(i)) for i, name in enumerate(wh_names)]
        session.add_all(warehouses)
        await session.commit()
        print(f"Inserted {len(warehouses)} Warehouses")

    if await check_table_empty(session, InventoryItem):
        warehouses = (await session.execute(select(Warehouse.id))).scalars().all()
        # 1000 Inventory Items
        items = []
        for i in range(1000):
            qty = random.randint(0, 500)
            reorder = random.randint(10, 100)
            
            # Stock Alerts integration: if qty < reorder, we might want to flag it later
            
            items.append(InventoryItem(
                id=uuid.uuid4(),
                name=f"Industrial Part {fake.bothify('??-###')}",
                sku=fake.unique.bothify('SKU-####-????'),
                quantity=qty,
                reorder_level=reorder,
                unit_price=round(random.uniform(1.0, 5000.0), 2),
                warehouse_id=random.choice(warehouses) if warehouses else None
            ))
        session.add_all(items)
        await session.commit()
        print(f"Inserted {len(items)} Inventory Items")

