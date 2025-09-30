####################
# Download GLORYS12v1 data (provided by Copernicus Marine Service)
#   Copernicus Marine Service   : https://marine.copernicus.eu
#   GLORYS12v1                  : https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030
#
# How to use:
#   GLORYS12v1(topdir,now).main()
#       topdir  : top-level directory for storing downloaded data
#       now     : target time (yyyymmddHH)
#
# NOTE:
#   Data is available since 1993-01-01
#   If target time is recent, the data will be interim-data
#
#   You need to register the account (https://data.marine.copernicus.eu/register)
#   You can make '~/.dodsrc' & '~/.netrc' to avoid entering the account name and password
#       '~/.dodsrc':
#           HTTP.NETRC=/home/[username in server]/.netrc
#           HTTP.COOKIEJAR=/home/[username in server]/.cookies
#
#       '~/.netrc'
#           machine my.cmems-du.eu
#           login [registered username]
#           password [registerd password]
#
#           machine myint.cmems-du.eu
#           login [registered username]
#           password [registered password]
#
#   Domain of original data is 180W - 0 - 180E & 80S - 90N
#   This domain is modified to 0 - 360E & 90S - 90N for the usability
#
####################

import os
import sys
import numpy as np
import netCDF4 as nc
import subprocess as sub
import copernicusmarine as cm
from datetime   import datetime

class GLORYS12v1 :
    def __init__(self,topdir,now):
        #--- output file setting
        ymdh    = datetime.strftime(now,'%Y%m%d%H')
        tdir    = f'{topdir}/{now.year}/'
        sub.run(['mkdir','-p',tdir])

        #--- shared variables
        self.byte       = 'f4'
        self.undef      = -9.99E30
        self.dim4       = ('time','lev','lat','lon')
        self.vdict      = { 'uo'        :   'uo',\
                            'vo'        :   'vo',\
                            'thetao'    :   'to',\
                            'so'        :   'so' }
        self.now        = now
        self.tmpname    = f'{tdir}/uvts_{ymdh}_tmp.nc'
        self.ofname     = f'{tdir}/uvts_{ymdh}.nc'

    def download(self):
        #--- data ID setting
        if self.now<datetime(1993,1,1) :
            exit('STOP: data is available after 1993-01-01')
        elif self.now<datetime(2021,7,1) :
            data_id = 'cmems_mod_glo_phy_my_0.083deg_P1D-m'
        else :
            data_id = 'cmems_mod_glo_phy_myint_0.083deg_P1D-m'

        #--- download data via liblary 'copernicusmarine'
        print(f'WARN: download may take a while')
        ymd = datetime.strftime(self.now,'%Y-%m-%d')
        cm.subset(  dataset_id      = data_id,\
                    variables       = list(self.vdict.keys()),\
                    start_datetime  = ymd,\
                    end_datetime    = ymd,\
                    output_filename = self.tmpname)

    def set_basicinfo(self,tfout,lon_tmp,lat_tmp,lev,time):
        def mk_axis(name,var,lname,units):
            tfout.createDimension(name,len(var))
            tfout.createVariable(name,self.byte,(name))
            tfout.variables[name][:]        = var
            tfout.variables[name].long_name = lname
            tfout.variables[name].units     = units

        def mk_varinfo(name,lname,units):
            tfout.createVariable(name,self.byte,self.dim4,fill_value=self.undef)
            tfout.variables[name].long_name = lname
            tfout.variables[name].units     = units

        #--- change longitude (180W - 0 - 180E) -> (0 - 360E)
        nx  = len(lon_tmp)
        lon = np.concatenate([lon_tmp,lon_tmp+360])[int(nx/2):int(3*nx/2)]
        #--- extend latitude (80S - 90N) -> (90S - 90N)
        lat = np.concatenate([-lat_tmp[-120:][::-1],lat_tmp])

        #--- make axes
        mk_axis('lon', lon, 'longitude','degrees_east')
        mk_axis('lat', lat, 'latitude', 'degrees_north')
        mk_axis('lev', lev, 'level',    'm')
        mk_axis('time',time,'Time',     'hours since '+str(self.now))
        #--- set variable information
        mk_varinfo('uo','eastward velocity', 'm/s')
        mk_varinfo('vo','northward velocity','m/s')
        mk_varinfo('to','temperature',       'degC')
        mk_varinfo('so','salinity',          'psu')

    def modify_data(self,tfin,tfout,iname):
        nx  = tfin.dimensions['longitude'].size
        ny  = tfin.dimensions['latitude'].size+120
        nz  = tfin.dimensions['depth'].size

        for kz in range(nz):
            var_in  = tfin.variables[iname][0,kz]
            var_tmp = np.ma.masked_array(np.zeros((ny,nx)),mask=True)

            #--- extend latitude (80S - 90N) -> (90S - 90N)
            var_tmp[120:,:] = var_in[:]
            #--- change longitude (180W - 0 - 180E) -> (0 - 360E)
            var_out = np.concatenate([var_tmp,var_tmp],axis=1)[:,int(nx/2):int(3*nx/2)]

            tfout.variables[self.vdict[iname]][0,kz]    = var_out

        print(f'finished outputting {iname}')

    def main(self):
        #--- skip downloading if the target data already exsits
        if os.path.isfile(self.ofname) :
            print(f'SKIP: {self.ofname} already exists!')
            return
        else :
            self.download()
            fin     = nc.Dataset(self.tmpname,'r')
            fout    = nc.Dataset(self.ofname,'w')

            #--- set grids
            self.set_basicinfo(fout,\
                fin.variables['longitude'][:],\
                fin.variables['latitude'][:],\
                fin.variables['depth'][:],\
                np.array([0]))

            #--- output variables
            for vname in self.vdict.keys() :
                self.modify_data(fin,fout,vname)

            fin.close()
            fout.close()
            sub.run(['rm','-f',self.tmpname])
            print(f'finished making {self.ofname}')

