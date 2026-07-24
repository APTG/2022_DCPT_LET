#!/usr/bin/env python3
"""
parse_mdata.py

Parses MCNP's legacy TMESH ("RMESH"/type-3 mesh tally) binary-text dump
file and writes flat, plottable tables for the lateral (XY) and
longitudinal (XZ) meshes defined in this deck:

    rmesh13 -> longitudinal XZ map (mesh id 13)
    rmesh33 -> lateral      XY map (mesh id 33)

Output format - one row per mesh element, coordinate = BIN CENTER (not
edge), fastest-varying column first:

    XY map: x_center  y_center  value
    XZ map: x_center  z_center  value

File layout this parser expects:
  - a mesh "header" line of 19 numbers: token[2]=nx_edges, token[3]=ny_edges,
    token[4]=nz_edges, token[7]=mesh id (13 / 33 here), token[6]/token[8]=
    total number of mesh elements.
  - after a couple of housekeeping lines, three boundary-coordinate lines:
    cora (nx_edges values), corb (ny_edges values), corc (nz_edges values).
    These boundary arrays are ALWAYS printed in increasing numeric order by
    MCNP, regardless of the order the data rows below are written in.
  - then VALUE rows (one row of nx values per (z,y) combination),
    immediately followed by the same number of ERROR rows in the same
    order.
  - the next mesh's header line follows immediately after the error rows.

Z-AXIS FIX: MCNP writes the VALUE/ERROR rows for a TMESH block with z as
the slowest-varying index counting DOWN from kzmax to 1 (not up from 1 to
kzmax), while corc (the z boundary array, hence the z centers derived from
it) is always listed in increasing order. Pairing row r=z_idx directly
with the z_idx-th z-center (the previous behaviour) therefore mirrors the
whole longitudinal profile - a point that should read as upstream (large
negative z, near the beam entrance) came out downstream and vice versa,
i.e. the "+ and - reversed" symptom. Fixed in write_xz_map() below by
pairing each z-center with the row from the OTHER end of the row block
instead. The lateral (XY) map is left as before since only the z-axis was
reported as reversed; if the y-axis of xy_map.dat ever shows the same
mirroring, apply the identical fix (reverse the row index) in
write_xy_map().

Usage:
    python3 parse_mdata.py [mdata_file] [--outdir OUTDIR]
"""
import argparse
import locale
import sys
from pathlib import Path

locale.setlocale(locale.LC_NUMERIC, "C")


def to_float(tok):
    try:
        return float(tok)
    except ValueError:
        # Fortran fixed-width field overflow (prints '****...' when the
        # number doesn't fit the column width) - can't recover the real
        # value from this file alone.
        return float('nan')


def read_tokens_per_line(path):
    with open(path) as f:
        return [line.split() for line in f]


def parse_mdata(path):
    lines = read_tokens_per_line(path)
    n = len(lines)

    # line 0: title, line 1: "<n_meshes> <something>"
    n_meshes = int(lines[1][0])

    # Phase 1: all mesh headers are grouped together at the top of the
    # file (one 19-token header line + a couple of housekeeping lines per
    # mesh), BEFORE any boundary/data lines for any mesh.
    headers = []
    i = 2
    while i < n and len(headers) < n_meshes:
        if len(lines[i]) == 19:
            header = lines[i]
            headers.append({
                'nx_e': int(header[2]), 'ny_e': int(header[3]),
                'nz_e': int(header[4]), 'id': int(header[7]),
            })
        i += 1

    # Phase 2: boundaries + value/error rows for each mesh, in the same
    # order as the headers were listed.
    meshes = []
    for h in headers:
        nx_e, ny_e, nz_e = h['nx_e'], h['ny_e'], h['nz_e']
        while i < n and len(lines[i]) != nx_e:
            i += 1
        cora = [to_float(x) for x in lines[i]]
        i += 1
        corb = [to_float(x) for x in lines[i]]
        i += 1
        corc = [to_float(x) for x in lines[i]]
        i += 1

        nx, ny, nz = nx_e - 1, ny_e - 1, nz_e - 1
        nrows = ny * nz

        values = []
        for r in range(nrows):
            values.append([to_float(x) for x in lines[i]])
            i += 1
        errors = []
        for r in range(nrows):
            errors.append([to_float(x) for x in lines[i]])
            i += 1

        meshes.append({
            'id': h['id'], 'nx': nx, 'ny': ny, 'nz': nz,
            'cora': cora, 'corb': corb, 'corc': corc,
            'values': values, 'errors': errors,
        })

    for mesh in meshes:
        nan_count = sum(1 for row in mesh['values'] for v in row if v != v)
        if nan_count:
            print(f"warning: mesh id={mesh['id']}: {nan_count} value(s) were "
                  f"printed as '****' (Fortran field overflow) in the mdata "
                  f"file and could not be recovered - written as NaN",
                  file=sys.stderr)

    return meshes


def centers(edges):
    return [(edges[k] + edges[k + 1]) / 2.0 for k in range(len(edges) - 1)]


def write_xy_map(mesh, path):
    """lateral map: nz == 1 -> rows are y-index, columns within a row are x."""
    xc = centers(mesh['cora'])
    yc = centers(mesh['corb'])
    with open(path, 'w') as f:
        for y_idx in range(mesh['ny']):
            row = mesh['values'][y_idx]
            for x_idx in range(mesh['nx']):
                f.write(f"{xc[x_idx]:g} {yc[y_idx]:g} {row[x_idx]:g}\n")


def write_xz_map(mesh, path):
    """
    longitudinal map: ny == 1 -> rows are z-index, columns within a row
    are x.

    Z-AXIS FIX: row r=z_idx from the file is paired with z-center
    zc[nz-1-z_idx], not zc[z_idx] - see module docstring.
    """
    xc = centers(mesh['cora'])
    zc = centers(mesh['corc'])
    nz = mesh['nz']
    with open(path, 'w') as f:
        for z_idx in range(nz):
            row = mesh['values'][nz - 1 - z_idx]
            for x_idx in range(mesh['nx']):
                f.write(f"{xc[x_idx]:g} {zc[z_idx]:g} {row[x_idx]:g}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mdata_file', nargs='?', default='mdata')
    ap.add_argument('--outdir', default='.')
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    meshes = parse_mdata(args.mdata_file)
    if not meshes:
        print("error: no meshes found in the mdata file", file=sys.stderr)
        return

    for mesh in meshes:
        print(f"mesh id={mesh['id']}: nx={mesh['nx']} ny={mesh['ny']} nz={mesh['nz']}",
              file=sys.stderr)
        if mesh['id'] == 33:
            write_xy_map(mesh, outdir / "xy_map.dat")
        elif mesh['id'] == 13:
            write_xz_map(mesh, outdir / "xz_map.dat")
        else:
            print(f"note: unrecognized mesh id {mesh['id']}, skipped",
                  file=sys.stderr)

    print(f"Done. Files written to: {outdir}")


if __name__ == '__main__':
    main()
