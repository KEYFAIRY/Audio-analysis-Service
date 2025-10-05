import logging
from typing import List
from app.domain.entities.musical_error import MusicalError
from app.domain.entities.practice_data import PracticeData
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.domain.repositories.i_videos_repo import IVideoRepo

logger = logging.getLogger(__name__)

class MusicalErrorService:
    """Domain service for management of musical errors"""

    def __init__(self, music_repo: IMusicalErrorRepo, video_repo: IVideoRepo):
        self.music_repo = music_repo
        self.video_repo = video_repo

    async def process_and_store_error(self, data: PracticeData) -> List[MusicalError]:
        uid = data.uid
        practice_id = data.practice_id
        scale = data.scale
        scale_type = data.scale_type
        duration = data.duration
        bpm = data.bpm
        figure = data.figure
        octaves = data.octaves

        try:
            logger.info(
                "Processing errors for uid=%s, practice_id=%s, scale=%s, scale_type=%s, duration=%s, bpm=%s, figure=%s, octaves=%s",
                uid,
                practice_id,
                scale,
                scale_type,
                duration,
                bpm,
                figure,
                octaves,
                extra={
                    "uid": uid,
                    "practice_id": practice_id,
                    "scale": scale,
                    "scale_type": scale_type,
                    "duration": duration,
                    "bpm": bpm,
                    "figure": figure,
                    "octaves": octaves,
                },
            )

            # TODO: Implementar análisis de audio y extracción de errores
            # 1. obtener el video en video_route
            path = await self.video_repo.read(uid, practice_id)
            # 2. convertir el video en audio
            # 3. analizar el audio y extraer errores
            # 4. guardar cada uno de los errores en la base de datos
            
            # stored_errors solamente se usó para colocar algo en los logs
            stored_errors: List[MusicalError] = []

            logger.info(
                "Finished processing errors for uid=%s, practice_id=%s. Stored=%d",
                uid,
                practice_id,
                len(stored_errors),
                extra={"uid": uid, "practice_id": practice_id, "stored": len(stored_errors)},
            )

            return stored_errors

        except Exception as e:
            logger.error(
                "Error processing/storing errors for uid=%s, practice_id=%s",
                uid,
                practice_id,
                exc_info=True,
                extra={"uid": uid, "practice_id": practice_id},
            )
            raise
