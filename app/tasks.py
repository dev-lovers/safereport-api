import os
import redis
import json
import logging
from celery import Celery
from celery.schedules import crontab
from datetime import date, timedelta
import asyncio


from app.services.occurrences_service import OccurrencesProcessor
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.services.crossfire_auth_service import CrossfireAuthService
from app.core.config import settings

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = (
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

DEFAULT_CACHE_KEY = "analysis_result_salvador"
DEFAULT_CITY = "Salvador"
DEFAULT_STATE = "Bahia"
DEFAULT_DAYS_AGO = 365

PRODUCTION_SCHEDULE = getattr(settings, "CELERY_BEAT_SCHEDULE", timedelta(days=1))

# PRODUCTION_SCHEDULE = getattr(
#     settings, "CELERY_BEAT_SCHEDULE", crontab(hour=0, minute=1)
# )

app = Celery("tasks", broker=CELERY_BROKER_URL)


@app.task(name="tasks.process_and_cache_occurrences")
def process_and_cache_occurrences(
    city_name: str = DEFAULT_CITY,
    state_name: str = DEFAULT_STATE,
    days_ago: int = DEFAULT_DAYS_AGO,
    cache_key: str = DEFAULT_CACHE_KEY,
):
    logger.info(f"WORKER: Tarefa agendada iniciada para {city_name}/{state_name}.")

    try:
        auth_service = CrossfireAuthService()
        occurrence_gateway = CrossfireAPIService()

        logger.info("WORKER: Obtendo token de autenticação...")
        access_token = auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API, settings.PASSWORD_CROSSFIRE_API
        )
        occurrence_gateway.set_access_token(access_token)
        logger.info("WORKER: Token obtido com sucesso.")

        today = date.today()
        final_date = today.strftime("%Y-%m-%d")
        initial_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        logger.info(
            f"WORKER: Buscando ocorrências para {city_name}/{state_name} entre {initial_date} e {final_date}..."
        )

        raw_data = asyncio.run(
            occurrence_gateway.get_occurrences(
                city_name=city_name,
                state_name=state_name,
                initial_date=initial_date,
                final_date=final_date,
            )
        )

        print(raw_data[0])
        logger.info(f"WORKER: {len(raw_data)} ocorrências encontradas.")

        logger.info("WORKER: Iniciando processamento (clusterização)...")
        processor = OccurrencesProcessor(epsilon_km=0.7, min_samples=8)

        analyzed_data_dict = processor.cluster_occurrences(raw_data)
        logger.info("WORKER: Processamento finalizado.")

        json_output = json.dumps(analyzed_data_dict)

        redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )
        redis_client.set(cache_key, json_output)

        logger.info(f"WORKER: Resultado salvo no cache com a chave '{cache_key}'.")
        return f"Cache atualizado com sucesso para {city_name}."

    except Exception as e:
        logger.exception(f"WORKER: Falha crítica na tarefa para {city_name}. Erro: {e}")
        raise


app.conf.beat_schedule = {
    f"processar-dados-diarios-{DEFAULT_CITY.lower()}": {
        "task": "tasks.process_and_cache_occurrences",
        "schedule": PRODUCTION_SCHEDULE,
        "kwargs": {
            "city_name": DEFAULT_CITY,
            "state_name": DEFAULT_STATE,
            "days_ago": DEFAULT_DAYS_AGO,
            "cache_key": DEFAULT_CACHE_KEY,
        },
    },
}
app.conf.timezone = "UTC"
