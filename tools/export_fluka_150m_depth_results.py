#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

CASES = [
    "plan01_field01_geoA_SOBPcent",
    "plan01_field01_geoB_SOBP95",
    "plan01_field01_geoC_SOBP74",
    "plan02_field01_geoD_mono",
    "plan03_field01_geoA_rampFull",
    "plan03_field02_geoA_rampFull",
    "plan04_field01_geoA_rampMiddle",
    "plan04_field02_geoA_rampMiddle",
]

CSV_ROOT = Path("/home/dewh/runs/let_benchmark/ALLLET_8CASES_150M_20260724")
OUT_ROOT = Path("data/fluka.cern/results")

# output filename -> CSV column
COLUMN_MAP = {
    "depth_Z.DOSE.all.mat": "FL_dose_all_MeV_g_primary",
    "depth_Z.DOSE.protons.mat": "FL_dose_protons_MeV_g_primary",
    "depth_Z.DOSE.primary.mat": "FL_dose_primary_MeV_g_primary",

    "depth_Z.FLUENCE.all.mat": "FL_fluence_all_cm-2_primary-1",
    "depth_Z.FLUENCE.protons.mat": "FL_fluence_protons_cm-2_primary-1",
    "depth_Z.FLUENCE.primary.mat": "FL_fluence_primary_cm-2_primary-1",

    "depth_Z.DLET.all.mat": "FL_DLET_allcharged_local_MeV_cm-1",
    "depth_Z.DLET.protons.mat": "FL_DLET_protons_local_MeV_cm-1",
    "depth_Z.DLET.primary.mat": "FL_DLET_primary_local_MeV_cm-1",
    "depth_Z.TLET.all.mat": "FL_TLET_allcharged_local_MeV_cm-1",
    "depth_Z.TLET.protons.mat": "FL_TLET_protons_local_MeV_cm-1",
    "depth_Z.TLET.primary.mat": "FL_TLET_primary_local_MeV_cm-1",

    "depth_Z.DLET.protons.H2O": "FL_DLET_protons_water_MeV_cm-1",
    "depth_Z.DLET.primary.H2O": "FL_DLET_primary_water_MeV_cm-1",
    "depth_Z.TLET.protons.H2O": "FL_TLET_protons_water_MeV_cm-1",
    "depth_Z.TLET.primary.H2O": "FL_TLET_primary_water_MeV_cm-1",
}

GROUPS = [
    (
        "Depth profiles - dose in material (Z_narrow)",
        "Exported from FLUKA 150M post-processed CSVs. Values are MeV/g/primary.",
        ["depth_Z.DOSE.all.mat", "depth_Z.DOSE.protons.mat", "depth_Z.DOSE.primary.mat"],
    ),
    (
        "Depth profiles - fluence in material (Z_narrow)",
        "Exported from FLUKA 150M post-processed CSVs. Values are 1/cm^2/primary.",
        ["depth_Z.FLUENCE.all.mat", "depth_Z.FLUENCE.protons.mat", "depth_Z.FLUENCE.primary.mat"],
    ),
    (
        "Depth profiles - LET in material (Z_narrow)",
        "Exported from FLUKA 150M post-processed CSVs. Local/material LET values are MeV/cm.",
        [
            "depth_Z.DLET.all.mat",
            "depth_Z.DLET.protons.mat",
            "depth_Z.DLET.primary.mat",
            "depth_Z.TLET.all.mat",
            "depth_Z.TLET.protons.mat",
            "depth_Z.TLET.primary.mat",
        ],
    ),
    (
        "Depth profiles - LET in water (Z_narrow)",
        "Exported from FLUKA 150M post-processed CSVs. Water LET values are MeV/cm. Only proton and primary-proton water LET are exported here.",
        [
            "depth_Z.DLET.protons.H2O",
            "depth_Z.DLET.primary.H2O",
            "depth_Z.TLET.protons.H2O",
            "depth_Z.TLET.primary.H2O",
        ],
    ),
]

def read_csv_rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def write_mat(path, rows, column):
    with path.open("w") as f:
        for row in rows:
            z = float(row["depth_cm"])
            value = float(row[column])
            f.write(f"{z:g} {value:.12e} 0\n")

def make_manifest(case):
    outputs = []
    for description, notes, files in GROUPS:
        outputs.append({
            "description": description,
            "role": "derived",
            "notes": notes + " Relative-error column is present but set to zero because the current post-processed FLUKA CSVs do not carry per-bin statistical uncertainties.",
            "files": [
                {"path": filename, "output_type": filename}
                for filename in files
            ],
        })

    return {
        "schema_version": "1",
        "plan": case,
        "code": {
            "name": "FLUKA.cern",
            "short": "FLUKA.cern",
            "version": "4-5.1",
            "notes": "Custom FLUKA source sampler and LET/dose user routine. Browser depth profiles exported from validated 150M post-processed CSVs.",
        },
        "provenance": {
            "date": "2026-08-26",
            "input_path": f"data/fluka.cern/input/{case}",
            "runner": "dewh",
            "git_ref": "ALLLET_8CASES_150M_20260724 production workflow",
        },
        "statistics": {
            "n_primaries": 150000000,
            "normalization": "per_primary",
        },
        "frame": {
            "native": "mc+z",
            "to_patient": "Depth profiles are exported on the shared isocenter-referenced Z_narrow depth grid in cm, increasing downstream along the beam.",
            "beam_model": "v2",
            "source_plane_cm": 50,
        },
        "capabilities": {
            "notes": "150M browser export includes 1D Z_narrow dose, fluence, local/material LET, and selected water LET depth profiles. Local/material LET includes all charged particles, all protons, and primary protons. Water LET is exported for all protons and primary protons only. Relative-error columns are set to zero because per-bin statistical uncertainties are not carried by the current FLUKA post-processing CSVs.",
        },
        "outputs": outputs,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Actually write files. Without this, only print planned mapping.")
    args = ap.parse_args()

    for case in CASES:
        csv_path = CSV_ROOT / case / f"{case}_ALLLET_150M_absolute_vs_SHIELDHIT.csv"
        out_dir = OUT_ROOT / case
        rows = read_csv_rows(csv_path)

        print()
        print(case)
        print("  CSV:", csv_path)
        print("  OUT:", out_dir)

        missing = [col for col in COLUMN_MAP.values() if col not in rows[0]]
        if missing:
            raise SystemExit(f"Missing CSV columns for {case}: {missing}")

        for filename, column in COLUMN_MAP.items():
            print(f"  {filename:32s} <- {column}")
            if args.write:
                out_dir.mkdir(parents=True, exist_ok=True)
                write_mat(out_dir / filename, rows, column)

        if args.write:
            (out_dir / "VERSION.txt").write_text("FLUKA.cern 4-5.1, ALLLET_8CASES_150M_20260724, 150000000 primaries per case\n")
            (out_dir / "manifest.json").write_text(json.dumps(make_manifest(case), indent=2) + "\n")

    if args.write:
        print()
        print("WROTE FLUKA.cern 150M depth result files")
    else:
        print()
        print("DRY RUN ONLY: add --write to create files")

if __name__ == "__main__":
    main()
