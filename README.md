# 🔍 CanLens

[![Automated Build and Release](https://github.com/winterx64/can-lens/actions/workflows/release.yml/badge.svg)](https://github.com/winterx64/can-lens/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/)
[![Built with Textual](https://img.shields.io/badge/built%20with-Textual-f39c12.svg?style=flat-square)](https://textual.textualize.io/)

> **CanLens** is a professional terminal-based CAN Investigation Workstation designed for low-overhead reverse engineering, real-time packet parsing, and secure high-fidelity logging diagnostics. Built natively using `Textual`, `Rich`, and `python-can`.



## ⚡ Core Architecture Features

* **High-Performance Isolated Pipeline:** Implements an asynchronous background parsing system decoupling real-time CAN bus streams from terminal rendering loops to guarantee zero frame drop overhead.
* **Granular Trace Markers:** Drop instant synchronization timeline checkpoints using structural indices mapping high-resolution runtime deltas to incoming stream boundaries.
* **Self-Contained Portable Executable:** Leverages modern Python build systems for zero-dependency localized sandboxed tool runtimes using `uv`.
* **Standardized Persistence Footprints:** Outputs independent tracking directories detailing synchronized hex telemetry matrices, human-readable layout run lists, and detailed session data blocks.


## 📂 Structural Codebase Hierarchy

The workstation uses a standardized industry-compliant `src/` application framework for package namespace isolation:

```text
can-lens/
├── .github/workflows/          # Automated release compilation actions
├── src/
│   └── canlens/
│       ├── __init__.py         # Package initialization marker
│       ├── app.py              # Application main workspace entry loop
│       ├── capture/            # Real-time data collection wrappers
│       │   ├── can_reader.py   # Async loop interface background threads
│       │   ├── models.py       # Core telemetry data abstractions
│       │   ├── recorder.py     # Recording buffer handlers
│       │   └── session_writer.py
│       └── ui/                 # Textual frontend environment layers
│           ├── screens/        # Full TUI layout dashboard screens
│           └── widgets/        # Isolated tracking interface elements
├── pyproject.toml              # Build tool chain dependencies & metadata
└── README.md                   # Core project documentation profile

```



## 🛠️ Hardware Driver Pipeline Setup

If you are deploying on a Raspberry Pi using the **Waveshare USB-CAN-B (Microchip/Chuangxin Tech `04d8:0053` architecture)**, the hardware operates via bulk endpoints rather than generic virtual serial lines. Bridge it cleanly into native Linux **SocketCAN** with these steps:

### 1. Build and Inject the Kernel Module Driver

```bash
# Install development headers and toolchains
sudo apt update
sudo apt install -y git dkms linux-headers-rpi-v8 build-essential

# Clone and compile the kernel space driver wrapper mapping framework
git clone [https://github.com/romtech/canalystii_usb.git](https://github.com/romtech/canalystii_usb.git)
cd canalystii_usb
make
sudo make install
sudo modprobe canalystii_usb

```

### 2. Initialize and Activate the SocketCAN Interface

Unplug your USB-CAN-B adapter, reconnect it to a blue USB 3.0 port, and bring the mapped interface online at your target network bus speed (e.g., 500kbps):

```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
sudo ip link set can0 txqueuelen 1000

```

Verify your active physical network signal activity streams prior to launching the application workstation layout:

```bash
candump can0

```



## 🚀 Native Shell Workspace Installation

Ensure your local or target device has the modern fast environment manager **`uv`** installed.

### Production Environment Deployment (Recommended)

Install the standardized application executable tool securely out of the automated build distribution tracking pipeline channel:

```bash
uv tool install [https://github.com/winterx64/can-lens/releases/download/v0.1.1/canlens-0.1.1-py3-none-any.whl](https://github.com/winterx64/can-lens/releases/download/v0.1.1/canlens-0.1.1-py3-none-any.whl)

```

Launch the workstation interface utility instantly right from your active shell environment terminal directory:

```bash
canlens

```

### Local Workspace Development Sandbox

If you are modifying tracking layers or extending interface features inside your local repository folder path:

```bash
# Clone the repository framework layout
git clone [https://github.com/winterx64/can-lens.git](https://github.com/winterx64/can-lens.git)
cd can-lens

# Lock toolchains and dependencies locally
uv sync

# Launch the validation workbench
uv run canlens

```

## 💾 Telemetry Session Storage Footprint

Active telemetry recording file sets are stored directly within a local `storage/` directory inside your active running terminal paths:

```text
./storage/sessions/
└── [Timestamp]_TelemetryRun/
    ├── activity.log    # TUI operations history and hardware logs
    ├── capture.tsv     # Tab-separated high-resolution delta frame hex log
    ├── markers.json    # Pinpoint timestamps dropped manually during runs
    └── metadata.json   # Session properties, bitrates, and packet metrics

```


## 📝 License

Distributed under the MIT License. See `LICENSE` inside your repository profile for extended tracking information details.
