import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.application.use_cases.process_and_store_error import ProcessAndStoreErrorUseCase
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.mongo_practice_service import MongoPracticeService
from app.infrastructure.kafka.kafka_message import KafkaMessage
from app.infrastructure.repositories.mysql_repo import MySQLMusicalErrorRepository
from app.infrastructure.repositories.mongo_repo import MongoRepo
from app.application.dto.practice_data_dto import PracticeDataDTO

logger = logging.getLogger(__name__)


async def start_kafka_consumer():
    # Inicializar dependencias
    mysql_repo = MySQLMusicalErrorRepository()
    mongo_repo = MongoRepo()

    music_service = MusicalErrorService(mysql_repo)
    mongo_service = MongoPracticeService(mongo_repo)

    use_case = ProcessAndStoreErrorUseCase(
        music_service=music_service,
        mongo_service=mongo_service,
    )

    consumer = AIOKafkaConsumer(
        settings.KAFKA_INPUT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        enable_auto_commit=True,
        auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
        group_id=settings.KAFKA_GROUP_ID if settings.KAFKA_GROUP_ID else None,
    )

    await consumer.start()
    try:
        logger.info("Kafka consumer started")
        async for msg in consumer:
            try:
                decoded = msg.value.decode()
                logger.info(f"Received raw message: {decoded}")

                # JSON → KafkaMessage
                data = json.loads(decoded)
                kafka_msg = KafkaMessage(**data)  # <--- ahora usas tu dataclass

                # Si necesitas un DTO intermedio:
                dto = PracticeDataDTO(
                    uid=kafka_msg.uid,
                    practice_id=kafka_msg.practice_id,
                    message=kafka_msg.message,
                )

                # Ejecutar caso de uso
                errors = await use_case.execute(dto)
                logger.info(f"Processed KafkaMessage with {len(errors)} errors")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
