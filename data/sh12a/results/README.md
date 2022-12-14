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
