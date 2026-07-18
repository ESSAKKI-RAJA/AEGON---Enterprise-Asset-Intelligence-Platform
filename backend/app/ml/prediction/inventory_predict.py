import os
import joblib
from typing import List

from pydantic import BaseModel

class InventoryForecastDTO(BaseModel):
    asset_id: str
    forecast_30_days: int
    forecast_90_days: int
    recommended_reorder_point: int
    safety_stock: int
    inventory_risk: str

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
PROPHET_MODEL_PATH = os.path.join(MODEL_DIR, "inventory_prophet.pkl")

_prophet_model = None

def get_prophet_model():
    global _prophet_model
    if _prophet_model is None:
        if os.path.exists(PROPHET_MODEL_PATH):
            _prophet_model = joblib.load(PROPHET_MODEL_PATH)
        else:
            raise FileNotFoundError("Prophet model not found.")
    return _prophet_model

def predict_inventory(items_data: List[dict]) -> List[InventoryForecastDTO]:
    """
    items_data: list of dicts with 'asset_id', 'unit_price', 'current_quantity'
    """
    model = get_prophet_model()
    
    # Generate future dates
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    
    # Get last 30 and 90 days total forecasted demand (global)
    last_30_global = forecast['yhat'].iloc[-30:].sum()
    last_90_global = forecast['yhat'].iloc[-90:].sum()
    
    # We trained on aggregated sum. We need to scale it down per item.
    # We estimate total global base demand was roughly 1000 items * avg demand.
    # To avoid complex SQL joins during fast inference, we just use the item's price.
    
    results = []
    for item in items_data:
        base_demand = max(1, 100 / max(1, item.get('unit_price', 10.0)))
        
        # Scaling factor: base_demand / (avg_global_demand_per_item * num_items)
        # We simplify this by just giving each item a scaled fraction.
        item_scale = base_demand / 1000.0 # Approximation
        
        demand_30 = int(last_30_global * item_scale)
        demand_90 = int(last_90_global * item_scale)
        
        # Safety stock is usually Z * std_dev * sqrt(lead_time). 
        # Using heuristic: 20% of 30 day demand.
        safety_stock = int(demand_30 * 0.2)
        reorder_point = int((demand_30 / 30.0) * 14.0) + safety_stock # assuming 14 days lead time
        
        qty = item.get('current_quantity', 0)
        if qty < safety_stock:
            risk = "CRITICAL"
        elif qty < reorder_point:
            risk = "HIGH"
        elif qty > demand_90:
            risk = "OVERSTOCKED"
        else:
            risk = "HEALTHY"
            
        results.append(InventoryForecastDTO(
            asset_id=str(item['asset_id']),
            forecast_30_days=demand_30,
            forecast_90_days=demand_90,
            recommended_reorder_point=reorder_point,
            safety_stock=safety_stock,
            inventory_risk=risk
        ))
        
    return results
