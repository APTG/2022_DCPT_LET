# Plan 2 - 160 MeV
- Beam is a monoenergetic 160 MeV (TODO: nominal?)
- Field size is 10 x 10 cm² wide
- Phantom is 30 x 30 x 20.5 cm³ large, Gammex solid water, where 0.5 cm PMMA is added after 2 cm solid water.

## Regions of interest
- 0.25 cm into the PMMA slab, i.e. 2.25 cm downstream the phantom.


# Description of DICOM files
There two versions, one with 180 MU per spot, another with just 1 MU per spot.

Two plans were calculated:
 a) 2 Gy SOBP target dose
 b) 100 Gy SOBP target dose

And both plans were made in two versions (TBC):
 i)  180 MU per spot
 ii) 1 MU per spot.


## Eclipse Calculated dose distributions
```
RD.1.2.246.352.71.7.37402163639.1763071.20220929151910.dcm
RD.1.2.246.352.71.7.37402163639.1826470.20221020145033.dcm
RD.1.2.246.352.71.7.37402163639.1828235.20221021112348.dcm
RD.1.2.246.352.71.7.37402163639.1828238.20221021125901.dcm
```
## Accelerator control files (containing spot MUs)
```
RN.1.2.246.352.71.5.37402163639.162240.20220929101251.dcm
RN.1.2.246.352.71.5.37402163639.167470.20221020144648.dcm
RN.1.2.246.352.71.5.37402163639.167545.20221021111407.dcm
RN.1.2.246.352.71.5.37402163639.167546.20221021125257.dcm
```

## Structure file
```
RS.1.2.246.352.205.4897660338717507947.3201811908429754044.dcm
```
