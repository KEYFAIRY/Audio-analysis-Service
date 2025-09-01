from dataclasses import dataclass
from typing import Optional

@dataclass
class KafkaMessageDTO:
    uid: str
    practice_id: int
    message: str