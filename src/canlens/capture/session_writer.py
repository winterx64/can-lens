import asyncio
import json
import os
from datetime import datetime
from typing import List

from .models import CanFrame, Marker


class SessionWriter:
    def __init__(self, base_path: str = "storage/sessions"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save_session(
        self,
        session_id: str,
        start_time_iso: str,
        duration: float,
        frames: List[CanFrame],
        markers: List[Marker],
    ) -> str:
        return await asyncio.to_thread(
            self._write_blocking, session_id, start_time_iso, duration, frames, markers
        )

    def _write_blocking(
        self,
        session_id: str,
        start_time_iso: str,
        duration: float,
        frames: List[CanFrame],
        markers: List[Marker],
    ) -> str:
        folder_path = os.path.join(self.base_path, session_id)
        os.makedirs(folder_path, exist_ok=True)

        tsv_path = os.path.join(folder_path, "capture.tsv")
        with open(tsv_path, "w", encoding="utf-8") as f:
            f.write(
                "Time Stamp\tID\tExtended\tDir\tBus\tLEN\tD1\tD2\tD3\tD4\tD5\tD6\tD7\tD8\n"
            )
            for frame in frames:
                hex_id = f"0x{frame.arbitration_id:X}"
                data_bytes = list(frame.data)
                padded = [
                    f"{data_bytes[i]:02X}" if i < len(data_bytes) else "00"
                    for i in range(8)
                ]
                f.write(
                    f"{frame.timestamp:.6f}\t{hex_id}\t{frame.is_extended_id}\tRX\t{frame.channel}\t{frame.dlc}\t"
                    + "\t".join(padded)
                    + "\n"
                )

        with open(
            os.path.join(folder_path, "markers.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(
                [
                    {"timestamp": round(m.timestamp, 3), "label": m.label}
                    for m in markers
                ],
                f,
                indent=2,
            )

        with open(
            os.path.join(folder_path, "metadata.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(
                {
                    "session_name": session_id,
                    "start_time": start_time_iso,
                    "duration": round(duration, 2),
                    "frames": len(frames),
                },
                f,
                indent=2,
            )

        with open(
            os.path.join(folder_path, "activity.log"), "w", encoding="utf-8"
        ) as f:
            f.write(
                f"[{start_time_iso}] Log initialised.\n[{datetime.now().isoformat()}] Log closed. Collected {len(frames)} records.\n"
            )

        return folder_path
