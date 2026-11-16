# Lapse Lab by Little

A lightweight G-code post-processing utility built for FDM 3D printers (such as the Anycubic Kobra 2 Neo) to automate smooth, park-and-trigger 3D printing timelapses using a physical camera shutter remote or limit switch[cite: 8]. Instead of relying on OctoPrint or firmware-level webcam plugins, it injects precise motion, retraction, Z-hop, and dwell commands directly into sliced G-code files[cite: 8].
<img width="535" height="535" alt="image" src="https://github.com/user-attachments/assets/2dd4683f-b809-464e-9e14-ff67bb9ad344" />


## Dual Operating Modes

Lapse Lab automatically adapts its interface and file-handling workflow depending on how it is launched[cite: 7, 8]:

- **Standalone Mode (Manual Patching):** When launched directly from the desktop shortcut, Start Menu, or `LapseLab.exe`, the app lets you browse for any pre-sliced `.gcode` file[cite: 8]. After injecting the timelapse macros, it recalculates the total print duration, updates internal `;TIME:` metadata, and prompts you to save a new copy (`<filename>_timelapse_<duration>.gcode`) without overwriting your original file[cite: 7, 8].



- **Slicer Plugin Mode (Anycubic Slicer Next Integration):** When selected via one of the dedicated `(LapseLab)` process presets in Anycubic Slicer Next, slicing and exporting G-code launches Lapse Lab automatically with the temporary `.gcode` file pre-loaded and the file browser locked[cite: 7, 8]. Once you configure your capture settings and click **Apply Timelapse & Return to Slicer**, Lapse Lab patches the temporary file in place and closes cleanly so the slicer immediately finishes exporting[cite: 7, 8].

<img width="1599" height="852" alt="image" src="https://github.com/user-attachments/assets/738de8c3-fd17-4fde-acc5-0cffc2dd14e4" />

## Configurable Timelapse & Motion Parameters

<img width="536" height="538" alt="image" src="https://github.com/user-attachments/assets/eac56005-2f04-4eb1-ad44-36e9e014f1a8" />


Every parameter in the right-hand control panel directly maps to the G-code macro injected between layers[cite: 7, 8]:

| Parameter | Default | Unit | Function & G-code Behavior |
| :--- | :--- | :--- | :--- |
| **How often (layers)** | `Every Layer` | Layers | Sets capture frequency (`Every Layer`, `2nd`, `3rd`, `5th`, `10th`, or `25th`), allowing shorter timelapses on tall prints[cite: 7, 8]. |
| **Pause before click (anti-shake)** | `250` | `ms` | Inserts a `G4 P<ms>` dwell after parking so gantry vibrations settle before triggering the shutter[cite: 7, 8]. |
| **Button Pressing Time** | `150` | `ms` | Controls how long the printhead holds the physical shutter switch depressed (`G4 P<ms>`) to ensure reliable camera focus and capture[cite: 7, 8]. |
| **Pause after image** | `600` | `ms` | Holds the printhead stationary (`G4 P<ms>`) while the camera writes the photo to storage, preventing motion blur in the frame[cite: 7, 8]. |
| **Shutter Click X Location** | `228.0` | `mm` | The exact X-axis coordinate where the toolhead physically presses the mounted shutter switch (`G1 X<val> F3000`)[cite: 7, 8]. |
| **Approach / Pre-click Distance** | `2.0` | `mm` | Positions the toolhead just short of the trigger (`Shutter X - Approach`) before decelerating into the button press, avoiding hard mechanical impacts[cite: 7, 8]. |
| **Park Print Head Y (Focus)** | `190.0` | `mm` | Moves the build plate forward along the Y-axis (`G0 Y<val>`) to frame the printed model cleanly in the camera's focal plane[cite: 7, 8]. |
| **Retract when required** | `ON` | Toggle | Performs a `0.80 mm` filament retraction (`G1 E-0.80 F3000`) before parking and primes (`G1 E0.80 F2400`) upon returning to prevent oozing and stringing[cite: 7, 8]. |
| **Z-Hop Height When Parking** | `2.0` | `mm` | Lifts the nozzle vertically (`G0 Z<val> F3000`) in relative mode (`G91`) before traveling across the print bed, then lowers it back before resuming extrusion[cite: 7, 8]. |
| **Ensure Final Image** | `ON` | Toggle | Appends an end-of-print capture macro at the end of the G-code so the completed model is always photographed after the final layer finishes[cite: 7, 8]. |

## Smart G-code Processing & Safety Features

- **Multi-Slicer Layer Marker Detection:** Automatically parses layer transitions across Anycubic Slicer Next, OrcaSlicer, PrusaSlicer (`; AFTER_LAYER_CHANGE` / `;LAYER_CHANGE`), and Cura (`;LAYER:`)[cite: 7, 8].
- **Idempotent Re-Patching:** Automatically detects and strips any previously injected Lapse Lab macro blocks (`; --- Upgraded Timelapse Macro Begin ---` through `End ---`) before applying new settings, preventing duplicate triggers if a file is patched twice[cite: 7, 8].
- **Motion Synchronization (`M400`):** Wraps travel moves and shutter clicks with `M400` planner-sync commands so the printer never fires the shutter early while moves are still buffered[cite: 7, 8].
- **Accurate Print Time Recalculation:** Parses the slicer's original estimated print time, adds the exact travel, Z-hop, shutter press, and dwell overhead for every triggered layer, updates the `;TIME:` header, and appends the updated duration (e.g., `_2h14m30s`) to the exported filename[cite: 7, 8].

## Installer & Slicer Integration Architecture

- **Zero-Dependency Executable:** Packaged as a standalone Windows `.exe` (`LapseLab.exe`) with Python, Tkinter, Pillow, and UI assets bundled internally—end users do not need Python or external libraries installed[cite: 8].
- **Automated Preset Provisioning:** The Windows installer (`LapseLab_Setup.exe`) detects Anycubic Slicer Next, installs `LapseLab.exe` into `C:\Program Files\AnycubicSlicerNext\scripts\`, and registers 5 dedicated user presets (`0.12mm` through `0.28mm Standard @Anycubic Kobra 2 Neo 0.4 nozzle (LapseLab)`) alongside the factory presets with the post-processing path pre-configured[cite: 8].
- **Clean Uninstallation:** Uninstalling through Windows Settings automatically removes `LapseLab.exe`, desktop/Start Menu shortcuts, and all generated `(LapseLab)` `.json` and `.info` preset files from Anycubic Slicer Next without altering factory profiles[cite: 8].

## Requirements (Running from Source)
- Python 3.8+
- `Pillow` *(optional, for high-resolution sidebar splash image rendering)*:
  ```bash
  pip install pillow
