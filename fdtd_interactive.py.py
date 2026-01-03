import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import Scale, HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ============================================================================
# PART 1: PHYSICAL CONSTANTS (EM Wave Physics)
# ============================================================================

c = 3e8                           # Speed of light (m/s)
mu0 = 4*np.pi*1e-7              # Permeability of free space (H/m)
eps0 = 8.854e-12                # Permittivity of free space (F/m)

# ============================================================================
# PART 2: SIMULATION GRID SETUP
# ============================================================================

Nx = 400                         # Number of cells (space discretization)
dx = 0.8e-3                      # Cell size: 0.8 mm
dt = dx/(2*c)                    # Time step (CFL stability condition)
Nt = 500                         # Number of time steps (500 frames)

# ============================================================================
# PART 3: FIELD ARRAYS (Electromagnetic Fields)
# ============================================================================

Ez = np.zeros(Nx)                # Electric field (E_z component) - 400 values
Hy = np.zeros(Nx)                # Magnetic field (H_y component) - 400 values

# ============================================================================
# PART 4: MATERIAL PROPERTIES (Will Change with Sliders!)
# ============================================================================

eps_r = np.ones(Nx)              # Relative permittivity (starts as air: 1.0)
sigma = np.zeros(Nx)             # Conductivity (0 = no loss initially)
eps = eps0 * eps_r               # Absolute permittivity

# ============================================================================
# PART 5: SOURCE FUNCTION (1.5 GHz Pulse)
# ============================================================================

def source(t, f0=1.5e9):
    """
    Creates a realistic electromagnetic pulse
    
    Two parts:
    1. Envelope: Gaussian pulse (smooth bell curve)
    2. Carrier: 1.5 GHz sine wave (oscillation)
    
    Result: Modulated pulse (like real radar signal)
    """
    t0 = 25                       # Pulse starts at t0
    sigma_t = 8                   # Width of pulse
    
    # Part 1: Envelope (makes pulse turn on/off smoothly)
    envelope = np.exp(-((t-t0)/sigma_t)**2)   # e^(-(t-25)²/64)
    
    # Part 2: Carrier (1.5 GHz oscillation)
    carrier = np.sin(2*np.pi*f0*t*dt)         # sin(2π × 1.5e9 × t × dt)
    
    # Multiply them: smooth modulated pulse
    return envelope * carrier

# ============================================================================
# PART 6: COEFFICIENT UPDATE (Pre-compute for Speed)
# ============================================================================

def update_coefficients():
    """
    These coefficients handle material properties in FDTD equations.
    
    ca = damping factor (how much old field survives)
    cb = curl coefficient (how much new field is created)
    
    In vacuum (σ=0): ca=1, cb=dt/(ε₀×dx)
    In lossy media (σ>0): ca<1 (energy absorbed), cb changes
    """
    global ca, cb, eps
    
    eps = eps0 * eps_r            # Update permittivity with new ε_r
    
    ca = np.ones(Nx)              # Start with all 1's (no loss)
    cb = np.ones(Nx)              # Curl coefficient
    
    # Find cells with conductivity (lossy material)
    mask = sigma > 0
    
    # Apply lossy media formula (from Maxwell's equations)
    ca[mask] = (1 - sigma[mask]*dt/(2*eps[mask])) / (1 + sigma[mask]*dt/(2*eps[mask]))
    cb[mask] = dt/(eps[mask]*dx) / (1 + sigma[mask]*dt/(2*eps[mask]))

# ============================================================================
# PART 7: TKINTER GUI SETUP (Windows & Sliders)
# ============================================================================

# Create main window
root = tk.Tk()
root.title("Interactive FDTD Material Explorer")      # Window title
root.geometry("1200x700")                             # Window size (width x height)

# ============================================================================
# PART 8: LEFT PANEL - SLIDERS (for changing materials)
# ============================================================================

# Create frame (container) on left side
frame_sliders = tk.Frame(root)
frame_sliders.pack(side=tk.LEFT, padx=10, pady=10)

# ========== SLIDER 1: Glass Permittivity ==========
tk.Label(frame_sliders, text="GLASS SLAB", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(Change how slow glass is)", font=("Arial", 9)).pack()

slider_eps = Scale(
    frame_sliders,                    # Put slider in this frame
    from_=1,                          # Minimum value: 1 (air)
    to=9,                             # Maximum value: 9 (diamond)
    orient=HORIZONTAL,                # Horizontal slider (left-right)
    label="Glass ε_r (refractive index)"  # Label text
)
slider_eps.set(4)                    # Start at 4 (regular glass)
slider_eps.pack()

# ========== SLIDER 2: Water Conductivity (Loss) ==========
tk.Label(frame_sliders, text="WATER LAYER", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(How much water absorbs energy)", font=("Arial", 9)).pack()

slider_sigma = Scale(
    frame_sliders,
    from_=0,                          # No loss
    to=1,                             # High loss (seawater)
    orient=HORIZONTAL,
    label="Water σ (conductivity, S/m)",
    resolution=0.01                   # Slider precision
)
slider_sigma.set(0.15)               # Start at 0.15 (regular water)
slider_sigma.pack()

# ========== SLIDER 3: Water Permittivity ==========
tk.Label(frame_sliders, text="WATER ε_r", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(How slow water slows wave)", font=("Arial", 9)).pack()

slider_eps_water = Scale(
    frame_sliders,
    from_=1,                          # Minimum
    to=15,                            # Maximum
    orient=HORIZONTAL,
    label="Water ε_r"
)
slider_eps_water.set(4)              # Start at 4 (salt water ~ 4)
slider_eps_water.pack()

# Info text
tk.Label(frame_sliders, text="\n--- INSTRUCTIONS ---", font=("Arial", 10, "bold")).pack()
tk.Label(frame_sliders, text="Drag sliders →\nWatch wave change instantly!\n", 
         font=("Arial", 9), justify=tk.LEFT).pack()

# ============================================================================
# PART 9: RIGHT PANEL - MATPLOTLIB PLOT
# ============================================================================

# Create matplotlib figure (graph)
fig, ax = plt.subplots(figsize=(8, 6))

# Embed matplotlib in tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Setup plot
line, = ax.plot(Ez, 'b-', lw=2)       # Blue line for electric field
ax.set_ylim(-1.5, 1.5)                # Y-axis limits
ax.set_xlim(0, Nx)                    # X-axis limits
ax.set_ylabel('Electric Field Ez (V/m)', fontsize=12)
ax.set_xlabel('Space (cell index)', fontsize=12)
ax.grid(True, alpha=0.3)              # Grid lines

# Add colored background regions
ax.axvspan(100, 250, alpha=0.1, color='green', label='Glass slab')
ax.axvspan(250, 350, alpha=0.1, color='blue', label='Water layer')
ax.legend(loc='upper right')

# ============================================================================
# PART 10: FDTD SIMULATION LOOP (Main Physics Update)
# ============================================================================

frame_count = 0                        # Counter for animation frames

def update(framedata):
    """
    This function runs EVERY FRAME (30ms):
    1. Read slider values
    2. Update material properties
    3. Perform FDTD calculation
    4. Update plot
    5. Loop again
    """
    global Ez, Hy, frame_count, eps_r, sigma, ca, cb
    
    frame_count += 1
    
    # ========== STEP 1: Read Sliders (Live Material Change!) ==========
    
    # Glass region (cells 100-250): User sets ε_r via slider
    eps_r[100:250] = slider_eps.get()
    
    # Water region (cells 250-350): User sets ε_r via slider
    eps_r[250:350] = slider_eps_water.get()
    
    # Water region: User sets conductivity (loss) via slider
    sigma[250:350] = slider_sigma.get()
    
    # Glass is lossless (no conductivity)
    sigma[100:250] = 0
    
    # ========== STEP 2: Update Coefficients ==========
    # Recalculate ca, cb based on new material properties
    update_coefficients()
    
    # ========== STEP 3: FDTD Update (Maxwell's Equations) ==========
    
    # *** PART A: Update Magnetic Field Hy ***
    # Physics: ∂H_y/∂t = (1/μ₀) × ∂E_z/∂z
    # Difference: E_z[i+1] - E_z[i] = ∂E_z/∂z
    
    Hy[0:Nx-1] += (dt/(mu0*dx)) * (Ez[1:Nx] - Ez[0:Nx-1])
    
    # *** PART B: Update Electric Field Ez ***
    # Physics: ∂E_z/∂t = (1/ε) × ∂H_y/∂z - (σ/ε) × E_z
    # Difference: H_y[i] - H_y[i-1] = ∂H_y/∂z
    
    dHy_dx = Hy[1:Nx] - Hy[0:Nx-1]  # Magnetic field gradient
    Ez[1:Nx-1] = ca[1:Nx-1] * Ez[1:Nx-1] + cb[1:Nx-1] * dHy_dx[0:Nx-2]
    
    # ========== STEP 4: Inject Source Pulse ==========
    # Add Gaussian-modulated 1.5 GHz pulse at cell 50
    Ez[50] += 1.5 * source(frame_count)
    
    # ========== STEP 5: Boundary Conditions ==========
    # Zero field at edges (free space boundary)
    Ez[0] = 0
    Ez[Nx-1] = 0
    
    # ========== STEP 6: Update Plot ==========
    
    # Update line data (y-values)
    line.set_ydata(Ez)
    
    # Create dynamic title showing current slider values
    glass_str = f"Glass ε_r={slider_eps.get()}"
    water_str = f"Water (ε_r={slider_eps_water.get()}, σ={slider_sigma.get():.2f} S/m)"
    time_str = f"t={frame_count*dt*1e9:.0f}ns"
    
    ax.set_title(
        f'FDTD Explorer | {glass_str} | {water_str} | {time_str}', 
        fontsize=11, 
        fontweight='bold'
    )
    
    # Redraw plot (without blocking GUI)
    canvas.draw_idle()
    
    # ========== STEP 7: Schedule Next Frame ==========
    # Loop every 30ms (gives animation effect)
    root.after(30, lambda: update(frame_count))

# ============================================================================
# PART 11: START THE APPLICATION
# ============================================================================

# First update at startup
root.after(100, lambda: update(0))

# Run GUI event loop (keeps window open until you close it)
root.mainloop()