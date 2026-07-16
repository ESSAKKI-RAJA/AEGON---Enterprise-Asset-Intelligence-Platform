# Enterprise Vision Intelligence

The Vision Intelligence module enables automated defect detection, asset health monitoring, and operational safety compliance through advanced computer vision.

## Architecture

The Vision Intelligence pipeline is designed to be decoupled from the core API to ensure that heavy GPU/CPU workloads do not block standard HTTP requests.

### 1. Ingestion Layer
- **Sources**: Real-time RTSP streams (IP cameras), scheduled batch uploads from drones, or manual mobile uploads.
- **Processing**: The API receives the payload, validates the metadata (asset ID, timestamp), and queues the payload into RabbitMQ.

### 2. Inference Engine (Celery Worker)
- **Frameworks**: OpenCV for image preprocessing, PyTorch/ONNX for model inference (e.g., YOLO variants).
- **Execution**: A dedicated Celery worker pulls the image, loads the cached ML model into memory, and executes the inference pass.
- **Output**: Generates a bounding box array, confidence scores, and defect classification.

### 3. Action Layer (Business Rules)
- The results are passed back to the `VisionIntelligenceService`.
- If a defect meets a critical threshold (e.g., Confidence > 85% on an active asset), the Service automatically interacts with the `MaintenanceService` to generate an urgent Maintenance Ticket.

## Model Metadata and Observability

To maintain enterprise accountability, every AI prediction is logged permanently. The `ai_predictions` table records:
- `model_version`: The exact hash/version of the model used.
- `inference_latency`: Processing time in milliseconds.
- `confidence`: The raw confidence output from the model.
- `bounding_boxes`: The spatial location of the defect.

This data is surfaced in the Executive Dashboard to track AI reliability and drift over time.

## Future Extensibility

The pipeline is designed using the Strategy Pattern. Integrating a new model (e.g., a custom transformer model for microscopic defect detection) only requires implementing a new `InferenceStrategy` class. The API routing, queuing, and action layers remain untouched.
