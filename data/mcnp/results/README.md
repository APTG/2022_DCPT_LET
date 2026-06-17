Results contributed by Hrvoje Brkic. All output filenames use the `HB_` prefix.
Output files were named loosely following the SHIELD-HIT12A convention, but
with inconsistencies in page numbering and underscore use across plans.
The per-plan `manifest.json` files map each file to its semantic meaning.

## File naming key

| Pattern | Tally | Quantity | Unit |
|---|---|---|---|
| `*narrow_LET_p3` | F4 | DLET protons | MeV/cm |
| `*narrow_LET_p6` | F4 | TLET protons | MeV/cm |
| `*narrow_dose_p01` | F4 | Flux of primary particles along Z | per SP |
| `*narrow_dose_p02` | F6 | Dose along Z-axis | MeV/g/SP |
| `*target_p02` | F6 | Dose in target volume | MeV/g/SP |

All results are normalised per source particle (SP).
Stopping power values are interpreted in MeV/cm (F4 tally energy bins).

## Known issues

- Filename inconsistencies: some files use double underscores before the page
  number (e.g. `HB_Z_narrow_LET__p6.dat`) while others do not. See individual
  `manifest.json` files for details.
