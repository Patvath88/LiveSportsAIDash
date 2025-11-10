from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ---------- Database setup ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./nba_ai.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- Model Definition ----------
class ModelAccuracy(Base):
    __tablename__ = "model_accuracy"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, default=lambda: datetime.now().isoformat(timespec='seconds'))
    metric_name = Column(String, default="overall_accuracy")
    value = Column(Float)

# ---------- Create all tables ----------
Base.metadata.create_all(bind=engine)

