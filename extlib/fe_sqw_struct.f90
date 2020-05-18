module fe_sqw
    use iso_c_binding
    type my_struct
        real(8) background
        type(c_ptr) :: strdata
        integer intdata
    end type my_struct

    contains
        function c2fstr(c_str)
            interface
                pure function strlen(s) bind(C, name="strlen")
                    use, intrinsic :: iso_c_binding
                    type(c_ptr), intent(in) :: s
                    integer(c_size_t) strlen
                end function strlen
            end interface
            type(c_ptr) c_str
            character(kind=c_char, len=strlen(c_str)), pointer :: c2fstr
            call c_f_pointer(c_str, c2fstr)
        end function c2fstr

        subroutine user_model_sqw(qh, qk, ql, en, parameters, results, n_elem, c_struct) bind(C)
            implicit none
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
            !print *, c2fstr(my_data%strdata)
        
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
