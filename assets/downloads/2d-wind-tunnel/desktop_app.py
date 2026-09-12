import ctypes
import sys
import struct
import time
import tkinter as tk
from tkinter import ttk, font as tkfont

import numpy as np
from PIL import Image, ImageTk

from solver import LBMSolver


def enable_high_dpi_rendering():
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


OBJECT_TYPES = [
    "NACA 0012",
    "NACA 2412",
    "NACA 4412",
    "NACA 23012",
    "NACA 0018",
    "NACA 6409",
    "NACA 6418",
    "Double-wedge supersonic",
    "Circular cylinder",
    "Golfball",
    "Flat rectangle",
    "Square block",
    "Ellipse",
    "Triangle wedge",
    "Two cylinders",
]

PLOT_TYPES = ["Velocity magnitude", "Vorticity"]
TARGET_FPS = 30

VELOCITY_PALETTE = np.array(
    [
        [2, 10, 24],
        [5, 42, 101],
        [0, 139, 210],
        [12, 220, 218],
        [166, 235, 64],
        [255, 189, 0],
        [242, 71, 35],
    ],
    dtype=np.float32,
)

VORTICITY_PALETTE = np.array(
    [
        [30, 58, 138],
        [73, 132, 190],
        [229, 236, 240],
        [221, 118, 83],
        [157, 38, 51],
    ],
    dtype=np.float32,
)

PARTICLE_PALETTE = np.array(
    [
        [76, 178, 255],
        [120, 238, 248],
        [205, 255, 232],
        [255, 250, 160],
    ],
    dtype=np.float32,
)

# The visualizer deliberately renders to this fixed pixel budget.  The window
# can grow around the graph without increasing the per-frame image, particle,
# or overlay work.
FLOW_RENDER_MAX_SIZE = (840, 420)
COLORMAP_TABLES = {}


def apply_colormap(values, palette):
    key = palette.tobytes()
    table = COLORMAP_TABLES.get(key)
    if table is None:
        samples = np.linspace(0, len(palette) - 1, 4096)
        table = np.column_stack([
            np.interp(samples, np.arange(len(palette)), palette[:, channel])
            for channel in range(3)
        ]).astype(np.uint8)
        COLORMAP_TABLES[key] = table
    indices = (np.clip(values, 0, 1) * 4095).astype(np.int32)
    return table[indices]


def field_to_rgb(field, plot_type, inlet_speed=None):
    finite = np.isfinite(field)
    if not np.any(finite):
        return np.zeros(field.shape + (3,), dtype=np.uint8)

    if plot_type == "Vorticity":
        limit = np.nanmax(np.abs(field))
        if limit <= 0:
            limit = 1.0
        normalized = (field + limit) / (2 * limit)
        normalized = np.where(finite, normalized, 0.0)
        rgb = apply_colormap(normalized, VORTICITY_PALETTE)
    else:
        high = max(1e-6, float(np.max(field[finite])))
        normalized = field / high
        normalized = np.where(finite, normalized, 0.0)
        rgb = apply_colormap(normalized, VELOCITY_PALETTE)

    # The smooth high-resolution body layer is composited during rendering.
    # Keeping solver-solid cells dark here avoids exposing the coarse boolean
    # collision mask beneath that layer.
    rgb[~finite] = [11, 17, 25]
    return np.flipud(rgb)


class InstrumentSlider(tk.Canvas):
    def __init__(self, parent, variable, minimum, maximum, command=None):
        super().__init__(
            parent,
            height=34,
            bg="#101a26",
            highlightthickness=0,
            bd=0,
        )
        self.variable = variable
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.command = command
        self.pad = 8
        self.bind("<Configure>", lambda _event: self.redraw())
        self.bind("<Button-1>", self.set_from_event)
        self.bind("<B1-Motion>", self.set_from_event)
        self.variable.trace_add("write", lambda *_args: self.redraw())

    def normalized_value(self):
        span = max(1e-9, self.maximum - self.minimum)
        return np.clip((float(self.variable.get()) - self.minimum) / span, 0.0, 1.0)

    def set_from_event(self, event):
        width = max(1, self.winfo_width())
        usable = max(1, width - 2 * self.pad)
        normalized = np.clip((event.x - self.pad) / usable, 0.0, 1.0)
        value = self.minimum + normalized * (self.maximum - self.minimum)
        if isinstance(self.variable, tk.IntVar):
            value = round(value)
        self.variable.set(value)
        if self.command is not None:
            self.command()

    def redraw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        track_y = 15
        left = self.pad
        right = width - self.pad
        value_x = left + self.normalized_value() * max(1, right - left)

        self.create_line(left, track_y, right, track_y, fill="#6d7480", width=2)
        for index in range(11):
            x = left + (right - left) * index / 10
            tick = 7 if index in (0, 5, 10) else 4
            self.create_line(x, track_y - tick, x, track_y + tick, fill="#6d7480", width=1)
        self.create_line(left, track_y, value_x, track_y, fill="#54b9ff", width=2)
        self.create_oval(
            value_x - 7,
            track_y - 7,
            value_x + 7,
            track_y + 7,
            fill="#4eb3ff",
            outline="#8fd0ff",
            width=1,
        )


class FlowDisplay(tk.Frame):
    """Present a fixed-size bitmap using Windows' native stretch operation."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bitmap = None
        self.bitmap_size = None
        self.display_size = None
        self.paint_bounds = None
        if sys.platform == "win32":
            self.user32 = ctypes.WinDLL("user32", use_last_error=True)
            self.gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
            self.user32.GetDC.argtypes = [ctypes.c_void_p]
            self.user32.GetDC.restype = ctypes.c_void_p
            self.user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            self.user32.FillRect.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
            self.gdi32.CreateSolidBrush.argtypes = [ctypes.c_ulong]
            self.gdi32.CreateSolidBrush.restype = ctypes.c_void_p
            self.gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
            self.gdi32.SetStretchBltMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
            self.gdi32.StretchDIBits.argtypes = [ctypes.c_void_p] + [ctypes.c_int] * 8 + [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_ulong]
            self.gdi32.StretchDIBits.restype = ctypes.c_int
            self.bind("<Expose>", lambda event: self.after_idle(self.paint))

    def present(self, image):
        self.bitmap_size = image.size
        self.bitmap = image.tobytes("raw", "BGRX")
        width, height = image.size
        self.bitmap_header = struct.pack(
            "<IiiHHIIiiII", 40, width, -height, 1, 32, 0,
            len(self.bitmap), 0, 0, 0, 0,
        )
        self.paint()

    def paint(self):
        if self.bitmap is None or not self.winfo_exists():
            return
        width, height = self.winfo_width(), self.winfo_height()
        source_width, source_height = self.bitmap_size
        scale = min(width / source_width, height / source_height)
        dw, dh = max(1, int(source_width * scale)), max(1, int(source_height * scale))
        self.display_size = (dw, dh)
        hwnd = self.winfo_id()
        dc = self.user32.GetDC(hwnd)
        if dc:
            try:
                bounds = (width, height, dw, dh)
                if self.paint_bounds != bounds:
                    rect = (ctypes.c_long * 4)(0, 0, width, height)
                    brush = self.gdi32.CreateSolidBrush(0x1A1006)
                    try:
                        self.user32.FillRect(dc, ctypes.byref(rect), brush)
                    finally:
                        self.gdi32.DeleteObject(brush)
                    self.paint_bounds = bounds
                self.gdi32.SetStretchBltMode(dc, 3)
                self.gdi32.StretchDIBits(dc, (width-dw)//2, (height-dh)//2,
                    dw, dh, 0, 0, source_width, source_height,
                    self.bitmap, self.bitmap_header, 0, 0x00CC0020)
            finally:
                self.user32.ReleaseDC(hwnd, dc)


class WindTunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2D Wind Tunnel")
        self.root.geometry("1320x760")
        self.root.minsize(980, 560)
        self.root.configure(bg="#111820")
        self.configure_display_scaling()

        self.solver = None
        self.solver_key = None
        self.running = False
        self.frame_count = 0
        self.after_id = None
        self.photo = None
        self.photo_size = None
        self.flow_image = None
        self.current_rgb = None
        self.last_actual_fps = 0.0
        self.last_frame_time = 0.0
        self.fps_sample_start = None
        self.fps_sample_count = 0
        self.obstacle_overlay_key = None
        self.obstacle_overlay = None
        self.particles = None
        self.previous_particles = None
        self.particle_speed = None
        self.trail_image = None
        self.trail_buffer = None
        self.trail_key = None
        self.rng = np.random.default_rng(7)

        self.configure_styles()
        self.build_ui()
        self.reset_solver()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.option_add("*TCombobox*Listbox.background", "#0f1720")
        self.root.option_add("*TCombobox*Listbox.foreground", "#f4f8fb")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#2b82c6")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

        style.configure("Root.TFrame", background="#111820")
        style.configure("Sidebar.TFrame", background="#101a26")
        style.configure(
            "Panel.TLabelframe",
            background="#101a26",
            foreground="#dce7ef",
            bordercolor="#24364a",
            lightcolor="#24364a",
            darkcolor="#24364a",
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Panel.TLabelframe.Label",
            background="#101a26",
            foreground="#9fb6c8",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure("TLabel", background="#101a26", foreground="#dce7ef", font=("Segoe UI", 10))
        style.configure("Value.TLabel", background="#101a26", foreground="#8fd0ff", font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel", background="#101a26", foreground="#f4f8fb")
        style.configure("Status.TLabel", background="#111820", foreground="#dce7ef")
        style.configure("TCheckbutton", background="#101a26", foreground="#dce7ef", font=("Segoe UI", 10))
        style.map(
            "TCheckbutton",
            background=[("active", "#101a26")],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "TButton",
            padding=(11, 8),
            background="#202d3b",
            foreground="#eaf2f8",
            borderwidth=0,
            focusthickness=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map("TButton", background=[("active", "#2a3a4b")])
        style.configure(
            "Accent.TButton",
            padding=(11, 8),
            background="#2b82c6",
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Accent.TButton", background=[("active", "#399be8")])
        style.configure(
            "TCombobox",
            fieldbackground="#0f1720",
            background="#233242",
            foreground="#f4f8fb",
            arrowcolor="#f4f8fb",
            bordercolor="#2b3a49",
            lightcolor="#2b3a49",
            darkcolor="#2b3a49",
            padding=(8, 7),
            font=("Segoe UI", 10),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#0f1720"), ("focus", "#0f1720")],
            foreground=[("readonly", "#f4f8fb"), ("focus", "#ffffff")],
            selectbackground=[("readonly", "#0f1720"), ("focus", "#0f1720")],
            selectforeground=[("readonly", "#f4f8fb"), ("focus", "#ffffff")],
        )
        style.configure(
            "Modern.Horizontal.TScale",
            background="#101a26",
            troughcolor="#0f1720",
            bordercolor="#101a26",
            lightcolor="#2b82c6",
            darkcolor="#2b82c6",
        )
        style.configure(
            "Vertical.TScrollbar",
            background="#162535",
            troughcolor="#0b1521",
            bordercolor="#0b1521",
            arrowcolor="#8fd0ff",
        )

    def configure_display_scaling(self):
        if sys.platform != "win32":
            return

        try:
            dpi = self.root.winfo_fpixels("1i")
            self.root.tk.call("tk", "scaling", dpi / 72)
        except tk.TclError:
            pass

    def build_ui(self):
        self.object_var = tk.StringVar(value="NACA 2412")
        self.plot_var = tk.StringVar(value="Velocity magnitude")
        self.quality_var = tk.StringVar(value="Balanced")
        self.angle_var = tk.IntVar(value=0)
        self.size_var = tk.IntVar(value=18)
        self.detail_var = tk.IntVar(value=4)
        self.speed_var = tk.DoubleVar(value=0.08)
        self.reynolds_var = tk.IntVar(value=324)
        self.mach_var = tk.IntVar(value=14)
        self.steps_var = tk.IntVar(value=10)
        self.env_width_var = tk.IntVar(value=620)
        self.env_height_var = tk.IntVar(value=260)
        self.zoom_var = tk.BooleanVar(value=False)
        self.particles_on_var = tk.BooleanVar(value=True)
        self.tau = 0.6
        self.syncing_conditions = False
        self.viscosity_value = tk.StringVar()
        self.tau_value = tk.StringVar()
        self.airspeed_value = tk.StringVar()
        self.mach_note_value = tk.StringVar()
        self.model_value = tk.StringVar(value="2D lattice model")

        self.root.columnconfigure(0, minsize=58)
        self.root.columnconfigure(1, minsize=520)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, minsize=74)
        self.root.rowconfigure(1, weight=1)

        rail = tk.Frame(self.root, bg="#08111b", width=58)
        rail.grid(row=0, column=0, rowspan=2, sticky="nsew")
        rail.grid_propagate(False)
        for label, active in [
            ("~", True),
            ("/", False),
            ("O", False),
            ("=", False),
            ("[]", False),
        ]:
            self.add_rail_button(rail, label, active)

        topbar = tk.Frame(self.root, bg="#08111b", highlightthickness=1, highlightbackground="#162535")
        topbar.grid(row=0, column=1, columnspan=2, sticky="nsew")
        topbar.columnconfigure(0, minsize=300)
        topbar.columnconfigure(1, weight=1)
        topbar.columnconfigure(2, minsize=190)

        title_block = tk.Frame(topbar, bg="#08111b")
        title_block.grid(row=0, column=0, sticky="w", padx=(18, 12), pady=12)
        tk.Label(
            title_block,
            text="2D Wind Tunnel",
            bg="#08111b",
            fg="#f4f8fb",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_block,
            text="Desktop LBM flow lab",
            bg="#08111b",
            fg="#6f879a",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        metrics = tk.Frame(topbar, bg="#08111b")
        metrics.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.metric_mach = tk.StringVar(value="0.14")
        self.metric_re = tk.StringVar(value="324")
        self.metric_aoa = tk.StringVar(value="0 deg")
        self.metric_time = tk.StringVar(value="0.00 s")
        self.metric_status = tk.StringVar(value="Ready")
        for idx, (label, value) in enumerate(
            [
                ("Mach", self.metric_mach),
                ("Re", self.metric_re),
                ("AoA", self.metric_aoa),
                ("Time", self.metric_time),
                ("Status", self.metric_status),
            ]
        ):
            self.add_metric(metrics, label, value, idx)

        actions = tk.Frame(topbar, bg="#08111b")
        actions.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=16)
        self.add_action_button(actions, "RUN", self.start, active=True).pack(side="left", padx=5)
        self.add_action_button(actions, "II", self.pause).pack(side="left", padx=5)
        self.add_action_button(actions, "STEP", self.single_step).pack(side="left", padx=5)

        self.sidebar = ttk.Frame(
            self.root,
            style="Sidebar.TFrame",
            padding=(14, 14, 14, 12),
            width=520,
        )
        self.sidebar.grid(row=1, column=1, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure(0, weight=1)

        self.sidebar_canvas = tk.Canvas(self.sidebar, width=470, bg="#101a26", highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.grid(row=0, column=0, sticky="nsew")
        sidebar_scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))

        controls = ttk.Frame(self.sidebar_canvas, style="Sidebar.TFrame", padding=(10, 8, 10, 8))
        controls.columnconfigure(0, weight=1)
        self.sidebar_controls = controls
        self.sidebar_controls_window = self.sidebar_canvas.create_window(
            (0, 0), window=controls, anchor="nw"
        )

        def update_scroll_region(_event=None):
            canvas_width = max(1, self.sidebar_canvas.winfo_width())
            # Keep the embedded controls clear of the canvas edge and vertical
            # scrollbar.  Tk's requested-size propagation can otherwise place
            # a value label a few pixels underneath the neighboring graph.
            self.sidebar_canvas.itemconfigure(
                self.sidebar_controls_window, width=max(1, canvas_width - 6)
            )
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

        controls.bind("<Configure>", update_scroll_region)
        self.sidebar_canvas.bind("<Configure>", update_scroll_region)

        def wheel_scroll(event):
            self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.sidebar_canvas.bind("<MouseWheel>", wheel_scroll)
        controls.bind("<MouseWheel>", wheel_scroll)

        object_panel = self.add_panel(controls, "OBJECT", 0)
        self.add_combo(
            object_panel, "Shape", self.object_var, OBJECT_TYPES, self.flow_conditions_changed
        )
        self.add_scale(
            object_panel, "Angle", self.angle_var, -30, 30, self.angle_changed, " deg"
        )
        self.add_scale(object_panel, "Size", self.size_var, 8, 35, self.flow_conditions_changed)
        self.add_scale(
            object_panel,
            "Edge detail",
            self.detail_var,
            1,
            6,
            self.reset_solver_if_needed,
        )

        flow_panel = self.add_panel(controls, "FLOW", 1)
        self.add_scale(
            flow_panel,
            "Inlet speed (lattice)",
            self.speed_var,
            0.02,
            0.15,
            self.flow_conditions_changed,
        )
        self.add_scale(flow_panel, "Steps/frame", self.steps_var, 1, 150)

        conditions_panel = self.add_panel(controls, "SIMULATION", 2)
        self.add_scale(
            conditions_panel,
            "Reynolds number",
            self.reynolds_var,
            50,
            1500,
            self.reynolds_changed,
        )
        self.add_scale(
            conditions_panel,
            "Mach number",
            self.mach_var,
            3,
            26,
            self.mach_changed,
            scale=100,
        )
        self.add_readout(conditions_panel, "Sea-level speed ref", self.airspeed_value)
        self.add_readout(conditions_panel, "Mach regime", self.mach_note_value)
        self.add_readout(conditions_panel, "Kinematic viscosity", self.viscosity_value)
        self.add_readout(conditions_panel, "Relaxation time", self.tau_value)
        self.add_readout(conditions_panel, "Model", self.model_value)

        view_panel = self.add_panel(controls, "VISUALIZATION", 3)
        self.add_combo(view_panel, "Plot", self.plot_var, PLOT_TYPES, self.update_image)
        self.add_combo(
            view_panel,
            "Quality",
            self.quality_var,
            ["Fast preview", "Balanced", "High quality", "Custom"],
            self.reset_solver_if_needed,
        )
        self.add_scale(
            view_panel,
            "Environment width",
            self.env_width_var,
            220,
            1400,
            self.custom_grid_changed,
            initial_callback=False,
        )
        self.add_scale(
            view_panel,
            "Environment height",
            self.env_height_var,
            90,
            480,
            self.custom_grid_changed,
            initial_callback=False,
        )
        ttk.Checkbutton(
            view_panel,
            text="Zoom around object",
            variable=self.zoom_var,
            command=self.update_image,
        ).pack(anchor="w", pady=(3, 0))
        ttk.Checkbutton(
            view_panel,
            text="Flow particles (P)",
            variable=self.particles_on_var,
            command=self.update_image,
        ).pack(anchor="w", pady=(5, 0))

        ttk.Button(controls, text="Reset Simulation", command=self.reset_solver).grid(
            row=4, column=0, sticky="ew", pady=(4, 8)
        )

        self.sidebar_status = tk.StringVar(value="Ready")
        ttk.Label(
            controls,
            textvariable=self.sidebar_status,
            wraplength=420,
            foreground="#9fb6c8",
            font=("Segoe UI", 9),
        ).grid(row=5, column=0, sticky="ew")

        main = ttk.Frame(self.root, style="Root.TFrame", padding=(14, 14, 14, 12))
        main.grid(row=1, column=2, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        header = ttk.Frame(main, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        self.plot_title = ttk.Label(
            header,
            text="Velocity magnitude",
            style="Status.TLabel",
            font=("Segoe UI", 16, "bold"),
        )
        self.plot_title.grid(row=0, column=0, sticky="w")
        self.status_var = tk.StringVar(value="")
        ttk.Label(header, textvariable=self.status_var, style="Status.TLabel").grid(
            row=0, column=1, sticky="e"
        )

        display_frame = tk.Frame(main, bg="#06101a", highlightthickness=1, highlightbackground="#24364a")
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        self.image_label = (
            FlowDisplay(display_frame, bg="#06101a") if sys.platform == "win32"
            else tk.Label(display_frame, bg="#06101a")
        )
        self.image_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.image_label.bind("<Configure>", self.on_display_resize)

        legend_frame = tk.Frame(main, bg="#0b1521", highlightthickness=1, highlightbackground="#203244")
        legend_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        legend_frame.columnconfigure(0, weight=1)
        legend_frame.columnconfigure(1, weight=1)
        self.velocity_legend_canvas = tk.Canvas(
            legend_frame,
            height=64,
            bg="#0b1521",
            highlightthickness=0,
        )
        self.velocity_legend_canvas.grid(row=0, column=0, sticky="ew", padx=18, pady=10)
        self.vorticity_legend_canvas = tk.Canvas(
            legend_frame,
            height=64,
            bg="#0b1521",
            highlightthickness=0,
        )
        self.vorticity_legend_canvas.grid(row=0, column=1, sticky="ew", padx=18, pady=10)
        self.velocity_legend_canvas.bind("<Configure>", lambda _event: self.draw_legend())
        self.vorticity_legend_canvas.bind("<Configure>", lambda _event: self.draw_legend())
        self.root.bind_all("<Up>", self.increase_angle)
        self.root.bind_all("<Down>", self.decrease_angle)
        self.root.bind_all("<KeyPress-p>", self.toggle_particles)
        self.root.bind_all("<KeyPress-P>", self.toggle_particles)
        self.root.bind("<Configure>", self.update_responsive_layout)
        self.update_condition_readouts()
        self.update_responsive_layout()

    def add_rail_button(self, parent, label, active=False):
        bg = "#0f5f9f" if active else "#08111b"
        fg = "#7fe7ff" if active else "#9aa9b5"
        border = "#1da8f2" if active else "#263646"
        button = tk.Label(
            parent,
            text=label,
            bg=bg,
            fg=fg,
            font=("Consolas", 15, "bold"),
            highlightthickness=1,
            highlightbackground=border,
            padx=8,
            pady=13,
        )
        button.pack(anchor="n", fill="x", padx=8, pady=(16 if active else 8, 0))
        return button

    def add_metric(self, parent, label, value, column):
        frame = tk.Frame(parent, bg="#08111b", padx=7, pady=7)
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 5))
        tk.Label(
            frame,
            text=label,
            bg="#08111b",
            fg="#7f92a4",
            font=("Segoe UI", 8),
        ).pack(anchor="w")
        tk.Label(
            frame,
            textvariable=value,
            bg="#08111b",
            fg="#14e3e9" if label == "Status" else "#f0f6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

    def add_action_button(self, parent, label, command, active=False):
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg="#113f63" if active else "#101a26",
            fg="#69d9ff" if active else "#dce7ef",
            activebackground="#185a87",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#1a9de0" if active else "#263646",
            font=("Segoe UI", 8, "bold"),
            padx=18,
            pady=13,
        )

    def update_responsive_layout(self, event=None):
        if event is not None and event.widget is not self.root:
            return
        if not hasattr(self, "sidebar"):
            return

        if event is not None and event.widget is self.root:
            window_width = event.width
        elif self.root.state() == "zoomed":
            window_width = self.root.winfo_screenwidth()
        else:
            window_width = max(self.root.winfo_width(), self.root.winfo_reqwidth(), 1)

        # The controls need enough room for labels, readouts, a scrollbar, and
        # the sidebar padding.  Let this column grow on larger windows while
        # retaining a usable minimum at the app's smallest supported size.
        screen_width = max(1, self.root.winfo_screenwidth())
        is_expanded = (
            self.root.state() == "zoomed"
            or window_width >= screen_width - 20
        )
        if is_expanded:
            # A maximized workspace has ample room.  Give the control deck a
            # deliberately larger share instead of leaving it at its compact
            # window width.
            target_width = int(np.clip(window_width * 0.36, 620, 740))
        else:
            target_width = int(np.clip(window_width * 0.31, 520, 680))
        sidebar_padding = 28
        scrollbar_space = 24
        canvas_width = max(468, target_width - sidebar_padding - scrollbar_space)

        self.root.columnconfigure(1, minsize=target_width, weight=0)
        self.sidebar.configure(width=target_width)
        self.sidebar_canvas.configure(width=canvas_width)
        self.sidebar_canvas.itemconfigure(
            self.sidebar_controls_window, width=max(1, canvas_width - 6)
        )
        self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

    def add_panel(self, parent, label, row):
        section = ttk.Frame(parent, style="Sidebar.TFrame")
        section.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        section.columnconfigure(0, weight=1)
        tk.Label(
            section,
            text=label,
            bg="#101a26",
            fg="#58c7ff",
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        tk.Frame(section, bg="#263848", height=1).grid(row=1, column=0, sticky="ew", pady=(0, 8))
        body = ttk.Frame(section, style="Sidebar.TFrame")
        body.grid(row=2, column=0, sticky="ew")
        body.columnconfigure(0, weight=1)
        return body

    def add_combo(self, parent, label, variable, values, callback):
        ttk.Label(parent, text=label).pack(anchor="w")
        combo = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly")
        combo.configure(height=min(12, len(values)))
        combo.selection_clear()
        combo.pack(fill="x", pady=(2, 8))
        combo.bind("<<ComboboxSelected>>", lambda _event: callback())
        # A focused ttk.Combobox handles Up/Down before bind_all(), which
        # would open or navigate the shape menu instead of changing AoA.
        combo.bind("<Up>", self.increase_angle)
        combo.bind("<Down>", self.decrease_angle)

    def add_scale(
        self,
        parent,
        label,
        variable,
        minimum,
        maximum,
        callback=None,
        suffix="",
        scale=1,
        initial_callback=True,
    ):
        value_var = tk.StringVar()

        def update_value(_value=None, notify=True):
            raw = variable.get()
            if scale == 1 and isinstance(raw, float):
                value_var.set(f"{raw:.3f}{suffix}")
            elif scale == 1:
                value_var.set(f"{raw}{suffix}")
            else:
                value_var.set(f"{raw / scale:.2f}{suffix}")
            if callback is not None and notify:
                callback()

        variable.trace_add("write", lambda *_args: update_value(notify=False))

        row = ttk.Frame(parent, style="Sidebar.TFrame")
        row.pack(fill="x", pady=(3, 0))
        row.columnconfigure(0, weight=1)
        ttk.Label(row, text=label).grid(row=0, column=0, sticky="w")
        ttk.Label(
            row,
            textvariable=value_var,
            style="Value.TLabel",
            anchor="e",
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        InstrumentSlider(
            parent,
            variable=variable,
            minimum=minimum,
            maximum=maximum,
            command=lambda: update_value(notify=True),
        ).pack(fill="x", pady=(2, 10))
        update_value(notify=initial_callback)

    def add_readout(self, parent, label, value):
        row = ttk.Frame(parent, style="Sidebar.TFrame")
        row.pack(fill="x", pady=(2, 5))
        row.columnconfigure(0, weight=1)
        ttk.Label(row, text=label).grid(row=0, column=0, sticky="w")
        # Readout values such as the Mach-regime description can be much wider
        # than slider values.  Giving them their own line guarantees they wrap
        # inside the sidebar instead of being clipped at its right boundary.
        ttk.Label(
            row,
            textvariable=value,
            style="Value.TLabel",
            anchor="w",
            justify="left",
            wraplength=390,
        ).grid(
            row=1, column=0, sticky="ew", pady=(1, 0)
        )

    def grid_size(self):
        quality = self.quality_var.get()
        if quality == "Fast preview":
            return 300, 120
        if quality == "Balanced":
            return 420, 180
        if quality == "Custom":
            return self.env_width_var.get(), self.env_height_var.get()
        return 620, 260

    def current_key(self):
        nx, ny = self.grid_size()
        return (
            self.object_var.get(),
            self.size_var.get(),
            self.detail_var.get(),
            self.inlet_speed(),
            nx,
            ny,
            self.quality_var.get(),
            round(self.tau, 5),
        )

    def reference_chord(self):
        if self.object_var.get() == "Double-wedge supersonic":
            return self.size_var.get() * 8.5
        return self.size_var.get() * 7.5

    def inlet_speed(self):
        return float(self.speed_var.get())

    def reynolds_number(self):
        viscosity = (self.tau - 0.5) / 3
        return self.inlet_speed() * self.reference_chord() / viscosity

    def lattice_mach_number(self):
        lattice_speed_of_sound = 1 / np.sqrt(3)
        return self.inlet_speed() / lattice_speed_of_sound

    def mach_regime(self, mach):
        if mach < 0.30:
            return "Subsonic / LBM-friendly"
        if mach < 0.80:
            return "Subsonic reference"
        if mach < 1.20:
            return "Transonic reference"
        return "Supersonic reference"

    def update_condition_readouts(self):
        viscosity = (self.tau - 0.5) / 3
        mach = self.lattice_mach_number()
        sea_level_mph = mach * 767.0
        self.viscosity_value.set(f"{viscosity:.4f} lattice")
        self.tau_value.set(f"{self.tau:.3f}")
        self.airspeed_value.set(f"{sea_level_mph:.0f} mph")
        self.mach_note_value.set(self.mach_regime(mach))
        self.update_top_metrics()

    def update_top_metrics(self, actual_fps=None, frame_time=None):
        if not hasattr(self, "metric_mach"):
            return

        if actual_fps is None:
            actual_fps = self.last_actual_fps
        if frame_time is None:
            frame_time = self.last_frame_time

        self.metric_mach.set(f"{self.lattice_mach_number():.2f}")
        self.metric_re.set(f"{round(self.reynolds_number())}")
        self.metric_aoa.set(f"{self.angle_var.get()} deg")
        self.metric_time.set(f"{frame_time * 1000:.1f} ms")
        self.metric_status.set("Running" if self.running else "Paused")

    def flow_conditions_changed(self):
        if self.syncing_conditions:
            return
        self.syncing_conditions = True
        self.reynolds_var.set(round(self.reynolds_number()))
        self.mach_var.set(round(self.lattice_mach_number() * 100))
        self.syncing_conditions = False
        self.update_condition_readouts()
        self.reset_solver_if_needed()

    def custom_grid_changed(self):
        """Apply dimension sliders immediately by switching to Custom quality."""
        if self.quality_var.get() != "Custom":
            self.quality_var.set("Custom")
        self.reset_solver_if_needed()

    def reynolds_changed(self):
        if self.syncing_conditions:
            return

        target_reynolds = max(1, self.reynolds_var.get())
        target_tau = 0.5 + 3 * self.inlet_speed() * self.reference_chord() / target_reynolds
        # Very small relaxation times are numerically fragile in this simple
        # real-time solver. Clamp to a practical range and report the actual Re.
        self.tau = float(np.clip(target_tau, 0.52, 0.90))
        actual_reynolds = round(self.reynolds_number())
        self.syncing_conditions = True
        self.reynolds_var.set(actual_reynolds)
        self.syncing_conditions = False
        self.update_condition_readouts()
        self.reset_solver_if_needed()

    def mach_changed(self):
        if self.syncing_conditions:
            return

        lattice_speed_of_sound = 1 / np.sqrt(3)
        requested_mach = self.mach_var.get() / 100
        requested_speed = requested_mach * lattice_speed_of_sound
        clamped_speed = float(np.clip(requested_speed, 0.02, 0.15))

        self.syncing_conditions = True
        self.speed_var.set(clamped_speed)
        self.mach_var.set(round(self.lattice_mach_number() * 100))
        self.reynolds_var.set(round(self.reynolds_number()))
        self.syncing_conditions = False
        self.update_condition_readouts()
        self.reset_solver_if_needed()

    def reset_solver_if_needed(self):
        if self.solver_key is not None and self.current_key() != self.solver_key:
            self.reset_solver()

    def reset_solver(self):
        nx, ny = self.grid_size()
        self.solver = LBMSolver(
            nx=nx,
            ny=ny,
            u0=self.inlet_speed(),
            object_type=self.object_var.get(),
            angle_deg=self.angle_var.get(),
            obstacle_radius=self.size_var.get(),
            object_detail=self.detail_var.get(),
            tau=self.tau,
        )
        self.solver_key = self.current_key()
        self.frame_count = 0
        self.obstacle_overlay_key = None
        self.trail_image = None
        self.trail_buffer = None
        self.trail_key = None
        self.init_particles()
        self.update_image()
        self.update_status(0.0, 0.0)

    def start(self):
        if self.running:
            return
        self.running = True
        self.fps_sample_start = time.perf_counter()
        self.fps_sample_count = 0
        self.update_top_metrics()
        self.schedule_next_frame(1)

    def pause(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.update_top_metrics()

    def single_step(self):
        self.pause()
        self.run_frame()

    def schedule_next_frame(self, delay_ms=None):
        if not self.running:
            return
        if delay_ms is None:
            delay_ms = max(1, round(1000 / TARGET_FPS))
        self.after_id = self.root.after(delay_ms, self.run_frame)

    def run_frame(self):
        start = time.perf_counter()
        self.solver.set_angle_of_attack(self.angle_var.get())
        self.solver.step(self.steps_var.get())
        if self.particles_on_var.get():
            self.update_particles()
        else:
            self.trail_image = None
            self.trail_buffer = None
            self.trail_key = None
        self.frame_count += 1
        self.update_image()

        frame_time = time.perf_counter() - start
        target_frame_time = 1 / TARGET_FPS
        self.fps_sample_count += 1
        if self.fps_sample_start is None:
            self.fps_sample_start = start
        elapsed = time.perf_counter() - self.fps_sample_start
        if elapsed >= 0.5 or not self.running:
            self.update_status(self.fps_sample_count / max(elapsed, 1e-6), frame_time)
            self.fps_sample_start = time.perf_counter()
            self.fps_sample_count = 0
        remaining_ms = max(1, round((target_frame_time - frame_time) * 1000))
        self.schedule_next_frame(remaining_ms)

    def get_field(self):
        plot_type = self.plot_var.get()
        if plot_type == "Vorticity":
            return self.solver.get_vorticity()
        return self.solver.get_velocity_magnitude()

    def get_current_rgb(self):
        x_min, x_max, y_min, y_max = self.view_bounds()
        view = np.s_[y_min:y_max, x_min:x_max]

        if self.plot_var.get() == "Vorticity":
            field = self.solver.get_vorticity()[view]
        else:
            ux = self.solver.ux[view]
            uy = self.solver.uy[view]
            field = np.sqrt(ux * ux + uy * uy)
            field = field.copy()
            field[self.solver.obstacle[view]] = np.nan

        return field_to_rgb(field, self.plot_var.get(), self.inlet_speed())

    def angle_changed(self):
        if self.solver is not None:
            self.solver.set_angle_of_attack(self.angle_var.get())
            self.obstacle_overlay_key = None
            self.reseed_solid_particles()
        self.update_top_metrics()
        self.update_image()

    def increase_angle(self, _event=None):
        self.angle_var.set(min(30, self.angle_var.get() + 1))
        self.angle_changed()
        return "break"

    def decrease_angle(self, _event=None):
        self.angle_var.set(max(-30, self.angle_var.get() - 1))
        self.angle_changed()
        return "break"

    def toggle_particles(self, _event=None):
        self.particles_on_var.set(not self.particles_on_var.get())
        if not self.particles_on_var.get():
            self.trail_image = None
            self.trail_buffer = None
            self.trail_key = None
        self.update_top_metrics()
        self.update_image()
        return "break"

    def view_bounds(self):
        if not self.zoom_var.get():
            return 0, self.solver.nx, 0, self.solver.ny

        x_min = max(self.solver.obstacle_x - 90, 0)
        x_max = min(self.solver.obstacle_x + 280, self.solver.nx)
        y_min = max(self.solver.obstacle_y - 90, 0)
        y_max = min(self.solver.obstacle_y + 90, self.solver.ny)
        return x_min, x_max, y_min, y_max

    def crop_to_view(self, field):
        x_min, x_max, y_min, y_max = self.view_bounds()
        return field[y_min:y_max, x_min:x_max]

    def update_image(self):
        if self.solver is None:
            return

        self.plot_title.configure(
            text=self.plot_var.get()
        )
        self.current_rgb = self.get_current_rgb()
        self.render_image()
        self.draw_legend()

    def render_image(self):
        if self.current_rgb is None:
            return

        # Build the expensive layers only at a fixed internal resolution.
        # This is independent of the physical size of the surrounding panel.
        image = Image.fromarray(self.current_rgb)
        source_width, source_height = image.size
        max_width, max_height = FLOW_RENDER_MAX_SIZE
        scale = min(max_width / source_width, max_height / source_height)
        target_size = (
            max(1, int(source_width * scale)),
            max(1, int(source_height * scale)),
        )
        image = image.resize(target_size, Image.Resampling.BILINEAR).convert("RGBA")
        if self.particles_on_var.get():
            self.composite_particle_trails(image, target_size)
        body = Image.new("RGBA", target_size, (255, 255, 255, 0))
        body.putalpha(self.get_smooth_obstacle_overlay(target_size))
        image.alpha_composite(body)
        self.flow_image = image.convert("RGB")
        self.present_flow_image()

    def present_flow_image(self):
        """Scale the finished fixed-resolution image to the visible panel.

        The display can grow with the window, but the solver field, particle
        trails, and smooth obstacle mask always use FLOW_RENDER_MAX_SIZE.
        """
        if self.flow_image is None:
            return

        if isinstance(self.image_label, FlowDisplay):
            self.image_label.present(self.flow_image)
            self.photo_size = self.image_label.display_size
            return

        available_width = self.image_label.winfo_width()
        available_height = self.image_label.winfo_height()
        if available_width < 40 or available_height < 40:
            # During construction Tk reports a 1x1 label.  Keep the real
            # image ready and let the first Configure event present it.
            return

        source_width, source_height = self.flow_image.size
        scale = min(available_width / source_width, available_height / source_height)
        display_size = (
            max(1, int(source_width * scale)),
            max(1, int(source_height * scale)),
        )
        display_image = self.flow_image.resize(display_size, Image.Resampling.NEAREST)
        if self.photo is not None and self.photo_size == display_size:
            self.photo.paste(display_image)
        else:
            self.photo = ImageTk.PhotoImage(image=display_image)
            self.photo_size = display_size
            self.image_label.configure(image=self.photo)

    def init_particles(self):
        count = max(1800, min(3600, self.solver.nx * self.solver.ny // 28))
        self.particles = np.empty((count, 2), dtype=np.float64)
        self.previous_particles = np.empty_like(self.particles)
        self.particle_speed = np.zeros(count, dtype=np.float64)
        self.particles[:, 0] = self.rng.uniform(0, self.solver.nx - 1, count)
        self.particles[:, 1] = self.rng.uniform(1, self.solver.ny - 2, count)
        self.previous_particles[:] = self.particles
        self.trail_image = None
        self.trail_buffer = None
        self.trail_key = None

    def reseed_particles(self, indices):
        if self.particles is None or len(indices) == 0:
            return

        self.particles[indices, 0] = self.rng.uniform(0.1, 2.0, len(indices))
        self.particles[indices, 1] = self.seed_particle_y(len(indices))
        self.previous_particles[indices] = self.particles[indices]
        if self.particle_speed is not None:
            self.particle_speed[indices] = self.inlet_speed()

    def seed_particle_y(self, count):
        y = self.rng.uniform(1, self.solver.ny - 2, count)
        center_band = self.rng.random(count) < 0.42
        center_count = int(center_band.sum())
        if center_count:
            center = self.solver.ny / 2
            y[center_band] = center + self.rng.uniform(
                -self.solver.ny / 5,
                self.solver.ny / 5,
                center_count,
            )
        return np.clip(y, 1, self.solver.ny - 2)

    def reseed_solid_particles(self):
        if self.particles is None:
            return

        x = np.clip(self.particles[:, 0].astype(np.int32), 0, self.solver.nx - 1)
        y = np.clip(self.particles[:, 1].astype(np.int32), 0, self.solver.ny - 1)
        solid = self.solver.obstacle[y, x]
        self.reseed_particles(np.flatnonzero(solid))

    def update_particles(self):
        if self.particles is None:
            self.init_particles()
            return

        self.previous_particles[:] = self.particles
        x = np.clip(self.particles[:, 0], 0, self.solver.nx - 1.001)
        y = np.clip(self.particles[:, 1], 0, self.solver.ny - 1.001)
        x0 = np.floor(x).astype(np.int32)
        y0 = np.floor(y).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, self.solver.nx - 1)
        y1 = np.clip(y0 + 1, 0, self.solver.ny - 1)
        wx = x - x0
        wy = y - y0

        ux = (
            self.solver.ux[y0, x0] * (1 - wx) * (1 - wy)
            + self.solver.ux[y0, x1] * wx * (1 - wy)
            + self.solver.ux[y1, x0] * (1 - wx) * wy
            + self.solver.ux[y1, x1] * wx * wy
        )
        uy = (
            self.solver.uy[y0, x0] * (1 - wx) * (1 - wy)
            + self.solver.uy[y0, x1] * wx * (1 - wy)
            + self.solver.uy[y1, x0] * (1 - wx) * wy
            + self.solver.uy[y1, x1] * wx * wy
        )
        self.particle_speed[:] = np.sqrt(ux * ux + uy * uy)

        visual_dt = max(1, self.steps_var.get()) * 2.6
        self.particles[:, 0] += ux * visual_dt
        self.particles[:, 1] += uy * visual_dt

        px = self.particles[:, 0]
        py = self.particles[:, 1]
        xi = np.clip(px.astype(np.int32), 0, self.solver.nx - 1)
        yi = np.clip(py.astype(np.int32), 0, self.solver.ny - 1)
        invalid = (
            (px < 0)
            | (px >= self.solver.nx - 1)
            | (py < 1)
            | (py >= self.solver.ny - 2)
            | self.solver.obstacle[yi, xi]
            | (self.particle_speed < 1e-5)
        )
        self.reseed_particles(np.flatnonzero(invalid))

    def composite_particle_trails(self, image, target_size):
        trail_buffer = self.get_particle_trail_layer(target_size)
        self.stamp_particles(trail_buffer, target_size)
        self.trail_image = Image.fromarray(trail_buffer)
        image.alpha_composite(self.trail_image)

    def get_particle_trail_layer(self, target_size):
        x_min, x_max, y_min, y_max = self.view_bounds()
        key = (target_size, x_min, x_max, y_min, y_max, self.solver_key)
        if self.trail_buffer is None or self.trail_key != key:
            self.trail_buffer = np.zeros((target_size[1], target_size[0], 4), dtype=np.uint8)
            self.trail_key = key
            return self.trail_buffer

        self.trail_buffer[:, :, 3] = (self.trail_buffer[:, :, 3] * 0.92).astype(np.uint8)
        return self.trail_buffer

    def stamp_particles(self, trail_buffer, target_size):
        if self.particles is None or self.particle_speed is None:
            return

        x_min, x_max, y_min, y_max = self.view_bounds()
        view_width = x_max - x_min
        view_height = y_max - y_min
        sx = target_size[0] / view_width
        sy = target_size[1] / view_height

        x = (self.particles[:, 0] - x_min) * sx
        y = (y_max - self.particles[:, 1]) * sy
        visible = (
            (x >= 0)
            & (x < target_size[0])
            & (y >= 0)
            & (y < target_size[1])
        )

        if not np.any(visible):
            return

        speed_scale = max(1e-6, 2 * self.inlet_speed())
        color_values = np.clip(self.particle_speed[visible] / speed_scale, 0, 1)
        colors = apply_colormap(color_values, PARTICLE_PALETTE)

        xi = np.rint(x[visible]).astype(np.int32)
        yi = np.rint(y[visible]).astype(np.int32)
        offsets = np.array(
            [
                (-2, 0, 70),
                (-1, 0, 125),
                (0, 0, 195),
                (1, 0, 125),
                (2, 0, 70),
                (0, -1, 80),
                (0, 1, 80),
            ],
            dtype=np.int32,
        )

        for dx, dy, alpha in offsets:
            px = xi + dx
            py = yi + dy
            inside = (
                (px >= 0)
                & (px < target_size[0])
                & (py >= 0)
                & (py < target_size[1])
            )
            if not np.any(inside):
                continue

            px = px[inside]
            py = py[inside]
            stamped = trail_buffer[py, px]
            stamped[:, :3] = np.maximum(stamped[:, :3], colors[inside])
            stamped[:, 3] = np.maximum(stamped[:, 3], alpha)
            trail_buffer[py, px] = stamped

    def get_smooth_obstacle_overlay(self, target_size):
        """Return a cached antialiased body mask for the display only.

        The LBM keeps its coarse boolean mask for fast simulation, while this
        separately rasterizes the same analytic shape at screen resolution.
        """
        x_min, x_max, y_min, y_max = self.view_bounds()
        view_width = x_max - x_min
        view_height = y_max - y_min
        scale = max(
            2,
            int(
                np.ceil(
                    max(target_size[0] / view_width, target_size[1] / view_height)
                )
            ),
        )
        key = (
            self.solver_key,
            self.angle_var.get(),
            self.zoom_var.get(),
            x_min,
            x_max,
            y_min,
            y_max,
            target_size,
            scale,
        )
        if key == self.obstacle_overlay_key:
            return self.obstacle_overlay

        mask = self.solver.create_obstacle_mask_at_resolution(
            self.solver.nx * scale, self.solver.ny * scale, scale
        )
        mask = mask[y_min * scale:y_max * scale, x_min * scale:x_max * scale]
        # field_to_rgb() flips the flow image for display; mirror the separate
        # high-resolution body mask the same way before compositing it.
        mask = np.flipud(mask)
        mask_image = Image.fromarray((mask * 255).astype(np.uint8))
        self.obstacle_overlay = mask_image.resize(target_size, Image.Resampling.LANCZOS)
        self.obstacle_overlay_key = key
        return self.obstacle_overlay

    def on_display_resize(self, _event):
        # Only the already-composited bitmap is scaled here.  Resizing never
        # reruns the flow, particle, or body-overlay rendering work.
        self.present_flow_image()

    def draw_legend(self):
        if not hasattr(self, "velocity_legend_canvas"):
            return

        self.draw_legend_canvas(
            self.velocity_legend_canvas,
            "Velocity magnitude",
            VELOCITY_PALETTE,
            "Slow",
            "Fast",
        )
        self.draw_legend_canvas(
            self.vorticity_legend_canvas,
            "Vorticity",
            VORTICITY_PALETTE,
            "Clockwise",
            "Counter-clockwise",
        )

    def draw_legend_canvas(self, canvas, title, palette, left_label, right_label):
        width = max(1, canvas.winfo_width())
        title_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        label_font = tkfont.Font(family="Segoe UI", size=8)
        title_height = title_font.metrics("linespace")
        label_height = label_font.metrics("linespace")
        height = title_height + label_height + 42
        key = (width, height, title, left_label, right_label)
        if getattr(canvas, "legend_key", None) == key:
            return
        canvas.legend_key = key
        canvas.configure(height=height)
        canvas.delete("all")
        bar_left = 2
        bar_right = max(bar_left + 12, width - 8)
        bar_top = title_height + 14
        bar_bottom = bar_top + 16

        canvas.create_text(
            0,
            7,
            anchor="nw",
            text=title,
            fill="#dce7ef",
            font=("Segoe UI", 9, "bold"),
        )
        canvas.create_text(
            0,
            bar_bottom + 8,
            anchor="nw",
            text=left_label,
            fill="#7f92a4",
            font=("Segoe UI", 8),
        )
        canvas.create_text(
            width - 2,
            bar_bottom + 8,
            anchor="ne",
            text=right_label,
            fill="#7f92a4",
            font=("Segoe UI", 8),
        )

        samples = np.linspace(0.0, 1.0, bar_right - bar_left)
        colors = apply_colormap(samples, palette)

        for offset, color in enumerate(colors):
            x = bar_left + offset
            fill = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            canvas.create_line(x, bar_top, x, bar_bottom, fill=fill)

        canvas.create_rectangle(
            bar_left,
            bar_top,
            bar_right - 1,
            bar_bottom,
            outline="#344658",
        )

    def update_status(self, actual_fps, frame_time):
        self.last_actual_fps = actual_fps
        self.last_frame_time = frame_time
        nx, ny = self.grid_size()
        status = (
            f"{actual_fps:.1f} FPS   "
            f"Frame {self.frame_count}   "
            f"{self.object_var.get()}   "
            f"Grid {nx} x {ny}"
        )
        self.status_var.set(status)
        self.sidebar_status.set(status)
        self.update_top_metrics(actual_fps, frame_time)


def main():
    enable_high_dpi_rendering()
    root = tk.Tk()
    WindTunnelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
