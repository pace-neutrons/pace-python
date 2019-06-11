function mccCommand = compile_python(nargin)

    src_dir = fileparts(mfilename('fullpath'));
    horace_dir = [src_dir '/Horace'];
    herbert_dir = [src_dir '/Herbert'];
    if ~exist('copy_files_list')
        addpath([src_dir '/Herbert/admin']);
    end
    target_dir = [src_dir '/ISIS'];
    copy_files_list(herbert_dir, [target_dir '/Herbert']);
    copy_files_list(horace_dir, [target_dir '/Horace']);
    % Have to remove zero-byte files as mcc doesn't like them
    flist = rdir([src_dir '/ISIS']);
    for ii = 1:numel(flist)
        if flist(ii).bytes == 0 && ~flist(ii).isdir
            delete([flist(ii).folder filesep flist(ii).name]);
        end
    end
    % Remove unwanted directories
    deldir = {'Horace/demo', 'Horace/test', 'Herbert/applications/docify'};
    for ii = 1:numel(deldir)
        dirname = [src_dir '/ISIS/' deldir{ii}];
        if exist(dirname, 'dir')
            rmdir(dirname, 's');
        end
    end

   mccCommand = ['mcc -W python:horace '...
       '-d ' src_dir '/../pyHorace '...
       '-a ' src_dir '/ISIS ' ...
       '-a ' src_dir '/call2.m ' ...
       '-a ' src_dir '/call.m ' ...
       '-a ' src_dir '/compile_python.m ' ...
       '-a ' src_dir '/getArgOut.m ' ...
       '-a ' src_dir '/get_global.m ' ...
       '-a ' src_dir '/recfind.m ' ...
       '-a ' src_dir '/set_global.m ' ...
       '-a ' src_dir '/waitforgui.m ' ...
       '-v ' ...
       src_dir '/horace_main.m'
       ];
   eval(mccCommand);

end

function fl = rdir(dirname)
% Recursively lists files
    fl = dir(dirname);
    for ii = 1:numel(fl)
        if fl(ii).isdir && fl(ii).name(1) ~= '.'
            f2 = rdir([fl(ii).folder '/' fl(ii).name]);
            for jj = 1:numel(f2)
                fl(end+1) = f2(jj);
            end
        end
    end
end

