from dataclasses import dataclass

@dataclass
class PracticeData:
    uid: int
    practice_id: int
    scale: str
    scale_type: str
    reps: str
    bpm: int