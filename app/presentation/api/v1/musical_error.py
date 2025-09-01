from fastapi import APIRouter, Depends, status
from typing import List
import logging

from app.presentation.schemas.musical_error_schema import MusicalErrorResponse
from app.presentation.schemas.common_schema import StandardResponse
from app.application.use_cases.list_errors_by_practice import ListErrorsByPracticeUseCase
from app.presentation.api.v1.dependencies import list_errors_by_practice_use_case_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/errors", tags=["Musical Errors"])


@router.get(
    "/practice/{practice_id}",
    response_model=StandardResponse[List[MusicalErrorResponse]],
    status_code=status.HTTP_200_OK,
    summary="List musical errors by practice",
    description="Retrieve all musical errors detected for a given practice ID"
)
async def list_errors_by_practice(
    practice_id: int,
    use_case: ListErrorsByPracticeUseCase = Depends(list_errors_by_practice_use_case_dependency)
):
    logger.info(f"Fetching musical errors for practice_id={practice_id}")

    # Ejecutar caso de uso
    errors_dto = await use_case.execute(practice_id)

    # Mapear DTO -> Response Schema
    errors_response = [
        MusicalErrorResponse(
            id=e.id,
            practice_id=e.practice_id,
            min_sec=e.min_sec,
            note_played=e.note_played,
            note_correct=e.note_correct
        )
        for e in errors_dto
    ]

    logger.info(f"Found {len(errors_response)} errors for practice_id={practice_id}")
    return StandardResponse.success(
        data=errors_response,
        message=f"Found {len(errors_response)} errors"
    )
