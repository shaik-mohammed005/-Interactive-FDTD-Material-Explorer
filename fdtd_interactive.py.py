import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import Scale, HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

c = 3e8
mu0 = 4*np.pi*1e-7
eps0 = 8.854e-12

Nx = 400
dx = 0.8e-3
dt = dx/(2*c)
Nt = 500

Ez = np.zeros(Nx)
Hy = np.zeros(Nx)

eps_r = np.ones(Nx)
sigma = np.zeros(Nx)
eps = eps0 * eps_r

def source(t, f0=1.5e9):
    t0 = 25
    sigma_t = 8
    
    envelope = np.exp(-((t-t0)/sigma_t)**2)
    carrier = np.sin(2*np.pi*f0*t*dt)
    
    return envelope * carrier

def update_coefficients():
    global ca, cb, eps
    
    eps = eps0 * eps_r
    
    ca = np.ones(Nx)
    cb = np.ones(Nx)
    
    mask = sigma > 0
    
    ca[mask] = (1 - sigma[mask]*dt/(2*eps[mask])) / (1 + sigma[mask]*dt/(2*eps[mask]))
    cb[mask] = dt/(eps[mask]*dx) / (1 + sigma[mask]*dt/(2*eps[mask]))

root = tk.Tk()
root.title("Interactive FDTD Material Explorer")
root.geometry("1200x700")

frame_sliders = tk.Frame(root)
frame_sliders.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(frame_sliders, text="GLASS SLAB", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(Change how slow glass is)", font=("Arial", 9)).pack()

slider_eps = Scale(
    frame_sliders,
    from_=1,
    to=9,
    orient=HORIZONTAL,
    label="Glass ε_r (refractive index)"
)
slider_eps.set(4)
slider_eps.pack()

tk.Label(frame_sliders, text="WATER LAYER", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(How much water absorbs energy)", font=("Arial", 9)).pack()

slider_sigma = Scale(
    frame_sliders,
    from_=0,
    to=1,
    orient=HORIZONTAL,
    label="Water σ (conductivity, S/m)",
    resolution=0.01
)
slider_sigma.set(0.15)
slider_sigma.pack()

tk.Label(frame_sliders, text="WATER ε_r", font=("Arial", 12, "bold")).pack()
tk.Label(frame_sliders, text="(How slow water slows wave)", font=("Arial", 9)).pack()

slider_eps_water = Scale(
    frame_sliders,
    from_=1,
    to=15,
    orient=HORIZONTAL,
    label="Water ε_r"
)
slider_eps_water.set(4)
slider_eps_water.pack()

tk.Label(frame_sliders, text="\n--- INSTRUCTIONS ---", font=("Arial", 10, "bold")).pack()
tk.Label(frame_sliders, text="Drag sliders →\nWatch wave change instantly!\n", 
         font=("Arial", 9), justify=tk.LEFT).pack()

fig, ax = plt.subplots(figsize=(8, 6))

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

line, = ax.plot(Ez, 'b-', lw=2)
ax.set_ylim(-1.5, 1.5)
ax.set_xlim(0, Nx)
ax.set_ylabel('Electric Field Ez (V/m)', fontsize=12)
ax.set_xlabel('Space (cell index)', fontsize=12)
ax.grid(True, alpha=0.3)

ax.axvspan(100, 250, alpha=0.1, color='green', label='Glass slab')
ax.axvspan(250, 350, alpha=0.1, color='blue', label='Water layer')
ax.legend(loc='upper right')

frame_count = 0

def update(framedata):
    global Ez, Hy, frame_count, eps_r, sigma, ca, cb
    
    frame_count += 1
    
    eps_r[100:250] = slider_eps.get()
    eps_r[250:350] = slider_eps_water.get()
    sigma[250:350] = slider_sigma.get()
    sigma[100:250] = 0
    
    update_coefficients()
    
    Hy[0:Nx-1] += (dt/(mu0*dx)) * (Ez[1:Nx] - Ez[0:Nx-1])
    
    dHy_dx = Hy[1:Nx] - Hy[0:Nx-1]
    Ez[1:Nx-1] = ca[1:Nx-1] * Ez[1:Nx-1] + cb[1:Nx-1] * dHy_dx[0:Nx-2]
    
    Ez[50] += 1.5 * source(frame_count)
    
    Ez[0] = 0
    Ez[Nx-1] = 0
    
    line.set_ydata(Ez)
    
    glass_str = f"Glass ε_r={slider_eps.get()}"
    water_str = f"Water (ε_r={slider_eps_water.get()}, σ={slider_sigma.get():.2f} S/m)"
    time_str = f"t={frame_count*dt*1e9:.0f}ns"
    
    ax.set_title(
        f'FDTD Explorer | {glass_str} | {water_str} | {time_str}', 
        fontsize=11, 
        fontweight='bold'
    )
    
    canvas.draw_idle()
    
    root.after(30, lambda: update(frame_count))

root.after(100, lambda: update(0))
root.mainloop()
