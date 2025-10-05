import json
import logging
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.application.use_cases.process_and_store_error import ProcessAndStoreErrorUseCase
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.metadata_practice_service import MetadataPracticeService
from app.infrastructure.kafka.kafka_message import KafkaMessage
from app.infrastructure.kafka.kafka_producer import KafkaProducer
from app.infrastructure.repositories.local_video_repo import LocalVideoRepository
from app.infrastructure.repositories.mysql_musical_error_repo import MySQLMusicalErrorRepository
from app.infrastructure.repositories.mongo_metadata_repo import MongoMetadataRepo
from app.application.dto.practice_data_dto import PracticeDataDTO

logger = logging.getLogger(__name__)


async def start_kafka_consumer(kafka_producer: KafkaProducer):
    # Initialize dependencies
    mysql_repo = MySQLMusicalErrorRepository()
    mongo_repo = MongoMetadataRepo()
    video_repo = LocalVideoRepository()

    music_service = MusicalErrorService(mysql_repo, video_repo)
    mongo_service = MetadataPracticeService(mongo_repo)

    use_case = ProcessAndStoreErrorUseCase(
        music_service=music_service,
        mongo_service=mongo_service,
        kafka_producer=kafka_producer,
    )

    consumer = AIOKafkaConsumer(
        settings.KAFKA_INPUT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        enable_auto_commit=False,
        auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
        group_id=settings.KAFKA_GROUP_ID,
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
                kafka_msg = KafkaMessage(**data)
                
                dto = PracticeDataDTO(
                    uid=kafka_msg.uid,
                    practice_id=kafka_msg.practice_id,
                    date=kafka_msg.date,
                    time=kafka_msg.time,
                    scale=kafka_msg.scale,
                    scale_type=kafka_msg.scale_type,
                    num_postural_errors=0,  # Placeholder
                    num_musical_errors=0,   # Placeholder
                    duration=kafka_msg.duration,
                    bpm=kafka_msg.bpm,
                    figure=kafka_msg.figure,
                    octaves=kafka_msg.octaves,
                )

                # Execute use case
                errors = await use_case.execute(dto)
                logger.info(f"Processed KafkaMessage with {len(errors)} errors")
                await consumer.commit()
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
