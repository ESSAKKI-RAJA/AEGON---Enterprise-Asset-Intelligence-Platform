import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import numpy as np

from app.models.inventory import InventoryItem

async def build_inventory_history_features(session: AsyncSession) -> pd.DataFrame:
    """
    Generates synthetic daily consumption history for Prophet training.
    """
    items_stmt = select(InventoryItem)
    items_res = await session.execute(items_stmt)
    items = items_res.scalars().all()
    
    data = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365) # 1 year of history
    dates = pd.date_range(start=start_date, end=end_date)
    
    for item in items:
        # Base daily demand based on unit price and current quantity
        # Cheaper items are consumed more often
        base_demand = max(1, 100 / max(1, item.unit_price)) 
        
        # Add seasonality (e.g. higher demand in summer)
        for d in dates:
            # 1. Base demand
            demand = base_demand
            
            # 2. Seasonality (sine wave)
            day_of_year = d.timetuple().tm_yday
            seasonality = np.sin(2 * np.pi * day_of_year / 365.25) * (base_demand * 0.5)
            
            # 3. Random noise
            noise = np.random.normal(0, base_demand * 0.2)
            
            # 4. Weekly pattern (less demand on weekends)
            if d.weekday() >= 5:
                demand *= 0.3
                
            final_demand = max(0, int(demand + seasonality + noise))
            
            data.append({
                "asset_id": str(item.id), # We map it to asset_id key for consistency in pipeline
                "ds": d,
                "y": final_demand
            })
            
    return pd.DataFrame(data)
