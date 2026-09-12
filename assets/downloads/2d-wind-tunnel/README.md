# 2D Wind Tunnel

This download contains the Python source code for Andrew Peene's educational 2D fluid-flow visualizer. It uses a D2Q9 lattice-Boltzmann solver and a Tkinter desktop interface.

The simulator is intended for learning and visualization. It has not been validated for engineering design or safety-critical calculations.

## Requirements

- Python 3.11 or newer
- A desktop environment with Tkinter
- NumPy, Numba, and Pillow (installed from `requirements.txt`)

Tkinter is included with standard Python installations on Windows and macOS. Some Linux distributions require a separate package such as `python3-tk`.

## Install and run

Open a terminal in this folder, then create an isolated Python environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The first simulation run may pause briefly while Numba compiles the accelerated solver.

## Using the simulation

- Choose an object geometry from the **Shape** menu.
- Adjust its angle, size, inlet speed, Reynolds number, and grid quality.
- Switch between velocity-magnitude and vorticity views.
- Use **Run**, **Pause**, and **Step** to control the simulation.

For best performance, begin with the **Fast preview** or **Balanced** grid preset.
