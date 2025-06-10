"""Service data"""
from sqlmodel import Session

class DataService:
    def __init__(self, db: Session):
        self.db = db
