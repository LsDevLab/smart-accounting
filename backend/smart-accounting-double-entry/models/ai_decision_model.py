from sqlalchemy import Column, String, Float, JSON
from infrastructure.database import Base

class AIDecisionLogModel(Base):
    __tablename__ = "ai_decision_logs"
    id = Column(String, primary_key=True)
    raw_description = Column(String, nullable=False)
    mapped_account = Column(String, nullable=False)
    confidence = Column(Float)
