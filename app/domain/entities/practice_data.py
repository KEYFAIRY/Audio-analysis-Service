from dataclasses import dataclass

@dataclass
class PracticeData:
    uid: int
    practice_id: int
    scale: str
    scale_type: str
    duration: int
    bpm: int
    figure: float
    octaves: int