from pydantic import BaseModel, Field

class MusicalErrorResponse(BaseModel):
    """Response with details of a musical error."""
    min_sec: float = Field(..., description="Minute and second when the error occurred", example=12.5)
    note_played: str = Field(..., description="Note played by the user", example="C#")
    note_correct: str = Field(..., description="Expected correct note", example="D")

    class Config:
        schema_extra = {
            "example": {
                "min_sec": 12.5,
                "note_played": "C#",
                "note_correct": "D"
            }
        }