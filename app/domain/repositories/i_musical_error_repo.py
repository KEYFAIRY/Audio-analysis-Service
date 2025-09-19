from abc import ABC, abstractmethod
from app.domain.entities.musical_error import MusicalError

class IMusicalErrorRepo(ABC):

    @abstractmethod
    async def create(self, musical_error: MusicalError) -> MusicalError:
        """Stores a musical error in the database and returns the stored entity."""
        pass
