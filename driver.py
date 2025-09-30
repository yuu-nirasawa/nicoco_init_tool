##################################################
# This is the driver for making COCO-input data initialized with ocean reanalysis data
# Programs can run on Python version 3.10 or later
#
# How to use:
#   python driver.py [stime] [tspan] (--check)
#       stime   : initialized time
#       tspan   : spin-up span [days] (default : 10)
#       --check : check flag for interpolation
#
# Necessary libraries:
#   os, sys, argparse, subprocess, datetime,
#   numpy, ctypes, netCDF4, copernicusmarine,
#   matplotlib
#
# Necessary files (other files & directories are created in programs if not exist):
#   driver.py               : this program
#   sub/
#       common.py           : Useful program
#       download.py         : Download ocean reanalysis data (GLORYS12v1)
#       interpolation.py    : Call 'mod_interp.f90'
#       mk_data.py          : Core program
#       mod_interp.f90      : Fortran program used for interpolation
#   NICOCO-INIT/long-run/coco_restart_[yyyymmddHH].gt3
#                           : restart file made in COCO_NOnudge
#   GRID/
#       GRID_COCO010.stream : grid file of COCO in 0.10 degrees horizontal resolution
#       GRID_COCO025.stream : grid file of COCO in 0.25 degrees horizontal resolution
#       GRID_COCO100.stream : grid file of COCO in 1.00 degrees horizontal resolution
#
##################################################

import os
import sys
import argparse
import subprocess as sub
from datetime   import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sub    import download, mk_data

if __name__=='__main__' :
    parser  = argparse.ArgumentParser(description='*** make data for NICOCO-initialization ***')
    parser.add_argument('stime',type=str,help='initialized time (yyyymmddHH)')
    parser.add_argument('tspan',type=int,default=10,help='spin-up span [days] (default : 10)')
    parser.add_argument('--check',action='store_true',help='check flag for interpolation')
    args    = parser.parse_args()
    symdh   = args.stime
    tspan   = args.tspan
    check   = args.check

    if len(symdh)!=10   : exit('STOP: \'stime\' must be yyyymmddHH')

    ndir    = os.path.dirname(os.path.abspath(__file__))
    time1   = datetime.strptime(symdh,'%Y%m%d%H')
    time2   = time1+timedelta(days=tspan)
    ymdh1   = datetime.strftime(time1,'%Y%m%d%H')
    ymdh2   = datetime.strftime(time2,'%Y%m%d%H')

    #--- compile 'sub/mod_interp.f90'
    prgname = ndir+'/sub/mod_interp.f90'
    exename = ndir+'/sub/mod_interp.so'
    if not os.path.isfile(exename) :
        sub.run(['gfortran','-Ofast','-O3','-shared','-fPIC',prgname,'-o',exename])

    #--- download necessary data
    # download.GLORYS12v1(topdir,now).main()
    #   topdir  : top-level directory for storing downloaded data
    #   now     : target time (yyyymmddHH)
    download.GLORYS12v1(ndir+'/GLORYS12v1/',time1).main()
    download.GLORYS12v1(ndir+'/GLORYS12v1/',time2).main()

    #--- main program
    # mk_data.CONVERT(topdir,ymdh1,ymdh2)
    #   .INIT(uv_on=True,check=False)
    #   .NUDGE(dt=72,check=False)
    #       topdir  : directory of this program
    #       ymdh1   : initialized time (yyyymmddHH)
    #       ymdh2   : initialized time + spin-up time (yyyymmddHH)
    #       uv_on   : flag for interpolating U & V
    #       check   : flag for checking interpolation (if True, figures are made)
    #       dt      : relaxation time [hours]
    main    = mk_data.CONVERT(ndir,ymdh1,ymdh2)
    main.INIT(check=check)
    main.NUDGE(check=check)

