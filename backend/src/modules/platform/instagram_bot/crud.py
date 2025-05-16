# src/modules/platform/instagram_bot/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_bot_report(db: Session, report: schemas.InstagramBotReportCreate):
    db_report = models.InstagramBotReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report
