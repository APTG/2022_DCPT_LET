# postprocess.ps1 — Convert .bdo simulation outputs to images, plotdata, and text
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$exe = Get-Command convertmc -ErrorAction SilentlyContinue |
       Select-Object -ExpandProperty Source
if (-not $exe) {
    $exe = Get-Command convertmc.exe -ErrorAction SilentlyContinue |
           Select-Object -ExpandProperty Source
}
if (-not $exe) {
    Write-Error "convertmc not found on PATH. Install with: pip install pymchelper"
    exit 1
}

# basenames for 1-d plots
$bplot = @("NB_Z_narrow_dose_", "NB_Z_narrow_dose_water_", "NB_Z_narrow_LET_",
           "NB_Z_narrow_LET_water_", "NB_Z_narrow_QEFF_",
           "NB_target_diff_", "NB_target_water_diff_")
# basenames for images (2-d and 1-d)
$bimg  = @("NB_XY_", "NB_XZ_map_") + $bplot
# basenames for text
$btxt  = @("NB_target_", "NB_target_water_")

$td = Get-Location   # directory where command was started from

function Find-BdoFiles {
    param([string]$Basename, [string]$OutputDir)
    # Try page-suffixed pattern first (e.g. NB_XZ_map_0001.bdo)
    $files = Get-ChildItem -Path $OutputDir -Filter "${Basename}????.bdo" -File -ErrorAction SilentlyContinue
    if (-not $files -or $files.Count -eq 0) {
        # Fall back to non-suffixed filename (e.g. NB_XZ_map.bdo)
        $nosuffix = $Basename.TrimEnd('_') + ".bdo"
        $candidate = Join-Path $OutputDir $nosuffix
        if (Test-Path $candidate) {
            $files = Get-Item $candidate
        }
    }
    return $files
}

foreach ($dir in Get-ChildItem -Path "input\plan*" -Directory) {
    Write-Host ""
    Write-Host "== Processing: $($dir.FullName) =="

    $runDirs = Get-ChildItem -Path $dir.FullName -Filter "run_*" -Directory -ErrorAction SilentlyContinue |
               Sort-Object Name | Select-Object -Last 1
    if (-not $runDirs) {
        Write-Host "  No run_* directories found, skipping."
        continue
    }
    $ed = $runDirs.FullName
    $od = Join-Path $ed "output"
    $rdd = $dir.Name
    $rd = Join-Path "results" $rdd

    if (-not (Test-Path $rd)) { New-Item -ItemType Directory -Path $rd -Force | Out-Null }

    Write-Host "  Run dir:    $ed"
    Write-Host "  Output dir: $od"
    Write-Host "  Results:    $rd"

    if (-not (Test-Path $od)) {
        Write-Host "  Output directory missing, skipping."
        continue
    }

    # Work inside the output directory so convertmc writes files there
    Push-Location $od

    # --- generate PNG images ---
    foreach ($b in $bimg) {
        $files = Find-BdoFiles -Basename $b -OutputDir $od
        if ($files) {
            $names = ($files | ForEach-Object { $_.Name }) -join ", "
            Write-Host "  convert `"$names`" to image files"
            & $exe image --many ($files | ForEach-Object { $_.Name })
        }
    }

    # --- generate plotdata (.dat) ---
    foreach ($b in $bplot) {
        $files = Find-BdoFiles -Basename $b -OutputDir $od
        if ($files) {
            $names = ($files | ForEach-Object { $_.Name }) -join ", "
            Write-Host "  convert `"$names`" to plotdata files"
            & $exe plotdata --many ($files | ForEach-Object { $_.Name })
        }
    }

    # --- generate text results (.txt) for VOIs ---
    foreach ($b in $btxt) {
        $files = Find-BdoFiles -Basename $b -OutputDir $od
        if ($files) {
            $names = ($files | ForEach-Object { $_.Name }) -join ", "
            Write-Host "  convert `"$names`" to text files"
            & $exe txt --many ($files | ForEach-Object { $_.Name })
        }
    }

    Pop-Location

    # Move results from output dir to results dir
    Get-ChildItem -Path $od -Filter "NB*.png" -File -ErrorAction SilentlyContinue |
        ForEach-Object { Move-Item $_.FullName -Destination $rd -Force }
    Get-ChildItem -Path $od -Filter "NB*.dat" -File -ErrorAction SilentlyContinue |
        ForEach-Object { Move-Item $_.FullName -Destination $rd -Force }
    Get-ChildItem -Path $od -Filter "NB*.txt" -File -ErrorAction SilentlyContinue |
        ForEach-Object { Move-Item $_.FullName -Destination $rd -Force }
}
