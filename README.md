# Lapse Lab by Little

A lightweight G-code and `.gcode.3mf` post-processing utility built for FDM 3D printers to automate smooth, park-and-trigger 3D printing timelapses using a physical camera shutter remote or limit switch. Instead of relying on OctoPrint or firmware-level webcam plugins, it injects synchronized motion, retraction, Z-hop, and dwell commands directly into sliced files.

<img width="535" height="535" alt="image" src="https://github.com/user-attachments/assets/2dd4683f-b809-464e-9e14-ff67bb9ad344" />

## What's New in v1.2.0
- **`.gcode.3mf` & `.3mf` Archive Support:** Directly patches sliced plates (`Metadata/plate_*.gcode`) inside OrcaSlicer, Bambu Studio, and Anycubic Slicer Next `.gcode.3mf` packages while automatically recalculating internal `.md5` checksums so printers validate the modified file cleanly[cite: 10].
- **Persistent User Preferences:** Automatically saves your custom shutter X/Y coordinates, delays, Z-hop, and interval choices to `%LOCALAPPDATA%\LapseLab\config.json` between sessions[cite: 10].
- **Extrusion Mode Auto-Detection (`M82` / `M83`):** Detects whether the sliced file uses absolute (`M82`) or relative (`M83`) extrusion, switches safely to `M83` for retraction/priming, and restores the original mode afterward to prevent extrusion blobbing or under-extrusion[cite: 10].
- **Modular Windows Installer (`LapseLab_Setup.exe`):** Installs standalone into `C:\Program Files\Lapse Lab` with an optional **Anycubic Slicer Next** component checkbox that automatically detects your slicer path via the Windows Registry and provisions `(LapseLab)` process presets[cite: 11, 12].
- **Upgrade Guard:** Detects older v1.0/v1.1 installations before setup and prompts for a clean uninstall first to prevent duplicate slicer presets[cite: 11].

## Dual Operating Modes

Lapse Lab automatically adapts its interface and file-handling workflow depending on how it is launched:

- **Standalone Mode (Manual Patching):** Launch from the desktop shortcut, Start Menu, or `LapseLab.exe` to browse for any pre-sliced `.gcode` or `.gcode.3mf` file[cite: 10, 11]. After injecting the timelapse macros, it recalculates the total print duration, updates internal `;TIME:` metadata, and saves a new copy (`<filename>_timelapse_<duration>.gcode` or `.gcode.3mf`) without overwriting your original file[cite: 10].
- **Slicer Plugin Mode (Anycubic Slicer Next Integration):** Select one of the dedicated `(LapseLab)` process presets in Anycubic Slicer Next[cite: 12]. Slicing and exporting launches Lapse Lab automatically with the temporary file pre-loaded and the file browser locked[cite: 10]. Click **Apply Timelapse & Return to Slicer** to patch the file in place and return immediately to the slicer[cite: 10].

<img width="1599" height="852" alt="image" src="https://github.com/user-attachments/assets/738de8c3-fd17-4fde-acc5-0cffc2dd14e4" />

## Configurable Timelapse & Motion Parameters

<img width="536" height="538" alt="image" src="https://github.com/user-attachments/assets/eac56005-2f04-4eb1-ad44-36e9e014f1a8" />

| Parameter | Default | Unit | Function & G-code Behavior |
| :--- | :--- | :--- | :--- |
| **How often (layers)** | `Every Layer` | Layers | Sets capture frequency (`Every Layer`, `2nd`, `3rd`, `5th`, `10th`, or `25th`), allowing shorter timelapses on tall prints[cite: 10]. |
| **Pause before click (anti-shake)** | `250` | `ms` | Inserts a `G4 P<ms>` dwell after parking so gantry vibrations settle before triggering the shutter[cite: 10]. |
| **Button Pressing Time** | `150` | `ms` | Controls how long the printhead holds the physical shutter switch depressed (`G4 P<ms>`) to ensure reliable camera focus and capture[cite: 10]. |
| **Pause after image** | `600` | `ms` | Holds the printhead stationary (`G4 P<ms>`) while the camera writes the photo to storage, preventing motion blur in the frame[cite: 10]. |
| **Shutter Click X Location** | `228.0` | `mm` | The exact X-axis coordinate where the toolhead physically presses the mounted shutter switch (`G1 X<val> F3000`)[cite: 10]. |
| **Approach / Pre-click Distance** | `2.0` | `mm` | Positions the toolhead just short of the trigger (`Shutter X - Approach`) before decelerating into the button press, avoiding hard mechanical impacts[cite: 10]. |
| **Park Print Head Y (Focus)** | `190.0` | `mm` | Moves the build plate forward along the Y-axis (`G0 Y<val>`) to frame the printed model cleanly in the camera's focal plane[cite: 10]. |
| **Retract when required** | `ON` | Toggle | Switches to relative extrusion (`M83`), retracts `0.80 mm` (`G1 E-0.80 F3000`) before parking, primes `0.80 mm` (`G1 E0.80 F2400`) upon returning, and restores the original `M82`/`M83` mode[cite: 10]. |
| **Z-Hop Height When Parking** | `2.0` | `mm` | Lifts the nozzle vertically (`G0 Z<val> F3000`) in relative mode (`G91`) before traveling across the print bed, then lowers it back before resuming extrusion[cite: 10]. |
| **Ensure Final Image** | `ON` | Toggle | Appends an end-of-print capture macro at the end of the G-code so the completed model is always photographed after the final layer finishes[cite: 10]. |

## Smart G-code Processing & Safety Features

- **Multi-Slicer Layer Marker Detection:** Parses layer transitions across Anycubic Slicer Next, OrcaSlicer, Bambu Studio, PrusaSlicer (`; AFTER_LAYER_CHANGE` / `;LAYER_CHANGE`), and Cura (`;LAYER:`)[cite: 10].
- **Idempotent Re-Patching:** Detects and strips any previously injected Lapse Lab macro blocks (`; --- Upgraded Timelapse Macro Begin ---` through `End ---`) before applying new settings, preventing duplicate triggers if a file is patched twice[cite: 10].
- **Motion Synchronization (`M400`):** Wraps travel moves and shutter clicks with `M400` planner-sync commands so the printer never fires the shutter early while moves are still buffered[cite: 10].
- **Accurate Print Time Recalculation:** Parses the slicer's original estimated print time, adds travel, Z-hop, shutter press, and dwell overhead for every triggered layer, updates the `;TIME:` header, and appends the updated duration (e.g., `_2h14m30s`) to the exported filename[cite: 10].

## Building & Running from Source

- **Requirements:** Python 3.8+ and `Pillow` *(optional, for high-resolution sidebar splash image rendering)*[cite: 10]:
  ```bash
  pip install pillow
