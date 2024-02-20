## Plans and Measurement positions:
There will 3 plans, and in total 5 measurement points:

- **Plan 1**: SOBP covering a 10 x 10 x 10 cm³ PTV. 3 mm margin is added to the PTV.
  The PTV is centered on z = 10.25 cm into the phantom measured from the phantom surface.
  Isocenter is always exactly at this position for Plan 1, and will not move, even if the detector plate is moved.

  Distances below in () are relative from phantom surface facing the beam, positive along beam axis.
  Distances in [] are relative to isocenter plane, or you may say, absolute positions.
  These positions are nominal, actual positions are still to be determined.
  Distances are positive downstream the beam axis, traveling along the z-axis.

    a) Center of SOBP (z_c = 10.25 cm) [z_iso = 0.0 cm]\
    b) Distal edge at 95 % dose falloff (z_d95 = 15.25 cm)  [z_iso_d95 = +5.00 cm] \
    c) Distal edge at 74 % dose falloff (z_d74 = 15.45 cm)  [z_iso_d74 = +5.20 cm]

  A reduced version of plan 1 is added as `plan1_sobp_reduced`: Some detectors requires very low doses below 1 Gy in the PTV. Since the PTV is very extensive along the depth axis (10 cm), this resulted in very low doses for single spots, which cannot be delivered by the spot scanning system. For these cases, the lowest energy layers were removed, but without changing the weights of the remaining energy layers. For distal edge (plan 1b and plan 1c) this means a reduced neutron contribution for the reduced case, but the proton dose is unchanged.


- **Plan 2**: 160 MeV monoenergetic proton beam.\
   a) z = 2.25 cm, located on isocenter [z_iso = 0.0 cm]

- **Plan 3**: as plan 1, but ramped fields to create a local LET boost at the SOBP center.\
   a) z_c = 10.25 cm, located on isocenter [z_iso = 0.0 cm]
