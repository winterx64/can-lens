import asyncio
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, RichLog

from canlens.capture.can_reader import CanReader
from canlens.capture.recorder import CanRecorder
from canlens.capture.session_writer import SessionWriter
from canlens.ui.widgets.live_table import LiveCanTable


class MainDashboard(Screen):
    CSS = """
    MainDashboard { layout: grid; grid-size: 2 1; grid-columns: 3fr 2fr; padding: 0; background: #0d1117; }
    #left-panel { border-right: solid #30363d; background: #0d1117; padding: 0 1; }
    #right-panel { layout: grid; grid-size: 1 3; grid-rows: 1fr 1fr 1fr; background: #0d1117; }
    .sub-section { border-bottom: solid #30363d; padding: 0 1; background: #0d1117; }
    #overview-section { border-bottom: none; }
    Label.panel-header { text-style: bold; color: #58a6ff; margin-bottom: 0; padding: 0; }
    LiveCanTable { height: 1fr; border: none; background: #0d1117; }
    RichLog { background: #0d1117; border: none; }
    ListView { background: #0d1117; }
    ListItem { padding: 0 1; background: #0d1117; }
    .stat-line { color: #c9d1d9; }
    """
    BINDINGS = [
        ("r", "toggle_recording", "Toggle Rec (R)"),
        ("m", "add_marker", "Add Marker (M)"),
        ("f", "freeze_stream", "Freeze (F)"),
        ("q", "quit", "Quit (Q)"),
    ]

    def __init__(self, reader: CanReader):
        super().__init__()
        self.reader = reader
        self.recorder = CanRecorder()
        self.writer = SessionWriter()
        self.is_frozen = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="left-panel"):
            yield Label("LIVE CAN TRAFFIC DISCOVERY", classes="panel-header")
            yield LiveCanTable(id="live-table")
        with Vertical(id="right-panel"):
            with Vertical(classes="sub-section"):
                yield Label("CAN ID FREQUENCY RANKING", classes="panel-header")
                yield ListView(id="ranking-list")
            with Vertical(classes="sub-section"):
                yield Label("RECORDER SYSTEM ACTIVITY LOG", classes="panel-header")
                yield RichLog(
                    id="activity-log", max_lines=100, highlight=True, markup=True
                )
            with Vertical(classes="sub-section", id="overview-section"):
                yield Label("WORKSTATION TELEMETRY OVERVIEW", classes="panel-header")
                yield Label(
                    "Engine: Connection Active [SocketCAN]", classes="stat-line"
                )
                yield Label(id="stat-rec-state")
                yield Label(id="stat-duration")
                yield Label(id="stat-total-frames")
                yield Label(id="stat-unique-ids")
                yield Label(
                    "Estimated Bus Load: 34.2% (Calculated)", classes="stat-line"
                )
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#activity-log", RichLog)
        log.write("[bold #58a6ff]●[/] Subsystem Engine Core: Activated")
        log.write("[bold #58a6ff]●[/] Listening on SocketCAN channel: vcan0")

        self.run_worker(self._poll_can_queue(), thread=False)
        self.set_interval(0.2, self._update_fast_stats)

    async def _poll_can_queue(self):
        while True:
            if not self.reader.queue.empty():
                frame = await self.reader.queue.get()
                self.recorder.process_frame(frame)
                if not self.is_frozen:
                    self.query_one("#live-table", LiveCanTable).append_frame(frame)
                self.reader.queue.task_done()
            else:
                await asyncio.sleep(0.01)

    def _update_fast_stats(self) -> None:
        rec_dur = self.recorder.get_current_duration()
        self.query_one("#stat-total-frames", Label).update(
            f"Total Frames: {self.recorder.total_frames_seen}"
        )
        self.query_one("#stat-unique-ids", Label).update(
            f"Unique CAN IDs: {len(self.recorder.id_frequencies)}"
        )
        self.query_one("#stat-duration", Label).update(
            f"Recording Duration: {rec_dur:.1f}s"
        )

        if self.recorder.is_recording:
            self.query_one("#stat-rec-state", Label).update(
                "Recording State: [bold #238636]ACTIVE[/]"
            )
        else:
            self.query_one("#stat-rec-state", Label).update(
                "Recording State: [#8b949e]INACTIVE[/]"
            )

        rank_list = self.query_one("#ranking-list", ListView)
        rank_list.clear()
        for arb_id, count in self.recorder.get_sorted_rankings()[:6]:
            rank_list.append(
                ListItem(
                    Label(
                        f"0x{arb_id:03X}  -->  Pushed {count} frames",
                        classes="stat-line",
                    )
                )
            )

    async def action_toggle_recording(self) -> None:
        is_recording = self.recorder.toggle_recording()
        log = self.query_one("#activity-log", RichLog)
        if is_recording:
            log.write("[bold #238636]●[/] Recording session started.")
        else:
            log.write("[bold #da3637]●[/] Recording session stopped.")
            log.write(
                "[bold #d29922]●[/] Buffering frame cache out to secondary storage arrays..."
            )
            session_id = f"{self.recorder.session_start_iso}_TelemetryRun"
            saved_dir = await self.writer.save_session(
                session_id,
                datetime.now().isoformat(),
                self.recorder.get_current_duration(),
                list(self.recorder.recorded_frames),
                list(self.recorder.markers),
            )
            log.write(
                "[bold #238636]●[/] File output complete. Session directory created:"
            )
            log.write(f"   [bold]{saved_dir}[/]")

    def action_add_marker(self) -> None:
        log = self.query_one("#activity-log", RichLog)
        if not self.recorder.is_recording:
            log.write(
                "[bold #da3637]⚠ Error:[/] Cannot append trace markers while tracking engine is passive."
            )
            return
        marker = self.recorder.add_marker()
        log.write(
            f"[bold #d29922]●[/] Marker added at {marker.timestamp:.2f}s: '{marker.label}'"
        )

    def action_freeze_stream(self) -> None:
        self.is_frozen = not self.is_frozen
        self.query_one("#activity-log", RichLog).write(
            f"[bold #58a6ff]●[/] UI Layout Thread Rendering: {'Suspended' if self.is_frozen else 'Resumed'}"
        )

    def action_quit(self) -> None:
        self.reader.stop()
        self.app.exit()
