import json
from typing import Any
from sqlalchemy.orm import Session

from app.db.models import RateLimitDB


class RateLimitRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> dict[str, Any]:
        rows = self.db.query(RateLimitDB).all()
        result: dict[str, Any] = {}
        for row in rows:
            try:
                result[row.key] = json.loads(row.timestamps_json)
            except Exception:
                result[row.key] = []
        return result

    def save_all(self, data: dict[str, Any]) -> None:
        existing = {r.key: r for r in self.db.query(RateLimitDB).all()}

        for key, timestamps in data.items():
            encoded = json.dumps(timestamps)
            if key in existing:
                existing[key].timestamps_json = encoded
            else:
                db_item = RateLimitDB(key=key, timestamps_json=encoded)
                self.db.add(db_item)

        for key, db_item in existing.items():
            if key not in data:
                self.db.delete(db_item)

        self.db.commit()
