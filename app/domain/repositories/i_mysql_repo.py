from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.musical_error import MusicalError

class IMySQLRepo(ABC):
    
    # TODO: This method is for reports service
    @abstractmethod
    async def list_by_practice_id(self, id_practice: int) -> List[MusicalError]:
        pass

    @abstractmethod
    async def create(self, musical_error: MusicalError) -> MusicalError:
        pass
