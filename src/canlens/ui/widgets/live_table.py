from textual.widgets import DataTable

from canlens.capture.models import CanFrame


class LiveCanTable(DataTable):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Time", "ID", "LEN", "DATA")

    def append_frame(self, frame: CanFrame, max_buffer_size: int = 50):
        hex_id = f"0x{frame.arbitration_id:03X}"
        hex_data = " ".join(f"{b:02X}" for b in frame.data)
        self.add_row(f"{frame.timestamp:.4f}", hex_id, str(frame.dlc), hex_data)

        if len(self.rows) > max_buffer_size:
            try:
                first_row_key = list(self.rows.keys())[0]
                self.remove_row(first_row_key)
            except Exception:
                pass
