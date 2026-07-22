from sqlalchemy.orm import Session

from app.db.models import ContactDB
from app.models.contact import ContactRecord, Sentiment


class ContactRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, contact: ContactRecord) -> ContactRecord:
        db_contact = ContactDB(
            id=str(contact.id),
            name=contact.name,
            phone=contact.phone,
            email=str(contact.email),
            comment=contact.comment,
            sentiment=contact.ai_analysis.sentiment.value if contact.ai_analysis else Sentiment.unknown.value,
            category=contact.ai_analysis.category if contact.ai_analysis else None,
            suggested_reply=contact.ai_analysis.suggested_reply if contact.ai_analysis else None,
            ai_available=contact.ai_analysis.is_available if contact.ai_analysis else False,
            created_at=contact.created_at,
        )
        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return contact

    def count(self) -> int:
        return self.db.query(ContactDB).count()

    def list_all(self) -> list[dict]:
        records = self.db.query(ContactDB).order_by(ContactDB.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "phone": r.phone,
                "email": r.email,
                "comment": r.comment,
                "ai_analysis": {
                    "sentiment": r.sentiment,
                    "category": r.category,
                    "suggested_reply": r.suggested_reply,
                    "is_available": r.ai_available,
                },
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
