from abc import ABC, abstractmethod

class IMongoRepo(ABC):
    
    @abstractmethod
    async def mark_practice_audio_done(self, uid: str, id_practice: int) -> bool:
        """Marks audio_done = true for the specific user and practice"""
        pass
