from pathlib import Path

from app.models.contact import ContactRecord
from app.repositories.json_repository import JsonRepository


class ContactRepository:
    def __init__(self, storage_dir: Path) -> None:
        self.repository = JsonRepository(
            file_path=storage_dir / "contacts.json",
            default_data=[],
        )

    def create(self, contact: ContactRecord) -> ContactRecord:
        contacts = self.repository.read()
        contacts.append(contact.model_dump(mode="json"))
        self.repository.write(contacts)
        return contact

    def count(self) -> int:
        return len(self.repository.read())

    def list_all(self) -> list[dict]:
        return self.repository.read()
