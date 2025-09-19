import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.domain.entities.musical_error import MusicalError
from app.infrastructure.database.models.MusicalErrorModel import MusicalErrorModel
from app.infrastructure.database.mysql_connection import mysql_connection
from app.core.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)

class MySQLMusicalErrorRepository(IMusicalErrorRepo):
    """Concrete implementation of IMusicalErrorRepo using MySQL."""

    async def create(self, musical_error: MusicalError) -> MusicalError:
        async with mysql_connection.get_async_session() as session:
            try:
                model = MusicalErrorModel(
                    min_sec=musical_error.min_sec,
                    note_played=musical_error.note_played,
                    note_correct=musical_error.note_correct,
                    id_practice=musical_error.id_practice
                )
                session.add(model)
                await session.commit()
                await session.refresh(model)

                logger.info(f"Musical error created with id={model.id} for practice_id={musical_error.id_practice}")
                return self._model_to_entity(model)

            except IntegrityError as e:
                await session.rollback()
                logger.error(
                    f"Integrity error creating musical error for practice_id={musical_error.id_practice}: {e}",
                    exc_info=True
                )
                raise DatabaseConnectionException(f"Integrity error: {str(e)}")

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(
                    f"MySQL error creating musical error for practice_id={musical_error.id_practice}: {e}",
                    exc_info=True
                )
                raise DatabaseConnectionException(f"Error creating musical error: {str(e)}")

    def _model_to_entity(self, model: MusicalErrorModel) -> MusicalError:
        return MusicalError(
            id=model.id,
            min_sec=model.min_sec,
            note_played=model.note_played,
            note_correct=model.note_correct,
            id_practice=model.id_practice
        )
