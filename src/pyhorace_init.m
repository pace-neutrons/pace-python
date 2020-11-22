function pyhorace_init
% Performs initialization for pyHorace (everything in horace/herbert_init except addpath)

% set up multiusers computer specific settings,
% namely settings which are common for all new users of the specific computer
% e.g.:
hec = herbert_config();
parc = parallel_config();
if hec.is_default || parc.is_default
    warning(['Found Herbert is not configured. ',...
        ' Setting up the configuration, identified as optimal for this type of the machine.',...
        ' Please, check configurations (typing:',...
        ' >>herbert_config and ',...
        ' >>parallel_config)',...
        ' to ensure these configurations are correct.'])
    ocp = opt_config_manager();
    ocp.load_configuration('-set_config','-change_only_default','-force_save');
end
%

if hec.init_tests % this is developer vesion
    % set unit tests to the Matlab search path, to overwrite the unit tests
    % routines, added to Matlab after Matlab 2017b, as new routines have
    % signatures, different from the standard unit tests routines.
    hec.set_unit_test_path();
end

width = 66;
lines = {'ISIS utilities for visualization and analysis', ...
         'of neutron spectroscopy data', ...
         ['Herbert ', herbert_version()]
};
fprintf('!%s!\n', repmat('=', 1, width));
for i = 1:numel(lines)
    fprintf('!%s!\n', center_and_pad_string(lines{i}, ' ', width));
end
fprintf('!%s!\n', repmat('-', 1, width));


% Set up graphical defaults for plotting
genieplot_init;
horace_plot.name_oned = 'Horace 1D plot';
horace_plot.name_multiplot = 'Horace multiplot';
horace_plot.name_stem = 'Horace stem plot';
horace_plot.name_area = 'Horace area plot';
horace_plot.name_surface = 'Horace surface plot';
horace_plot.name_contour = 'Horace contour plot';
horace_plot.name_sliceomatic = 'Sliceomatic';
set_global_var('horace_plot',horace_plot);

hc = hor_config;
check_mex = false;
if hc.is_default
    check_mex = true;
end

hpcc = hpc_config;
if hc.is_default ||hpcc.is_default
    warning([' Found Horace is not configured. ',...
        ' Setting up the configuration, identified as optimal for this type of the machine.',...
        ' Please, check configurations (typing:',...
        ' >>hor_config and >>hpc_config)',...
        ' to ensure these configurations are correct.'])
    % load and apply configuration, assumed to be optimal for this kind of the machine.
    conf_c = opt_config_manager();
    conf_c.load_configuration('-set_config','-change_only_default','-force_save');
end

if check_mex
    [~, n_mex_errors] = check_horace_mex();
    if n_mex_errors >= 1
        hc.use_mex = false;
    else
        hc.use_mex = true;
    end
end

hec = herbert_config;
if hec.init_tests
    % add path to folders, which responsible for administrative operations
    up_root = fileparts(rootpath);
    addpath_message(1,fullfile(up_root,'admin'))
end

width = 66;
lines = {
    ['Horace ', horace_version()], ...
    repmat('-', 1, width), ...
    'Visualisation of multi-dimensional neutron spectroscopy data', ...
    '', ...
    'R.A. Ewings, A. Buts, M.D. Le, J van Duijn,', ...
    'I. Bustinduy, and T.G. Perring', ...
    '', ...
    'Nucl. Inst. Meth. A 834, 132-142 (2016)', ...
    '', ...
    'http://dx.doi.org/10.1016/j.nima.2016.07.036'
};
fprintf('!%s!\n', repmat('=', 1, width));
for i = 1:numel(lines)
    fprintf('!%s!\n', center_and_pad_string(lines{i}, ' ', width));
end
fprintf('!%s!\n', repmat('-', 1, width));

