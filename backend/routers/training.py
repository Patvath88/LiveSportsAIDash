from fastapi import APIRouter
from models.database import SessionLocal, ModelAccuracy
from datetime import datetime
import random

router = APIRouter(prefix="/train", tags=["Training"])

@router.post("/")
def train_model():
    """
    Simulates model training and logs accuracy to SQLite.
    Later, replace random accuracy with real model results.
    """
    db = SessionLocal()
    try:
        # Simulate model training accuracy
        accuracy = round(random.uniform(0.65, 0.9), 3)

        # Create new accuracy record
        record = ModelAccuracy(
            timestamp=datetime.now().isoformat(timespec='seconds'),
            metric_name="overall_accuracy",
            value=accuracy
        )

        db.add(record)
        db.commit()

        return {
            "message": "Model retrained successfully!",
            "timestamp": record.timestamp,
            "accuracy": accuracy
        }
    finally:
        db.close()
