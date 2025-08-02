# Cartesian Fruit-Picking Robot

### A Project by CPP Robotics Club  
**Goal:** Reduce agricultural waste by automating accurate and efficient produce picking.

---

## Project Overview

Every year, significant amounts of fruits go to waste due to inefficient produce picking. Our project addresses this issue by developing a **Cartesian robot** capable of autonomously identifying and picking ripe produce using:

- **Dual-camera** visual localization  
- A **Monte Carlo optimization algorithm** for target convergence  
- Fast and accurate **stepper motors**
- **Custom end effector** to pick each fruit accurately 

---

## Repository Contents

This repository includes everything needed to understand, replicate, and improve upon the project:

- `/code` — All source code, including the Monte Carlo control algorithm and camera processing scripts  
- `/cad` — Full CAD assemblies, individual part files, and previous iterations  
- `/bom` — Bill of Materials

---

## System Architecture

### 1. **Robot Design**
- **3-axis Cartesian system** for predictable linear motion  
- Custom end effector that cuts at the stem   
- **Modular** build using **low-cost materials**

### 2. **Vision System**
- Two RGB cameras provide **stereo** vision  
- **OpenCV** image processing to detect fruit centers

### 3. **Control Algorithm**
- Monte Carlo method used for iterative movement refinement  
- Robot converges on optimal gripper pose through probabilistic sampling  
- Tolerant to vision and motion errors

---

## Getting Started

### Prerequisites
- Python 3.9+  
- OpenCV  
- NumPy  
- 3D printer

### Build Instructions
- Find the Final Assembly file
- Cut all aluminium extrusions and belts to size defined in the assembly
- Attach supporting brackets and plates to the frame 
- Print all components found in the assembly that are not aluminium 
- Assemble motor carriage
  - Assemble the Z Axis 
  - Assemble the Y Axis
  - Attach the Z Axis to the Y Axis
  - Assemble the X Axis
  - Attach the YZ Axis assembly to the X Axis
  - Attach the XYZ Axis assembly to the frame
- Solder limit switches and attach to frame with adhesive
- Assemble and attach the claw
- Assemble and attach the Camera Mount 

### Code Setup Instructions

```bash
git clone https://github.com/harrisonchung06/GrowBot.git
cd code
pip install -r requirements.txt
python main.py
```
