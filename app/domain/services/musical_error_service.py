import logging
from typing import List
from app.domain.entities.musical_error import MusicalError
from app.domain.entities.practice_data import PracticeData
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.domain.repositories.i_videos_repo import IVideoRepo
from app.infrastructure.audio.model_manager import ModelManager
from app.infrastructure.audio.utils.time_utils import format_seconds_to_mmss
from app.infrastructure.audio.utils.note_utils import get_correct_notes, solfege_to_note, note_to_solfege
from app.infrastructure.audio.analyzer import extract_notes_audio

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
            logger.debug(f"Starting audio analysis for practice_id={practice_id}")
            # 2. Obtener las notas correctas de la escala
            solfege_of_scale = scale.split()[0]
            expected_notes = get_correct_notes(solfege_to_note(solfege_of_scale), scale_type, octaves)
            # 3. Analizar el audio a partir del video mp4.
            extracted_notes = extract_notes_audio(path, bpm, figure, len(expected_notes))
            # 4. Comparar las notas esperadas con las notas extraidas y guardar errores musicales.
            stored_errors: List[MusicalError] = []
            print("NOTAS")
            
            for i in range(len(expected_notes)):
                print(f"Esperada: {expected_notes[i]} | Detectada: {extracted_notes[i]['name']}")
                if expected_notes[i] != extracted_notes[i]['name']:
                    # print(f"Esperada: {expected_notes[i]}, Detectada: {extracted_notes[i]['name']} | start: {extracted_notes[i]['start']:.4f} |✖|")
                    note = extracted_notes[i]
                    error_time = format_seconds_to_mmss(note['start'])
                    note_played = note_to_solfege(note['name'])
                    correct_note = note_to_solfege(expected_notes[i])

                    stored_errors.append(MusicalError(error_time,
                                                      note_played,
                                                      correct_note,
                                                      practice_id))

            # 4. guardar cada uno de los errores en la base de datos
            
            # stored_errors solamente se usó para colocar algo en los logs
            print(f"HOLLAAAAAAA: {len(stored_errors)}")
            print("NOTAS")
            print(stored_errors)

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
