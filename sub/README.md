# Comments for programs in this directory

<details>
  <summary><h2>common.py</h2></summary>

  ## Useful programs

  ### How to use
  - COCO(*ddir*,*coco_type*='COCO025')  
    - *ddir* : directory of COCO grid data  
    - *coco_type* : resolution type of COCO ('COCO100', 'COCO025', 'COCO010')

  - GLORYS12v1(*ddir*,*ymdh*)
    - *ddir* : directory of GLORYS12v1 data
    - *ymdh* : yyyymmddHH (anything is OK)

  - LUT(*coco*,*glorys*)
    - *coco* : COCO grid information (object variable)
    - *glorys* : GLORYS12v1 grid information (object variable)

  - HEADER(*ddir*,*ymdh*).write(*tfout*,*num*)
    - *ddir* : directory of COCO restart file
    - *ymdh* : yyyymmddHH (anything is OK)
    - *tfout* : output file
    - *num* : variable number in the restart file

  - CHECK(*ifname*,*ofname*,*varname*,*grid1*,*grid2*,*tlev*)
    - *ifname* : file name of original data
    - *ofname* : file name of created data
    - *varname* : target variable name ('to','so')
    - *grid1* : grid of original data (object variable)
    - *grid2* : grid of created data (object variable)
    - *tlev* : target level [m]
</details>

<details>
  <summary><h2>download.py</h2></summary>

  ## Download [GLORYS12v1](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030) data (provided by [Copernicus Marine Service](https://marine.copernicus.eu))

  ### How to use
  - GLORYS12v1(*topdir*,*now*).main()
    - *topdir* : top-level directory for storing downloaded data
    - *now* : target time (yyyymmddHH)

  ### NOTE
  - Data is available since 1993-01-01  
    If target time is recent, the data will be interim-data

  - You need to register the account at the [registration page](https://data.marine.copernicus.eu/register)

  - You can make '\~/.dodsrc' & '\~/.netrc' to avoid entering the account name and password
    - '~/.dodsrc'
      ```
      HTTP.NETRC=/home/[username in the server]/.netrc
      HTTP.COOKIEJAR=/home/[username in the server]/.cookies
      ```
    - '~/.netrc'
      ```
      machine my.cmems-du.eu
      login [registered username]
      password [registered password]

      machine nrt.cmems-du.eu
      login [registered username]
      password [registered password]
      ```
      
  - Domain of original data is 180W - 0 - 180E & 80S - 90N  
    This domain is modified to 0 - 360E & 90S - 90N for the usability
</details>

<details>
  <summary><h2>mk_data.py</h2></summary>

  ## Make gt3-type data for running COCO

  ### How to use
  - CONVERT(*topdir*,*ymdh1*,*ymdh2*)  
    .INIT(*uv_on*=True,*check*=False)
    .NUDGE(*dt*=72,*check*=False)
    - *topdir* : directory of 'driver.py'
    - *ymdh1* : initialized time (yyyymmddHH)
    - *ymdh2* : initialized time + spin-up time (yyyymmddHH)
    - *uv_on* : flag for interpolating U & V
    - *check* : flag for checking interpolation (figures are made)
    - *dt* : relaxation time [hours]

  ### NOTE
  - Output variables (total : 24) are ordered as
    - UO, VO, TO, SO, SHO, UBTO, VBTO, WO, AI, HI, UI, VI,  
      TI, HS, FT, SWABS, FW, FS, TAUX, TAUY, AMV, AHV, PTOP, TSI

    - eastward/northward velocity, temperature, salinity (UO,VO,TO,SO):
      - interpolated by ocean reanalysis data

    - sea surface height (SHO):
      - calculated with ice data in COCO restart file as  
        z = -(0.9\*HI+0.3\*HS)*AI

    - ice concentration, ice/snow thickness, ice temperature, sea ice surface temperature (AI,HI,HS,TI,TSI):
      - copied from COCO restart file

    - other variables (UBTO,VBTO,WO,UI,VI,FT,SWABS,FW,FS,TAUX,TAUY,AMV,AHV,PTOP)
      - filled with zero

  - Body forcing coefficient is defined as  
    coeff = 1/(relaxation time) [1/s]
</details>

<details>
  <summary><h2>interpolation.py</h2></summary>

  ## Interpolate ocean reanalysis data grid into COCO grid

  ### How to use
  - INTERP(*coco*,*glorys*,*lut*).main(*ifname*,*vname*)
    - *coco* : object variable of COCO grid (made in 'common.py')
    - *glorys* : object variable of GLORYS12v1 grid (made in 'common.py')
    - *lut* : object variable of Look-Up Table (made in 'common.py')
    - *ifname* : input file name (uvts_[yyyymmddHH].nc)
    - *vname* : target variable name ('uo', 'vo', 'to', 'so')

  ### NOTE
  - Core programs are written in Fortran90 ('mod_interp.f90') for calculating faster
</details>
