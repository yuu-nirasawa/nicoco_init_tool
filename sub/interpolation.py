import os
import sys
import numpy as np
import netCDF4 as nc
from ctypes import *

class INTERP :
    def __init__(self,coco,glorys,lut):
        ndir    = os.path.dirname(os.path.abspath(__file__))

        #--- shared variables
        self.mytool = np.ctypeslib.load_library('mod_interp.so',ndir)
        self.coco   = coco
        self.glorys = glorys
        self.lut    = lut
        self.dim2   = (coco.ny,coco.nx)
        self.dim3_1 = (glorys.nz-1,coco.ny,coco.nx) # all Nan at kz=49 in GLORYS12v1
        self.dim3_2 = (coco.nz,coco.ny,coco.nx)

    def remove_undef(self,io_data,undef=-32767.0):
        io_data = np.array(io_data.filled(undef),dtype=np.float32)

        self.mytool.remove_undef.argtypes   = [\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            POINTER(c_int32),\
            POINTER(c_int32),\
            POINTER(c_float)]
        self.mytool.remove_undef(\
            io_data,\
            byref(c_int32(self.glorys.nx)),\
            byref(c_int32(self.glorys.ny)),\
            byref(c_float(undef)))

        return io_data

    def h_interp(self,in_data):
        out_data    = np.zeros(self.dim2,dtype=np.float32)

        self.mytool.h_interp.argtypes   = [\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.int32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            POINTER(c_int32),\
            POINTER(c_int32),\
            POINTER(c_int32),\
            POINTER(c_int32)]
        self.mytool.h_interp(\
            np.array(in_data,dtype=np.float32),\
            out_data,\
            # python index -> fortran index
            np.array(self.lut+1,dtype=np.int32),\
            np.array(self.glorys.lon,dtype=np.float32),\
            np.array(self.glorys.lat,dtype=np.float32),\
            np.array(self.coco.lon,dtype=np.float32),\
            np.array(self.coco.lat,dtype=np.float32),\
            byref(c_int32(self.glorys.nx)),\
            byref(c_int32(self.glorys.ny)),\
            byref(c_int32(self.coco.nx)),\
            byref(c_int32(self.coco.ny)))

        return out_data

    def v_interp(self,in_data):
        out_data    = np.zeros(self.dim3_2,dtype=np.float32)

        self.mytool.v_interp.argtypes   = [\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            np.ctypeslib.ndpointer(dtype=np.float32),\
            POINTER(c_int32),\
            POINTER(c_int32),\
            POINTER(c_int32),\
            POINTER(c_int32)]
        self.mytool.v_interp(\
            np.array(in_data,dtype=np.float32),\
            out_data,\
            np.array(self.glorys.lev,dtype=np.float32),\
            np.array(self.coco.lev,dtype=np.float32),\
            byref(c_int32(self.coco.nx)),\
            byref(c_int32(self.coco.ny)),\
            byref(c_int32(self.glorys.nz)),\
            byref(c_int32(self.coco.nz)))

        return out_data

    def main(self,ifname,varname):
        fin         = nc.Dataset(ifname,'r')
        h_interped  = np.zeros(self.dim3_1,dtype='f4')
        for kz in range(self.dim3_1[0]):
            #--- remove undef grids with the neighbor grids (important for grids near coastlines)
            not_undef       = self.remove_undef(fin.variables[varname][0,kz])
            #--- horizontal interpolation
            h_interped[kz]  = self.h_interp(not_undef)
        fin.close()

        #--- vertical interpolation
        v_interped  = self.v_interp(h_interped)

        return v_interped

