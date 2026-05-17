from dataclasses import dataclass


@dataclass(frozen=True)
class CanFrame:
    timestamp: float  # Relative monotonic timestamp
    arbitration_id: int
    dlc: int
    data: bytes
    is_extended_id: bool = False
    channel: str = "0"


@dataclass
class Marker:
    timestamp: float
    label: str


@dataclass
class SessionMetadata:
    session_name: str
    start_time_iso: str
    duration: float = 0.0
    total_frames: int = 0
