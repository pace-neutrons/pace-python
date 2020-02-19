function horace_init
% Performs initialization for pyHorace (everything in horace/herbert_init except addpath)

hc = herbert_config;
if hc.is_default % force saving default configuration if it has never been saved to hdd
    instance = config_store.instance();
    instance.store_config(hc,'-forcesave');
end
phc = parallel_config;
if phc.is_default
    instance = config_store.instance();
    instance.store_config(phc,'-forcesave');
end
if hc.init_tests
    % set unit tests to the Matlab search path, to overwrite the unit tests
    % routines, added to Matlab after Matlab 2017b, as new routines have
    % signatures, different from the standard unit tests routines.
    hc.set_unit_test_path();
    copy_git_hooks('herbert');
end

disp('!==================================================================!')
disp('!         ISIS utilities for visualisation and analysis            !')
disp('!              of neutron spectroscopy data                        !')
disp('!------------------------------------------------------------------!')

% Set up graphical defaults for plotting
horace_plot.name_oned = 'Horace 1D plot';
horace_plot.name_multiplot = 'Horace multiplot';
horace_plot.name_stem = 'Horace stem plot';
horace_plot.name_area = 'Horace area plot';
horace_plot.name_surface = 'Horace surface plot';
horace_plot.name_contour = 'Horace contour plot';
horace_plot.name_sliceomatic = 'Sliceomatic';
set_global_var('horace_plot',horace_plot);

[~,Matlab_code,mexMinVer,mexMaxVer,date] = horace_version();
mc = [Matlab_code(1:48),'$)'];
hc = hor_config;

if hc.is_default
    if isempty(mexMaxVer)
        hc.use_mex = false;
    else
        hc.use_mex = true;
    end
%    % force saving default configuration if it has never been saved to hdd
%    % to avoid repetitive messages about default configuration
%    config_store.instance().store_config(hc,'-forcesave');
end
hec = herbert_config;
if hec.init_tests % install githooks for users who may run unit tests 
    % (and push to git repository)
    copy_git_hooks('horace');
end

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
