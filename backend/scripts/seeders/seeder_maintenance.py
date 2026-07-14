import random
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.maintenance import MaintenancePlan, WorkOrder, MaintenanceRecord, TechnicianAssignment
from app.models.asset import Asset
from app.models.identity import User
from app.models.enums import WorkOrderStatus, Priority
from scripts.seeder_core import check_table_empty, fake, random_past_date, random_future_date

async def seed_maintenance(session: AsyncSession):
    print("Seeding Maintenance...")
    
    if await check_table_empty(session, MaintenancePlan):
        assets = (await session.execute(select(Asset.id))).scalars().all()
        # 100 Maintenance Plans
        plans = []
        for i in range(100):
            plans.append(MaintenancePlan(
                id=uuid.uuid4(),
                name=f"{fake.bs().capitalize()} Schedule",
                description=f"Preventive maintenance for {fake.catch_phrase()}",
                interval_days=random.choice([7, 14, 30, 90, 180, 365])
            ))
        session.add_all(plans)
        await session.commit()
        print(f"Inserted {len(plans)} Maintenance Plans")

    if await check_table_empty(session, WorkOrder):
        assets = (await session.execute(select(Asset.id))).scalars().all()
        users = (await session.execute(select(User.id))).scalars().all()
        
        # 350 Work Orders
        orders = []
        for i in range(350):
            orders.append(WorkOrder(
                id=uuid.uuid4(),
                wo_number=fake.unique.bothify('WO-######'),
                title=f"Maintenance - {fake.catch_phrase()}",
                description=f"Issue reported: {fake.sentence()}",
                status=random.choice(list(WorkOrderStatus)),
                priority=random.choice(list(Priority)),
                asset_id=random.choice(assets) if assets else None
            ))
        session.add_all(orders)
        await session.commit()
        
        # Technician Assignments
        assignments = []
        for wo in orders:
            if wo.status != WorkOrderStatus.OPEN:
                assignments.append(TechnicianAssignment(
                    id=uuid.uuid4(),
                    work_order_id=wo.id,
                    technician_user_id=random.choice(users) if users else None
                ))
        session.add_all(assignments)
        await session.commit()
        print(f"Inserted {len(orders)} Work Orders")
        
        # Maintenance Records (for completed/closed WOs)
        records = []
        for wo in orders:
            if wo.status == WorkOrderStatus.COMPLETED or random.random() > 0.7:
                records.append(MaintenanceRecord(
                    id=uuid.uuid4(),
                    description=f"Resolution: {fake.paragraph()}",
                    cost=round(random.uniform(100.0, 15000.0), 2),
                    maintenance_date=random_past_date(90),
                    maintenance_type=random.choice(["Routine", "Emergency", "Preventive", "Corrective"]),
                    asset_id=wo.asset_id
                ))
        session.add_all(records)
        await session.commit()
        print(f"Inserted {len(records)} Maintenance Records")
