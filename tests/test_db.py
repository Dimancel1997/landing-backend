import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.models.contact import AIAnalysis, ContactRecord, Sentiment
from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.rate_limit_repository import RateLimitRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_contact_repository_db(db_session):
    repo = ContactRepository(db_session)
    assert repo.count() == 0

    record = ContactRecord(
        name="Тест Имя",
        phone="+79991112233",
        email="test@example.com",
        comment="Тестовое сообщение для базы данных",
        ai_analysis=AIAnalysis(
            sentiment=Sentiment.positive,
            category="pricing",
            suggested_reply="Ответ AI",
            is_available=True,
        ),
    )

    repo.create(record)
    assert repo.count() == 1

    all_contacts = repo.list_all()
    assert len(all_contacts) == 1
    assert all_contacts[0]["name"] == "Тест Имя"
    assert all_contacts[0]["ai_analysis"]["sentiment"] == "positive"


def test_metrics_repository_db(db_session):
    repo = MetricsRepository(db_session)
    metrics = repo.get()
    assert metrics["total_contacts"] == 0

    repo.save({
        "total_contacts": 10,
        "ai_success_count": 8,
        "ai_fallback_count": 2,
        "sentiment_distribution": {
            "positive": 5,
            "neutral": 3,
            "negative": 2,
            "unknown": 0,
        },
    })

    updated = repo.get()
    assert updated["total_contacts"] == 10
    assert updated["ai_success_count"] == 8
    assert updated["sentiment_distribution"]["positive"] == 5


def test_rate_limit_repository_db(db_session):
    repo = RateLimitRepository(db_session)
    assert repo.get_all() == {}

    repo.save_all({"127.0.0.1": [100.0, 105.0]})
    data = repo.get_all()
    assert "127.0.0.1" in data
    assert data["127.0.0.1"] == [100.0, 105.0]
