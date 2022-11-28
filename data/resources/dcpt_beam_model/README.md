# Description of the beam model format

The file `DCPT_beam_model__v2.csv`contains a beam model for DCPT.
The beam model was reverseengineered using actual experimental data and TOPAS simulations.

1) Energy: Nominal (i.e. requested energy) [MeV]
2) E_real: actual energy derived from range measurements [MeV]
3) E_real_sigma: energy spread 1-sigma Gaussian [MeV]
4) protons/MU: number of protons per given monitor Unit (this is proportional to air mass stopping power)

The remaining columns describe the spot size and the emittance along x and y.

- The measurements are valid at -50 cm before the iso-center
- in the experimental room x and y axis are flipped, i.e. y is horizontal and x is vertical.


### Acknowledgements
The beam model was kindly provided by Anne Vestergaard and Peter Lægdsmand from DCPT.
