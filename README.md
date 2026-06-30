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

---

## 📅 Changelog

### [v2.0.0] - Ultimate Production Edition (Current)
* **Golden Left-Hand Hotkey Flow**: Migrated all standard hotkeys to ` ` ` + Number` combinations to completely eliminate typing conflicts with daily workflows.
  * `` ` + 1 ``: Auto-copy & instant **English to Traditional Chinese** translation (logs to Vocabulary DB).
  * `` ` + 2 ``: Spawns an **on-demand Chinese-to-English** input dialog; auto-destroys upon Enter submission.
  * `` ` + 3 ``: Instantly toggles the interactive **Vocabulary Database Log** window.
  * `` ` + 4 ``: Safe-exit macro that instantly terminates the entire background process.
* **Intelligent Dynamic HUD Sizing**: 
  * The HUD notification window now automatically calculates text row count and dynamically scales its height.
  * Implemented an upward-growth positioning algorithm to ensure the card stays pinned perfectly to the bottom-right corner without clipping off-screen.
  * Enforced a hard `max_height` ceiling to allow smooth text scrolling for long-form paragraphs.
* **Interactive Vocabulary DB Management**:
  * Enhanced the log window with a responsive, dedicated layout featuring a smooth **vertical scrollbar** and full **mouse-wheel scrolling** support.
  * Embedded an instant **"❌ Delete" button** for each logged entry, allowing users to wipe accidentally triggered words from the local `vocabulary_log.txt` on the fly.
* **Architecture Stability**: Added safety toggle locks (`is_input_active`, `is_vocab_open`) to strictly prevent multi-window layering glitches from accidental rapid keystrokes.

### [v1.0.0] - Initial Prototype Release
* Implemented the baseline asynchronous `keyboard` hook listener thread.
* Created the frameless `overrideredirect` Tkinter window with automatic 5-second fade/demote timer.
* Integrated lightweight web translation endpoints with basic `vocabulary_log.txt` storage.
