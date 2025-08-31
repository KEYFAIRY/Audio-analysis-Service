from typing import List
from app.application.dto.musical_error_dto import MusicalErrorDTO
from app.domain.services.musical_error_service import MusicalErrorService
from app.core.exceptions import DatabaseConnectionException, ValidationException
import logging

logger = logging.getLogger(__name__)

class ListErrorsByPracticeUseCase:
    """Use case to list musical errors filtered by practice ID"""

    def __init__(self, music_service: MusicalErrorService):
        self.music_service = music_service

    async def execute(self, id_practice: int) -> List[MusicalErrorDTO]:
        if not id_practice:
            logger.warning("Invalid id_practice provided")
            raise ValidationException("id_practice is required")
        try:
            errors = await self.music_service.list_errors_by_practice(id_practice)
            # Map domain entities to DTOs
            return [MusicalErrorDTO(
                min_sec=e.min_sec,
                note_played=e.note_played,
                note_correct=e.note_correct
            ) for e in errors]
        except Exception as e:
            logger.error(f"Error listing musical errors: {e}")
            raise DatabaseConnectionException(f"Failed to list errors: {str(e)}")
