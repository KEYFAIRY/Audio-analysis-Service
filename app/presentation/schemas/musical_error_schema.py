from typing import List

from pydantic import BaseModel, Field
from app.application.dto.musical_error_dto import MusicalErrorDTO

class MusicalErrorRequest(BaseModel):
    """Esquema para registrar un error musical en una práctica"""
    min_sec: float = Field(..., description="Minuto y segundo en el que ocurre el error", example=12.5)
    note_played: str = Field(..., min_length=1, description="Nota tocada por el usuario", example="C#")
    note_correct: str = Field(..., min_length=1, description="Nota correcta esperada", example="D")

    class Config:
        schema_extra = {
            "example": {
                "min_sec": 12.5,
                "note_played": "C#",
                "note_correct": "D"
            }
        }


class MusicalErrorResponse(BaseModel):
    """Respuesta con información de un error musical"""
    id: int = Field(..., description="ID único del error musical en la base de datos", example=101)
    practice_id: int = Field(..., description="ID de la práctica asociada", example=5)
    min_sec: float = Field(..., description="Minuto y segundo en el que ocurre el error", example=12.5)
    note_played: str = Field(..., description="Nota tocada por el usuario", example="C#")
    note_correct: str = Field(..., description="Nota correcta esperada", example="D")

    class Config:
        schema_extra = {
            "example": {
                "id": 101,
                "practice_id": 5,
                "min_sec": 12.5,
                "note_played": "C#",
                "note_correct": "D"
            }
        }