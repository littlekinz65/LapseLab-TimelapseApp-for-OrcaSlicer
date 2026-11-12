# Lapse Lab by Little

A lightweight desktop GUI application built in Python & Tkinter that patches sliced 3D printing G-code files with automated shutter-trigger macros for smooth, layer-by-layer 3D printing timelapses[cite: 1, 2].

<img width="535" height="535" alt="image" src="https://github.com/user-attachments/assets/d417d434-d7f2-4902-8f31-349f28a870c0" />

## Features
- **Universal Slicer Support:** Automatically detects layer markers from OrcaSlicer, PrusaSlicer (`; AFTER_LAYER_CHANGE` / `;LAYER_CHANGE`), and Cura (`;LAYER:`)[cite: 1, 2].
- **Physical Shutter Triggering:** Parks the print head at a custom X/Y coordinate to press a physical Bluetooth or wired camera shutter button, complete with approach distance and anti-shake settle delays[cite: 1, 2].
- **Print Quality Protection:** Built-in filament retraction, Z-hop lift before travel, and nozzle priming after each frame to prevent oozing, stringing, and surface blobs[cite: 1, 2].
- **Flexible Capture Intervals:** Trigger every layer or every 2nd, 3rd, 5th, 10th, or 25th layer, plus an option to ensure a final completion frame[cite: 1, 2].
- **Accurate Print Time Estimation:** Recalculates the total print duration (`;TIME:`) by factoring in travel, Z-hop, and dwell times, and appends the updated duration directly to the output filename[cite: 1, 2].

## Parameter Guide

| Parameter | Default | Unit | Description |
| :--- | :--- | :--- | :--- |
| **How often (layers)** | `Every Layer` | Layers | Sets the capture interval (`Every Layer`, `Every 2nd`, `Every 3rd`, `Every 5th`, `Every 10th`, or `Every 25th`). Useful for shortening final video length on tall prints[cite: 1, 2]. |
| **Pause before click (anti-shake)** | `250` | `ms` | Dwell time (`G4`) after the print head parks at the pre-click position, allowing printer vibrations to settle before taking a photo[cite: 1, 2]. |
| **Button Pressing Time** | `150` | `ms` | How long the print head holds the physical shutter button pressed (`G4`) so the camera/phone reliably registers the trigger[cite: 1, 2]. |
| **Pause after image** | `600` | `ms` | Wait time after releasing the shutter button, giving the camera sensor time to capture and save the frame before the print head moves back[cite: 1, 2]. |
| **Shutter Click X Location** | `228.0` | `mm` | The exact X-axis coordinate where the toolhead physically presses the shutter switch[cite: 1, 2]. |
| **Approach / Pre-click Distance** | `2.0` | `mm` | The offset distance before `Shutter Click X Location` (`Shutter X - Approach Distance`) where the toolhead initially parks before moving in slowly (`F3000`) to press the button[cite: 1, 2]. |
| **Park Print Head Y (Focus)** | `190.0` | `mm` | The Y-axis position where the bed/print head parks during photo capture—ideal for positioning the print cleanly in your camera's focal plane[cite: 1, 2]. |
| **Retract when required** | `ON` | Toggle | Retracts filament (`0.8 mm` at `F3000`) before parking and primes it (`0.8 mm` at `F2400`) upon returning to prevent oozing onto the print[cite: 1, 2]. |
| **Z-Hop Height When Parking** | `2.0` | `mm` | Lifts the nozzle vertically by this amount before traveling to the shutter button and lowers it back afterward, preventing nozzle collisions or scarring on the top layer (set to `0` to disable)[cite: 1, 2]. |
| **Ensure Final Image** | `ON` | Toggle | Appends one final shutter-trigger sequence at the very end of the G-code so the completed model is always captured[cite: 1, 2]. |

## Usage
1. Slice your 3D model in OrcaSlicer, PrusaSlicer, or Cura and export the `.gcode` file[cite: 1, 2].
2. Open **Lapse Lab** and click **Browse...** to load your `.gcode` file[cite: 1, 2].
3. Adjust your shutter X-coordinate, Y-parking position, and timing delays to match your physical shutter mount and camera speed[cite: 1, 2].
4. Click **Patch G-code & Save File As...** to export the timelapse-ready file (automatically named with `_timelapse` and the recalculated print duration)[cite: 1, 2].

## Requirements (Running from Source)
- Python 3.8+
- `Pillow` *(optional, for high-resolution sidebar splash image rendering)*[cite: 1, 2]:
  ```bash
  pip install pillow
