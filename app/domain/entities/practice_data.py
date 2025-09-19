from dataclasses import dataclass

@dataclass
class PracticeData:
    uid: int
    practice_id: int
    video_route: str
    scale: str
    scale_type: str
    reps: str
    bpm: int