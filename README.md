# flash-sidebar-translator

An ultra-lightweight, non-intrusive Windows desktop HUD utility designed for seamless reading workflows. Operating purely as an invisible background process, the application monitors global inputs and renders an elegant, borderless translation card in the bottom-right corner of the screen for exactly 5 seconds upon request. 

The user interface utilizes a frameless overlay design with zero taskbar footprint, providing a clean system-native notification experience.

## Core Mechanics
- **Frameless Overlay Design**: Built with an unbordered, frameless overlay (`overrideredirect`) to match professional system HUDs, removing standard native operating system window dressing.
- **Zero Taskbar Footprint**: Utilizing low-level system flags (`WS_EX_TOOLWINDOW`), the application hides completely from the Windows taskbar, running solely as a lightweight agent.
- **Hot-Key Automation**: Captures the active system selection and executes an automated translation workflow via `Ctrl + Q`. No manual copying, pasting, or application switching is required.
- **Asynchronous Execution**: Threaded global keyboard listeners ensure that hotkey monitoring never blocks the desktop window thread or compromises UI responsiveness.
- **Transient HUD Presence**: The interface elevates itself to the front layer dynamically when called, holds visibility for 5,000 milliseconds, and automatically demotes itself beneath active windows.

## Technical Architecture
- **Language**: Python 3.13+
- **GUI Engine**: Tkinter
- **Dependencies**:
  - `translators`: Handles robust interface communication with translation endpoints.
  - `keyboard`: Low-level global hooks for asynchronous macro monitoring.
  - `ctypes`: Native Windows API bindings for system window configuration.

## Installation and Deployment

### 1. Install Dependencies
Clone the repository and install the production requirements using pip:
```bash
pip install translators keyboard pyinstaller
