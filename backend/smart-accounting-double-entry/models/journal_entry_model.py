from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    entry_date = Column(DateTime)
    document_reference = Column(String, nullable=True)
    
    lines = relationship("DoubleEntryLineModel", back_populates="journal_entry", cascade="all, delete-orphan")
