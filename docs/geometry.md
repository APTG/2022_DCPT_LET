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


## 2026 Simulation Geometries:

For the 2026 measurement campaign, the same phantom setup is used (30 x 30 cm² slabs, 20.5 cm total), but the isocenter depth varies per plan, shifting the phantom surface position relative to the isocenter (z = 0).
A 3 cm range shifter was used for the deliveries in plans 06 and 07. The spot energies in the DCM files are assumed to already account for the range shifter (i.e. effective energies post-degradation), so it is not modelled in the simulation geometry.

Clinical to simulation name mapping:
- SOBP 3d → plan05, geoE
- SOBP 4d → plan06, geoF
- SOBP 5d → plan07, geoG


### Geometry E - Plan 05, SOBP, isocenter at 7.5 cm depth, detector at 9.6 cm depth
- First slab solid water : `z = [-7.75, +1.85]`
- PMMA detector plate : `z = [+1.85, +2.35]`
- Second slab solid water : `z = [+2.35, +12.75]`


### Geometry F - Plan 06, SOBP, isocenter at 4.5 cm depth, detector at 6.5 cm depth
- First slab solid water : `z = [-4.75, +1.50]`
- PMMA detector plate : `z = [+1.50, +2.00]`
- Second slab solid water : `z = [+2.00, +15.75]`


### Geometry G - Plan 07, SOBP, isocenter at 8.5 cm depth, detector at 14.5 cm depth
- First slab solid water : `z = [-8.75, +5.50]`
- PMMA detector plate : `z = [+5.50, +6.00]`
- Second slab solid water : `z = [+6.00, +11.75]`


Notice that the target scoring volume, must follow the detector plate, thus the scoring geometry will always be attached to the simulation geometry.

See scoring geometry: [scoring.md](scoring.md) for further details.
