import os
import sys
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller --onefile."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class ToggleSwitch(tk.Canvas):
    """Modern pill-shaped ON/OFF toggle switch widget."""
    def __init__(self, parent, variable, width=36, height=18, bg_color="#ffffff",
                 on_color="#0066cc", off_color="#cccccc", knob_color="#ffffff"):
        super().__init__(parent, width=width, height=height, bg=bg_color,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.variable = variable
        self.width = width
        self.height = height
        self.on_color = on_color
        self.off_color = off_color
        self.knob_color = knob_color

        self.bind("<Button-1>", self.toggle)
        self.variable.trace_add("write", lambda *args: self.draw())
        self.draw()

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())

    def draw(self):
        self.delete("all")
        state = self.variable.get()
        track_color = self.on_color if state else self.off_color
        r = self.height // 2

        # Pill track
        self.create_oval(1, 1, self.height - 1, self.height - 1, fill=track_color, outline=track_color)
        self.create_oval(self.width - self.height + 1, 1, self.width - 1, self.height - 1, fill=track_color, outline=track_color)
        self.create_rectangle(r, 1, self.width - r, self.height - 1, fill=track_color, outline=track_color)

        # Sliding circular knob
        pad = 3
        knob_d = self.height - (pad * 2)
        x_pos = (self.width - knob_d - pad) if state else pad
        self.create_oval(x_pos, pad, x_pos + knob_d, pad + knob_d, fill=self.knob_color, outline="")


class SmoothProgressBar(tk.Canvas):
    """Smooth green-gradient progress bar matching the UI layout."""
    def __init__(self, parent, height=13, track_color="#d3d3d3"):
        super().__init__(parent, height=height, bg=track_color, highlightthickness=0, bd=0)
        self.height = height
        self.track_color = track_color
        self.progress = 0.0  # 0.0 to 1.0
        self.bind("<Configure>", lambda e: self.draw())

    def set_progress(self, value):
        self.progress = max(0.0, min(1.0, value))
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            return

        fill_w = int(w * self.progress)
        if fill_w <= 0:
            return

        # Smooth green gradient (#4eb832 -> #8ce02c)
        r1, g1, b1 = 0x4e, 0xb8, 0x32
        r2, g2, b2 = 0x8c, 0xe0, 0x2c
        steps = max(1, min(fill_w, 60))
        step_w = fill_w / steps

        for i in range(steps):
            ratio = i / max(1, steps - 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            x0 = int(i * step_w)
            x1 = int((i + 1) * step_w) + 1
            self.create_rectangle(x0, 0, min(x1, fill_w), h, fill=color, outline="")


class AnycubicTimelapseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lapse Lab by Little")
        self.root.geometry("537x507")
        self.root.resizable(False, False)

        # Set window icon if available
        icon_file = resource_path("icon.ico")
        if os.path.exists(icon_file):
            try:
                self.root.iconbitmap(icon_file)
            except Exception:
                pass

        self.style = ttk.Style()
        self.style.theme_use("clam")

        bg_color = "#ffffff"
        self.root.configure(bg=bg_color)
        self.style.configure(".", background=bg_color, font=("Segoe UI", 9))
        self.style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"), foreground="#111111", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=("Segoe UI", 9), foreground="#111111")
        self.style.configure("Unit.TLabel", foreground="#777777", background=bg_color, font=("Segoe UI", 9))
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#0066cc")
        self.style.map("Action.TButton", background=[("active", "#004c99"), ("disabled", "#cccccc")])

        self.filepath_var = tk.StringVar()
        self.frequency_var = tk.StringVar(value="Every Layer")
        self.anti_shake_var = tk.IntVar(value=250)
        self.button_press_var = tk.IntVar(value=150)
        self.pause_after_var = tk.IntVar(value=600)
        self.shutter_x_var = tk.DoubleVar(value=228.0)
        self.approach_dist_var = tk.DoubleVar(value=2.0)
        self.park_y_var = tk.DoubleVar(value=190.0)
        self.retract_var = tk.BooleanVar(value=True)
        self.zhop_var = tk.DoubleVar(value=2.0)
        self.ensure_final_var = tk.BooleanVar(value=True)
        self.is_processing = False

        self.build_ui()

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- LEFT SIDEBAR (splash.png - borderless) ---
        sidebar_w, sidebar_h = 225, 491
        left_frame = tk.Frame(main_frame, width=sidebar_w, height=sidebar_h,
                              bg="#ffffff", highlightthickness=0, bd=0)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        splash_file = resource_path("splash.png")
        if os.path.exists(splash_file):
            try:
                if HAS_PIL:
                    img = Image.open(splash_file)
                    img = img.resize((sidebar_w, sidebar_h), Image.Resampling.LANCZOS)
                    self.splash_img = ImageTk.PhotoImage(img)
                else:
                    self.splash_img = tk.PhotoImage(file=splash_file)
                tk.Label(left_frame, image=self.splash_img, bg="#ffffff", bd=0, highlightthickness=0).pack(fill=tk.BOTH, expand=True)
            except Exception:
                tk.Label(left_frame, text="Lapse Lab\nby Little", font=("Segoe UI", 14, "bold"),
                         fg="#3897f0", bg="#ffffff").pack(expand=True)
        else:
            tk.Label(left_frame, text="Lapse Lab\nby Little", font=("Segoe UI", 14, "bold"),
                     fg="#3897f0", bg="#ffffff").pack(expand=True)

        # --- RIGHT CONTROLS PANEL ---
        right_frame = ttk.Frame(main_frame, padding=(8, 4, 6, 2))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, text="Add your Sliced GCode", style="Title.TLabel").pack(anchor="w", pady=(2, 6))

        file_frame = ttk.Frame(right_frame)
        file_frame.pack(fill=tk.X, pady=(0, 8))
        file_entry = ttk.Entry(file_frame, textvariable=self.filepath_var, font=("Segoe UI", 9))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=2)
        ttk.Button(file_frame, text="Browse...", width=9, command=self.browse_file).pack(side=tk.RIGHT)

        ttk.Separator(right_frame, orient="horizontal").pack(fill=tk.X, pady=(2, 6))

        grid_frame = ttk.Frame(right_frame)
        grid_frame.pack(fill=tk.X)
        grid_frame.columnconfigure(0, weight=1)

        r = 0
        ttk.Label(grid_frame, text="How often (layers)").grid(row=r, column=0, sticky="w", pady=3)
        freq_combo = ttk.Combobox(grid_frame, textvariable=self.frequency_var, width=10, state="readonly")
        freq_combo["values"] = ("Every Layer", "Every 2nd", "Every 3rd", "Every 5th", "Every 10th", "Every 25th")
        freq_combo.grid(row=r, column=1, columnspan=2, sticky="e", padx=(2, 2), pady=3)

        r += 1
        self.add_field(grid_frame, r, "Pause before click (anti-shake)", self.anti_shake_var, "ms")
        r += 1
        self.add_field(grid_frame, r, "Button Pressing Time", self.button_press_var, "ms")
        r += 1
        self.add_field(grid_frame, r, "Pause after image", self.pause_after_var, "ms")
        r += 1
        self.add_field(grid_frame, r, "Shutter Click X Location", self.shutter_x_var, "mm")
        r += 1
        self.add_field(grid_frame, r, "Approach / Pre-click Distance", self.approach_dist_var, "mm")
        r += 1
        self.add_field(grid_frame, r, "Park Print Head Y (Focus)", self.park_y_var, "mm")
        r += 1
        self.add_toggle(grid_frame, r, "Retract when required", self.retract_var)
        r += 1
        self.add_field(grid_frame, r, "Z-Hop Height When Parking", self.zhop_var, "mm")
        r += 1
        self.add_toggle(grid_frame, r, "Ensure Final Image", self.ensure_final_var)

        # Bottom Progress Bar, Status & Action Button
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(2, 0))

        self.progress_bar = SmoothProgressBar(bottom_frame, height=13)
        self.progress_bar.pack(fill=tk.X, pady=(0, 6))

        self.status_var = tk.StringVar(value="Select a G-code file to process.")
        ttk.Label(bottom_frame, textvariable=self.status_var, foreground="#555555",
                  font=("Segoe UI", 8), wraplength=275).pack(anchor="w", pady=(0, 6))

        self.action_btn = ttk.Button(bottom_frame, text="Patch G-code & Save File As...",
                                     style="Action.TButton", command=self.start_processing)
        self.action_btn.pack(fill=tk.X, ipady=5)

    def add_field(self, parent, row, label_text, var, unit):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
        ent = ttk.Entry(parent, textvariable=var, width=6, justify="left")
        ent.grid(row=row, column=1, sticky="w", padx=(2, 4), pady=2)
        ttk.Label(parent, text=unit, style="Unit.TLabel", width=4).grid(row=row, column=2, sticky="w", pady=2)

    def add_toggle(self, parent, row, label_text, var):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=3)
        toggle = ToggleSwitch(parent, variable=var, width=36, height=18)
        toggle.grid(row=row, column=1, sticky="w", padx=(2, 4), pady=3)

    def browse_file(self):
        f = filedialog.askopenfilename(title="Select G-code File", filetypes=[("G-code Files", "*.gcode"), ("All Files", "*.*")])
        if f:
            self.filepath_var.set(f)
            self.progress_bar.set_progress(0.0)
            self.status_var.set(f"Selected: {os.path.basename(f)}")

    def parse_time_from_string(self, text):
        d = re.search(r"(\d+)\s*d", text, re.I)
        h = re.search(r"(\d+)\s*h", text, re.I)
        m = re.search(r"(\d+)\s*m", text, re.I)
        s = re.search(r"(\d+)\s*s", text, re.I)
        days = int(d.group(1)) if d else 0
        hours = int(h.group(1)) if h else 0
        mins = int(m.group(1)) if m else 0
        secs = int(s.group(1)) if s else 0
        return days * 86400 + hours * 3600 + mins * 60 + secs

    def start_processing(self):
        if self.is_processing:
            return

        src_path = self.filepath_var.get().strip()
        if not src_path or not os.path.isfile(src_path):
            messagebox.showerror("Error", "Please select a valid .gcode file first.")
            return

        self.is_processing = True
        self.action_btn.configure(state="disabled")
        self.progress_bar.set_progress(0.0)
        self.status_var.set("Patching G-code layers...")

        # Animate progress bar over ~1.0 second (25 steps x 40ms = 1000ms)
        self._animate_progress(step=0, total_steps=25)

    def _animate_progress(self, step, total_steps):
        if step <= total_steps:
            self.progress_bar.set_progress(step / total_steps)
            self.root.after(40, lambda: self._animate_progress(step + 1, total_steps))
        else:
            self.process_gcode()

    def process_gcode(self):
        src_path = self.filepath_var.get().strip()

        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            content = re.sub(
                r"; --- (?:Upgraded|Native) Timelapse Macro Begin ---.*?; --- (?:Upgraded|Native) Timelapse Macro End ---\r?\n?",
                "",
                content,
                flags=re.DOTALL
            )

            orig_seconds = 0
            est_match = re.search(r";\s*estimated printing time.*?=\s*(.*)", content, re.IGNORECASE)
            if est_match:
                orig_seconds = self.parse_time_from_string(est_match.group(1))

            if orig_seconds == 0:
                print_time_match = re.search(r";\s*print_time\s*=\s*(.*)", content, re.IGNORECASE)
                if print_time_match:
                    orig_seconds = self.parse_time_from_string(print_time_match.group(1))

            if orig_seconds == 0:
                time_match = re.search(r";TIME:(\d+)", content)
                if time_match:
                    orig_seconds = int(time_match.group(1))

            if "; AFTER_LAYER_CHANGE" in content:
                raw_layers = re.split(r"(?=;\s*AFTER_LAYER_CHANGE)", content)
            elif ";LAYER_CHANGE" in content:
                raw_layers = re.split(r"(?=;LAYER_CHANGE)", content)
            elif ";LAYER:" in content:
                raw_layers = re.split(r"(?=;LAYER:\s*\d+)", content)
            else:
                self.progress_bar.set_progress(0.0)
                messagebox.showerror("Error", "Could not locate layer markers in this G-code file.")
                return

            shutter_x = self.shutter_x_var.get()
            approach_dist = self.approach_dist_var.get()
            pre_park_x = round(shutter_x - approach_dist, 2)
            park_y = self.park_y_var.get()

            anti_shake = self.anti_shake_var.get()
            btn_press = self.button_press_var.get()
            pause_after = self.pause_after_var.get()
            zhop = self.zhop_var.get()
            retract_enabled = self.retract_var.get()
            ensure_final = self.ensure_final_var.get()

            retract_dist = 0.8
            travel_feed = 6000
            z_feed = 3000

            freq_map = {
                "Every Layer": 1, "Every 2nd": 2, "Every 3rd": 3,
                "Every 5th": 5, "Every 10th": 10, "Every 25th": 25
            }
            step_freq = freq_map.get(self.frequency_var.get(), 1)

            total_added_seconds = 0.0
            new_layers = []

            for idx, layer_chunk in enumerate(raw_layers):
                if idx >= 2 and (idx - 1) % step_freq == 0:
                    dist = 150.0
                    t_travel = (dist / (travel_feed / 60.0)) * 2.0
                    t_zhop = (zhop / (z_feed / 60.0)) * 2.0 if zhop > 0 else 0.0
                    t_switch = (approach_dist / 50.0) * 2.0
                    t_pauses = (anti_shake + btn_press + pause_after) / 1000.0
                    total_added_seconds += (t_travel + t_zhop + t_switch + t_pauses + 0.5)

                    macro = [
                        "; --- Upgraded Timelapse Macro Begin ---",
                        "M400 ; Wait for moves to finish",
                        f"G1 E-{retract_dist:.2f} F3000 ; Retract" if retract_enabled else "",
                        "G91 ; Relative positioning",
                        f"G0 Z{zhop:.2f} F{z_feed} ; Lift Z-hop" if zhop > 0 else "",
                        "G90 ; Absolute positioning",
                        f"G0 X{pre_park_x:.2f} Y{park_y:.2f} F{travel_feed} ; Park at pre-click",
                        "M400 ; Wait for stop",
                        f"G4 P{anti_shake} ; Settle anti-shake" if anti_shake > 0 else "",
                        f"G1 X{shutter_x:.2f} F3000 ; Press trigger",
                        f"G4 P{btn_press} ; Hold trigger",
                        f"G1 X{pre_park_x:.2f} F3000 ; Release trigger",
                        f"G4 P{pause_after} ; Wait for camera" if pause_after > 0 else "",
                        "G91 ; Relative positioning",
                        f"G0 Z-{zhop:.2f} F{z_feed} ; Restore Z-hop" if zhop > 0 else "",
                        "G90 ; Absolute positioning",
                        f"G1 E{retract_dist:.2f} F2400 ; Prime nozzle" if retract_enabled else "",
                        "M400 ; Finish",
                        "; --- Upgraded Timelapse Macro End ---"
                    ]
                    clean_macro = "\n".join([cmd for cmd in macro if cmd])
                    new_layers.append(clean_macro + "\n" + layer_chunk)
                else:
                    new_layers.append(layer_chunk)

            if ensure_final:
                final_block = (
                    "\n; --- Final Frame Timelapse ---\n"
                    "M400\n"
                    "G91\n"
                    f"G0 Z{zhop:.2f} F{z_feed}\n"
                    "G90\n"
                    f"G0 X{pre_park_x:.2f} Y{park_y:.2f} F{travel_feed}\n"
                    "M400\n"
                    f"G1 X{shutter_x:.2f} F3000\n"
                    f"G4 P{btn_press}\n"
                    f"G1 X{pre_park_x:.2f} F3000\n"
                    f"G4 P{pause_after}\n"
                )
                new_layers[-1] = new_layers[-1] + final_block

            patched_content = "".join(new_layers)
            new_total_seconds = int(orig_seconds + total_added_seconds)

            if ";TIME:" in patched_content:
                patched_content = re.sub(r";TIME:\d+", f";TIME:{new_total_seconds}", patched_content, count=1)
            else:
                patched_content = f";TIME:{new_total_seconds}\n" + patched_content

            new_h = new_total_seconds // 3600
            new_m = (new_total_seconds % 3600) // 60
            new_s = new_total_seconds % 60
            time_suffix = f"_{new_h}h{new_m}m{new_s}s" if new_h > 0 else f"_{new_m}m{new_s}s"

            dir_name, full_file_name = os.path.split(src_path)
            base_name, ext = os.path.splitext(full_file_name)
            clean_base = re.sub(r"_(\d+d)?(\d+h)?(\d+m)?(\d+s)?$", "", base_name, flags=re.IGNORECASE)
            suggested_name = f"{clean_base}_timelapse{time_suffix}{ext}"

            dest_path = filedialog.asksaveasfilename(
                title="Save Patched G-code File As",
                initialdir=dir_name,
                initialfile=suggested_name,
                defaultextension=".gcode",
                filetypes=[("G-code Files", "*.gcode"), ("All Files", "*.*")]
            )

            if not dest_path:
                self.progress_bar.set_progress(0.0)
                self.status_var.set("Save cancelled by user.")
                return

            with open(dest_path, "w", encoding="utf-8") as out_f:
                out_f.write(patched_content)

            saved_filename = os.path.basename(dest_path)
            self.status_var.set(f"Done! Saved: {saved_filename}")
            messagebox.showinfo(
                "Complete",
                f"Timelapse G-code generated successfully!\n\n"
                f"File Saved: {saved_filename}\n"
                f"Total Duration: {time_suffix.strip('_')} ({new_total_seconds} seconds)"
            )

        except Exception as e:
            self.progress_bar.set_progress(0.0)
            messagebox.showerror("Processing Error", f"An error occurred while parsing:\n{str(e)}")

        finally:
            self.is_processing = False
            self.action_btn.configure(state="normal")


def main():
    root = tk.Tk()
    app = AnycubicTimelapseApp(root)
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app.filepath_var.set(sys.argv[1])
        app.status_var.set(f"Selected: {os.path.basename(sys.argv[1])}")

    root.mainloop()


if __name__ == "__main__":
    main()