from dataclasses import dataclass
from typing import Optional

@dataclass
class KafkaMessage:
    uid: str
    practice_id: int
    message: str