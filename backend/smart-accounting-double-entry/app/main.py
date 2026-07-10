from fastapi import FastAPI
from api import health, accounts, documents, double_entry
from config.settings import settings
from infrastructure.database import Base, engine
import models  # Import to register all SQLAlchemy models before metadata creation

# Automatically create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(documents.router)
app.include_router(double_entry.router)

@app.get("/")
def read_root():
    return {"message": "SmartDE DoubleEntry API"}
