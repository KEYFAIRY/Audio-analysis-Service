from dataclasses import dataclass
from typing import Optional

@dataclass
class MusicalError:
    min_sec: str
    missed_note: str
    id_practice: int
    id: Optional[int] = None