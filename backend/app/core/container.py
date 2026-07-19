from dependency_injector import containers, providers
from app.repositories.user import UserRepository
from app.repositories.asset import AssetRepository
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.asset_service import AssetService
from app.services.maintenance_service import MaintenanceService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.finance_service import FinanceService
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService
from app.services.copilot_service import CopilotService
from app.services.search_service import SearchService
from app.services.storage_service import StorageService
from app.core.database import AsyncSessionLocal
from app.repositories.base import UnitOfWork
from app.core.cache import RedisCacheHook
from app.core.audit import DatabaseAuditHook

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.api.v1"])

    # Database — lazy resolution: AsyncSessionLocal is None until init_db() runs in lifespan.
    # Using a lambda factory ensures we never freeze a None reference at import time.
    db_session = providers.Factory(lambda: __import__('app.core.database', fromlist=['AsyncSessionLocal']).AsyncSessionLocal())

    # Repositories (provided as classes/factories to be bound to request sessions)
    user_repository = providers.Object(UserRepository)
    asset_repository = providers.Object(AssetRepository)

    # Hooks
    cache_hook = providers.Singleton(RedisCacheHook)
    audit_hook = providers.Factory(DatabaseAuditHook, session=db_session)

    # Core Services
    storage_service = providers.Factory(StorageService)

    # Business Services
    auth_service = providers.Factory(AuthService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    user_service = providers.Factory(UserService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    asset_service = providers.Factory(AssetService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    maintenance_service = providers.Factory(MaintenanceService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    inventory_service = providers.Factory(InventoryService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    procurement_service = providers.Factory(ProcurementService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    finance_service = providers.Factory(FinanceService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    analytics_service = providers.Factory(
        AnalyticsService, 
        asset_service=asset_service,
        maintenance_service=maintenance_service,
        uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook)
    )
    ai_service = providers.Factory(AIService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    copilot_service = providers.Factory(CopilotService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
    search_service = providers.Factory(SearchService, uow=providers.Factory(UnitOfWork, session=db_session, cache_hook=cache_hook, audit_hook=audit_hook))
