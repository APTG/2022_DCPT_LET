# Plan 2 - 160 MeV
- Beam is a monoenergetic 160 MeV, nominal
- Field size is 10 x 10 cm² wide
- Phantom is 30 x 30 x 20.5 cm³ large, Gammex solid water, where 0.5 cm PMMA is added after 2 cm solid water.
- Regions of interest (ROI): 0.25 cm into the PMMA slab, i.e. 2.25 cm downstream the phantom.
- Planned for 2 Gy at ROI.

## Eclipse Calculated dose distributions
```
RD.1.2.246.352.71.7.37402163639.1937725.20221207095327.dcm
```
## Accelerator control files (containing spot MUs)
```
RN.1.2.246.352.71.5.37402163639.178320.20221207095327.dcm
```

# Simplified plan for MC simulation
`sobp.dat` contains a simple list with energy, energy_spread, spot positions, spotsizes and spot weights, which was
converted from above DICOM-RN files using pymchelper.
