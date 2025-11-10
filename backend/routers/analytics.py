from fastapi import APIRouter
from models.database import SessionLocal, ModelAccuracy

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/accuracy")
def get_accuracy_data():
    """
    Fetches logged model accuracies from SQLite for visualization.
    Each entry corresponds to a training run, ordered by time.
    """
    db = SessionLocal()
    try:
        records = db.query(ModelAccuracy).order_by(ModelAccuracy.id.asc()).all()
        return [{"date": r.timestamp, "accuracy": r.value} for r in records]
    finally:
        db.close()
