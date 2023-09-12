# Results - file description
The filenames are in the format `<filename>__p<number>.suffix` where filename and page number can looked up from the table below, describing what scorer was used. It should be fairly self-explanatory.

```
Output
        Filename NB_Z_narrow_dose.bdo           # each quantity will be written to its own files
                                                # with a page index in the file name, as indicated below...
        Geo Z_narrow
        Quantity Fluence                        # __p1
        Quantity Dose                           # __p2
        Quantity Dose Protons                   # __p3

Output
        Filename NB_Z_narrow_dose_water.bdo
        Geo Z_narrow
        Quantity Fluence                        # __p1
        Quantity Dose in_Water                  # __p2
        Quantity Dose Protons in_Water          # __p3

Output
        Filename NB_Z_narrow_LET.bdo
        Geo Z_narrow
        Quantity DLET                           # __p1
        Quantity DLET Primary
        Quantity DLET Protons
        Quantity TLET                           # __p4
        Quantity TLET Primary
        Quantity TLET Protons

Output
        Filename NB_Z_narrow_LET_water.bdo
        Geo Z_narrow
        Quantity DLET in_Water                  # __p1
        Quantity DLET Primary in_Water
        Quantity DLET Protons in_Water
        Quantity TLET in_Water                  # __p4
        Quantity TLET Primary in_Water
        Quantity TLET Protons in_Water

Output
        Filename NB_Z_narrow_QEFF.bdo
        Geo Z_narrow
        Quantity DQEFF                          # __p1
        Quantity DQEFF Primary
        Quantity DQEFF Protons
        Quantity TQEFF                          # __p4
        Quantity TQEFF Primary
        Quantity TQEFF Protons


Output
        Filename NB_target.bdo
        Geo TARGET
        Quantity FLUENCE                        # __p1
        Quantity DOSE                           # __p2
        Quantity DLET                           # __p3
        Quantity DLET Primary
        Quantity DLET Protons
        Quantity TLET                           # __p6
        Quantity TLET Primary
        Quantity TLET Protons
        Quantity DQEFF                          # __p9
        Quantity DQEFF Primary
        Quantity DQEFF Protons
        Quantity TQEFF                          # __p12
        Quantity TQEFF Primary
        Quantity TQEFF Protons

Output
        Filename NB_target_water.bdo
        Geo TARGET
        Quantity DOSE in_Water                  # __p1
        Quantity DLET in_Water                  # __p2
        Quantity DLET Primary in_Water
        Quantity DLET Protons in_Water
        Quantity TLET in_Water                  # __p5
        Quantity TLET Primary in_Water
        Quantity TLET Protons in_Water
```

# Summary

| plan_name   | scorer         |   LET_keV_um |
|-------------|----------------|--------------|
| plan_1a     | dLET all       |     4.46073  |
| plan_1a     | dLET primaries |     1.75434  |
| plan_1a     | dLET protons   |     2.02641  |
| plan_1a     | tLET all       |     1.15392  |
| plan_1a     | tLET primaries |     1.10129  |
| plan_1a     | tLET protons   |     1.14294  |
| plan_1b     | dLET all       |     7.93594  |
| plan_1b     | dLET primaries |     6.96893  |
| plan_1b     | dLET protons   |     7.1299   |
| plan_1b     | tLET all       |     4.18712  |
| plan_1b     | tLET primaries |     4.14456  |
| plan_1b     | tLET protons   |     4.17518  |
| plan_1c     | dLET all       |    10.1196   |
| plan_1c     | dLET primaries |     9.38714  |
| plan_1c     | dLET protons   |     9.55678  |
| plan_1c     | tLET all       |     5.39175  |
| plan_1c     | tLET primaries |     5.34811  |
| plan_1c     | tLET protons   |     5.38136  |
| plan_2      | dLET all       |     3.99459  |
| plan_2      | dLET primaries |     0.552895 |
| plan_2      | dLET protons   |     0.897095 |
| plan_2      | tLET all       |     0.588241 |
| plan_2      | tLET primaries |     0.548203 |
| plan_2      | tLET protons   |     0.580093 |
| plan_3i     | dLET all       |     4.5209   |
| plan_3i     | dLET primaries |     1.79238  |
| plan_3i     | dLET protons   |     2.07036  |
| plan_3i     | tLET all       |     1.15685  |
| plan_3i     | tLET primaries |     1.10303  |
| plan_3i     | tLET protons   |     1.1459   |
| plan_3j     | dLET all       |     5.40472  |
| plan_3j     | dLET primaries |     3.10971  |
| plan_3j     | dLET protons   |     3.30872  |
| plan_3j     | tLET all       |     1.61801  |
| plan_3j     | tLET primaries |     1.57054  |
| plan_3j     | tLET protons   |     1.60535  |
| plan_3k     | dLET all       |     6.2123   |
| plan_3k     | dLET primaries |     4.28577  |
| plan_3k     | dLET protons   |     4.45938  |
| plan_3k     | tLET all       |     2.20562  |
| plan_3k     | tLET primaries |     2.15941  |
| plan_3k     | tLET protons   |     2.19172  |