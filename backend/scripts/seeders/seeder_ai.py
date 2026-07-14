import random
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ai import HealthScore, FailurePrediction, RemainingUsefulLife
from app.models.notifications import Notification
from app.models.identity import AuditLog, User
from app.models.asset import Asset
from app.models.enums import HealthStatus, FailureRisk
from scripts.seeder_core import check_table_empty, fake, random_future_date

async def seed_ai_analytics(session: AsyncSession):
    print("Seeding AI and Analytics...")

    assets = (await session.execute(select(Asset))).scalars().all()
    users = (await session.execute(select(User.id))).scalars().all()

    if await check_table_empty(session, HealthScore) and assets:
        scores = []
        for asset in assets:
            # Match the health status assigned to the asset
            status = asset.health_status.upper() if asset.health_status else "GOOD"
            if status == "EXCELLENT": enum_stat = HealthStatus.EXCELLENT
            elif status == "GOOD": enum_stat = HealthStatus.GOOD
            elif status == "FAIR": enum_stat = HealthStatus.FAIR
            else: enum_stat = HealthStatus.POOR
                
            scores.append(HealthScore(
                id=uuid.uuid4(),
                asset_id=asset.id,
                score=asset.health_score if asset.health_score else round(random.uniform(70, 100), 1),
                status=enum_stat
            ))
        session.add_all(scores)
        await session.commit()
        print(f"Inserted {len(scores)} Health Scores")

    if await check_table_empty(session, FailurePrediction) and assets:
        preds = []
        for asset in assets:
            # Simulate ML reasoning: older assets have higher risk
            if asset.health_score and asset.health_score < 50:
                prob = round(random.uniform(0.70, 0.99), 2)
                risk = FailureRisk.HIGH
                days_to_fail = random.randint(5, 30)
            elif asset.health_score and asset.health_score < 80:
                prob = round(random.uniform(0.30, 0.69), 2)
                risk = FailureRisk.MEDIUM
                days_to_fail = random.randint(31, 180)
            else:
                prob = round(random.uniform(0.01, 0.29), 2)
                risk = FailureRisk.LOW
                days_to_fail = random.randint(181, 700)
                
            preds.append(FailurePrediction(
                id=uuid.uuid4(),
                asset_id=asset.id,
                estimated_failure_date=random_future_date(days_to_fail).date(),
                probability=prob,
                risk_level=risk
            ))
        session.add_all(preds)
        await session.commit()
        print(f"Inserted {len(preds)} Failure Predictions")

    if await check_table_empty(session, RemainingUsefulLife) and assets:
        ruls = []
        for asset in assets:
            # RUL corresponds roughly to health score
            base_rul = (asset.health_score / 100.0) * 120.0 if asset.health_score else 60.0
            ruls.append(RemainingUsefulLife(
                id=uuid.uuid4(),
                asset_id=asset.id,
                estimated_remaining_months=round(base_rul * random.uniform(0.8, 1.2), 1)
            ))
        session.add_all(ruls)
        await session.commit()
        print(f"Inserted {len(ruls)} Remaining Useful Life records")

    if await check_table_empty(session, Notification) and users:
        from app.models.enums import NotificationStatus
        notifications = []
        for i in range(250):
            notifications.append(Notification(
                id=uuid.uuid4(),
                recipient_user_id=random.choice(users),
                subject=f"System Alert: {fake.catch_phrase()}",
                body=fake.paragraph(),
                status=NotificationStatus.UNREAD
            ))
        session.add_all(notifications)
        await session.commit()
        print(f"Inserted {len(notifications)} Notifications")

    if await check_table_empty(session, AuditLog) and users:
        logs = []
        actions = ["CREATE", "UPDATE", "DELETE", "LOGIN", "EXPORT", "APPROVE", "REJECT"]
        tables = ["assets", "work_orders", "users", "invoices", "purchase_orders", "inventory_items"]
        for i in range(1000):
            logs.append(AuditLog(
                id=uuid.uuid4(),
                user_id=random.choice(users),
                action=random.choice(actions),
                table_name=random.choice(tables),
                record_id=uuid.uuid4(),
                old_values=None,
                new_values='{"status": "processed", "user_agent": "Mozilla/5.0 AEGON_Enterprise_Client/1.0"}'
            ))
        session.add_all(logs)
        await session.commit()
        print(f"Inserted {len(logs)} Audit Logs")
