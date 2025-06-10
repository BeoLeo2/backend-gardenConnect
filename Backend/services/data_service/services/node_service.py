"""Service nodes"""
from sqlmodel import Session

class NodeService:
    def __init__(self, db: Session):
        self.db = db
