####################
# Useful programs
#
# How to use:
#   COCO(ddir,coco_type='COCO025')
#       ddir        : directory of COCO grid data
#       coco_type   : resolution type of COCO ('COCO100', 'COCO025', 'COCO010')
#
#   GLORYS12v1(ddir,ymdh)
#       ddir    : directory of GLORYS12v1 data
#       ymdh    : yyyymmddHH (anything is ok)
#
#   LUT(coco,glorys)
#       coco    : COCO grid information (object variable)
#       glorys  : GLORYS12v1 grid information (object variable)
#
#   HEADER(ddir,ymdh)
#       .write(tfout,num)
#       ddir    : directory of COCO restart file
#       ymdh    : yyyymmddHH (anything is ok)
#       tfout   : output file
#       num     : variable number
#
#   CHECK(ifname,ofname,varname,grid1,grid2,tlev)
#       ifname  : file name of original data
#       ofname  : file name of created data
#       varname : target variable name ('to','so')
#       grid1   : grid of original data (object variable)
#       grid2   : grid of created data (object variable)
#       tlev    : target level [m]
#
####################

import os
import sys
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt

class COCO :
    def __init__(self,ddir,coco_type='COCO025'):
        #--- minimum values of temperature and salinity (fixed)
        self.minT   = -1.8
        self.minS   = 10.0

        #--- grid numbers of each resolution
        match coco_type :
            case 'COCO100' :
                nx, ny, nz  = 360, 256, 63
            case 'COCO025' :
                nx, ny, nz  = 1440, 1280, 63
            case 'COCO010' :
                nx, ny, nz  = 3600, 3000, 62
            case _ :
                exit(f'STOP: \'coco_type\'={coco_type} is not available!')

        gname   = f'{ddir}GRID_{coco_type}.stream'
        self.set_grids(gname,nx,ny,nz)

    def set_grids(self,gname,nx,ny,nz):
        #--- read grid information
        fin = open(gname,'rb')
        lon = np.fromfile(fin,dtype='>f8',count=nx*ny).reshape(ny,nx)
        lat = np.fromfile(fin,dtype='>f8',count=nx*ny).reshape(ny,nx)
        geo = np.fromfile(fin,dtype='>f8',count=nx*ny).reshape(ny,nx)
        _   = np.fromfile(fin,dtype='>f8',count=(nx+1)*(ny+1))  # lon
        _   = np.fromfile(fin,dtype='>f8',count=(nx+1)*(ny+1))  # lat
        _   = np.fromfile(fin,dtype='>f8',count=nx*ny)          # geo
        _   = np.fromfile(fin,dtype='>f8',count=nx*ny)          # angles
        _   = np.fromfile(fin,dtype='>f8',count=(nx+1)*(ny+1))  # angles
        z_T = np.fromfile(fin,dtype='>f8',count=nz)
        z_M = np.fromfile(fin,dtype='>f8',count=nz)
        fin.close()

        #--- object variables
        self.lon    = lon
        self.lat    = lat
        self.lev    = z_T
        self.nx     = nx
        self.ny     = ny
        self.nz     = nz

class GLORYS12v1 :
    def __init__(self,ddir,ymdh):
        gname   = f'{ddir}{ymdh[:4]}/uvts_{ymdh}.nc'
        self.set_grids(gname)

    def set_grids(self,gname):
        #--- read grid information
        fin = nc.Dataset(gname,'r')
        lon = fin.variables['lon'][:]
        lat = fin.variables['lat'][:]
        lev = fin.variables['lev'][:]
        fin.close()

        #--- object variables
        self.lon    = lon
        self.lat    = lat
        self.lev    = lev
        self.nx     = len(lon)
        self.ny     = len(lat)
        self.nz     = len(lev)

class LUT :
    def __init__(self,coco,glorys):
        #--- get latitude & longitude in reanalysis data & COCO
        lon_in  = glorys.lon        # [glorys.nx]
        lat_in  = glorys.lat        # [glorys.ny]
        lon_out = coco.lon.ravel()  # [coco.nx*coco.ny]
        lat_out = coco.lat.ravel()  # [coco.nx*coco.ny]

        #--- search the nearest grid index in longitude
        # glorys.lon[0] = 0.0
        # coco.lon[0]   > 0.0
        ix1 = np.searchsorted(lon_in,lon_out,side='left')-1
        ix2 = ix1+1
        ix2 = np.where(ix2>=glorys.nx,ix2-glorys.nx,ix2)

        #--- search the nearest grid index in latitude
        jy1 = np.searchsorted(lat_in,lat_out,side='left')-1
        jy2 = jy1+1
        # glorys.lat[0]  = -90.0
        # glorys.lat[-1] =  90.0
        # coco.lat[0]    > -90.0
        jy2 = np.where(jy2>=glorys.ny,jy1,jy2)

        self.lut    = np.stack([ix1,ix2,jy1,jy2]).reshape(4,coco.ny,coco.nx)

class HEADER :
    def __init__(self,ddir,ymdh):
        self.name   = [\
             'IDFM',  'DSET',  'ITEM', 'EDIT1', 'EDIT2', 'EDIT3', 'EDIT4', 'EDIT5',\
            'EDIT6', 'EDIT7', 'EDIT8',  'FNUM',  'DNUM', 'TITL1', 'TITL2',  'UNIT',\
            'ETTL1', 'ETTL2', 'ETTL3', 'ETTL4', 'ETTL5', 'ETTL6', 'ETTL7', 'ETTL8',\
             'TIME',  'UTIM',  'DATE',  'TDUR', 'AITM1', 'ASTR1', 'AEND1', 'AITM2',\
            'ASTR2', 'AEND2', 'AITM3', 'ASTR3', 'AEND3',  'DFMT',  'MISS',  'DMIN',\
             'DMAX',  'DIVS', 'DIVL',   'STYP', 'COPTN', 'IOPTN', 'ROPTN', 'DATE1',\
            'DATE2', 'MEMO1', 'MEMO2', 'MEMO3', 'MEMO4', 'MEMO5', 'MEMO6', 'MEMO7',\
            'MEMO8', 'MEMO9','MEMO10', 'CDATE', 'CSIGN', 'MDATE', 'MSIGN',  'SIZE',\
            ]
        self.length = len(self.name)
        self.get_all(f'{ddir}coco_restart_{ymdh}.gt3')

    def get_all(self,tfname):
        self.value  = []

        fin = open(tfname,'rb')
        for ii in range(24):
            #--- header
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            tmp = np.fromfile(fin,dtype='>i1',count=np.int32(top))
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot
            res = [''.join([chr(jj) for jj in tmp[jj*16:(jj+1)*16]]) for jj in range(self.length)]

            #--- data
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            tmp = np.fromfile(fin,dtype='>f8',count=int(top/8))
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot

            self.value.append(res)
        fin.close()

    def write(self,tfout,num):
        out_val = self.value[num]

        #--- write header to output file
        np.array([int(self.length*16)],dtype='>i4').tofile(tfout)
        np.array([ord(s) for h in out_val for s in h],dtype='>i1').tofile(tfout)
        np.array([int(self.length*16)],dtype='>i4').tofile(tfout)

        #--- write header on the terminal
        print('')
        print('==================================')
        print('=====  HEADER OF OUTPUT DATA =====')
        print('==================================')
        for i in range(int(self.length/2)):
            head1, head2    = self.name[i], self.name[i+32]
            val1,  val2     = out_val[i],   out_val[i+32]
            print(f'   {i+1: >2} {head1: >5}  ({val1})     {i+33: >2} {head2: >6}  ({val2})')

class CHECK :
    def __init__(self,ifname,ofname,varname,grid1,grid2,tlev):
        #--- figure setting
        vmin        = { 'to':0,  'so':10 }[varname]
        vmax        = { 'to':30, 'so':40 }[varname]
        self.pdict  = { 'vmin'  :   vmin,\
                        'vmax'  :   vmax,\
                        's'     :   20 }

        #--- original data
        fin = nc.Dataset(ifname,'r')
        var = fin.variables[varname][0]
        fin.close()

        self.grid1  = grid1
        self.var1   = var[np.argmin(abs(grid1.lev-tlev))]

        #--- created data
        fin = open(ofname,'rb')
        while True :
            # header
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            tmp = np.fromfile(fin,dtype='>i1',count=np.int32(top))
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot

            # data size
            header  = [''.join([chr(ii) for ii in tmp[jj*16:(jj+1)*16]]) for jj in range(64)]
            nx      = int(header[30])
            ny      = int(header[33])
            nz      = int(header[36])

            # data
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            var = np.fromfile(fin,dtype='>f8',count=int(top/8)).reshape(nz,ny,nx)
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot
            if header[2].replace(' ','')==varname.upper()   : break
        fin.close()

        self.grid2  = grid2
        self.var2   = var[np.argmin(abs(grid2.lev-tlev))]

    def plot(self,tax,pvar,grid,title,dskip=10):
        pvar        = np.ma.masked_array(pvar,mask=(pvar==-32767))
        vmin, vmax  = np.min(pvar), np.max(pvar)

        lon = grid.lon
        lat = grid.lat
        if np.ndim(lon)==1  :   lon, lat = np.meshgrid(lon,lat)
        lon = lon[::dskip,::dskip]
        lat = lat[::dskip,::dskip]
        var = pvar[::dskip,::dskip]
        tax.set_title(f'{title}\n(min={vmin:.2f}, max={vmax:.2f})',fontsize=24)
        tax.set_xlim(0,360)
        tax.set_ylim(-90,90)
        cs  = tax.scatter(lon,lat,c=var,**self.pdict)
        plt.colorbar(cs,ax=tax,location='right')

    def main(self,figname):
        fig, axs    = plt.subplots(nrows=2,figsize=(12,16),dpi=100)
        fig.suptitle(f'scatter plot (interval={dskip})',fontsize=32)
        self.plot(axs[0],self.var1,self.grid1,'original data; land is masked')
        self.plot(axs[1],self.var2,self.grid2,'interpolated data; land is not masked')
        plt.savefig(figname,bbox_inches='tight',pad_inches=0.1)
        print(f'finished making {figname}')

