# Plan 1 - SOBP
- PTV is 10 x 10 x 10 cm³
- Planned in Eclipse assuming Gammex Solid Water Phantom 30 x 30 x 20.5 cm³, and 0.5 cm PMMA centered on 10.25 cm depth.
 - planned for 2 Gy SOBP target dose

## Eclipse calculated dose distributions
```
RD.1.2.246.352.71.7.37402163639.1937723.20221207095327.dcm
```

## Accelerator control files (containing spot MUs)
```
RN.1.2.246.352.71.5.37402163639.178319.20221207095327.dcm  # 2.0 Gy, 16 energy layers, 149.419 - 83.419 MeV
```

## Structure file
```
RS.1.2.246.352.71.4.37402163639.85715.20221103140746.dcm
```


# Reduced Plans
- Two additional plans where made with reduced doses. Since at least 1 MU must be delivered per spot,the reduced plans have some energy layers removed. Otherwise the spot number and position is the same as the reference 2.0 Gy plan mentioned above.

```
RN.1.2.246.352.71.5.37402163639.178041.20221206101625.dcm  # 1.0 Gy, 12 energy layers, 149.419 - 113.119 MeV
RN.1.2.246.352.71.5.37402163639.178042.20221206101750.dcm  # 0.5 Gy, 12 energy layers, 149.428 - 113.128 MeV
```
These will be used as field02 and field03, even if technically these are fields from separate plans.