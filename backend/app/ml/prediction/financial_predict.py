import os
import joblib
from pydantic import BaseModel

class FinancialForecastDTO(BaseModel):
    capex_30_days: float
    opex_30_days: float
    capex_90_days: float
    opex_90_days: float

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
FINANCE_CAPEX_MODEL = os.path.join(MODEL_DIR, "finance_capex_prophet.pkl")
FINANCE_OPEX_MODEL = os.path.join(MODEL_DIR, "finance_opex_prophet.pkl")

_capex_model = None
_opex_model = None

def get_financial_models():
    global _capex_model, _opex_model
    if _capex_model is None:
        if os.path.exists(FINANCE_CAPEX_MODEL):
            _capex_model = joblib.load(FINANCE_CAPEX_MODEL)
            _opex_model = joblib.load(FINANCE_OPEX_MODEL)
        else:
            raise FileNotFoundError("Financial models not found.")
    return _capex_model, _opex_model

def predict_financials() -> FinancialForecastDTO:
    capex_model, opex_model = get_financial_models()
    
    future = capex_model.make_future_dataframe(periods=90)
    
    capex_forecast = capex_model.predict(future)
    opex_forecast = opex_model.predict(future)
    
    capex_30 = capex_forecast['yhat'].iloc[-30:].sum()
    capex_90 = capex_forecast['yhat'].iloc[-90:].sum()
    
    opex_30 = opex_forecast['yhat'].iloc[-30:].sum()
    opex_90 = opex_forecast['yhat'].iloc[-90:].sum()
    
    return FinancialForecastDTO(
        capex_30_days=round(float(max(0, capex_30)), 2),
        opex_30_days=round(float(max(0, opex_30)), 2),
        capex_90_days=round(float(max(0, capex_90)), 2),
        opex_90_days=round(float(max(0, opex_90)), 2)
    )
