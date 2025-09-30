!--- subroutine list
! remove_undef(io_data, nx, ny, undef)
!   real(4), dimension(nx,ny), intent(inout)    :: io_data
!   integer(4),                intent(in)       :: nx, ny
!   real(4),                   intent(in)       :: undef
!
! h_interp(in_data, out_data, lut, lon_in, lat_in, lon_out, lat_out, nx_in, ny_in, nx_out, ny_out)
!
!   integer(4),                             intent(in)  :: nx_in, ny_in, nx_out, ny_out
!   integer(4), dimension(nx_out,ny_out,4), intent(in)  :: lut
!   real(4), dimension(nx_in,ny_in),        intent(in)  :: in_data
!   real(4), dimension(nx_in),              intent(in)  :: lon_in
!   real(4), dimension(ny_in),              intent(in)  :: lat_in
!   real(4), dimension(nx_out,ny_out),      intent(out) :: out_data, lon_out, lat_out

! v_interp(in_data, out_data, lev_in, lev_out, nx, ny, nz_in, nz_out)
!   integer(4),                       intent(in)    :: nx, ny, nz_in, nz_out
!   real(4), dimension(nx,ny,nz_in),  intent(in)    :: in_data
!   real(4), dimension(nx,ny,nz_out), intent(out)   :: out_data
!   real(4), dimension(nz_in),        intent(in)    :: lev_in
!   real(4), dimension(nz_out),       intent(in)    :: lev_out

subroutine remove_undef(io_data, nx, ny, undef) bind(C)
    implicit none

    integer(4),                intent(in)       :: nx, ny
    real(4),                   intent(in)       :: undef
    real(4), dimension(nx,ny), intent(inout)    :: io_data

    logical, allocatable    :: all_undef(:)
    real(4), allocatable    :: connected(:) ! (2*nx)
    logical                 :: flag
    real(4)                 :: l_val, r_val
    integer                 :: s_ix, e_ix, s_undef, e_undef,&
                               counts, ix, jy

    allocate(all_undef(ny))
    all_undef(:)    = .true.

    !--- remove undef grids in longitudinal direction
    allocate(connected(int(2*nx)))
    do jy = 1, ny
        !--- connect (0 ~ 360 ~ 720)
        connected(   1:       nx)   = io_data(:,jy)
        connected(nx+1:int(2*nx))   = io_data(:,jy)

        !--- find non-undef grids, which are start grids in the row
        do ix = 1, nx
            ! non-undef grids exist
            if (connected(ix) /= undef) then
                s_ix            = ix
                e_ix            = ix+nx-1
                all_undef(jy)   = .false.
                exit
            endif
        enddo   ! ix loop

        if (all_undef(jy)) then
            !out_data(:,jy)  = undef
            io_data(:,jy)   = undef
        else
            !--- fill undef grids with edge values (=non-undef grids)
            do ix = s_ix, e_ix

                !--- find start undef grids
                if (connected(ix) /= undef .and. connected(ix+1) == undef) then
                    s_undef = ix+1
                    e_undef = s_undef
                    flag    = .true.

                    !--- find end undef grids
                    do while (flag)
                        if (connected(e_undef) == undef .and. connected(e_undef+1) /= undef) then
                            flag    = .false.
                        else
                            e_undef = e_undef+1
                        endif

                    enddo   ! while loop

                    !--- substitude left edge into undef grids on the left side
                    !--- substitude right edge into undef grids on the right side
                    counts  = e_undef-s_undef+1
                    l_val   = connected(s_undef-1)
                    r_val   = connected(e_undef+1)

                    if (counts == 1) then
                        connected(s_undef)  = (l_val+r_val)/2d0
                    else
                        connected(s_undef:s_undef-1+counts/2)   = l_val
                        connected(s_undef+counts/2:e_undef)     = r_val
                        if (mod(counts,2) == 1) then
                            connected(s_undef+counts/2) = (l_val+r_val)/2d0
                        endif
                    endif

                endif

            enddo   ! ix loop

            io_data(s_ix:    nx,jy) = connected(s_ix:nx)
            io_data(   1:s_ix-1,jy) = connected(nx+1:e_ix)

        endif

    enddo   ! jy loop
    deallocate(connected)

    !--- remove undef grids in latitudinal direction
    ! southern semisphere
    do jy = int((ny+1)/2), 1, -1    ! equator -> south pole
        if (all_undef(jy)) then
            s_undef = jy
            exit
        endif
    enddo   ! jy loop

    ! substitute southest non-undef grids into undef grids on the southern semisphere
    do jy = s_undef, 1, -1
        io_data(:,jy)   = io_data(:,s_undef+1)
    enddo   ! jy loop

    ! northern semisphere
    do jy = int((ny+1)/2), ny   ! equator -> north pole
        if (all_undef(jy)) then
            s_undef = jy
            exit
        endif
    enddo   ! jy loop

    ! substitute northest non-undef grids into undef grids on the northern semisphere
    do jy = s_undef, ny
        io_data(:,jy)   = io_data(:,s_undef-1)
    enddo   ! jy loop

    !--- check undef grids
    do jy = 1, ny
    do ix = 1, nx
        if (io_data(ix,jy) == undef) then
            stop "STOP: undef grids still exist!"
        endif
    enddo   ! ix loop
    enddo   ! jy loop
    deallocate(all_undef)

end subroutine remove_undef

subroutine h_interp(in_data, out_data, lut, lon_in, lat_in, lon_out, lat_out, nx_in, ny_in, nx_out, ny_out) bind(C)
    implicit none

    integer(4),                             intent(in)  :: nx_in, ny_in, nx_out, ny_out
    integer(4), dimension(nx_out,ny_out,4), intent(in)  :: lut
    real(4), dimension(nx_in,ny_in),        intent(in)  :: in_data
    real(4), dimension(nx_in),              intent(in)  :: lon_in
    real(4), dimension(ny_in),              intent(in)  :: lat_in
    real(4), dimension(nx_out,ny_out),      intent(out) :: out_data, lon_out, lat_out

    real(4) :: dlon_1c, dlon_2c, dlat_1c, dlat_2c, dlon, dlat
    integer :: ix1, ix2, jy1, jy2,&
               ix, jy

    dlon    = lon_in(2)-lon_in(1)
    dlat    = lat_in(2)-lat_in(1)

    do jy = 1, ny_out
    do ix = 1 ,nx_out

        !--- indices in input data grids
        ix1 = lut(ix,jy,1); ix2 = lut(ix,jy,2)
        jy1 = lut(ix,jy,3); jy2 = lut(ix,jy,4)

        !--- distances [degree]
        dlon_1c = lon_out(ix,jy)-lon_in(ix1)
        dlon_2c = lon_in(ix2)-lon_out(ix,jy)
        if (dlon_2c < 0)    dlon_2c = dlon_2c+360d0
        dlat_1c = lat_out(ix,jy)-lat_in(jy1)
        dlat_2c = lat_in(jy2)-lat_out(ix,jy)

        !--- horizontal interpolation
        out_data(ix,jy) = ( in_data(ix1,jy1)*dlon_2c*dlat_2c+&
                            in_data(ix1,jy2)*dlon_2c*dlat_1c+&
                            in_data(ix2,jy1)*dlon_1c*dlat_2c+&
                            in_data(ix2,jy2)*dlon_1c*dlat_1c)/&
                            (dlon*dlat)

    enddo   ! ix loop
    enddo   ! jy loop

end subroutine h_interp

subroutine v_interp(in_data, out_data, lev_in, lev_out, nx, ny, nz_in, nz_out) bind(C)
    implicit none

    integer(4),                       intent(in)    :: nx, ny, nz_in, nz_out
    real(4), dimension(nx,ny,nz_in),  intent(in)    :: in_data
    real(4), dimension(nx,ny,nz_out), intent(out)   :: out_data
    real(4), dimension(nz_in),        intent(in)    :: lev_in
    real(4), dimension(nz_out),       intent(in)    :: lev_out

    real(4) :: tdepth, dz_1c, dz_2c, dz_12
    integer :: kz1, kz2,&
               kz, ii

    do kz = 1, nz_out
        tdepth  = lev_out(kz)

        !--- vertical interpolation
        if (tdepth < lev_in(nz_in)) then

            !--- find indices in input data
            do ii = 1, nz_in-1
                if (lev_in(ii) <= tdepth .and. tdepth <= lev_in(ii+1)) then
                    kz1 = ii;   kz2 = ii+1
                    exit
                endif
            enddo   ! ii loop

            !--- distance
            dz_1c   = abs(tdepth-lev_in(kz1))
            dz_2c   = abs(tdepth-lev_in(kz2))
            dz_12   = abs(lev_in(kz1)-lev_in(kz2))

            out_data(:,:,kz)    = ( in_data(:,:,kz1)*dz_2c+&
                                    in_data(:,:,kz2)*dz_1c)/&
                                    dz_12

        !--- if target depth exceeds the deepest grids in input data, continue using the deepest value
        else
            out_data(:,:,kz)    = out_data(:,:,kz-1)
        endif

    enddo   ! kz loop

end subroutine v_interp

