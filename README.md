# Interactive-FDTD-Material-Explorer
Team: shanmukhakumar   Members: BURUSU SHANMUKHA KUMAR, MOHAMMED SHAIK, SHARLI NELATURI     
RUN INSTRUCTIONS      
1.pip install numpy matplotlib

2.python fdtd_interactive.py


Window: 1200×700 with 3 sliders (left) + live plot (right)

Simulation CONTROLS
  Slider      Range    Effect 
  Glass εr    1-9      Slows wave 
  Water σ    0-1 S/m   Absorbs energy 
  Water εr    1-15     Slows in water 

LAYOUT
Cells 0-99: Vacuum
Cells 100-249: GLASS ← User εr
Cells 250-349: WATER ← User εr, σ
Cells 350-399: Vacuum
SOURCE: Cell 50 (1.5 GHz pulse)

WHAT YOU SEE
1. Pulse launches cell 50 → moves right
2. Slows in green glass region  
3. Decays in blue water region
4. Drag sliders →  instant change
SPECS
- Grid: 400×0.8mm = 32cm domain
- Source: 1.5 GHz modulated pulse
- Time step: CFL stable (dt=dx/(2c))
- FPS: 33 (30ms/frame)

TESTED
- Python 3.11.9 (Windows)
- No additional setup needed
