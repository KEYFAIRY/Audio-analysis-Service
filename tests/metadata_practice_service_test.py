import pytest
from unittest.mock import AsyncMock, patch
from app.domain.services.metadata_practice_service import MetadataPracticeService
from app.domain.repositories.i_metadata_repo import IMetadataRepo


@pytest.fixture
def mock_metadata_repo():
    """Fixture que proporciona un repositorio de metadatos mock"""
    return AsyncMock(spec=IMetadataRepo)


@pytest.fixture
def metadata_practice_service(mock_metadata_repo):
    """Fixture que proporciona una instancia del servicio"""
    return MetadataPracticeService(mock_metadata_repo)


class TestMarkAudioDone:
    """Suite de pruebas para marcar audio como procesado"""

    @pytest.mark.asyncio
    async def test_mark_audio_done_with_existing_practice(
        self,
        metadata_practice_service,
        mock_metadata_repo
    ):
        """
        Descripción: Existe el registro de la práctica en la base de datos de metadatos
        Condiciones: Verificar que el sistema actualice el campo de análisis de audio correctamente
        Resultado esperado: Se retorna true
        """
        # Arrange
        uid = "test-uid-123"
        id_practice = 1
        mock_metadata_repo.mark_practice_audio_done.return_value = True

        # Act
        result = await metadata_practice_service.mark_audio_done(uid, id_practice)

        # Assert
        mock_metadata_repo.mark_practice_audio_done.assert_awaited_once_with(uid, id_practice)
        
        # Verificar que se retorna True
        assert result is True


    @pytest.mark.asyncio
    async def test_mark_audio_done_with_nonexistent_practice(
        self,
        metadata_practice_service,
        mock_metadata_repo
    ):
        """
        Descripción: No existe el registro de la práctica en la base de datos de metadatos
        Condiciones: Verificar que el sistema no modifique nada en la base de datos de metadatos
        Resultado esperado: Se retorna false
        """
        # Arrange
        uid = "test-uid-456"
        id_practice = 999
        mock_metadata_repo.mark_practice_audio_done.return_value = False

        # Act
        result = await metadata_practice_service.mark_audio_done(uid, id_practice)

        # Assert
        mock_metadata_repo.mark_practice_audio_done.assert_awaited_once_with(uid, id_practice)
        
        # Verificar que se retorna False
        assert result is False