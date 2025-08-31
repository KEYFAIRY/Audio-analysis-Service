from app.domain.repositories.i_mongo_repo import IMongoRepo
import logging

logger = logging.getLogger(__name__)

class MongoPracticeService:
    """Servicio de dominio para operaciones sobre prácticas en Mongo"""

    def __init__(self, mongo_repo: IMongoRepo):
        self.mongo_repo = mongo_repo

    async def mark_audio_done(self, uid: str, id_practice: int) -> bool:
        try:
            updated = await self.mongo_repo.mark_practice_audio_done(uid, id_practice)
            if not updated:
                logger.warning(f"Mongo update failed for uid={uid}, practice={id_practice}")
            return updated
        except Exception as e:
            logger.error(f"Error updating audio_done in Mongo: {e}")
            raise
