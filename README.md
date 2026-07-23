# Landing Backend API

Backend-сервис для лендинг-презентации разработчика с REST API, формой обратной связи, реляционной базой данных (SQLAlchemy, SQLite/PostgreSQL), rate limiting, логированием и AI-интеграцией через OpenRouter (OpenAI-совместимый API).

## 🌐 Демо

Проект задеплоен на Render:

- **Swagger UI (интерактивная документация):** https://landing-backend-6a24.onrender.com/docs
- **Health check:** https://landing-backend-6a24.onrender.com/api/health

> ⚠️ Бесплатный тариф Render «засыпает» после 15 минут без запросов — первое открытие может занять 30–60 секунд.

## Возможности

- `POST /api/contact` — прием формы обратной связи.
- Валидация имени, телефона, email и комментария.
- Имитация email-уведомлений владельцу сайта и пользователю через логирование.
- AI-интеграция: анализ тональности, классификация типа обращения и генерация ответа.
- Двухуровневый graceful fallback:
  - если AI-провайдер недоступен (нет ключа, нет квоты, таймаут, ошибка API), включается локальный rule-based анализ;
  - основной сценарий обработки заявки никогда не ломается.
- Хранение данных в реляционной БД через **SQLAlchemy** (SQLite по умолчанию или PostgreSQL при переключении `DATABASE_URL`).
- `GET /api/health` — проверка статуса.
- `GET /api/metrics` — статистика обращений.
- Rate limiting через БД.
- Логирование всех запросов в файл.
- Глобальный error handler с корректными HTTP-статусами.
- CORS и конфигурация через `.env`.
- Swagger UI из коробки: `/docs`.

## Стек

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0+
- SQLite / PostgreSQL
- OpenAI Python SDK (клиент для OpenRouter)
- Poetry / pip

## Архитектура

```text
Routers / Controllers  ->  Services / Business Logic  ->  Repositories  ->  SQLAlchemy ORM (SQLite / PostgreSQL)
```

- **Роутеры** (`app/api`) принимают HTTP-запросы, валидируют их через Pydantic и вызывают сервисы.
- **Сервисы** (`app/services`) содержат бизнес-логику: обработка заявки, AI-анализ, email, метрики, rate limiting.
- **База данных и модели** (`app/db`) содержат сессии SQLAlchemy и ORM-модели `ContactDB`, `MetricsDB`, `RateLimitDB`.
- **Репозитории** (`app/repositories`) отвечают за изоляцию операций с базой данных через SQLAlchemy Session.

### Структура проекта

```text
landing-backend/
├── app/
│   ├── main.py                  # Точка входа, CORS, error handlers
│   ├── api/
│   │   ├── deps.py              # Dependency injection
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── contact.py
│   │           ├── health.py
│   │           └── metrics.py
│   ├── core/
│   │   ├── config.py            # Настройки из .env
│   │   ├── exceptions.py        # Кастомные исключения
│   │   ├── logging.py           # Настройка логов
│   │   └── middleware.py        # Логирование запросов
│   ├── db/                      # SQLAlchemy сессии и ORM-модели (ContactDB, MetricsDB, RateLimitDB)
│   ├── models/                  # Pydantic-модели (DTO/schemas)
│   ├── repositories/            # Репозиторный слой абстракции над SQLAlchemy Session
│   ├── services/                # Бизнес-логика
│   └── storage/                 # Хранилище SQLite базы данных (landing.db)
├── logs/
├── tests/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Запуск

### Через Poetry

```bash
cp .env.example .env
poetry install
poetry run uvicorn app.main:app --reload
```

### Через pip

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

## Переменные окружения

См. `.env.example`. Ключевые:

| Переменная | Описание |
|---|---|
| `DATABASE_URL` | Строка подключения к БД (`sqlite:///./app/storage/landing.db` по умолчанию или `postgresql://...`) |
| `OPENAI_API_KEY` | Ключ OpenRouter (`sk-or-v1-...`), https://openrouter.ai/keys |
| `OPENAI_BASE_URL` | Адрес API. По умолчанию `https://openrouter.ai/api/v1` |
| `OPENAI_MODEL` | Модель, напр. `openai/gpt-4o-mini` или бесплатная `meta-llama/llama-3.1-8b-instruct:free` |
| `RATE_LIMIT_MAX_REQUESTS` | Запросов на IP за окно (по умолчанию 5) |
| `RATE_LIMIT_WINDOW_SECONDS` | Длина окна (по умолчанию 60 сек) |

Если `OPENAI_API_KEY` пустой — сервис работает с локальным fallback-анализом.

## API

### `GET /api/health`

```bash
curl http://localhost:8000/api/health
```

### `POST /api/contact`

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Петров",
    "phone": "+7 999 123-45-67",
    "email": "ivan@example.com",
    "comment": "Здравствуйте! Хочу узнать стоимость разработки лендинга."
  }'
```

Ответ (AI доступен):

```json
{
  "id": "a2e7e4d4-b8ce-4b2d-a2ad-9e2f5cdd85e4",
  "status": "accepted",
  "message": "Contact request has been accepted.",
  "ai_analysis": {
    "sentiment": "neutral",
    "category": "pricing",
    "suggested_reply": "Здравствуйте, Иван! Спасибо за обращение...",
    "is_available": true
  }
}
```

Ответ (AI недоступен — локальный fallback, `is_available: false`):

```json
{
  "id": "a2e7e4d4-b8ce-4b2d-a2ad-9e2f5cdd85e4",
  "status": "accepted",
  "message": "Contact request has been accepted.",
  "ai_analysis": {
    "sentiment": "neutral",
    "category": "pricing",
    "suggested_reply": "Здравствуйте, Иван Петров! Спасибо за обращение...",
    "is_available": false
  }
}
```

Ошибка валидации — `422`:

```json
{
  "error_code": "validation_error",
  "message": "Invalid request payload.",
  "details": [ ... ]
}
```

Превышение лимита — `429`:

```json
{
  "error_code": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "details": null
}
```

### `GET /api/metrics`

```bash
curl http://localhost:8000/api/metrics
```

```json
{
  "total_contacts": 12,
  "ai_success_count": 10,
  "ai_fallback_count": 2,
  "sentiment_distribution": {
    "positive": 6,
    "neutral": 4,
    "negative": 0,
    "unknown": 2
  }
}
```

## AI-интеграция

Реализована в `app/services/ai_service.py` через **OpenRouter** — OpenAI-совместимый API-шлюз, позволяющий использовать разные модели (включая бесплатные) с одним ключом. Используется официальный OpenAI Python SDK с `base_url=https://openrouter.ai/api/v1`.

AI выполняет три функции:

1. Анализ тональности комментария: `positive` / `neutral` / `negative`.
2. Классификация обращения: `pricing`, `cooperation`, `technical_question`, `complaint`, `other`.
3. Генерация короткого вежливого ответа пользователю на русском языке.

### Graceful fallback (двухуровневый)

1. **Внешний AI** — основной путь.
2. **Локальный rule-based анализ** — если провайдер недоступен: нет ключа, неверный ключ, нет квоты, таймаут, невалидный JSON. Тональность и категория определяются по ключевым словам, ответ строится из шаблонов. Поле `is_available: false` показывает, что сработал fallback.

В любом случае заявка сохраняется, email имитируется, метрики обновляются, клиент получает успешный ответ.

### Промпт

System message:

```text
You analyze landing page contact form messages. Return only valid JSON without markdown.
```

User prompt:

```text
Analyze the following landing page contact form submission.

Return strictly valid JSON with this schema:
{
  "sentiment": "positive | neutral | negative",
  "category": "pricing | cooperation | technical_question | complaint | other",
  "suggested_reply": "A short polite reply in Russian, 2-4 sentences"
}

Rules:
- sentiment must be one of: positive, neutral, negative.
- category must be one of: pricing, cooperation, technical_question, complaint, other.
- suggested_reply must be friendly, professional and relevant to the user's message.
- Do not include markdown.
- Do not include any text outside JSON.
- If the message is too vague, use neutral sentiment and other category.

Contact data:
Name: {name}
Email: {email}
Phone: {phone}
Comment: {comment}
```

## Хранение данных

Все данные приложения хранятся в реляционной БД через **SQLAlchemy 2.0**.
По умолчанию используется SQLite, для production можно переключиться на
PostgreSQL сменой `DATABASE_URL` — код приложения при этом не меняется.

ORM-модели (`app/db/models.py`):
- `ContactDB` — обращения из формы (имя, телефон, email, комментарий,
  результат AI-анализа, дата создания).
- `MetricsDB` — агрегированная статистика обращений (всего, успехи/фолбэки
  AI, распределение тональности).
- `RateLimitDB` — записи по IP для контроля частоты запросов.

Доступ к БД инкапсулирован в **репозиторном слое** (`app/repositories/`):
сервисы не работают с SQLAlchemy Session напрямую, что позволяет заменить
хранилище (например, на PostgreSQL/Redis) без изменения бизнес-логики и API.

Файл БД по умолчанию: `app/storage/landing.db`.

Логи хранятся отдельно от БД, в файлах:
- `logs/requests.log` — все HTTP-запросы (метод, путь, статус, IP, длительность).
- `logs/app.log` — прикладные события и ошибки.

## Rate limiting

Реализован по алгоритму sliding window на таблице `RateLimitDB`: не более
`RATE_LIMIT_MAX_REQUESTS` запросов с одного IP за `RATE_LIMIT_WINDOW_SECONDS`
секунд (по умолчанию 5 запросов за 60 секунд). При превышении лимита сервис
возвращает `429 Too Many Requests` с телом:

{
  "error_code": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "details": null
}

## Email

Email-отправка реализована как имитация через логирование — осознанное решение для тестового задания, чтобы не подключать внешний SMTP-провайдер. `EmailService` изолирован и может быть заменен на SMTP/SendGrid/SES без изменения бизнес-логики. Отправляются два «письма»: владельцу сайта и копия пользователю.

## Обработка ошибок

Глобальные обработчики в `app/main.py`:

- `AppException` — бизнес-ошибки с корректным статусом и кодом;
- `RequestValidationError` — ошибки валидации (422);
- `Exception` — непредвиденные ошибки (500, детали только в логах).

Единый формат ответа: `{ "error_code", "message", "details" }`.

## Тесты

```bash
pytest -q
```

Покрывают: healthcheck, успешную заявку с fallback-анализом, ошибки валидации, метрики.

## Что сделано с помощью AI

AI использовался как ассистент для генерации первичного каркаса: структура проекта, Pydantic-модели, роутеры, сервисный слой, репозитории, интеграция с AI-провайдером, README и тесты.

Пример промпта:

```text
Разработай backend-сервис на Python FastAPI для лендинг-презентации. Нужны POST /api/contact, валидация формы, email-уведомления, AI-анализ комментария, graceful fallback, rate limiting через файлы, логирование, .env, CORS, Swagger, слоистая архитектура Controllers → Services → Repositories.
```

Вручную исправлено и доработано:

- форматирование и читаемость кода;
- переход с прямого OpenAI API на OpenRouter (`base_url`), т.к. он дает доступ к бесплатным моделям;
- добавлен локальный rule-based fallback вместо простого `null` при недоступности AI;
- строгие валидаторы телефона и имени;
- единый формат ошибок и глобальные handlers;
- потокобезопасная запись JSON-файлов;
- тесты.

## Деплой

Проект готов к деплою на Render/Railway/Fly.io.

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Если деплой не выполнен, используйте инструкцию локального запуска выше.


