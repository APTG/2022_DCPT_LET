# Description of the beam model format

The file `DCPT_beam_model__v2.csv` contains a beam model for DCPT.
The beam model was reverse-engineered using actual experimental data and TOPAS simulations.

The beam model is defined at a plane z = 50.0 cm *upstream* from the iso-center.
The beam model assumes transport in *negative* z direction.

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

"# sigma x [mm]","# sigma y [mm]","# sigma x' [rad]","# sigma y' [rad]","# cor(x x')","# cor(y y')"


### Acknowledgements
The beam model was kindly provided by Anne Vestergaard and Peter Lægdsmand from DCPT.
