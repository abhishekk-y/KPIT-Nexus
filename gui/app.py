import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import time
import numpy as np
from core.simulation import SimulationRunner
import webbrowser
import sys
import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- Premium Cyberpunk/Modern Theme ---
COLOR_BG = "#0b0b0b"        # Deepest Black
COLOR_PANEL = "#181818"     # Dark Grey
COLOR_TEXT = "#e0e0e0"      # Off-White
COLOR_ACCENT = "#00d2ff"    # Neon Cyan
COLOR_ACCENT_2 = "#ff007a"  # Neon Pink
COLOR_SUCCESS = "#00ff9d"   # Neon Green
COLOR_DANGER = "#ff3838"    # Bright Red
COLOR_GRID = "#2a2a2a"      # Subtle Grid
COLOR_WARNING = "#ffb302"   # Amber

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.title("SYSTEM CONFIGURATION")
        self.geometry("500x600")
        self.configure(fg_color=COLOR_BG)
        self.attributes("-topmost", True)
        
        # Title
        ctk.CTkLabel(self, text="SETTINGS & CONFIGURATION", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_ACCENT).pack(pady=20)
        
        # 1. Appearance
        frame_app = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        frame_app.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_app, text="VISUAL INTERFACE", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.theme_switch = ctk.CTkSwitch(frame_app, text="Cyberpunk Glow Effects", onvalue=True, offvalue=False, progress_color=COLOR_ACCENT)
        self.theme_switch.pack(anchor="w", padx=15, pady=10)
        self.theme_switch.select()
        
        # 2. Simulation
        frame_sim = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        frame_sim.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_sim, text="SIMULATION KERNEL", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(frame_sim, text="Time Step (dt):", text_color="#aaaaaa").pack(anchor="w", padx=15, pady=(5, 0))
        self.dt_slider = ctk.CTkSlider(frame_sim, from_=0.01, to=0.2, number_of_steps=19)
        self.dt_slider.set(0.05)
        self.dt_slider.pack(fill="x", padx=15, pady=5)
        
        # 3. Logging
        frame_log = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        frame_log.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_log, text="SYSTEM LOGGING", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.log_switch = ctk.CTkSwitch(frame_log, text="Verbose Telemetry Logging", onvalue=True, offvalue=False, progress_color=COLOR_SUCCESS)
        self.log_switch.pack(anchor="w", padx=15, pady=10)
        self.log_switch.select()
        
        # Save Button
        ctk.CTkButton(self, text="APPLY CONFIGURATION", fg_color=COLOR_ACCENT, text_color="black", font=ctk.CTkFont(weight="bold"),
                     command=self.apply_settings).pack(pady=30)
                     
    def apply_settings(self):
        # Apply dt
        new_dt = self.dt_slider.get()
        self.app.runner.dt = new_dt
        
        # Apply Logging
        self.app.verbose_logging = self.log_switch.get()
        
        print(f"[CONFIG] Time step updated to {new_dt}s")
        print(f"[CONFIG] Verbose logging set to {self.app.verbose_logging}")
        self.destroy()

class TerminalWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("NEXUS SYSTEM CONSOLE")
        self.geometry("600x400")
        self.configure(fg_color="#000000")
        self.attributes("-alpha", 0.95)
        
        # Header
        self.header = ctk.CTkFrame(self, height=30, fg_color="#111111", corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text="root@nexus-core:~#", font=ctk.CTkFont(family="Courier New", size=12, weight="bold"), text_color=COLOR_SUCCESS).pack(side="left", padx=10)
        
        # Terminal Output
        self.text_area = ctk.CTkTextbox(self, fg_color="#000000", text_color=COLOR_SUCCESS, 
                                      font=ctk.CTkFont(family="Courier New", size=12), wrap="char")
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_area.configure(state="disabled")
        
        # Input Line
        self.input_frame = ctk.CTkFrame(self, height=30, fg_color="#000000")
        self.input_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(self.input_frame, text=">", font=ctk.CTkFont(family="Courier New", size=12, weight="bold"), text_color=COLOR_SUCCESS).pack(side="left")
        self.input_entry = ctk.CTkEntry(self.input_frame, fg_color="#000000", border_width=0, text_color="white", 
                                      font=ctk.CTkFont(family="Courier New", size=12))
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>", self.process_command)
        
        self.write("NEXUS KERNEL v3.2 INITIALIZED...")
        self.write("Connected to local simulation instance.")
        self.write("Type 'help' for available commands.")

    def write(self, text):
        try:
            if not self.winfo_exists():
                return
            self.text_area.configure(state="normal")
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
            self.text_area.insert("end", timestamp + str(text) + "\n")
            self.text_area.see("end")
            self.text_area.configure(state="disabled")
        except Exception:
            pass

    def process_command(self, event):
        cmd = self.input_entry.get()
        self.input_entry.delete(0, "end")
        self.write(f"> {cmd}")
        
        if cmd == "help":
            self.write("AVAILABLE COMMANDS:\n  status - Show system status\n  clear - Clear terminal\n  exit - Close console")
        elif cmd == "clear":
            self.text_area.configure(state="normal")
            self.text_area.delete("1.0", "end")
            self.text_area.configure(state="disabled")
        elif cmd == "status":
            self.write("SYSTEM NOMINAL. CPU: 12% | MEM: 450MB | UPTIME: 00:42:15")
        elif cmd == "exit":
            self.destroy()
        else:
            self.write(f"Command not found: {cmd}")

class StdoutRedirector:
    def __init__(self, terminal):
        self.terminal = terminal
    def write(self, text):
        if text.strip():
            self.terminal.write(text.strip())
    def flush(self):
        pass

class MetricCard(ctk.CTkFrame):
    """A premium card to display a metric name, value, and trend"""
    def __init__(self, master, title, value_format="{:.2f}", trend_value="+0.0%", trend_color=COLOR_SUCCESS, **kwargs):
        super().__init__(master, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color="#333333", **kwargs)
        self.value_format = value_format
        
        # Prevent the frame from resizing based on its children
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Set a fixed height
        self.configure(height=110)
        
        # Title
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=ctk.CTkFont(family="Roboto Medium", size=11), text_color="#888888")
        self.title_label.pack(pady=(12, 0), padx=15, anchor="w")
        
        # Value - using monospace font for consistent width
        self.value_label = ctk.CTkLabel(self, text="0.00", font=ctk.CTkFont(family="Courier New", size=26, weight="bold"), text_color=COLOR_TEXT)
        self.value_label.pack(pady=(2, 5), padx=15, anchor="w")
        
        # Trend Indicator (Visual only for now)
        self.trend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.trend_frame.pack(pady=(0, 12), padx=15, anchor="w")
        
        self.trend_label = ctk.CTkLabel(self.trend_frame, text=trend_value, font=ctk.CTkFont(size=11, weight="bold"), text_color=trend_color)
        self.trend_label.pack(side="left")
        
        self.trend_desc = ctk.CTkLabel(self.trend_frame, text=" vs target", font=ctk.CTkFont(size=11), text_color="#666666")
        self.trend_desc.pack(side="left", padx=5)
        
    def update_value(self, value):
        self.value_label.configure(text=self.value_format.format(value))

class GraphCard(ctk.CTkFrame):
    """A container for a Matplotlib figure with a custom header and Info button"""
    def __init__(self, master, title, figure, info_text, **kwargs):
        super().__init__(master, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color="#333333", **kwargs)
        
        # Header
        self.header = ctk.CTkFrame(self, height=35, fg_color="transparent")
        self.header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.title_lbl = ctk.CTkLabel(self.header, text=title.upper(), font=ctk.CTkFont(family="Roboto", size=12, weight="bold"), text_color="#aaaaaa")
        self.title_lbl.pack(side="left")
        
        self.info_btn = ctk.CTkButton(self.header, text="i", width=24, height=24, corner_radius=12, 
                                    font=ctk.CTkFont(family="Times", size=14, weight="bold", slant="italic"),
                                    fg_color="#333333", hover_color=COLOR_ACCENT, text_color="white",
                                    command=lambda: self.show_info(title, info_text))
        self.info_btn.pack(side="right")
        
        # Canvas Container
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.canvas = FigureCanvasTkAgg(figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_info(self, title, text):
        # Create a Toplevel overlay
        top = ctk.CTkToplevel(self)
        top.title("INFO: " + title)
        top.geometry("400x300")
        top.resizable(False, False)
        top.attributes("-topmost", True)
        
        # Center it (rough approximation)
        x = self.winfo_rootx() + 50
        y = self.winfo_rooty() + 50
        top.geometry(f"+{x}+{y}")
        
        # Content
        bg = ctk.CTkFrame(top, fg_color=COLOR_BG)
        bg.pack(fill="both", expand=True)
        
        ctk.CTkLabel(bg, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_ACCENT).pack(pady=(20, 10))
        
        textbox = ctk.CTkTextbox(bg, fg_color="transparent", text_color="#cccccc", font=ctk.CTkFont(size=14), wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=10)
        textbox.insert("0.0", text)
        textbox.configure(state="disabled")
        
        ctk.CTkButton(bg, text="CLOSE", command=top.destroy, fg_color="#333333", hover_color=COLOR_DANGER, width=100).pack(pady=20)

class MainDashboardFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#0b0b0b")
        self.app = master
        self.runner = self.app.runner
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row 0 is Header

        self.create_sidebar()
        self.create_header()
        self.create_main_view()
        
        # Setup Animation
        self.setup_plots()
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=50, blit=False, cache_frame_data=False)

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_PANEL)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Logo Area
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        
        ctk.CTkLabel(self.logo_frame, text="NEXUS", font=ctk.CTkFont(family="Roboto", size=28, weight="bold"), text_color=COLOR_ACCENT).pack(anchor="w")
        ctk.CTkLabel(self.logo_frame, text="CONTROL SYSTEMS", font=ctk.CTkFont(family="Roboto", size=10, weight="bold"), text_color="#666666").pack(anchor="w")

        # Navigation Items (Visual Only)
        nav_items = ["DASHBOARD", "ANALYTICS", "SYSTEM LOGS", "SETTINGS"]
        for i, item in enumerate(nav_items):
            cmd = None
            if item == "SYSTEM LOGS": cmd = self.open_terminal
            elif item == "SETTINGS": cmd = self.open_settings
            
            btn = ctk.CTkButton(self.sidebar_frame, text=item, height=40, anchor="w", 
                              fg_color="transparent", text_color="#aaaaaa", hover_color="#222222",
                              font=ctk.CTkFont(size=12, weight="bold"), command=cmd)
            btn.grid(row=i+1, column=0, padx=10, pady=2, sticky="ew")
            
        # Separator
        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#333333").grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # Control Group
        self.controls_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.controls_frame.grid(row=6, column=0, padx=15, pady=0, sticky="ew")
        
        self.create_slider(self.controls_frame, "Kp (Proportional)", 0, 10, 2.0, 0)
        self.create_slider(self.controls_frame, "Ki (Integral)", 0, 5, 0.5, 1)
        self.create_slider(self.controls_frame, "Kd (Derivative)", 0, 5, 0.1, 2)
        self.create_slider(self.controls_frame, "Setpoint Target", -10, 10, 5.0, 3, command=self.update_target)
        self.create_slider(self.controls_frame, "Disturbance", 0, 5, 0.0, 4, command=self.update_noise)

        # Mode Selection
        self.mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["HYBRID", "RL_TRAIN", "RL_INFERENCE"], 
                                         command=self.change_mode, variable=ctk.StringVar(value="HYBRID"),
                                         fg_color=COLOR_ACCENT, button_color=COLOR_ACCENT, button_hover_color="#00b8e6",
                                         text_color="#000000", font=ctk.CTkFont(weight="bold"))
        self.mode_menu.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        self.mode_var = self.mode_menu._variable

        # Action Buttons
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="INITIATE SIMULATION", command=self.toggle_sim, 
                                        height=45, font=ctk.CTkFont(size=13, weight="bold"), 
                                        fg_color=COLOR_SUCCESS, hover_color="#00e68e", text_color="#000000")
        self.start_button.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.reset_button = ctk.CTkButton(self.sidebar_frame, text="RESET SYSTEM", command=self.reset_sim, 
                                        height=45, font=ctk.CTkFont(size=13, weight="bold"), 
                                        fg_color="#222222", hover_color="#333333", text_color="#aaaaaa")
        self.reset_button.grid(row=9, column=0, padx=20, pady=0, sticky="ew")

    def create_slider(self, parent, text, from_, to, default, row, command=None):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color="#888888").grid(row=row*2, column=0, sticky="w", pady=(10, 0))
        slider = ctk.CTkSlider(parent, from_=from_, to=to, number_of_steps=100, command=command if command else self.update_params)
        slider.set(default)
        slider.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 5))
        
        if "Kp" in text: self.kp_slider = slider
        elif "Ki" in text: self.ki_slider = slider
        elif "Kd" in text: self.kd_slider = slider
        elif "Target" in text: self.target_slider = slider
        elif "Disturbance" in text: self.noise_slider = slider

    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self, self.app)
        else:
            self.settings_window.focus()

    def open_terminal(self):
        if not hasattr(self, 'terminal_window') or not self.terminal_window.winfo_exists():
            self.terminal_window = TerminalWindow(self)
            # Redirect stdout
            sys.stdout = StdoutRedirector(self.terminal_window)
        else:
            self.terminal_window.focus()

    def create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLOR_BG)
        self.header_frame.grid(row=0, column=1, sticky="ew", padx=30, pady=(20, 0))
        
        # Title / Breadcrumb
        title = ctk.CTkLabel(self.header_frame, text="MISSION CONTROL / MAIN DASHBOARD", font=ctk.CTkFont(family="Roboto", size=14, weight="bold"), text_color="#666666")
        title.pack(side="left")
        
        # Right Side Items
        user_badge = ctk.CTkButton(self.header_frame, text="ADMINISTRATOR", width=120, height=32, fg_color="#222222", hover_color="#333333", corner_radius=20)
        user_badge.pack(side="right")
        
        notif_btn = ctk.CTkButton(self.header_frame, text="🔔", width=40, height=32, fg_color="transparent", hover_color="#222222", text_color="#aaaaaa")
        notif_btn.pack(side="right", padx=10)

    def create_main_view(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=30, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. Telemetry
        self.telemetry_frame = ctk.CTkFrame(self.main_frame, height=110, fg_color="transparent")
        self.telemetry_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        
        metrics = [
            ("Position", "{:.2f} m", "+0.0%", COLOR_SUCCESS),
            ("Target", "{:.2f} m", "SET", "#888888"),
            ("Error", "{:.4f}", "-12%", COLOR_ACCENT),
            ("Velocity", "{:.2f} m/s", "STABLE", COLOR_ACCENT_2),
            ("Control", "{:.2f} u", "NOMINAL", COLOR_WARNING)
        ]
        self.metric_cards = {}
        
        # Configure grid columns for equal width
        for i in range(len(metrics)):
            self.telemetry_frame.grid_columnconfigure(i, weight=1)

        for i, (m, fmt, trend, col) in enumerate(metrics):
            card = MetricCard(self.telemetry_frame, m, fmt, trend, col)
            card.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
            self.metric_cards[m] = card

        # 2. Tabs
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color=COLOR_PANEL, 
                                     segmented_button_selected_color=COLOR_ACCENT,
                                     segmented_button_selected_hover_color="#00b8e6",
                                     segmented_button_unselected_color="#222222",
                                     segmented_button_unselected_hover_color="#333333",
                                     text_color="#ffffff",
                                     height=40)
        self.tab_view.grid(row=1, column=0, sticky="nsew")
        
        self.tab_main = self.tab_view.add("DASHBOARD")
        self.tab_analysis = self.tab_view.add("ANALYSIS")
        self.tab_components = self.tab_view.add("PID DETAILS")
        self.tab_ai = self.tab_view.add("AI TRAINING")

    def setup_plots(self):
        # Common style
        style = {
            'facecolor': COLOR_PANEL,
            'edgecolor': 'none',
            'linewidth': 0
        }
        
        # --- Tab 1: Main Dashboard ---
        self.fig = Figure(figsize=(6, 4), dpi=100, **style)
        self.ax1 = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.15)
        
        self.line_target, = self.ax1.plot([], [], color=COLOR_DANGER, linestyle='--', label='Target', alpha=0.8, linewidth=2)
        self.line_pos, = self.ax1.plot([], [], color=COLOR_SUCCESS, linestyle='-', linewidth=2.5, label='Output')
        self.line_pred, = self.ax1.plot([], [], color='white', linestyle=':', alpha=0.5, label='MPC Pred') 
        self.ax1.set_ylabel("Position (m)", color=COLOR_TEXT)
        # Remove internal title, use Card title
        
        # Control Plot
        self.fig_ctrl = Figure(figsize=(6, 4), dpi=100, **style)
        self.ax2 = self.fig_ctrl.add_subplot(111)
        self.fig_ctrl.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.15)
        
        self.line_control, = self.ax2.plot([], [], color=COLOR_WARNING, linestyle='-', label='Control (u)')
        self.ax2.set_ylabel("Effort", color=COLOR_TEXT)
        
        self.ax2_twin = self.ax2.twinx()
        self.line_alpha, = self.ax2_twin.plot([], [], color=COLOR_ACCENT, linestyle='-', label='Alpha', linewidth=2)
        self.ax2_twin.set_ylabel("Alpha", color=COLOR_ACCENT)
        
        # Create Cards for Tab 1
        self.card_sys = GraphCard(self.tab_main, "System Response", self.fig, 
                                "Shows the real-time position of the system (Green) vs the Target Setpoint (Red).\n\nThe White Dotted line represents the MPC's predicted future trajectory.")
        self.card_sys.pack(fill="both", expand=True, pady=5)
        
        self.card_ctrl = GraphCard(self.tab_main, "Control Effort & Mixing", self.fig_ctrl,
                                 "Yellow line: The raw control signal sent to the actuators.\n\nCyan line: The 'Alpha' mixing factor.\n1.0 = Pure PID (Fast)\n0.0 = Pure MPC (Optimal)\n\nThe system automatically adjusts Alpha based on error magnitude.")
        self.card_ctrl.pack(fill="both", expand=True, pady=5)
        
        self.canvas = self.card_sys.canvas

        # --- Tab 2: Analysis ---
        self.fig2 = Figure(figsize=(6, 4), dpi=100, **style)
        self.ax_phase = self.fig2.add_subplot(221)
        self.ax_error = self.fig2.add_subplot(222)
        
        # Radar Chart (Spider Plot) for System Health
        self.ax_radar = self.fig2.add_subplot(223, polar=True)
        self.ax_radar.set_facecolor(COLOR_PANEL)
        
        # Radar Data
        categories = ['Stability', 'Response', 'Accuracy', 'Efficiency', 'Robustness']
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        self.radar_values = [0.8, 0.7, 0.9, 0.6, 0.8]
        self.radar_values += self.radar_values[:1]
        
        self.ax_radar.set_xticks(angles[:-1])
        self.ax_radar.set_xticklabels(categories, color="#888888", size=8)
        self.ax_radar.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        self.ax_radar.set_yticklabels([])
        self.ax_radar.spines['polar'].set_color(COLOR_GRID)
        self.ax_radar.grid(color=COLOR_GRID, linestyle='--')
        
        self.line_radar, = self.ax_radar.plot(angles, self.radar_values, color=COLOR_ACCENT, linewidth=2)
        self.fill_radar = self.ax_radar.fill(angles, self.radar_values, color=COLOR_ACCENT, alpha=0.25)
        
        # FFT / Spectrum (Placeholder for now, or simple bar)
        self.ax_fft = self.fig2.add_subplot(224)
        self.ax_fft.set_title("FREQ SPECTRUM", color="#888888", fontsize=8)
        self.bar_fft = self.ax_fft.bar(range(10), np.random.rand(10), color=COLOR_ACCENT_2, alpha=0.6)
        self.ax_fft.axis('off')

        self.fig2.subplots_adjust(wspace=0.3, hspace=0.4, left=0.08, right=0.95, top=0.90, bottom=0.1)
        
        self.line_phase, = self.ax_phase.plot([], [], color=COLOR_ACCENT, linestyle='-', linewidth=1.5)
        self.point_phase, = self.ax_phase.plot([], [], color=COLOR_DANGER, marker='o', markersize=8)
        self.ax_phase.set_title("PHASE PLANE", color="#888888", fontsize=8, weight='bold')
        self.ax_phase.set_xticks([])
        self.ax_phase.set_yticks([])
        
        self.line_error, = self.ax_error.plot([], [], color=COLOR_ACCENT_2, linestyle='-')
        self.ax_error.set_title("ERROR HISTORY", color="#888888", fontsize=8, weight='bold')
        self.ax_error.set_xticks([])
        
        self.card_analysis = GraphCard(self.tab_analysis, "Advanced System Analysis", self.fig2,
                                     "Top Left: Phase Plane (Stability)\nTop Right: Error History\nBottom Left: System Health Radar (Multi-metric evaluation)\nBottom Right: Frequency Spectrum (Vibration analysis)")
        self.card_analysis.pack(fill="both", expand=True)
        
        self.canvas2 = self.card_analysis.canvas

        # --- Tab 3: PID ---
        self.fig3 = Figure(figsize=(6, 4), dpi=100, **style)
        self.ax_pid = self.fig3.add_subplot(111)
        self.fig3.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.15)
        
        self.line_p, = self.ax_pid.plot([], [], label='P', color='#ff5252', linewidth=2)
        self.line_i, = self.ax_pid.plot([], [], label='I', color='#448aff', linewidth=2)
        self.line_d, = self.ax_pid.plot([], [], label='D', color='#ffd740', linewidth=2)
        self.ax_pid.legend()
        
        self.card_pid = GraphCard(self.tab_components, "PID Components", self.fig3,
                                "Breakdown of the PID controller terms:\n\nP (Red): Proportional to current error.\nI (Blue): Proportional to accumulated error (past).\nD (Yellow): Proportional to rate of change (future prediction).")
        self.card_pid.pack(fill="both", expand=True)
        
        self.canvas3 = self.card_pid.canvas
        
        # --- Tab 4: AI & 3D Landscape ---
        self.fig4 = Figure(figsize=(6, 4), dpi=100, **style)
        self.ax_loss = self.fig4.add_subplot(121)
        self.ax_3d = self.fig4.add_subplot(122, projection='3d')
        self.fig4.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15, wspace=0.3)
        
        self.line_loss, = self.ax_loss.plot([], [], color=COLOR_DANGER, linestyle='-')
        self.ax_loss.set_ylabel("Loss", color=COLOR_TEXT)
        self.ax_loss.set_title("TRAINING LOSS", color="#888888", fontsize=8, weight='bold')
        
        # 3D Surface (Static Mesh, Dynamic View)
        X = np.arange(-5, 5, 0.25)
        Y = np.arange(-5, 5, 0.25)
        X, Y = np.meshgrid(X, Y)
        R = np.sqrt(X**2 + Y**2)
        Z = np.sin(R)
        
        self.surf = self.ax_3d.plot_surface(X, Y, Z, cmap='viridis', linewidth=0, antialiased=False, alpha=0.8)
        self.ax_3d.set_axis_off() # Clean look
        self.ax_3d.set_facecolor(COLOR_PANEL)
        
        self.card_ai = GraphCard(self.tab_ai, "AI Training & Cost Landscape", self.fig4,
                               "Left: DDPG Agent Training Loss.\nRight: 3D Visualization of the Cost Function Landscape. The agent tries to find the global minimum (lowest point) on this surface.")
        self.card_ai.pack(fill="both", expand=True)
        self.card_ai.configure(border_color=COLOR_ACCENT_2, border_width=2) # Neon Pink Border
        
        self.canvas4 = self.card_ai.canvas

        # Initial Styling
        self.apply_plot_styles([self.ax1, self.ax2, self.ax_phase, self.ax_error, self.ax_pid, self.ax_loss])
        self.ax2_twin.set_ylim(0, 1.1)
        self.ax2_twin.spines['right'].set_color(COLOR_ACCENT)
        self.ax2_twin.tick_params(axis='y', colors=COLOR_ACCENT)
        
        # Modernize Cards
        self.card_sys.configure(border_color=COLOR_ACCENT, border_width=1)
        self.card_ctrl.configure(border_color=COLOR_WARNING, border_width=1)
        self.card_analysis.configure(border_color=COLOR_SUCCESS, border_width=1)
        self.card_pid.configure(border_color="#ffd740", border_width=1)

    def apply_plot_styles(self, axes):
        for ax in axes:
            ax.set_facecolor(COLOR_PANEL)
            ax.tick_params(colors=COLOR_TEXT, labelsize=10)
            for spine in ax.spines.values():
                spine.set_color(COLOR_GRID)
            ax.grid(True, color=COLOR_GRID, linestyle='--', alpha=0.3)
            if ax.get_legend():
                ax.legend(facecolor=COLOR_PANEL, labelcolor=COLOR_TEXT, framealpha=0.9, edgecolor=COLOR_GRID, loc='upper right')

    def update_params(self, _=None):
        self.runner.set_pid_gains(self.kp_slider.get(), self.ki_slider.get(), self.kd_slider.get())
        
    def update_target(self, _=None):
        self.runner.set_target(self.target_slider.get())
        
    def update_noise(self, _=None):
        self.runner.set_noise(self.noise_slider.get())
        
    def change_mode(self, mode):
        self.runner.set_mode(mode)
        text_map = {"RL_TRAIN": "START TRAINING", "RL_INFERENCE": "START AI CONTROL", "HYBRID": "START SIMULATION"}
        if not self.runner.running:
            self.start_button.configure(text=text_map.get(mode, "START"))

    def toggle_sim(self):
        if self.runner.running:
            self.runner.stop()
        else:
            self.runner.start()
            
        btn_text = "STOP" if self.runner.running else "START"
        mode_suffix = {"RL_TRAIN": " TRAINING", "RL_INFERENCE": " AI CONTROL", "HYBRID": " SIMULATION"}
        self.start_button.configure(
            text=btn_text + mode_suffix.get(self.mode_var.get(), ""),
            fg_color=COLOR_DANGER if self.runner.running else COLOR_SUCCESS,
            hover_color="#c0392b" if self.runner.running else "#27ae60"
        )

    def reset_sim(self):
        self.runner.reset()
        # Reset lines
        for line in [self.line_target, self.line_pos, self.line_pred, self.line_control, self.line_alpha, 
                     self.line_phase, self.line_error, self.line_p, self.line_i, self.line_d, self.line_loss]:
            line.set_data([], [])
        self.point_phase.set_data([], [])
        
        self.canvas.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        self.canvas4.draw()

    def update_plot(self, frame):
        if not self.runner.running:
            return

        # Fetch latest data snapshot from runner
        data = self.runner.get_history()
        metrics = self.runner.get_latest_metrics()
        radar_metrics = self.runner.get_radar_metrics()
        fft_data = self.runner.get_fft_data()
        
        # Unpack data
        times = data["time"]
        targets = data["target"]
        positions = data["position"]
        velocities = data["velocity"]
        controls = data["control"]
        alphas = data["alpha"]
        errors = data["error"]
        p_terms = data["p_term"]
        i_terms = data["i_term"]
        d_terms = data["d_term"]
        losses = data["loss"]
        
        if not times:
            return

        # Define current_time globally for all tabs
        current_time = times[-1]
        
        # --- VERBOSE LOGGING (System Logs) ---
        # Print key metrics to stdout (redirected to terminal)
        # We limit frequency to avoid spamming (every 10th frame approx)
        if self.app.verbose_logging and int(current_time * 10) % 10 == 0:
            print(f"[SIM] T={current_time:.2f} | POS={positions[-1]:.2f} | TGT={targets[-1]:.2f} | ERR={errors[-1]:.4f}")
            print(f"      PID: P={p_terms[-1]:.2f} I={i_terms[-1]:.2f} D={d_terms[-1]:.2f} | U={controls[-1]:.2f}")

        # Update Cards
        for k, v in metrics.items():
            if k in self.metric_cards:
                self.metric_cards[k].update_value(v)

        # Selective Rendering
        active_tab = self.tab_view.get()
        
        if active_tab == "DASHBOARD":
            self.line_target.set_data(times, targets)
            self.line_pos.set_data(times, positions)
            self.line_control.set_data(times, controls)
            self.line_alpha.set_data(times, alphas)
            
            # MPC Prediction (Ghost Line)
            pos = positions[-1]
            vel = velocities[-1]
            u = controls[-1]
            
            pred_t = np.linspace(current_time, current_time + 1.0, 10)
            pred_pos = [pos]
            v = vel
            p = pos
            for _ in range(9):
                p += v * 0.1
                v += (u - 0.5*v) * 0.1
                pred_pos.append(p)
            self.line_pred.set_data(pred_t, pred_pos)

            self.ax1.set_xlim(max(0, current_time - 10), current_time + 1)
            self.ax1.set_ylim(min(min(positions), min(targets)) - 1, max(max(positions), max(targets)) + 1)
            self.ax2.set_xlim(max(0, current_time - 10), current_time + 1)
            self.ax2.set_ylim(-11, 11)
            
            self.canvas.draw_idle()
            self.card_ctrl.canvas.draw_idle() # Explicitly draw the second canvas

        elif active_tab == "ANALYSIS":
            self.line_phase.set_data(positions, velocities)
            self.point_phase.set_data([positions[-1]], [velocities[-1]])
            self.line_error.set_data(times, errors)
            
            # Update Radar Chart
            # Update Radar Chart
            categories = ['Stability', 'Response', 'Accuracy', 'Efficiency', 'Robustness']
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            radar_metrics_closed = radar_metrics + radar_metrics[:1]
            
            self.line_radar.set_data(angles, radar_metrics_closed)
            
            # Update Radar Fill (Vertices)
            # The fill is a Polygon. We can update its vertices (xy).
            # xy is a (N, 2) array of (theta, radius) converted to cartesian? 
            # Matplotlib polar fill uses cartesian coords internally for the Polygon?
            # Actually, for polar axes, set_xy expects (theta, radius) if it's a specialized patch?
            # No, Polygon usually expects x,y. Polar projection handles the transform.
            # Let's try removing and adding a new fill for simplicity and reliability.
            if hasattr(self, 'fill_radar'):
                try:
                    self.fill_radar[0].remove()
                except: pass
            self.fill_radar = self.ax_radar.fill(angles, radar_metrics_closed, color=COLOR_ACCENT, alpha=0.25)
            
            # Update FFT Bar Chart
            for rect, h in zip(self.bar_fft, fft_data):
                rect.set_height(h)
            
            self.ax_phase.relim()
            self.ax_phase.autoscale_view()
            self.ax_error.set_xlim(max(0, current_time - 10), current_time + 1)
            self.ax_error.set_ylim(min(errors)-0.5, max(errors)+0.5)
            
            self.canvas2.draw_idle()

        elif active_tab == "PID DETAILS":
            self.line_p.set_data(times, p_terms)
            self.line_i.set_data(times, i_terms)
            self.line_d.set_data(times, d_terms)
            
            self.ax_pid.set_xlim(max(0, current_time - 10), current_time + 1)
            self.ax_pid.relim()
            self.ax_pid.autoscale_view()
            
            self.canvas3.draw_idle()
            
        elif active_tab == "AI TRAINING":
            self.line_loss.set_data(times, losses)
            self.ax_loss.set_xlim(max(0, current_time - 10), current_time + 1)
            self.ax_loss.relim()
            self.ax_loss.autoscale_view()
            
            # Rotate 3D Plot
            self.ax_3d.view_init(elev=30, azim=(current_time * 10) % 360)
            
            self.canvas4.draw_idle()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NEXUS: Adaptive Hybrid Control System")
        self.geometry("1600x900")
        self.configure(fg_color=COLOR_BG)
        
        # Simulation Runner (Threaded)
        self.runner = SimulationRunner(max_points=200, dt=0.05)
        self.verbose_logging = True
        
        # Direct Launch - No Login
        self.dashboard_frame = MainDashboardFrame(self)
        self.dashboard_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
