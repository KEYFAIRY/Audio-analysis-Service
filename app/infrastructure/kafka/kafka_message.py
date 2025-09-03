from dataclasses import dataclass

@dataclass
class KafkaMessage:
    uid: str
    practice_id: int
    message: str