import asyncio
import json
import logging
from datetime import date, timedelta

import redis
from celery import Celery
from slugify import slugify

from app.core.config import settings
from app.domain.occurrences.use_cases.cluster_occurrences_use_case import (
    ClusterOccurrencesUseCase,
)
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.auth.crossfire_auth_service import CrossfireAuthService


CELERY_BROKER_URL = (
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

app = Celery("tasks", broker=CELERY_BROKER_URL)
app.conf.timezone = "UTC"

PRODUCTION_SCHEDULE = getattr(settings, "CELERY_BEAT_SCHEDULE", timedelta(days=1))
CITIES_TO_PROCESS = getattr(settings, "CITIES_TO_PROCESS", [])


def generate_cache_key(city_name: str, state_name: str) -> str:
    return f"analysis:occurrences:{slugify(state_name)}:{slugify(city_name)}"


@app.task(name="tasks.process_and_cache_occurrences")
def process_and_cache_occurrences(
    city_name: str,
    state_name: str,
    days_ago: int,
    cache_key: str | None = None,
):

    try:
        auth_service = CrossfireAuthService()
        occurrence_gateway = CrossfireAPIService()

        access_token = auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API,
            settings.PASSWORD_CROSSFIRE_API,
        )
        occurrence_gateway.set_access_token(access_token)

        today = date.today()
        final_date = today.strftime("%Y-%m-%d")
        initial_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        raw_data = asyncio.run(
            occurrence_gateway.get_occurrences(
                city_name=city_name,
                state_name=state_name,
                initial_date=initial_date,
                final_date=final_date,
            )
        )

        if not raw_data:
            return f"Nenhum dado encontrado para {city_name}."

        processor = ClusterOccurrencesUseCase(epsilon_km=0.7, min_samples=8)

        analyzed_data = processor.execute(raw_data)
        json_output = json.dumps(analyzed_data)

        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )

        cache_key = cache_key or generate_cache_key(city_name, state_name)

        redis_client.set(cache_key, json_output)

        return f"Cache atualizado com sucesso para {city_name}."

    except Exception as e:
        raise


beat_tasks = {}

for item in CITIES_TO_PROCESS:
    city = item["city"]
    state = item["state"]
    days_ago = item.get("days_ago", 365)

    unique_id = slugify(city)
    cache_key = generate_cache_key(city, state)

    beat_tasks[f"processar-dados-diarios-{unique_id}"] = {
        "task": "tasks.process_and_cache_occurrences",
        "schedule": PRODUCTION_SCHEDULE,
        "kwargs": {
            "city_name": city,
            "state_name": state,
            "days_ago": days_ago,
            "cache_key": cache_key,
        },
    }

app.conf.beat_schedule = beat_tasks
