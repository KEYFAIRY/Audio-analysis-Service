from abc import ABC, abstractmethod

class IVideoRepo(ABC):

    @abstractmethod
    async def read(self, path: str, uid: str, practice_id: str) -> str:
        """Reads the video content and returns the content. Currently returns the path because of possible audio implementation"""
        pass