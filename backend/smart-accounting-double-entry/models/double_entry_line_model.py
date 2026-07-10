from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class DoubleEntryLineModel(Base):
    __tablename__ = "double_entry_lines"
    id = Column(String, primary_key=True)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=False)
    account_code = Column(String, nullable=False) # Stores account name or code as free text
    is_debit = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)

    journal_entry = relationship("JournalEntryModel", back_populates="lines")
