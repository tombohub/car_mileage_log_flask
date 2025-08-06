from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Literal


@dataclass
class JobSite:
    id: int | None
    name: str
    address: str


class DriveLogStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class StartKmTooLowError(Exception):
    def __init__(self, start_km: int, previous_end_km: int) -> None:
        super().__init__(
            f"Start km ({start_km}) cannot be lower than previous End km ({previous_end_km})"
        )


class EndKmTooLowError(Exception):
    def __init__(self, end_km: int, start_km: int):
        super().__init__(
            f"End km ({end_km}) cannot be lower than Start km ({start_km})"
        )
