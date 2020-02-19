function mccCommand = compile_python(nargin)

    sp = filesep;
    src_dir = fileparts(mfilename('fullpath'));
    horace_dir = [src_dir sp 'Horace' sp 'horace_core'];
    herbert_dir = [src_dir sp 'Herbert' sp 'herbert_core'];
    if ~exist('copy_files_list')
        addpath([src_dir sp 'Herbert' sp 'herbert_core' sp 'admin']);
    end
    target_dir = [src_dir sp 'ISIS'];
    copy_files_list(herbert_dir, [target_dir sp 'Herbert']);
    copy_files_list(horace_dir, [target_dir sp 'Horace']);
    % Have to remove zero-byte files as mcc doesn't like them
    flist = rdir([src_dir sp 'ISIS']);
    for ii = 1:numel(flist)
        if flist(ii).bytes == 0 && ~flist(ii).isdir
            delete([flist(ii).folder filesep flist(ii).name]);
        end
    end
    % Remove unwanted directories
    deldir = {['Herbert' sp 'applications' sp 'docify']};
    for ii = 1:numel(deldir)
        dirname = [src_dir sp 'ISIS' sp deldir{ii}];
        if exist(dirname, 'dir')
            rmdir(dirname, 's');
        end
    end

   mccCommand = ['mcc -W python:horace ' ...
       '-d ' src_dir sp ['..' sp 'pyHorace '] ...
       '-v ' ...
       '-a ' src_dir sp 'ISIS ' ...
       src_dir sp 'call2.m ' ...
       src_dir sp 'call.m ' ...
       src_dir sp 'getArgOut.m ' ...
       src_dir sp 'get_global.m ' ...
       src_dir sp 'recfind.m ' ...
       src_dir sp 'set_global.m ' ...
       src_dir sp 'waitforgui.m ' ...
       src_dir sp 'pybridge.m ' ...
       src_dir sp 'thinwrapper.m ' ...
       src_dir sp 'pyhorace_init.m'
       ];
   eval(mccCommand);

end

function fl = rdir(dirname)
% Recursively lists files
    fl = dir(dirname);
    for ii = 1:numel(fl)
        if fl(ii).isdir && fl(ii).name(1) ~= '.'
            f2 = rdir([fl(ii).folder filesep fl(ii).name]);
            for jj = 1:numel(f2)
                fl(end+1) = f2(jj);
            end
        end
    end
end

