import time
import logging
from typing import Dict, Any

# Configure structured logging for ML Observability
logger = logging.getLogger("ml_observability")
logger.setLevel(logging.INFO)

class MLObservability:
    """
    Tracks inference counts, latencies, model versions, and detects drift.
    """
    
    @staticmethod
    def log_inference(model_name: str, version: str, start_time: float, num_records: int, metadata: Dict[str, Any] = None):
        latency_ms = (time.time() - start_time) * 1000
        avg_latency = latency_ms / max(1, num_records)
        
        log_data = {
            "event": "inference",
            "model_name": model_name,
            "version": version,
            "latency_ms": round(latency_ms, 2),
            "avg_latency_per_record_ms": round(avg_latency, 2),
            "records_processed": num_records
        }
        
        if metadata:
            log_data.update(metadata)
            
        logger.info(f"ML Inference Log: {log_data}")
        
    @staticmethod
    def detect_drift(model_name: str, baseline_feature_means: Dict[str, float], current_feature_means: Dict[str, float]) -> bool:
        """
        Simple data drift detection comparing feature means against baselines.
        Returns True if significant drift is detected.
        """
        drift_detected = False
        for feature, baseline in baseline_feature_means.items():
            current = current_feature_means.get(feature, baseline)
            # Flag if mean drifted by more than 20%
            if baseline > 0 and abs(current - baseline) / baseline > 0.2:
                logger.warning(f"Data Drift Detected in {model_name} on feature {feature}: baseline={baseline}, current={current}")
                drift_detected = True
                
        return drift_detected
