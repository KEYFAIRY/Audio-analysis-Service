import logging
from typing import List
from app.application.dto.musical_error_dto import MusicalErrorDTO
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.domain.entities.practice_data import PracticeData
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.metadata_practice_service import MetadataPracticeService
from app.infrastructure.kafka.kafka_message import KafkaMessage
from app.infrastructure.kafka.kafka_producer import KafkaProducer
from app.core.exceptions import DatabaseConnectionException, ValidationException
from app.core.config import settings

logger = logging.getLogger(__name__)

class ProcessAndStoreErrorUseCase:
    """Use case to process a practice video, store MySQL errors, update Mongo, publish Kafka"""

    def __init__(
        self, 
        music_service: MusicalErrorService,
        mongo_service: MetadataPracticeService,
        kafka_producer: KafkaProducer
    ):
        self.music_service = music_service
        self.mongo_service = mongo_service
        self.kafka_producer = kafka_producer

    async def execute(self, data: PracticeDataDTO) -> List[MusicalErrorDTO]:
        if not data.uid or not data.practice_id:
            logger.warning(
                "Validation failed: uid=%s, practice_id=%s",
                data.uid, data.practice_id
            )
            raise ValidationException("uid and practice_id are required")
        
        try:
            # 1️ Process and store errors in MySQL
            practice_data = PracticeData(
                uid=data.uid,
                practice_id=data.practice_id,
                scale=data.scale,
                scale_type=data.scale_type,
                reps=data.reps,
                bpm=data.bpm,
            )
            
            errors = await self.music_service.process_and_store_error(practice_data)
            logger.info("Stored %d errors for practice_id=%s", len(errors), data.practice_id)

            # 2️ Updates metadata in MongoDB
            await self.mongo_service.mark_audio_done(uid=str(data.uid), id_practice=data.practice_id)
            logger.info("Marked audio as done in Mongo for uid=%s, practice_id=%s", data.uid, data.practice_id)

            # 3️ Publish message to Kafka
            kafka_message = KafkaMessage(
                uid=data.uid,
                practice_id=data.practice_id,
                message="audio_done",
                scale=data.scale,
                scale_type=data.scale_type,
                reps=data.reps,
                bpm=data.bpm,
            )
            
            logger.debug("Prepared Kafka message: %s", kafka_message)

            await self.kafka_producer.publish_message(topic=settings.KAFKA_OUTPUT_TOPIC, message=kafka_message)

            # 4️ Map to DTOs
            return [
                MusicalErrorDTO(
                    min_sec=e.min_sec,
                    note_played=e.note_played,
                    note_correct=e.note_correct
                ) for e in errors
            ]

        except Exception as e:
            logger.error("Error processing and storing practice", exc_info=True)
            raise DatabaseConnectionException(f"Failed to process practice: {str(e)}")
