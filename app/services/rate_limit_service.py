import time

from app.core.exceptions import RateLimitExceededException
from app.repositories.rate_limit_repository import RateLimitRepository


class RateLimitService:
    """Sliding-window rate limiter backed by a JSON file."""

    def __init__(
        self,
        repository: RateLimitRepository,
        *,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        self.repository = repository
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def check(self, client_id: str) -> None:
        now = time.time()
        data = self.repository.get_all()

        active_records = [
            timestamp
            for timestamp in data.get(client_id, [])
            if now - float(timestamp) < self.window_seconds
        ]

        if len(active_records) >= self.max_requests:
            raise RateLimitExceededException()

        active_records.append(now)
        data[client_id] = active_records

        self.repository.save_all(self._cleanup(data, now))

    def _cleanup(self, data: dict, now: float) -> dict:
        cleaned: dict = {}

        for client_id, timestamps in data.items():
            active = [
                timestamp
                for timestamp in timestamps
                if now - float(timestamp) < self.window_seconds
            ]
            if active:
                cleaned[client_id] = active

        return cleaned
