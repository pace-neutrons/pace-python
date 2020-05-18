module fe_sqw
    use iso_c_binding
    implicit none
    type my_struct
        real(8) background
        character(:), allocatable :: strdata
        integer intdata
    end type my_struct

    contains
        ! https://stackoverflow.com/questions/20365293/
        function c_to_f_string(s) result(str)
            use, intrinsic :: iso_c_binding
            character(kind=C_CHAR, len=1), intent(IN) :: s(*)
            character(:), allocatable  :: str
            integer i, nchars
            i = 1
            do
            if (s(i) == c_null_char) exit
               i = i + 1
            end do
            nchars = i - 1  ! Exclude null character from Fortran string
            allocate(character(len=nchars) :: str)
            str = transfer(s(1:nchars), str)
        end function c_to_f_string

        function user_model_init(background, strdat, intdat) bind(C) result(c_str)
            real(8), intent(in) :: background
            !type(c_ptr), intent(in), value :: strdat
            character(kind=C_CHAR, len=1), intent(IN) :: strdat(*)
            integer, intent(in) :: intdat
            integer slen, i
            character(kind=c_char, len=1), pointer :: fstr(:)
            ! We're passing this back to C so cannot use allocatable for my_data
            type(my_struct), pointer :: my_data
            type(c_ptr) :: c_str
            allocate(my_data)
            my_data%background = background
            my_data%strdata = c_to_f_string(strdat)
            my_data%intdata = intdat
            c_str = c_loc(my_data)
        end function user_model_init

        subroutine user_model_destroy(c_struct) bind(C)
            type(c_ptr), intent(in), value :: c_struct
            type(my_struct), pointer :: my_data
            character(kind=c_char), pointer :: fstring(:)
            call c_f_pointer(c_struct, my_data)
            deallocate(my_data%strdata)
            deallocate(my_data)
        end subroutine user_model_destroy

        subroutine user_model_sqw(qh, qk, ql, en, parameters, results, n_elem, c_struct) bind(C)
            real(8), parameter :: PI = 3.1415926535897932385
        
            real(8), dimension(n_elem), intent(in) :: qh, qk, ql, en
            real(8), dimension(5), intent(in) :: parameters
            real(8), dimension(n_elem), intent(out) :: results
            integer, intent(in) :: n_elem
            type(c_ptr), intent(in), value :: c_struct
            type(my_struct), pointer :: my_data 
            real(8) js, d, gam, tt, amp, qscal
            real(8) om, q2, ff, e2om2, game
            real(8), parameter :: A = 0.0706, aa=35.008, B=0.3589, bb=15.358, C=0.5819, cc=5.561, DD=-0.0114
            integer :: i
            real(8) bkg
            character(kind=c_char), pointer :: fstr
        
            call c_f_pointer(c_struct, my_data)
            bkg = my_data%background
            print *, my_data%strdata
        
            js = parameters(1) * 8
            d = parameters(2)
            gam = parameters(3)
            tt = parameters(4)
            amp = parameters(5) / PI
            qscal = (1. / (2. * 2.87))**2
        
            do i=1, n_elem
                om = d + js * (1. - cos(PI * qh(i)) * cos(PI * qk(i)) * cos(PI * ql(i)));
                q2 = qscal * (qh(i)*qh(i) + qk(i)*qk(i) + ql(i)*ql(i));
                ff = A * exp(-aa * q2) + B * exp(-bb * q2) + C * exp(-cc * q2) + DD;
                e2om2 = (en(i)*en(i) - om*om);
                game = gam * en(i);
                results(i) = (ff * ff) * amp * (en(i) / (1 - exp(-11.602*en(i) / tt))) * (4 * gam * om) &
                                / (e2om2*e2om2 + 4 * game * game);
            end do
        
            results = results + bkg;
        
        end subroutine user_model_sqw

end module fe_sqw
