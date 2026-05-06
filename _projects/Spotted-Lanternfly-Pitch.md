---
layout: project
title: "MAE 2250: Spotted Lanternfly Removal"
description: "A semester-long mechanical design project developing a contactless suction device to remove spotted lanternflies from grapevines."
date: 2026-02-21
image: /assets/images/SLF.jpg
imagealt: "Spotted lanternfly on a surface"
tags: [Mechanical Design, Mechanical Engineering, Concept Development]
technologies: [Fusion 360, Prototyping, Mechanical Testing, Design Validation]
---

This MAE 2250 project developed a mechanical removal method for spotted lanternflies (SLF) in grape vineyards. Our team, The Grape, worked from an initial client pitch through functional prototyping and a final client report for stakeholders connected to Cornell CALS Extension, E&J Gallo Winery, and National Grape.

The central design challenge was removing SLF from grapevines without damaging vines, contaminating grapes, or relying on chemical pesticides that are ineffective against SLF and may harm grape plants.

<style>
  .milestone-accordion {
    clear: both;
    margin: 2rem 0;
  }

  .milestone-accordion details {
    border: 1px solid #d8dbe3;
    border-radius: 8px;
    margin-bottom: 0.75rem;
    background: #fff;
    overflow: hidden;
  }

  .milestone-accordion summary {
    cursor: pointer;
    padding: 0.9rem 1rem;
    font-family: "Merriweather", serif;
    font-weight: 700;
    color: #3a3f58;
    background: #f7f8fa;
  }

  .milestone-accordion summary:hover {
    background: #eef0f5;
  }

  .milestone-accordion details[open] summary {
    border-bottom: 1px solid #d8dbe3;
  }

  .milestone-content {
    padding: 1rem;
  }

  .milestone-content > :first-child {
    margin-top: 0;
  }

  .milestone-content > :last-child {
    margin-bottom: 0;
  }
</style>



<div class="milestone-accordion">

<details id="client-pitch" markdown="1">
<summary>Client Pitch</summary>
<div class="milestone-content" markdown="1">

**Deliverable:** [Client Outline and Pitch PDF]({{ '/assets/Client-Outline-and-Pitch.pdf' | relative_url }})

The client pitch defined the problem as a grape production and harvest contamination issue. Even a small number of SLF in a harvested grape sample can contaminate a batch, while feeding damage from SLF can reduce vine health, shorten vine lifespan, and lower yield.

Our early problem framing focused on the risks of common removal methods:

- Physical contact methods such as brushes or grippers could damage vines or grapes.
- Killing SLF while they are still on the vine could expose grapes to contaminants from insect remains.
- Chemical pesticide strategies were not considered reliable enough for SLF and could introduce additional plant-health risks.
- Manual removal would be too slow and labor-intensive for vineyard-scale use.

The pitch proposed two possible solution directions. The first was a suction-based attachment that could mount to vineyard equipment and remove SLF into a capture chamber before grapes are harvested. The second was a decoy device that would attract SLF away from grape plants using lures such as scent, shape, light, or vibration, then capture or eliminate them.

We selected the suction-device path as the stronger direction because it aligned more directly with existing vineyard operations. A tractor- or harvester-mounted device could be used during regular vineyard passes, reducing labor while avoiding direct mechanical contact with the plants.

</div>
</details>

<details id="functional-prototype" markdown="1">
<summary>Functional Prototype</summary>
<div class="milestone-content" markdown="1">

**Deliverable:** [The Grape Poster PDF]({{ '/assets/The%20Grape%20Poster%20%2836%20x%2048%20in%29.pdf' | relative_url }})

The functional prototype translated the pitch direction into a suction device for contactless SLF removal. The goal was to capture adult spotted lanternflies during grape growth periods without significantly damaging grape plants.

The prototype used four main design elements:

- A motor and impeller to generate suction.
- A shaped intake cone to guide airflow and draw SLF toward the device.
- A mesh filter to separate insects and debris from the airflow path.
- A collection chamber to hold captured SLF.

The design evolved from an early rectangular-cone prototype to a more compact circular intake geometry. The first prototype showed that a suction approach was plausible, but it also revealed major weaknesses: the propeller did not generate enough suction, the rectangular cone did not provide useful vertical coverage, and the intermediate crush box disrupted airflow.

The refined prototype replaced the propeller with an impeller and motor casing to increase the pressure differential and improve suction. It also added aluminum mesh to prevent debris from reaching the blade and to redirect captured material into a storage area. A custom mounting case was included so the device could be attached to a tractor or harvester.

The prototype was tested for endurance, debris tolerance, and mounting strength. It operated continuously for 30 minutes without a performance drop, captured debris without visible internal damage, and supported 500 g of added mass at the mounting geometry without structural failure. These results supported the mechanical feasibility of the concept, while also showing that suction strength and intake geometry needed more refinement.

</div>
</details>

<details id="client-report" markdown="1">
<summary>Client Report</summary>
<div class="milestone-content" markdown="1">

**Deliverable:** [ODP 6 Exhibit and Client Report PDF]({{ '/assets/ODP%206_%20Exhibit%20and%20Client%20Report.pdf' | relative_url }})

The final client report presented the proposed solution as a suction-based attachment for removing spotted lanternflies from grapevines. The device uses a motor-driven impeller to generate localized airflow, pulling insects from the vine into a collection chamber. It is intended to mount to harvesting equipment during harvest season or to vineyard tractors during the off-season.

### How the Device Works

The device removes SLF through suction rather than direct physical contact. Airflow draws insects into the intake while an aluminum mesh filter separates debris such as small sticks or accidental grapes from the motor and blade path. The collection chamber stores captured insects so they can be removed away from the grapevine.

This approach is meant to reduce the chance of grape damage, vine damage, and contamination from SLF remains. It also fits the client need for a system that can integrate into existing agricultural routines instead of requiring a separate manual removal process.

### Testing Results

The final report documented several validation tests:

- **Longevity:** The device ran continuously for 30 minutes with no observed drop in performance.
- **Debris tolerance:** Test materials between 1-5 cm in diameter and 1-10 g in mass did not visibly damage the fan or internal casing, though some heavier debris above 5 g became trapped before reaching the storage container.
- **Mounting load:** The mounting geometry supported 500 g of added mass, roughly equivalent to 2,000 adult SLF, without structural damage or failure.
- **Nozzle distance:** The device collected paper model SLF at distances between 1.0 cm and 2.5 cm, with a mean collection distance of 1.7185 cm.

The nozzle-distance test was the most important limitation. In its current form, the device needs to be very close to the vine to collect SLF effectively. That result suggests that the suction strength must increase before the device can reliably avoid contact with grapevines in field use.

### Cost and Practical Value

The estimated unit cost of the prototype was **$102.99**, including the handheld vacuum components, aluminum filter mesh, 3D-printed PLA housing, nuts, and bolts. The report compared this to recurring crop spraying costs of approximately **$15-$22 per acre**, not including the cost of chemical pesticide in many cases.

Although the device has a higher upfront cost than a single spray application, it offers a reusable, targeted, contactless, and non-chemical removal method. Over time, that could reduce chemical use and labor costs while improving grape yield and harvest quality.

### Conclusion and Next Steps

The final recommendation was that the concept is promising but not yet ready for field testing. The main issue is the tradeoff between suction strength and intake coverage. Testing showed that increasing the intake area with a cone reduced suction power and made model SLF collection less efficient; removing the cone improved collection speed and effectiveness.

Next steps should focus on:

- Calculating an ideal nozzle size based on blade dimensions and motor power.
- Redesigning the blade housing to improve airflow and suction strength.
- Developing a coverage strategy for the full height of a grapevine.
- Testing either a vertically actuated device or multiple vertically stacked suction units.
- Evaluating durability under real tractor or harvester vibration and attachment-point stress.

Overall, the project supports continued development of a tractor-mounted suction device as a scalable SLF removal method, but airflow optimization and vine-height coverage must be solved before vineyard field trials.

</div>
</details>

</div>

<script>
  document.querySelectorAll(".milestone-accordion details").forEach((panel) => {
    panel.addEventListener("toggle", () => {
      if (!panel.open) return;

      document.querySelectorAll(".milestone-accordion details").forEach((otherPanel) => {
        if (otherPanel !== panel) {
          otherPanel.open = false;
        }
      });
    });
  });
</script>
