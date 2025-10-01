import os
import sys
import numpy as np
import subprocess as sub

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common         import *
from interpolation  import *

class CONVERT :
    def __init__(self,topdir,ymdh1,ymdh2):
        #--- get basic information
        coco    = COCO(topdir+'/GRID/')
        glorys  = GLORYS12v1(topdir+'/GLORYS12v1/',ymdh1)
        lut     = LUT(coco,glorys).lut
        header  = HEADER(topdir+'/NICOCO-INIT/long-run/',ymdh1)

        #--- shared variables
        self.topdir = topdir
        self.coco   = coco
        self.glorys = glorys
        self.lut    = lut
        self.header = header
        self.ymdh1  = ymdh1
        self.ymdh2  = ymdh2
        self.odim2  = (coco.ny,coco.nx)
        self.odim3  = (coco.nz,coco.ny,coco.nx)

    def write_data(self,tfout,hidx,odata):
        #--- write header
        self.header.write(tfout,hidx)
        dsize   = np.size(odata)
        assert int(self.header.value[hidx][-1])==dsize
        #--- output binary data
        np.array([8*dsize],dtype='>i4').tofile(tfout)
        np.array(odata,dtype='>f8').tofile(tfout)
        np.array([8*dsize],dtype='>i4').tofile(tfout)

    def INIT(self,uv_on=True,check=False):
        #--- read ice data (used for calculating SHO and copying ice variables)
        var_ice = {}
        ifname  = f'{self.topdir}/NICOCO-INIT/long-run/coco_restart_{self.ymdh1}.gt3'
        fin     = open(ifname,'rb')
        for ii in range(24):
            #--- header
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            tmp = np.fromfile(fin,dtype='>i1',count=np.int32(top))
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot

            header  = [''.join([chr(jj) for jj in tmp[jj*16:(jj+1)*16]]) for jj in range(64)]

            #--- data
            top = np.fromfile(fin,dtype='>i4',count=1)[0]
            var = np.fromfile(fin,dtype='>f8',count=int(top/8))
            bot = np.fromfile(fin,dtype='>i4',count=1)[0]
            assert top==bot

            varname = header[2].replace(' ','')
            if varname in ['AI','HI','TI','HS','TSI'] :
                var_ice[varname]    = var.reshape(5,self.coco.ny,self.coco.nx)
        fin.close()

        #--- output file setting
        odir    = f'{self.topdir}/NICOCO-INIT/init/'
        sub.run(['mkdir','-p',odir])
        ofname  = f'{odir}coco_init_{self.ymdh1}.gt3'
        fout    = open(ofname,'wb')

        #--- U, V, T, S (interpolated with ocean reanalysis data)
        ifname  = f'{self.topdir}/GLORYS12v1/{self.ymdh1[:4]}/uvts_{self.ymdh1}.nc'
        for ii, vname in enumerate(['uo','vo','to','so']):
            # U & V are interpolated
            if uv_on :
                res = INTERP(self.coco,self.glorys,self.lut).main(ifname,vname)
            # U & V are not interpolated (filled with zero)
            else :
                # T & S are always interpolated
                if vname in ['to','so'] :
                    res = INTERP(self.coco,self.glorys,self.lut).main(ifname,vname)
                else :
                    res = np.zeros(self.odim3)
            self.write_data(fout,ii,res)

        #--- SHO (calculated with ice data in COCO restart file)
        res = np.zeros(self.odim2)
        for kz in range(5):
            res[:] -= (0.9*var_ice['HI'][kz]+0.3*var_ice['HS'][kz])*var_ice['AI'][kz]
        self.write_data(fout,4,res)

        #--- others (fill zero or copy COCO restart file)
        self.write_data(fout,5,np.zeros(self.odim2))    # UBTO
        self.write_data(fout,6,np.zeros(self.odim2))    # VBTO
        self.write_data(fout,7,np.zeros(self.odim3))    # WO
        self.write_data(fout,8,var_ice['AI'])           # AI
        self.write_data(fout,9,var_ice['HI'])           # HI
        self.write_data(fout,10,np.zeros(self.odim2))   # UI
        self.write_data(fout,11,np.zeros(self.odim2))   # VI
        self.write_data(fout,12,var_ice['TI'])          # TI
        self.write_data(fout,13,var_ice['HS'])          # HS
        self.write_data(fout,14,np.zeros(self.odim2))   # FT
        self.write_data(fout,15,np.zeros(self.odim2))   # SWABS
        self.write_data(fout,16,np.zeros(self.odim2))   # FW
        self.write_data(fout,17,np.zeros(self.odim2))   # FS
        self.write_data(fout,18,np.zeros(self.odim2))   # TAUX
        self.write_data(fout,19,np.zeros(self.odim2))   # TAUY
        self.write_data(fout,20,np.zeros(self.odim3))   # AMV
        self.write_data(fout,21,np.zeros(self.odim3))   # AHV
        self.write_data(fout,22,np.zeros(self.odim2))   # PTOP
        self.write_data(fout,23,var_ice['TSI'])         # TSI
        fout.close()
        print(f'finished making {ofname}')

        #--- compare original data and created data
        if check :
            for vname in ['to','so'] :
                figname = f'check_{vname}_init.png'
                tlev    = 0 # [m]
                CHECK(ifname,ofname,vname,self.glorys,self.coco,tlev).main(figname)

    def NUDGE(self,dt=72,check=False):
        yyyy        = self.ymdh2[:4]
        yyyymmdd    = self.ymdh2[:8]
        hh          = self.ymdh2[8:]
        odir        = f'{self.topdir}/NICOCO-INIT/nudge/'
        sub.run(['mkdir','-p',odir])

        for ii, vname in enumerate(['to','so']) :
            #--- modify header
            self.header.value[ii+2][26] = f'{yyyymmdd} {hh}0000 '
            self.header.value[ii+2][47] = f'{yyyymmdd} {hh}0000 '
            self.header.value[ii+2][48] = f'{yyyymmdd} {hh}0000 '
            self.header.value[ii+2][49] = f'00{self.ymdh2}0000'

            #--- nudging file (interpolated with ocean reanalysis data)
            ifname  = f'{self.topdir}/GLORYS12v1/{yyyy}/uvts_{self.ymdh2}.nc'
            res     = INTERP(self.coco,self.glorys,self.lut).main(ifname,vname)

            ofname  = f'{odir}{vname}_nudge_{self.ymdh2}.gt3'
            fout    = open(ofname,'wb')
            self.write_data(fout,ii+2,res)
            fout.close()
            print(f'finished making {ofname}')

            #--- compare original data and created data
            if check :
                figname = f'check_{vname}_nudge.png'
                tlev    = 0 # [m]
                CHECK(ifname,ofname,vname,self.glorys,self.coco,tlev).main(figname)

            #--- body forcing coefficient file [1/s]
            ofname  = f'{odir}{vname}_coeff_{self.ymdh2}.gt3'
            fout    = open(ofname,'wb')
            self.write_data(fout,ii+2,np.full(self.odim3,1/(dt*3600)))
            fout.close()
            print(f'finished making {ofname}')

