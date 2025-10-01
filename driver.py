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
    parser.add_argument('--tspan','-T',type=int,default=10,help='spin-up span [days] (default : 10)')
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
    download.GLORYS12v1(ndir+'/data/GLORYS12v1/',time1).main()
    download.GLORYS12v1(ndir+'/data/GLORYS12v1/',time2).main()

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

