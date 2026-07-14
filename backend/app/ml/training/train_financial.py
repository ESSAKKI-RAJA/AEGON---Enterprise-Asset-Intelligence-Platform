import pandas as pd
from prophet import Prophet
import os
import joblib
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.models.finance import Budget, Expense
from app.core.database import AsyncSessionLocal

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
FINANCE_CAPEX_MODEL = os.path.join(MODEL_DIR, "finance_capex_prophet.pkl")
FINANCE_OPEX_MODEL = os.path.join(MODEL_DIR, "finance_opex_prophet.pkl")

async def build_financial_features() -> pd.DataFrame:
    # We simulate 3 years of daily financial aggregated data
    # In a real scenario we would group Expenses by date and type.
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365 * 3)
    dates = pd.date_range(start=start_date, end=end_date)
    
    data = []
    # Base daily OPEX and CAPEX
    base_opex = 5000
    base_capex = 2000
    
    for d in dates:
        # OPEX has weekly seasonality (more expenses on weekdays)
        # CAPEX is more sparse, high variance, quarterly spikes
        
        # OPEX
        opex = base_opex
        if d.weekday() >= 5: opex *= 0.2
        opex += np.random.normal(0, 500)
        
        # CAPEX (spikes at end of quarter)
        capex = base_capex + np.random.normal(0, 1000)
        if d.is_quarter_end:
            capex += np.random.uniform(10000, 50000)
            
        data.append({
            "ds": d,
            "opex": max(0, opex),
            "capex": max(0, capex)
        })
        
    return pd.DataFrame(data)

async def train_financial_models():
    print("Generating training data for Financial Intelligence...")
    df = await build_financial_features()
    
    print("Training OPEX Forecast Model...")
    opex_df = df[['ds', 'opex']].rename(columns={'opex': 'y'})
    opex_model = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    opex_model.fit(opex_df)
    
    print("Training CAPEX Forecast Model...")
    capex_df = df[['ds', 'capex']].rename(columns={'capex': 'y'})
    capex_model = Prophet(weekly_seasonality=False, yearly_seasonality=True)
    capex_model.fit(capex_df)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(opex_model, FINANCE_OPEX_MODEL)
    joblib.dump(capex_model, FINANCE_CAPEX_MODEL)
    
    print("Financial Models Trained and Saved.")

if __name__ == "__main__":
    import asyncio
    import logging
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
    logging.getLogger('prophet').setLevel(logging.WARNING)
    asyncio.run(train_financial_models())
