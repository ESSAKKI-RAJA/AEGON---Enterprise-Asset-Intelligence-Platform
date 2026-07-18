import glob

block = '''
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.asset import Asset, PurchaseOrder, VendorQuotation, Room, Recommendation, Prediction, DepreciationRecord, AssetDepreciation
    from app.models.identity import User, Department, Role, Permission
    from app.models.maintenance import WorkOrder, MaintenanceRecord, MaintenancePlan, MaintenanceTask, InventoryConsumption, InventoryReservation
    from app.models.inventory import InventoryItem, InventoryTransfer, StockAlert
    from app.models.procurement import PurchaseRequest, PurchaseRequestItem, PurchaseOrder as ProcPurchaseOrder, Vendor, Invoice, Quotation
    from app.models.organization import DepartmentBudget, Faculty, Floor, Building
    from app.models.finance import Budget
    from app.models.ai import Prediction as AIPrediction, Recommendation as AIRecommendation
'''

for file in glob.glob('app/models/*.py'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if block in content:
        new_content = content.replace(block + '\n', '')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
