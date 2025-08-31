from dataclasses import dataclass
from typing import Optional

@dataclass
class MusicalErrorDTO:
    min_sec: str
    note_played: str
    note_correct: str