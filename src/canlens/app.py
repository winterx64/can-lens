import asyncio

from textual.app import App

from canlens.capture.can_reader import CanReader
from canlens.ui.screens.main_screen import MainDashboard


class CanLensApplication(App):
    TITLE = "CanLens :: Investigation Workstation"
    SUB_TITLE = "Telemetry Analysis & Passive Frame Capture Terminal"

    def __init__(self):
        super().__init__()
        self.can_reader = CanReader(interface="socketcan", channel="vcan0")

    def on_mount(self) -> None:
        loop = asyncio.get_running_loop()
        self.can_reader.start(loop)
        self.push_screen(MainDashboard(self.can_reader))


def run_app():
    """Package entry point wrapper."""
    app = CanLensApplication()
    app.run()


if __name__ == "__main__":
    run_app()
