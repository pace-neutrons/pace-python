function sw_main(varargin)
% the main application of the deployed Horace app
[~,Matlab_code,mexMinVer,mexMaxVer,date] = horace_version();
mc = [Matlab_code(1:48),'$)'];
disp('!==================================================================!')
disp('!                      HORACE                                      !')
disp('!------------------------------------------------------------------!')
disp('!  Visualisation of multi-dimensional neutron spectroscopy data    !')
disp('!                                                                  !')
disp('!  R.A. Ewings, A. Buts, M.D. Le, J van Duijn,                     !')
disp('!  I. Bustinduy, and T.G. Perring                                  !')
disp('!                                                                  !')
disp('!  Nucl. Inst. Meth. A 834, 132-142 (2016)                         !')
disp('!                                                                  !')
disp('!  http://dx.doi.org/10.1016/j.nima.2016.07.036                    !')
disp('!------------------------------------------------------------------!')
disp(['! Matlab  code: ',mc,' !']);
if isempty(mexMaxVer)
    disp('! Mex code:    Disabled  or not supported on this platform         !')
else
    if mexMinVer==mexMaxVer
        mess=sprintf('! Mex files   : $Revision:: %4d (%s  $) !',mexMaxVer,date(1:28));
    else
        mess=sprintf(...
            '! Mex files   :$Revisions::%4d-%3d(%s$)!',mexMinVer,mexMaxVer,date(1:28));
    end
    disp(mess)
end
disp('!------------------------------------------------------------------!')
end
