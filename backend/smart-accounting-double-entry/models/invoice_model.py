from sqlalchemy import Column, String, Float, DateTime
from infrastructure.database import Base

class InvoiceModel(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False) # total amount
    vat_rate = Column(Float, nullable=False, default=0.22)
    sender_vat = Column(String, nullable=True)
    receiver_vat = Column(String, nullable=True)
    document_type = Column(String, nullable=False) # ENTRATA (active/sales) or USCITA (passive/purchase)
    created_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="RECEIVED") # RECEIVED, AI_ANALYZED, COMPLETED, FAILED
    mapped_account = Column(String, nullable=True) # Free-text account string (no accounts DB needed)
