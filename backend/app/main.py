from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import auth, customers, documents, chat

app = FastAPI(
    title="AI Receptionist API",
    description="API backend pour la plateforme AI Receptionist SaaS",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
