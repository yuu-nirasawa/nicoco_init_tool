## Driver for making COCO-input data initialized with ocean reanalysis data

### Reference
- [Nirasawa et al. (2025)](https://doi.org/10.2151/jmsj.2025-035)

### How to use
```shell
python driver.py [stime] (-T [tspan]) (--check)
```
- *stime* : initialized time
- *tspan* : spin-up span [days] (default : 10)
- *--check* : check flag for interpolation

### Necessary Python libraries
- os, sys, argparse, subprocess, datetime, numpy, ctypes, netCDF4, copernicusmarine, matplotlib

### Necessary files (other files & directories are automatically created in programs if not exist)
- Makefile : setting file (edit for your utility)
- driver.py : top program
- sub/
  - common.py : Useful program
  - download.py : Download ocean reanalysis data (GLORYS12v1)
  - mk_data.py : Core program
  - interpolation.py : Call 'mod_interp.f90'
  - mod_interp.f90 : Fortran program used for interpolation
- data/
  - long-run/coco_restart_[yyyymmddHH].gt3 : restart file made in COCO_NOnudge
  - init/ : output directory of initialized data
  - nudge/ : output directory of nudging data
  - GLORYS12v1/[yyyy]/uvts_[yyyymmddHH].nc : ocean reanalysis data
  - GRID/
    - GRID_COCO010.stream : grid file of COCO in 0.10 degrees horizontal resolution
    - GRID_COCO025.stream : grid file of COCO in 0.25 degrees horizontal resolution
    - GRID_COCO100.stream : grid file of COCO in 1.00 degrees horizontal resolution

### Other information
- Programs can run on Python version 3.10 or later
- Source codes and related files of COCO are not publicly opened
