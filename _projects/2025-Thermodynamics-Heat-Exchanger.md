---
layout: project
title: Counter Flow vs. Parallel Flow Heat Exchangers
description: A lab-based analysis comparing counter-flow and parallel-flow heat exchanger performance through temperature measurement.
technologies: []
image: /assets/images/full_HE.jpeg
---

A heat exchanger is a device that transfers thermal energy between two fluids while keeping them physically separate. One fluid is hotter and releases heat, and the other is cooler and absorbs that heat. They move through different channels, such as tubes or plates, divided by a solid wall that conducts heat but prevents mixing. As they pass through the exchanger, the temperature difference between the fluids drives heat from the hotter stream to the colder one.

<img src="{{'/assets/images/heat-exchanger-diagram.png' | relative_url }}" alt="Heat exchanger diagram" style="max-width: 700px; width: 100%; height: auto;">


The way the fluids flow determines how the exchanger performs. In parallel flow, both fluids enter from the same side and travel in the same direction, so the temperature difference is highest at the start and drops off quickly. In counter-flow, the fluids travel in opposite directions, which keeps the temperature difference more consistent and improves overall heat transfer.

In general, a heat exchanger’s role is to transfer thermal energy efficiently for heating, cooling, or energy recovery in applications like power plants, refrigeration systems, car radiators, and a wide range of industrial processes.

<img src="{{'/assets/images/counter-v-parallel.png' | relative_url }}" alt="Heat exchanger diagram" style="max-width: 700px; width: 100%; height: auto;">

#### Data:

My group and I conducted two experimental tests: one using a counterflow configuration and one using a parallel flow configuration. For each test, we recorded the initial and final temperatures of the hot reservoir, the cold reservoir, and the heat exchanger.

<img src="{{'/assets/images/thermo-table-he.png' | relative_url }}" alt="Heat exchanger diagram" style="max-width: 700px; width: 100%; height: auto;">

<div style="display:flex; gap:16px; flex-wrap:wrap;">
  <img src="{{ '/assets/images/full_HE.jpeg' | relative_url }}" alt="Full heat exchanger" style="max-width: 340px; width: 100%; height: auto;">
  <img src="{{ '/assets/images/empty_HE.jpeg' | relative_url }}" alt="Empty heat exchanger" style="max-width: 340px; width: 100%; height: auto;">
</div>


#### Analysis:

In the counter-flow setup, the cold fluid warmed up significantly in both trials, and the hot fluid cooled by a large amount, indicating strong heat transfer. Interestingly, the cold outlet temperature rose above the hot outlet temperature, which at first seemed to violate the second law of thermodynamics. After looking into it further, I learned that this can occur only in counter-flow exchangers. Because the two fluids move in opposite directions, the cold stream continually encounters hotter fluid upstream, allowing it to reach temperatures close to the hot inlet. This also explains why the effectiveness values were higher than those of the parallel-flow runs, reaching about 35 to 45 percent compared with 29 percent.

In the parallel-flow configuration, both fluids showed smaller temperature changes than in the counter-flow tests. The hot outlet temperature always stayed above the cold outlet temperature, and the temperature difference between the two streams dropped quickly along the exchanger. This leads to weaker heat transfer. Parallel flow has an inherent limitation: the fluids begin with their maximum temperature difference, but because they travel in the same direction, their temperatures converge quickly. As soon as this happens, the driving force for heat transfer falls off, resulting in lower effectiveness and more modest temperature changes.

Overall, counter-flow consistently produced larger temperature shifts and higher cold outlet temperatures, while parallel flow produced smaller changes and no temperature crossing. These outcomes match the expected thermal behavior of each configuration. Counter-flow preserves a strong temperature difference throughout the exchanger, enabling more complete heat transfer, whereas parallel flow loses its gradient early on, restricting performance. Both setups behaved exactly as theory predicts, clearly demonstrating the contrast between the two designs.

<img src="{{'/assets/images/group_photo.jpeg' | relative_url }}" alt="Heat exchanger diagram" style="max-width: 700px; width: 100%; height: auto;">