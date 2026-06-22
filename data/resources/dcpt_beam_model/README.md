# Description of the beam model format

The file `DCPT_beam_model__v2.csv` contains a beam model for DCPT.
The beam model was reverse-engineered using actual experimental data and TOPAS simulations.

There are two beam models available:
- Version 2: valid until July 2024
- Version 5: valid from August 2024

Both beam models are averaged versions of the beam properties of TR1, TR2 and TR3 (the gantry treatment rooms).
The fixed beam room TR4 deviates significantly from TR1,2,3.

**Version 2**: The beam model is defined on a plane 50.0 cm *upstream* from the iso-center. The beam model definition is this way independent of transport direction.

**Version 5**: Same as Version 2, except that the beam model has been defined at 60.0 cm upstream from the iso-center.

Columns are:
1) Energy: Nominal (i.e. requested energy) [MeV]
2) E_real: actual energy derived from range measurements [MeV]
3) E_real_sigma: energy spread 1-sigma Gaussian [MeV]
4) protons/MU: number of protons per given monitor Unit (this is proportional to air mass stopping power)
5) x: spot size 1sigma [mm]
6) y: spot size 1sigma [mm]
7) x': divergence [rad]
8) y': divergence [rad]
9) xx': correlation coefficient [-]
10) yy': correlation coefficient [-]



### Acknowledgements
The beam model V2 was kindly provided by Anne Vestergaard and Peter Lægdsmand from DCPT, Aarhus University and Aarhus University Hospital.
The beam model V5 was calculated by Simon Norrig, MSc student at Dept. of Physics and Astronomy, Aarhus University, with new data sets provided by Christian Søndergaard, DCPT, Aarhus University Hospital.
