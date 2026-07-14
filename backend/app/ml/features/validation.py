from typing import Dict, Any, List

class DataValidationError(Exception):
    pass

class FeatureValidator:
    """
    Validates datasets and features before they enter the feature store
    or training pipelines.
    """
    
    @staticmethod
    def validate_features(features: Dict[str, Any], required_keys: List[str]):
        """Checks for missing or invalid values."""
        errors = []
        
        for key in required_keys:
            if key not in features:
                errors.append(f"Missing required feature: {key}")
            elif features[key] is None:
                errors.append(f"Feature {key} cannot be None")
                
        # Basic outlier detection (e.g., negative age)
        if features.get("age_years", 0) < 0:
            errors.append("age_years cannot be negative")
            
        if features.get("utilization_rate", 0) < 0 or features.get("utilization_rate", 0) > 100:
            errors.append("utilization_rate must be between 0 and 100")
            
        if errors:
            raise DataValidationError(f"Feature validation failed: {', '.join(errors)}")
            
        return True
