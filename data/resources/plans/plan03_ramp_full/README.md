1) Base plans were made in RayStation.
2) Base plans were then imported and exported in Eclipse, without any recalculation.
3) Those Eclipse plans were then additionally edited with [DicomFix](https://github.com/nbassler/dicomfix), for irradiation.

In the GitHub repo, the final RTPLAN file is available, and RTDOSE (RD\*.dcm) and RTSTRUCT (RS\*.dcm) are taken from the RayStation base plan.

Available DICOM files:
- `ramped_2Gy_ver2_full.dcm` - final edited RTPLAN used for irradiation
- `RD1.2.752.243.1.1.20250523160113556.3000.73252.dcm` - RayStation dose distribution
- `RD1.2.752.243.1.1.20250523160113556.4000.16653.dcm` - RayStation dose distribution
- `RD1.2.752.243.1.1.20250523160113556.5000.84138.dcm` - RayStation dose distribution
- `RS1.2.752.243.1.1.20250522124652761.2000.43711.dcm` - RayStation structure set
