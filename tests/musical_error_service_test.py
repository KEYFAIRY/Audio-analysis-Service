import pytest
from unittest.mock import AsyncMock, patch
from app.domain.entities.musical_error import MusicalError
from app.domain.entities.practice_data import PracticeData
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.domain.repositories.i_videos_repo import IVideoRepo


@pytest.fixture
def mock_music_repo():
    """Fixture que proporciona un repositorio de errores musicales mock"""
    return AsyncMock(spec=IMusicalErrorRepo)


@pytest.fixture
def mock_video_repo():
    """Fixture que proporciona un repositorio de videos mock"""
    return AsyncMock(spec=IVideoRepo)


@pytest.fixture
def musical_error_service(mock_music_repo, mock_video_repo):
    """Fixture que proporciona una instancia del servicio"""
    return MusicalErrorService(mock_music_repo, mock_video_repo)


@pytest.fixture
def valid_practice_data():
    """Fixture que proporciona datos de práctica válidos"""
    return PracticeData(
        uid=123,
        practice_id=1,
        scale="DO MAYOR",
        scale_type="MAJOR",
        duration=10.5,
        bpm=60,
        figure=0.25,
        octaves=1
    )


@pytest.fixture
def valid_musical_errors():
    """Fixture que proporciona una lista de errores musicales válidos"""
    return [
        MusicalError(
            min_sec="00:02",
            note_played="RE",
            note_correct="DO",
            id_practice=1
        ),
        MusicalError(
            min_sec="00:05",
            note_played="FA",
            note_correct="MI",
            id_practice=1
        ),
        MusicalError(
            min_sec="00:08",
            note_played="SOL",
            note_correct="LA",
            id_practice=1
        )
    ]


class TestProcessAndStoreError:
    """Suite de pruebas para procesar y almacenar errores musicales"""

    @pytest.mark.asyncio
    @patch('app.domain.services.musical_error_service.extract_notes_audio')
    @patch('app.domain.services.musical_error_service.get_correct_notes')
    @patch('app.domain.services.musical_error_service.solfege_to_note')
    @patch('app.domain.services.musical_error_service.note_to_solfege')
    @patch('app.domain.services.musical_error_service.format_seconds_to_mmss')
    async def test_process_audio_with_musical_errors(
        self,
        mock_format_time,
        mock_note_to_solfege,
        mock_solfege_to_note,
        mock_get_correct_notes,
        mock_extract_notes,
        musical_error_service,
        mock_video_repo,
        mock_music_repo,
        valid_practice_data,
        valid_musical_errors
    ):
        """
        Descripción: El video para analizar contiene errores musicales
        Condiciones: Verificar que el sistema registre correctamente errores musicales
        Resultado esperado: Se retorna la lista de errores musicales identificados
        """
        # Arrange
        video_path = "/path/to/video.mp4"
        mock_video_repo.read.return_value = video_path
        
        # Simular notas correctas esperadas
        expected_notes = ["C4", "D4", "E4", "F4", "G4"]
        mock_solfege_to_note.return_value = "C"
        mock_get_correct_notes.return_value = expected_notes
        
        # Simular notas extraídas del audio (con errores)
        extracted_notes = [
            {"name": "C4", "start": 0.0},
            {"name": "E4", "start": 2.0},  # Error: debería ser D4
            {"name": "E4", "start": 4.0},
            {"name": "G4", "start": 6.0},  # Error: debería ser F4
            {"name": "A4", "start": 8.0},  # Error: debería ser G4
        ]
        mock_extract_notes.return_value = extracted_notes
        
        # Simular conversiones de notas y tiempo
        mock_format_time.side_effect = lambda x: x if isinstance(x, str) else f"00:{int(x):02d}"
        mock_note_to_solfege.side_effect = lambda note: {
            "C4": "DO", "D4": "RE", "E4": "MI", 
            "F4": "FA", "G4": "SOL", "A4": "LA"
        }.get(note, note)
        
        mock_music_repo.create.return_value = None

        # Act
        result = await musical_error_service.process_and_store_error(valid_practice_data)

        # Assert
        mock_video_repo.read.assert_awaited_once_with(
            valid_practice_data.uid,
            valid_practice_data.practice_id
        )
        
        mock_extract_notes.assert_called_once_with(
            video_path,
            valid_practice_data.practice_id,
            valid_practice_data.bpm,
            valid_practice_data.figure,
            len(expected_notes)
        )
        
        # Verificar que se intentó crear errores (3 errores detectados)
        assert mock_music_repo.create.await_count == 3
        
        # Verificar que se retornaron errores
        assert len(result) == 3
        assert all(isinstance(error, MusicalError) for error in result)


    @pytest.mark.asyncio
    @patch('app.domain.services.musical_error_service.extract_notes_audio')
    @patch('app.domain.services.musical_error_service.get_correct_notes')
    @patch('app.domain.services.musical_error_service.solfege_to_note')
    async def test_process_audio_without_musical_errors(
        self,
        mock_solfege_to_note,
        mock_get_correct_notes,
        mock_extract_notes,
        musical_error_service,
        mock_video_repo,
        mock_music_repo,
        valid_practice_data
    ):
        """
        Descripción: El video para analizar no contiene errores musicales
        Condiciones: Verificar que el sistema no registre ningún error musical
        Resultado esperado: Se retorna una lista vacía
        """
        # Arrange
        video_path = "/path/to/video.mp4"
        mock_video_repo.read.return_value = video_path
        
        # Simular notas correctas esperadas
        expected_notes = ["C4", "D4", "E4", "F4", "G4"]
        mock_solfege_to_note.return_value = "C"
        mock_get_correct_notes.return_value = expected_notes
        
        # Simular notas extraídas del audio (sin errores - todas correctas)
        extracted_notes = [
            {"name": "C4", "start": 0.0},
            {"name": "D4", "start": 2.0},
            {"name": "E4", "start": 4.0},
            {"name": "F4", "start": 6.0},
            {"name": "G4", "start": 8.0},
        ]
        mock_extract_notes.return_value = extracted_notes

        # Act
        result = await musical_error_service.process_and_store_error(valid_practice_data)

        # Assert
        mock_video_repo.read.assert_awaited_once_with(
            valid_practice_data.uid,
            valid_practice_data.practice_id
        )
        
        mock_extract_notes.assert_called_once_with(
            video_path,
            valid_practice_data.practice_id,
            valid_practice_data.bpm,
            valid_practice_data.figure,
            len(expected_notes)
        )
        
        # Verificar que NO se intentó crear ningún error
        mock_music_repo.create.assert_not_awaited()
        
        # Verificar que se retornó una lista vacía
        assert result == []
        assert len(result) == 0