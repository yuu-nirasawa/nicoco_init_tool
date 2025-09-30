# Comments for programs in this directory

<details>
  <summary><h2>common.py</h2></summary>
  
  - COCO(ddir,coco_type='COCO025')  
    - *ddir* : directory of COCO grid data  
    - *coco_type* : resolution type of COCO ('COCO100', 'COCO025', 'COCO010')

  - GLORYS12v1(ddir,ymdh)
    - *ddir* : directory of GLORYS12v1 data
    - *ymdh* : yyyymmddHH (anything is OK)

  - LUT(coco,glorys)
    - *coco* : COCO grid information (object variable)
    - *glorys* : GLORYS12v1 grid information (object variable)

  - HEADER(ddir,ymdh).write(tfout,num)
    - *ddir* : directory of COCO restart file
    - *ymdh* : yyyymmddHH (anything is OK)
    - *tfout* : output file
    - *num* : variable number in the restart file

  - CHECK(ifname,ofname,varname,grid1,grid2,tlev)
    - *ifname* : file name of original data
    - *ofname* : file name of created data
    - *varname* : target variable name ('to','so')
    - *grid1* : grid of original data (object variable)
    - *grid2* : grid of created data (object variable)
    - *tlev* : target level [m]
</details>
