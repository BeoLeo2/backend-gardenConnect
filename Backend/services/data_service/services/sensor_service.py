"""Service sensors"""
from sqlmodel import Session

class SensorService:
    def __init__(self, db: Session):
        self.db = db
