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
A 3 cm range shifter (LEXAN/polycarbonate) was used for the deliveries in plans 06 and 07. It is modelled explicitly in the simulation geometry as a 3 cm slab positioned upstream of the isocenter:
- Plan 06: range shifter center at 13.59 cm from isocenter, `z = [-15.09, -12.09]`
- Plan 07: range shifter center at 17.38 cm from isocenter, `z = [-18.88, -15.88]`

Clinical to simulation name mapping:
- SOBP 3d → plan05, geoE
- SOBP 4d → plan06, geoF
- SOBP 5d → plan07, geoG


### Geometry E - Plan 05, SOBP, isocenter at 7.28 cm depth, detector at 9.42 cm depth
- First slab solid water : `z = [-7.28, +1.89]`
- PMMA detector plate : `z = [+1.89, +2.39]`
- Second slab solid water : `z = [+2.39, +13.22]`


### Geometry F - Plan 06, SOBP, isocenter at 4.37 cm depth, detector at 6.42 cm depth
- First slab solid water : `z = [-4.37, +1.80]`
- PMMA detector plate : `z = [+1.80, +2.30]`
- Second slab solid water : `z = [+2.30, +16.13]`
- Range shifter (LEXAN) : `z = [-15.09, -12.09]` (13.59 cm upstream of isocenter)


### Geometry G - Plan 07, SOBP, isocenter at 8.25 cm depth, detector at 14.26 cm depth
- First slab solid water : `z = [-8.25, +5.76]`
- PMMA detector plate : `z = [+5.76, +6.26]`
- Second slab solid water : `z = [+6.26, +12.25]`
- Range shifter (LEXAN) : `z = [-18.88, -15.88]` (17.38 cm upstream of isocenter)


Notice that the target scoring volume, must follow the detector plate, thus the scoring geometry will always be attached to the simulation geometry.

See scoring geometry: [scoring.md](scoring.md) for further details.
