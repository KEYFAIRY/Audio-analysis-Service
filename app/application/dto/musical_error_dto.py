from dataclasses import dataclass

@dataclass
class MusicalErrorDTO:
    min_sec: str
    note_played: str
    note_correct: str