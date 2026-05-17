import time
from datetime import datetime
from typing import Dict, List, Optional

from .models import CanFrame, Marker


class CanRecorder:
    def __init__(self):
        self.is_recording = False
        self.recorded_frames: List[CanFrame] = []
        self.markers: List[Marker] = []
        self.total_frames_seen = 0
        self.id_frequencies: Dict[int, int] = {}
        self.recording_start_monotonic = 0.0
        self.session_start_iso = ""
        self.marker_counter = 0

    def process_frame(self, frame: CanFrame):
        self.total_frames_seen += 1
        self.id_frequencies[frame.arbitration_id] = (
            self.id_frequencies.get(frame.arbitration_id, 0) + 1
        )
        if self.is_recording:
            self.recorded_frames.append(frame)

    def toggle_recording(self) -> bool:
        if not self.is_recording:
            self.is_recording = True
            self.recorded_frames = []
            self.markers = []
            self.marker_counter = 0
            self.recording_start_monotonic = time.monotonic()
            self.session_start_iso = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            self.is_recording = False
        return self.is_recording

    def add_marker(self, label: Optional[str] = None) -> Marker:
        self.marker_counter += 1
        current_rel_time = (
            time.monotonic() - self.recording_start_monotonic
            if self.is_recording
            else 0.0
        )
        resolved_label = label if label else f"Manual Marker {self.marker_counter}"
        marker = Marker(timestamp=current_rel_time, label=resolved_label)
        self.markers.append(marker)
        return marker

    def get_current_duration(self) -> float:
        if not self.is_recording:
            return 0.0
        return time.monotonic() - self.recording_start_monotonic

    def get_sorted_rankings(self):
        return sorted(
            self.id_frequencies.items(), key=lambda item: item[1], reverse=True
        )
