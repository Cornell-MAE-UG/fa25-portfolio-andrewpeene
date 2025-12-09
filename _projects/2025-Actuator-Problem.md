---
layout: project
title: Actuator Problem
description: 
technologies: []
image: /assets/images/2020portfolio-load.png
---


# Actuator Height/Weight Optimization Problem

![Main mechanism image](/assets/images/2020portfolio-load.png)

Write a short paragraph here describing the design task:
- Mention the fixed 2D design space
- Mention rigid bar, three pin supports, and a catalog linear actuator
- Mention goals: lift as much weight as possible to the highest height

Add a second paragraph summarizing:
- How the bar is pinned
- How the actuator is pinned and how it applies force
- How geometry and stroke limits restrict motion and achievable height

![Rendering of design](/assets/images/2020portfolio-load.png)

Write another paragraph here describing:
- The actuator model you chose (manufacturer, model)
- Why it was chosen (peak thrust, stroke length, housing size)
- How the actuator fits inside the design box and what limits the positions

Add a paragraph summarizing your statics approach:
- Moment balance about the ground pin
- How bar angle affects required actuator force
- How actuator angle and projection of forces determine the max liftable weight

Conclude this intro section with:
- What you learned (using datasheets, balancing constraints, integrating geometry, etc.)

---

# Actuator Problem Portfolio Update

## Step 1: Rigid Bar Analysis

### a) Problem Definition, Constraints/Objectives, Degrees of Freedom

**Problem Definition:**  
Describe in your own words the task of designing a mechanism that uses an actuator and a rigid bar to lift a load through some displacement.

**Constraints (example bullets – customize):**

- Must support the applied load without excessive deformation.
- Actuator must operate within its stroke limits.
- Mechanism geometry must stay within the assigned design envelope.

**Objectives (example):**

- Achieve the required output displacement.
- Minimize required actuator force.
- Keep mechanism simple and light.

**Degrees of Freedom (DOF):**  
Explain that your mechanism effectively has one degree of freedom driven by the actuator (e.g., bar rotation about a pin).

---

### b) Static Analysis of the Rigid Bar

Describe your static analysis process:

- Summation of forces and moments about the pivot.
- Relationship between actuator force and external load.
- Geometric relations between actuator length, bar angle, and output position.

Summarize the final rigid-bar configuration you chose and why it meets the constraints.

---

### c) Final Rigid Mechanism Design

![Final rigid mechanism rendering](/assets/images/2020portfolio-dist-load.png)

Add a short paragraph explaining what this figure shows:
- Pin locations
- Actuator configuration at some key position
- Any important geometric dimensions

---

## Step 2: Beam (Flexible Bar) Analysis

### a) Maximum Beam Deflection

Explain that once you consider flexibility, the bar behaves as a beam subjected to transverse forces:

1. The load being lifted  
2. The transverse component of the actuator force  

List your assumptions (edit as needed):

- Prismatic, linearly elastic beam
- Small-deflection Euler–Bernoulli beam theory
- Only transverse loading considered

You can keep standard formulas here. For example:

For a cantilever with tip load \(F\):

```text
δ_max = (F * L^3) / (3 * E * I)
