from app.domain.repositories.i_mongo_repo import IMongoRepo
from app.infrastructure.database.mongo_connection import mongo_connection
import logging

logger = logging.getLogger(__name__)

class MongoRepo(IMongoRepo):
    def __init__(self):
        self.db = mongo_connection.connect()
        self.users_collection = self.db["users"]

    async def mark_practice_audio_done(self, uid: str, id_practice: int) -> bool:
        result = await self.users_collection.update_one(
            {"uid": uid, "practices.id_practice": id_practice},
            {"$set": {"practices.$.audio_done": True}}
        )
        if result.modified_count == 1:
            logger.info(f"Updated audio_done for uid={uid}, practice={id_practice}")
            return True
        logger.warning(f"No document updated for uid={uid}, practice={id_practice}")
        return False
