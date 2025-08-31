from abc import ABC, abstractmethod
from typing import List
from app.application.dto.musical_error_dto import MusicalErrorDTO
from app.application.dto.practice_data_dto import PracticeDataDTO

class IMusicalErrorService(ABC):
    
    @abstractmethod
    async def list_errors_by_practice(self, id_practice: int) -> List[MusicalErrorDTO]:
        """Return a list of MusicalErrorDTO filtered by practice ID"""
        pass

    @abstractmethod
    async def process_and_store_error(self, data: PracticeDataDTO) -> List[MusicalErrorDTO]:
        """Process a practice video, store errors in MySQL, update Mongo, publish Kafka message"""
        pass
