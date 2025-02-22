# Geometries

The simulation geometries can be combined with various plans. Here is a list of the geometries which we will use.


## Simulation Geometries A, B, C, D:

For all these geometries:
- 30 x 30 cm² slabs of Gammex solid water, 20 cm thick, but with
- one 30 x 30 x 0.5 cm³ slab of PMMA which hold detectors of interest.
- This means the total physical thickness is 20.5 cm along the beam axis.
- The detector slab will always be positioned so its center plane (0.25 cm depth in the PMMA slab) will mark the measurement position.
- Target scoring volume should be small enough in z direction, and larger, but not too large laterally. We suggest:
  - 2 mm thick along z, centered on the reference depth as described below for the different plans.
  - Laterally we suggest 5 cm in x and y, centered on the z-axis.

So, specifically, measured relative to iso-center planes:


### Geometry A - Center of SOBP
- First slab solid water : `z = [-10.25, -0.25]`
- PMMA detector plate : `z = [-0.25, +0.25]`
- Second slab solid water : `z = [+0.25, +10.25]`


### Geometry B - SOBP at distal edge 95%
- First slab solid water : `z = [-10.25, +4.75]`
- PMMA detector plate : `z = [+4.75, +5.25]`
- Second slab solid water : `z = [+5.25, +10.25]`


### Geometry C - SOBP at distal edge 74%
- First slab solid water : `z = [-10.25, +4.95]`
- PMMA detector plate : `z = [+4.95, +5.45]`
- Second slab solid water : `z = [+5.45, +10.25]`


### Geometry D - 160 MeV at 2.25 cm depth.
- First slab solid water : `z = [-2.25, -0.25]`
- PMMA detector plate : `z = [-0.25, +0.25]`
- Second slab solid water : `z = [+0.25, +18.25]`


Notice that the target scoring volume, must follow the detector plate, thus the scoring geometry will always be attached to the simulation geometry.

See scoring geometry: [scoring.md](scoring.md) for further details.
