import asyncio
import threading
import time

import can

from canlens.capture.models import CanFrame


class CanReader:
    def __init__(
        self,
        interface: str = "socketcan",
        channel: str = "vcan0",
        bitrate: int = 500000,
    ):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.queue: asyncio.Queue[CanFrame] = asyncio.Queue()
        self._loop = None
        self._running = False
        self._start_time = time.monotonic()

    def start(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._running = True
        self._start_time = time.monotonic()
        threading.Thread(target=self._reader_thread, daemon=True).start()

    def _reader_thread(self):
        try:
            bus = can.Bus(
                interface=self.interface, channel=self.channel, bitrate=self.bitrate
            )
        except Exception:
            bus = can.Bus(interface="virtual", channel="vcan0")

        while self._running:
            try:
                msg = bus.recv(timeout=0.1)
                if msg is not None:
                    frame = CanFrame(
                        timestamp=time.monotonic() - self._start_time,
                        arbitration_id=msg.arbitration_id,
                        dlc=msg.dlc,
                        data=bytes(msg.data),
                        is_extended_id=msg.is_extended_id,
                        channel=str(msg.channel),
                    )
                    if self._loop and self._loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            self.queue.put(frame), self._loop
                        )
            except Exception:
                continue
        try:
            bus.shutdown()
        except Exception:
            pass

    def stop(self):
        self._running = False
