from src.infrastructure.database.database import Database, Base
from src.infrastructure.database.tables.detection import Detection



class FakeDB:
    def __init__(self, url: str) -> None:
        self._db = Database(url=url)
        self._create_all()
    
    def _create_all(self):
        Base.metadata.create_all(self._db._engine)
