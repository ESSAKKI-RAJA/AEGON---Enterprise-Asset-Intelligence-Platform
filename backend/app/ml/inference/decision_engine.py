import pandas as pd
from typing import List, Dict, Any
from pydantic import BaseModel

from app.ml.prediction.asset_failure_predict import predict_asset_failure
from app.ml.prediction.maintenance_predict import predict_maintenance
from app.ml.prediction.inventory_predict import predict_inventory

class DecisionRecommendation(BaseModel):
    asset_id: str
    priority_ranking: int
    recommended_action: str
    business_justification: str
    operational_impact: str
    financial_impact: str
    risk_impact: str
    confidence: float

class DecisionEngine:
    """
    Aggregates ML predictions (Failure, Maintenance, Inventory) 
    to generate Enterprise-grade decision recommendations.
    """
    
    def __init__(self):
        pass
        
    def generate_asset_decisions(self, asset_df: pd.DataFrame, inventory_data: List[dict]) -> List[DecisionRecommendation]:
        # 1. Get raw predictions
        failure_preds = {p.asset_id: p for p in predict_asset_failure(asset_df)}
        maint_preds = {p.asset_id: p for p in predict_maintenance(asset_df)}
        
        # Assume inventory_data maps asset_id to its inventory metrics
        inv_preds = {p.asset_id: p for p in predict_inventory(inventory_data)} if inventory_data else {}
        
        decisions = []
        for i, row in asset_df.iterrows():
            asset_id = str(row["asset_id"])
            f_pred = failure_preds.get(asset_id)
            m_pred = maint_preds.get(asset_id)
            i_pred = inv_preds.get(asset_id)
            
            if not f_pred or not m_pred:
                continue
                
            # Aggregate Risk and Financials
            priority_ranking = 0
            financial_loss = m_pred.estimated_maintenance_cost
            
            if f_pred.risk_category == "HIGH":
                priority_ranking += 100
                financial_loss += row.get("purchase_cost", 5000.0) * 0.5 # 50% loss on critical failure
            elif f_pred.risk_category == "MEDIUM":
                priority_ranking += 50
                financial_loss += row.get("purchase_cost", 5000.0) * 0.1
                
            if m_pred.recommended_priority in ["HIGH", "CRITICAL"]:
                priority_ranking += 40
                
            # Check inventory availability for parts
            stock_warning = ""
            if i_pred and i_pred.inventory_risk in ["HIGH", "CRITICAL"]:
                priority_ranking += 20
                stock_warning = " WARNING: Required parts are low in stock."
                
            # Synthesize Action
            if priority_ranking >= 100:
                action = f"Replace or overhaul immediately within {f_pred.remaining_useful_life_days} days."
                op_impact = "High risk of sudden operational halt."
                risk_impact = "CRITICAL"
            elif priority_ranking >= 50:
                action = f"Schedule preventative maintenance within {f_pred.remaining_useful_life_days} days."
                op_impact = "Moderate risk of unplanned downtime."
                risk_impact = "HIGH"
            else:
                action = "Continue routine monitoring."
                op_impact = "Normal operations."
                risk_impact = "LOW"
                
            justification = (
                f"Failure Prob: {f_pred.probability*100:.1f}%. "
                f"Reason: {f_pred.explanation.reasoning} "
                f"{stock_warning}"
            )
            
            # Confidence is a blended average of the underlying model confidences
            confidence = (f_pred.confidence + m_pred.priority_confidence) / 2.0
            
            decisions.append(DecisionRecommendation(
                asset_id=asset_id,
                priority_ranking=priority_ranking,
                recommended_action=action,
                business_justification=justification,
                operational_impact=op_impact,
                financial_impact=f"Estimated Exposure: ${financial_loss:,.2f}",
                risk_impact=risk_impact,
                confidence=round(confidence, 2)
            ))
            
        # Sort by priority
        decisions.sort(key=lambda x: x.priority_ranking, reverse=True)
        return decisions
