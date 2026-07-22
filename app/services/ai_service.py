import json
import logging

from openai import AsyncOpenAI, OpenAIError

from app.core.config import Settings
from app.models.contact import AIAnalysis, ContactRequest, Sentiment

logger = logging.getLogger(__name__)


class AIService:
    """
    Service responsible for AI-powered contact form analysis.

    Primary flow:
    - send contact data to the AI provider (OpenRouter, OpenAI-compatible API);
    - receive sentiment, category and suggested reply;
    - return normalized AIAnalysis.

    Fallback flow:
    - if the AI provider is unavailable, misconfigured or out of quota,
      return a safe local rule-based fallback result;
    - never break the main contact form flow.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client: AsyncOpenAI | None = None

        if settings.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=settings.openai_timeout_seconds,
            )

    async def analyze_contact(self, contact: ContactRequest) -> AIAnalysis:
        if self.client is None:
            logger.warning(
                "AI provider key is not configured. Local fallback activated."
            )
            return self._local_fallback(contact)

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You analyze landing page contact form messages. "
                            "Return only valid JSON without markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(contact),
                    },
                ],
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("AI provider returned empty response.")

            payload = json.loads(content)

            sentiment = payload.get("sentiment", Sentiment.unknown.value)
            if sentiment not in {item.value for item in Sentiment}:
                sentiment = Sentiment.unknown.value

            return AIAnalysis(
                sentiment=Sentiment(sentiment),
                category=payload.get("category") or "other",
                suggested_reply=payload.get("suggested_reply"),
                is_available=True,
            )

        except (OpenAIError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                "AI provider failed. Local fallback activated. Reason: %s",
                exc,
                exc_info=True,
            )
            return self._local_fallback(contact)

    def _build_prompt(self, contact: ContactRequest) -> str:
        return f"""
Analyze the following landing page contact form submission.

Return strictly valid JSON with this schema:
{{
  "sentiment": "positive | neutral | negative",
  "category": "pricing | cooperation | technical_question | complaint | other",
  "suggested_reply": "A short polite reply in Russian, 2-4 sentences"
}}

Rules:
- sentiment must be one of: positive, neutral, negative.
- category must be one of: pricing, cooperation, technical_question, complaint, other.
- suggested_reply must be friendly, professional and relevant to the user's message.
- Do not include markdown.
- Do not include any text outside JSON.
- If the message is too vague, use neutral sentiment and other category.

Contact data:
Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}
Comment: {contact.comment}
""".strip()

    def _local_fallback(self, contact: ContactRequest) -> AIAnalysis:
        """Deterministic rule-based analysis used when the AI provider fails."""
        comment = contact.comment.lower()

        negative_words = [
            "плохо",
            "ужасно",
            "недоволен",
            "недовольна",
            "жалоба",
            "проблема",
            "не ответили",
        ]

        positive_words = [
            "понравилось",
            "отлично",
            "классно",
            "супер",
            "хорошо",
            "заинтересовало",
            "интересно",
        ]

        pricing_words = [
            "цена",
            "стоимость",
            "сколько стоит",
            "прайс",
            "бюджет",
        ]

        cooperation_words = [
            "сотрудничество",
            "партнерство",
            "партнёрство",
            "работать вместе",
        ]

        technical_words = [
            "api",
            "crm",
            "интеграция",
            "ошибка",
            "технический",
            "backend",
            "бэкенд",
        ]

        if any(word in comment for word in negative_words):
            sentiment = Sentiment.negative
        elif any(word in comment for word in positive_words):
            sentiment = Sentiment.positive
        else:
            sentiment = Sentiment.neutral

        if any(word in comment for word in pricing_words):
            category = "pricing"
        elif any(word in comment for word in cooperation_words):
            category = "cooperation"
        elif any(word in comment for word in technical_words):
            category = "technical_question"
        elif sentiment == Sentiment.negative:
            category = "complaint"
        else:
            category = "other"

        return AIAnalysis(
            sentiment=sentiment,
            category=category,
            suggested_reply=self._build_fallback_reply(contact.name, category),
            is_available=False,
        )

    def _build_fallback_reply(self, name: str, category: str) -> str:
        replies = {
            "pricing": (
                f"Здравствуйте, {name}! Спасибо за обращение. "
                "Мы получили ваш запрос по стоимости и скоро свяжемся с вами, "
                "чтобы уточнить детали проекта."
            ),
            "cooperation": (
                f"Здравствуйте, {name}! Спасибо за интерес к сотрудничеству. "
                "Мы получили ваше сообщение и скоро свяжемся с вами для обсуждения "
                "возможных вариантов работы."
            ),
            "technical_question": (
                f"Здравствуйте, {name}! Спасибо за ваш технический вопрос. "
                "Мы изучим детали обращения и скоро вернемся с ответом."
            ),
            "complaint": (
                f"Здравствуйте, {name}! Спасибо, что сообщили о проблеме. "
                "Мы внимательно рассмотрим ваше обращение и постараемся как можно "
                "быстрее помочь."
            ),
            "other": (
                f"Здравствуйте, {name}! Спасибо за обращение. "
                "Мы получили ваше сообщение и скоро свяжемся с вами."
            ),
        }

        return replies.get(category, replies["other"])
