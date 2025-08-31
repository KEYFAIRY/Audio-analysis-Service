from typing import List
from app.application.dto.musical_error_dto import MusicalErrorDTO
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.mongo_practice_service import MongoPracticeService
# from app.infrastructure.kafka.kafka_producer import KafkaProducer
from app.core.exceptions import DatabaseConnectionException, ValidationException
import logging

logger = logging.getLogger(__name__)

class ProcessAndStoreErrorUseCase:
    """Use case to process a practice video, store MySQL errors, update Mongo, publish Kafka"""

    def __init__(
        self, 
        music_service: MusicalErrorService,
        mongo_service: MongoPracticeService
        # kafka_producer: KafkaProducer
    ):
        self.music_service = music_service
        self.mongo_service = mongo_service
        # self.kafka_producer = kafka_producer

    async def execute(self, data: PracticeDataDTO) -> List[MusicalErrorDTO]:
        if not data.uid or not data.practice_id or not data.video_route:
            logger.warning("Invalid practice data received")
            raise ValidationException("uid, practice_id, and video_route are required")
        
        try:
            # 1️ Procesar y almacenar errores en MySQL
            errors = await self.music_service.process_and_store_error(data)

            # 2️ Actualizar Mongo usando el servicio
            await self.mongo_service.mark_audio_done(uid=str(data.uid), id_practice=data.practice_id)

            # 3️ Publicar mensaje en Kafka
            kafka_message = {
                "uid": data.uid,
                "practice_id": data.practice_id,
                "status": "audio_done"
            }
            #await self.kafka_producer.publish_message(topic="audio_done_topic", message=kafka_message)

            # 4️ Mapear a DTOs
            return [MusicalErrorDTO(
                min_sec=e.min_sec,
                note_played=e.note_played,
                note_correct=e.note_correct
            ) for e in errors]

        except Exception as e:
            logger.error(f"Error processing and storing practice: {e}")
            raise DatabaseConnectionException(f"Failed to process practice: {str(e)}")
