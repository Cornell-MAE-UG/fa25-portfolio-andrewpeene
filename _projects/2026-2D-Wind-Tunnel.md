---
layout: project
title: 2D Wind Tunnel
description: A self-directed fluid simulation built to connect classroom fluid mechanics with numerical modeling and programming.
date: 2026-09-12
image: /assets/images/2dtunnelflow.png
imagealt: Velocity field and vortex wake behind an airfoil in the 2D Wind Tunnel
hero_caption: Velocity magnitude and the developing vortex wake behind an airfoil.
wide_hero: true
tags: [Fluid Mechanics, Numerical Methods, Computational Engineering]
technologies: [Python, NumPy, D2Q9 Lattice Boltzmann Method, AI-Assisted Development]
---

## Project Overview

The **2D Wind Tunnel** is a self-directed fluid simulation I built while taking Intro to Fluid Mechanics. It turns equations and flow concepts from class into an interactive experiment: I can place a shape in a computational wind tunnel, change the flow and geometry, and watch the velocity field and wake develop in real time.

The project gave me a practical way to strengthen three skills at once: building intuition for fluid behavior, learning the numerical methods behind computational fluid dynamics, and becoming a more capable programmer. It also became an opportunity to learn how to use AI effectively during engineering development without treating it as a substitute for understanding or verification.

<div class="project-download">
  <h3>Run the Wind Tunnel</h3>
  <p>Download the complete Python source code, pinned dependencies, and setup instructions to experiment with the simulation on your own computer.</p>
  <a class="download-button" href="{{ '/assets/downloads/2d-wind-tunnel.zip' | relative_url }}" download>Download 2D Wind Tunnel (.zip)</a>
  <p class="download-note">Requires Python 3.11 or newer. This is an educational visualization tool, not validated CFD software.</p>
</div>

<figure class="project-figure">
  <img src="{{ '/assets/images/2dtunnelui.png' | relative_url }}" alt="2D Wind Tunnel interface showing velocity flow around a NACA 4412 airfoil at negative twelve degrees angle of attack">
  <figcaption>The running desktop interface combines geometry and flow controls with live velocity visualization, simulation status, and performance data.</figcaption>
</figure>

## Motivation

In Intro to Fluid Mechanics, many ideas begin as equations, diagrams, and idealized examples. Those tools are essential, but I wanted a stronger visual and intuitive understanding of what the equations describe. Building a simulation let me go beyond solving for a single answer on paper: I could change a condition, observe how the flow responded, and connect that response back to concepts such as velocity, viscosity, Reynolds number, pressure effects, separation, and wake formation.

I also wanted a project that would push my coding ability. A real-time numerical simulation demands more than writing a script that produces one result; it requires organizing a program, managing a user interface, updating and visualizing a large state efficiently, and diagnosing behavior that may come from either the code or the model. AI supported that process as a learning and development tool, while I remained responsible for understanding the method, checking the logic, and deciding whether each result was physically reasonable.

## Technical Approach

The simulation uses the **D2Q9 Lattice Boltzmann Method (LBM)**. Instead of directly solving the conventional fluid equations at every point, LBM represents the fluid using nine particle distribution functions at each cell of a two-dimensional grid: one stationary population and eight populations aligned with the grid axes and diagonals.

Each simulation step has two main operations:

1. **Collision:** The nine distributions within each cell relax toward a local equilibrium determined by the cell's density and velocity. The relaxation rate controls the model's kinematic viscosity.
2. **Streaming:** The updated distributions move to neighboring grid cells along their corresponding lattice directions.

Repeating these local operations across the grid produces larger flow structures. Density and velocity are recovered from the distributions and converted into the color field and directional traces shown on screen. This makes the method computationally approachable while still producing recognizable effects such as accelerated flow, separated wakes, and vortex shedding.

Solid objects are represented by a mask on the computational grid. When a distribution reaches a solid cell, a bounce-back rule reverses its direction, approximating a no-slip wall and transferring momentum between the flow and the object. Inlet and outlet rules maintain the wind-tunnel flow, while the outer boundaries keep the domain numerically controlled. Changing the selected geometry, size, or angle rebuilds the solid mask so the same solver can test an airfoil, circle, rectangle, or more detailed circular geometry.

<figure class="project-figure">
  <img src="{{ '/assets/images/2dtunnelvortex2.png' | relative_url }}" alt="Velocity field showing alternating vortices downstream of an airfoil">
  <figcaption>A resolved wake makes the numerical process tangible: local collision and streaming operations combine into an alternating downstream vortex pattern.</figcaption>
</figure>

## AI-Assisted Development Process

I used AI throughout the project as a **learning, debugging, and development tool**, not as a way to bypass the engineering. Early in the project, it helped me break an unfamiliar numerical method into smaller ideas, compare explanations of D2Q9 LBM, and identify which parts of the theory needed further study. During implementation, I used it to discuss alternative data structures, interpret errors, isolate unstable behavior, and generate possible explanations for performance bottlenecks.

The most valuable part of this process was learning to treat AI suggestions as hypotheses. I traced proposed changes through the collision and streaming logic, checked dimensions and boundary behavior, compared outputs before and after changes, and rejected solutions I could not justify. This made iteration faster while keeping the physics and program logic understandable to me. It also showed me that effective AI-assisted engineering depends on asking precise questions, supplying useful context, testing recommendations, and maintaining independent judgment.

## Features and Design Iterations

The project grew from a basic solver and plot into an interactive desktop flow lab. Its current features include:

- Selectable airfoil, circle, rectangle, and golf-ball-inspired geometries
- Adjustable object size and angle of attack
- Real-time velocity-field and flow-direction visualization
- Lift and drag indicators for comparing how the flow loads each object
- Interactive run, pause, and single-step controls
- Adjustable inlet speed, Reynolds number, Mach-number reference, and simulation steps per frame
- Live frame count, timestep, and FPS monitoring

<figure class="project-figure">
  <img src="{{ '/assets/images/2dtunnelgolfball.png' | relative_url }}" alt="2D Wind Tunnel interface simulating flow past a golf-ball-inspired circular geometry">
  <figcaption>The golf-ball-inspired geometry visibly disrupts the surrounding flow. Its dimples disturb the boundary layer so it can remain attached farther around the ball, reducing the size of the separated wake and therefore reducing pressure drag compared with a smooth sphere.</figcaption>
</figure>

The visualization also evolved as I learned what made a result useful. A single color field could show local speed, but directional traces and vortex-sensitive views made separation and wake behavior much easier to interpret. Controls were consolidated into the interface so experiments could be repeated without editing source values between runs.

<figure class="project-figure">
  <img src="{{ '/assets/images/2dtunnelvortex.png' | relative_url }}" alt="Close view of a vortex forming behind an airfoil in the 2D Wind Tunnel">
  <figcaption>A close view of the airfoil wake highlights recirculation near the trailing edge and the formation of downstream vortices.</figcaption>
</figure>

## Challenges and What I Learned

Performance became one of the clearest connections between numerical theory and software design. Increasing grid resolution or object detail increases the number of distribution values that must collide, stream, satisfy boundary rules, and be visualized every frame. Some configurations fell to very low FPS; the golf-ball screenshot, for example, records 1.1 FPS, while the smaller airfoil case records 25.6 FPS. That gap pushed me to learn more about NumPy vectorization, memory access, array allocation, numerical efficiency, and the cost of rendering in addition to computation.

This also showed me where Python is effective and where a compiled implementation may help. A future version could keep Python for the interface and experimentation while moving the most computationally intensive solver operations to C or C++. More broadly, I learned that a theoretically correct equation is only one part of a simulation. Grid resolution, boundary approximations, stability limits, units, visualization choices, and performance all affect what can be calculated and what conclusions can reasonably be drawn.

<figure class="project-figure">
  <img src="{{ '/assets/images/2dtunnelflow.png' | relative_url }}" alt="Wide velocity visualization showing the wake developing downstream of an airfoil">
  <figcaption>The full wake view helped me connect changes near the airfoil to flow structures that continue far downstream.</figcaption>
</figure>

## Future Development

The next stage is to make the simulator faster and more quantitative. Planned improvements include:

- Profiling the solver and visualization separately, then optimizing the dominant bottlenecks
- Evaluating compiled C/C++ routines or another accelerated backend for collision and streaming
- Calculating dimensionless lift and drag coefficients rather than relying only on qualitative indicators
- Validating results against analytical solutions, published airfoil data, and known vortex-shedding behavior
- Improving airfoil geometry and curved-wall boundary treatment
- Adding pressure, vorticity, streamline, and time-history visualization options
- Exploring more advanced flow behavior as the solver's stability and performance improve

The long-term goal is not simply to add more controls. It is to develop a simulation whose behavior I can explain, test, and compare against established fluid-mechanics results—and to keep using the project as a bridge between classroom theory and engineering computation.
