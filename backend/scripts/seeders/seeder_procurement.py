import random
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.procurement import PurchaseRequest, PurchaseOrder, Invoice
from app.models.finance import Budget, Expense, CostCenter
from app.models.enums import BudgetStatus
from app.models.organization import Department
from app.models.asset import Vendor
from scripts.seeder_core import check_table_empty, fake, random_past_date

async def seed_procurement_finance(session: AsyncSession):
    print("Seeding Procurement and Finance...")
    
    departments = (await session.execute(select(Department.id))).scalars().all()
    vendors = (await session.execute(select(Vendor.id))).scalars().all()

    if await check_table_empty(session, PurchaseRequest):
        # 300 Purchase Requests
        requests = []
        for i in range(300):
            requests.append(PurchaseRequest(
                id=uuid.uuid4(),
                title=f"Equipment PR - {fake.catch_phrase()}",
                justification=f"Required for operations: {fake.sentence()}",
                status=random.choice(["PENDING", "APPROVED", "REJECTED", "APPROVED"]),
                department_id=random.choice(departments) if departments else None
            ))
        session.add_all(requests)
        await session.commit()
        print(f"Inserted {len(requests)} Purchase Requests")
        
        # 200 Purchase Orders
        pos = []
        for i in range(200):
            pos.append(PurchaseOrder(
                id=uuid.uuid4(),
                po_number=fake.unique.bothify('PO-######'),
                order_date=random_past_date(180),
                total_amount=round(random.uniform(5000.0, 250000.0), 2),
                status=random.choice(["PENDING", "APPROVED", "COMPLETED"]),
                vendor_id=random.choice(vendors) if vendors else None
            ))
        session.add_all(pos)
        await session.commit()
        
        # Invoices
        invoices = []
        for po in pos:
            if po.status in ["APPROVED", "COMPLETED"] or random.random() > 0.5:
                invoices.append(Invoice(
                    id=uuid.uuid4(),
                    invoice_number=fake.unique.bothify('INV-######'),
                    purchase_order_id=po.id,
                    total_due=po.total_amount,
                    status=random.choice(["UNPAID", "PARTIAL", "PAID"])
                ))
        session.add_all(invoices)
        await session.commit()
        print(f"Inserted {len(pos)} POs and {len(invoices)} Invoices")

    if await check_table_empty(session, CostCenter):
        cc_names = ["Manufacturing Operations", "IT Infrastructure", "Facilities Management", "Logistics & Transport", "Corporate Services"]
        ccs = [CostCenter(id=uuid.uuid4(), name=name, code=f"CC{i+100}") for i, name in enumerate(cc_names)]
        session.add_all(ccs)
        await session.commit()

    if await check_table_empty(session, Budget):
        ccs = (await session.execute(select(CostCenter.id))).scalars().all()
        # 150 Budget Records
        budgets = []
        for i in range(150):
            budgets.append(Budget(
                id=uuid.uuid4(),
                fiscal_year=random.choice([2024, 2025, 2026]),
                total_amount=round(random.uniform(100000.0, 10000000.0), 2),
                status=random.choice(list(BudgetStatus)),
                cost_center_id=random.choice(ccs) if ccs else None
            ))
        session.add_all(budgets)
        await session.commit()
        print(f"Inserted {len(budgets)} Budget Records")

    if await check_table_empty(session, Expense):
        ccs = (await session.execute(select(CostCenter.id))).scalars().all()
        # 400 Expenses
        expenses = []
        for i in range(400):
            expenses.append(Expense(
                id=uuid.uuid4(),
                description=f"Expense for {fake.catch_phrase()}",
                amount=round(random.uniform(500.0, 50000.0), 2),
                expense_date=random_past_date(300),
                cost_center_id=random.choice(ccs) if ccs else None
            ))
        session.add_all(expenses)
        await session.commit()
        print(f"Inserted {len(expenses)} Expenses")
