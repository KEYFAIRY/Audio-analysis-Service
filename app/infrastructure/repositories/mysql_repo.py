import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.repositories.i_mysql_repo import IMySQLRepo
from app.domain.entities.musical_error import MusicalError
from app.infrastructure.database.models.MusicalErrorModel import MusicalErrorModel
from app.infrastructure.database.mysql_connection import mysql_connection
from app.core.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)

class MySQLMusicalErrorRepository(IMySQLRepo):
    """Concrete implementation of IMySQLRepo using MySQL."""

    async def list_by_practice_id(self, id_practice: int) -> List[MusicalError]:
        async with mysql_connection.get_async_session() as session:
            try:
                result = await session.execute(
                    select(MusicalErrorModel).where(MusicalErrorModel.id_practice == id_practice)
                )
                rows = result.scalars().all()
                logger.debug(f"Fetched {len(rows)} musical errors for practice_id={id_practice}")
                return [self._model_to_entity(row) for row in rows]
            except SQLAlchemyError as e:
                logger.error(
                    f"MySQL error listing musical errors for practice_id={id_practice}: {e}",
                    exc_info=True
                )
                raise DatabaseConnectionException(f"Error fetching musical errors: {str(e)}")

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
