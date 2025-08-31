from typing import List
from app.domain.entities.musical_error import MusicalError
from app.domain.entities.practice_data import PracticeData
from app.domain.repositories.i_mysql_repo import IMySQLRepo

class MusicalErrorService:
    """Lógica de dominio"""

    def __init__(self, music_repo: IMySQLRepo):
        self.music_repo = music_repo

    async def list_errors_by_practice(self, id_practice: int) -> List[MusicalError]:
        return await self.repo.list_by_practice_id(id_practice)
    
    async def process_and_store_error(self, data: PracticeData) -> List[MusicalError]:

        # Datos de la practica a procesar
        uid = data.uid
        practice_id = data.practice_id
        video_route = data.video_route
        scale = data.scale
        reps = data.reps
        
        # Aquí se procesa el video y se extraen los errores musicales, se guardan en la bd MySQL

        # ej. guardar un error: self.music_repo.create(MusicalError(...))

        return []
