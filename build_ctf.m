function build_ctf(cmake_bindir)
    out_dir = 'ctfs';
    VERSION = version('-release');
    package_name = ['pace_', VERSION];
    full_package = ['pace_', VERSION, '.ctf'];
    
    if nargin < 1
        cmake_bindir = 'buildtmp';
    end
    if ~exist('ctfs', 'dir')
        mkdir('ctfs')
    end
    mcc('-U', '-W', ['CTF:' package_name], '-N', ....
        '-d', out_dir, ...
        'src/call.m', ...
        'src/pyclasswrapper.m', ...
        'src/pyhorace_init.m', ...
        '-a', fullfile(cmake_bindir, 'CTF'))
end
