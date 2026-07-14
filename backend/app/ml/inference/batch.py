from typing import Dict, Any, List
from app.ml.dto.prediction import PredictionDTO
from app.ml.inference.real_time import real_time_predictor
import asyncio

class BatchPredictor:
    """Handles bulk asynchronous prediction requests for nightly jobs."""
    
    async def predict_batch(self, model_name: str, batch_features: List[Dict[str, Any]]) -> List[PredictionDTO]:
        """Processes a list of feature sets asynchronously."""
        # Simulate offloading to a distributed queue or thread pool
        loop = asyncio.get_event_loop()
        tasks = []
        for features in batch_features:
            tasks.append(loop.run_in_executor(None, real_time_predictor.predict, model_name, features))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out errors in a real system
        return [res for res in results if not isinstance(res, Exception) and res is not None]

batch_predictor = BatchPredictor()
