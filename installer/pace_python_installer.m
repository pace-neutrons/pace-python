classdef pace_python_installer < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                matlab.ui.Figure
        TabGroup                matlab.ui.container.TabGroup
        DefaultInstallationTab  matlab.ui.container.Tab
        Label                   matlab.ui.control.Label
        DefaultEditField        matlab.ui.control.EditField
        Label_2                 matlab.ui.control.Label
        JupyterCheckBox         matlab.ui.control.CheckBox
        SpyderCheckBox          matlab.ui.control.CheckBox
        InstallDefaultButton    matlab.ui.control.Button
        CustomInstallationTab   matlab.ui.container.Tab
        InstallBlurb            matlab.ui.control.Label
        AddButton               matlab.ui.control.Button
        CustomEditField         matlab.ui.control.EditField
        PythonListBox           matlab.ui.control.ListBox
        InstallCustomButton     matlab.ui.control.Button
        InfoLabel               matlab.ui.control.Label
        OKButton                matlab.ui.control.Button
    end

    % Callbacks that handle component events
    methods (Access = private)

        % Button pushed function: AddButton
        function AddButtonPushed(app, event)
            newdir = app.CustomEditField.Value;
            if isempty(newdir)
                return
            end
            cur_itm = app.PythonListBox.Items;
            app.PythonListBox.Items = horzcat({newdir}, cur_itm);
        end

        % Button pushed function: InstallDefaultButton
        function InstallDefaultButtonPushed(app, event)
            miniconda_path = app.DefaultEditField.Value;
            jupyter = app.JupyterCheckBox.Value;
            spyder = app.SpyderCheckBox.Value;
            app.TabGroup.Visible = 'off';
            app.InfoLabel.Visible = 'on';
            install_miniconda(miniconda_path, jupyter, spyder, app.InfoLabel);
        end

        % Button pushed function: InstallCustomButton
        function InstallCustomButtonPushed(app, event)
            py_path = app.PythonListBox.Value;
            app.TabGroup.Visible = 'off';
            app.InfoLabel.Visible = 'on';
            for ii = 1:numel(py_path)
                install_pace(py_path{ii}, app.InfoLabel);
            end
            app.InfoLabel.Text = 'Installation(s) Complete';
            app.OKButton.Visible = 'on';
            drawnow;
        end

        % Button pushed function: InstallCustomButton
        function OKButtonPushed(app, event)
            delete(app);
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [100 100 640 287];
            app.UIFigure.Name = 'MATLAB App';

            % Create TabGroup
            app.TabGroup = uitabgroup(app.UIFigure);
            app.TabGroup.Position = [16 34 613 242];

            % Create DefaultInstallationTab
            app.DefaultInstallationTab = uitab(app.TabGroup);
            app.DefaultInstallationTab.Title = 'Default Installation';

            % Create Label
            app.Label = uilabel(app.DefaultInstallationTab);
            app.Label.Position = [19 146 575 64];
            app.Label.Text = {...
                'Please enter the path you want to install to. If this folder does not exist, it will be created.';
                'The installer will download miniconda and install it in this folder.';
                'It will then install Pace-Python and any additional software you specify.'};

            % Create EditField_2
            app.DefaultEditField = uieditfield(app.DefaultInstallationTab, 'text');
            if ispc
                app.DefaultEditField.Value = [getenv('USERPROFILE') '\pace_python'];
            else
                app.DefaultEditField.Value = [getenv('HOME') '/pace_python'];
            end
            app.DefaultEditField.Position = [19 119 575 22];

            % Create Label_2
            app.Label_2 = uilabel(app.DefaultInstallationTab);
            app.Label_2.Position = [19 79 561 22];
            app.Label_2.Text = 'Please check if you want the following software to be installed with Pace-Python.';

            % Create JupyterCheckBox
            app.JupyterCheckBox = uicheckbox(app.DefaultInstallationTab);
            app.JupyterCheckBox.Text = 'Jupyter';
            app.JupyterCheckBox.Position = [19 50 61 22];

            % Create SpyderCheckBox
            app.SpyderCheckBox = uicheckbox(app.DefaultInstallationTab);
            app.SpyderCheckBox.Text = 'Spyder';
            app.SpyderCheckBox.Position = [141 50 60 22];

            % Create InstallDefaultButton
            app.InstallDefaultButton = uibutton(app.DefaultInstallationTab, 'push');
            app.InstallDefaultButton.ButtonPushedFcn = createCallbackFcn(app, @InstallDefaultButtonPushed, true);
            app.InstallDefaultButton.Position = [23 9 562 22];
            app.InstallDefaultButton.Text = 'Install Pace-Python';

            % Create CustomInstallationTab
            app.CustomInstallationTab = uitab(app.TabGroup);
            app.CustomInstallationTab.Title = 'Custom Installation';

            % Create PleaseselectaPythoninstallationfromthelistbelowtoLabel
            app.InstallBlurb = uilabel(app.CustomInstallationTab);
            app.InstallBlurb.Position = [23 146 562 62];
            app.InstallBlurb.Text = {...
                'Please select a Python installation(s) from the list below to install Pace-Python to.';
                'You can select multiple installations using the shift- or ctrl-keys and clicking.';
                'If your Python installation is not on the list, please enter the full path to the Python executable in the';
                'text box and click add.'};

            % Create AddButton
            app.AddButton = uibutton(app.CustomInstallationTab, 'push');
            app.AddButton.ButtonPushedFcn = createCallbackFcn(app, @AddButtonPushed, true);
            app.AddButton.Position = [535 39 50 22];
            app.AddButton.Text = 'Add';

            % Create EditField_3
            app.CustomEditField = uieditfield(app.CustomInstallationTab, 'text');
            app.CustomEditField.Position = [23 39 504 22];

            % Create PythonListBox
            app.PythonListBox = uilistbox(app.CustomInstallationTab);
            app.PythonListBox.Multiselect = 'on';
            app.PythonListBox.Position = [23 69 562 74];
            app.PythonListBox.Value = {'Item 1'};

            % Create InstallCustomButton
            app.InstallCustomButton = uibutton(app.CustomInstallationTab, 'push');
            app.InstallCustomButton.ButtonPushedFcn = createCallbackFcn(app, @InstallCustomButtonPushed, true);
            app.InstallCustomButton.Position = [23 9 562 22];
            app.InstallCustomButton.Text = 'Install Pace-Python';

            % Create Label_3
            app.InfoLabel = uilabel(app.UIFigure);
            app.InfoLabel.Position = [35 145 561 61];
            app.InfoLabel.Visible = 'off';

            % Create OKButton
            app.OKButton = uibutton(app.UIFigure, 'push');
            app.OKButton.ButtonPushedFcn = createCallbackFcn(app, @OKButtonPushed, true);
            app.OKButton.Position = [35 91 566 22];
            app.OKButton.Text = 'OK';
            app.OKButton.Visible = 'off';

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = pace_python_installer

            % Create UIFigure and components
            createComponents(app)

            % Populate the python environments list
            app.PythonListBox.Items = get_python_folders();
            
            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end

%% Module-private functions

function install_pace(py_exec, info)
    info.Text = sprintf('Installing pace-python to %s\n', py_exec);
    drawnow;
    [rv, out] = system([py_exec ' -m pip install -i https://test.pypi.org/simple/ pace-python']);
    if rv ~= 0
        error(sprintf('Could not install pace-python module: Error message is: %s', out));
    end
end

function conda_exec = install_miniconda(inst_path, inst_jupyter, inst_spyder, info)
    % Check we don't already have conda installed on the path
    has_conda = false;
    inst_path0 = inst_path;
    if ispc
        whichexec = 'where';
    else
        whichexec = 'which';
    end
    [rv, out] = system([whichexec ' conda']);
    if rv == 0
        conda_exec = split(out, sprintf('\n'));
        has_conda = true;
    end

    % If conda is already installed, pop a warning and use existing installation
    prefixtext = '';
    if has_conda
        conda_exec = sort(unique(conda_exec(~cellfun(@isempty, conda_exec))));
        conda_exec = cellfun(@lower, conda_exec, 'UniformOutput', false);
        conda_exec = conda_exec(contains(conda_exec, 'scripts'));
        conda_exec = conda_exec{1};
        prefixtext = sprintf('Conda already installed at %s\nWill use this installation.\n\n', conda_exec); 
        drawnow;
        if ispc, sep = '\'; else, sep = '/'; end
        inst_path = split(conda_exec, sep);
        inst_path = join(inst_path(1:end-2), sep);
        inst_path = inst_path{1};
    else
        % Get the conda installable
        info.Text = sprintf('%sPlease wait while miniconda is downloaded\n', prefixtext);
        drawnow;
        if ispc
            conda_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe';
            out_file = [getenv('TEMP') '\conda_install.exe'];
        elseif ismac
            conda_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh';
            out_file = [getenv('TMPDIR') '/conda_install.sh'];
        else
            conda_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh';
            out_file = '/tmp/conda_install.sh';
        end
        [filestr, status] = urlwrite(conda_url, out_file);
        if status == 0, error('Could not download miniconda'); end
        info.Text = sprintf('%s', prefixtext);
        drawnow;
        % Install conda
        if ~exist(inst_path, 'dir')
            mkdir(inst_path);
        end
        if ispc
            [rv, out] = system([out_file '/InstallationType=JustMe /RegisterPython=0 /S /D=' inst_path]);
            conda_exec = [inst_path '\scripts\conda.exe'];
        else
            [rv, out] = system(['bash ' out_file ' -b -f -p ' inst_path]);
            conda_exec = [inst_path '/bin/conda'];
        end
        if rv ~= 0
            error(sprintf('Could not install Miniconda: Error message is: %s', out));
        end
    end

    % Create pace_python environment
    info.Text = sprintf('%sPlease wait while a Python environment is created\n', prefixtext);
    drawnow;
    [rv, out] = system([conda_exec ' create -n pace_python -y -c conda-forge python=3.7']);
    if rv ~= 0
        error(sprintf('Could not create Python environment: Error message is: %s', out));
    end
    info.Text = sprintf('%sPlease wait while additional Python packages are installed\n', prefixtext);
    drawnow;
    [rv, out] = system([conda_exec ' install -n pace_python -y -c conda-forge euphonic']);
    if rv ~= 0
        error(sprintf('Could not install Euphonic: Error message is: %s', out));
    end
    if inst_jupyter
        [rv, out] = system([conda_exec ' install -n pace_python -y -c conda-forge jupyter']);
        if rv ~= 0
            error(sprintf('Could not install Jupyter: Error message is: %s', out));
        end
    end
    if inst_spyder
        [rv, out] = system([conda_exec ' install -n pace_python -y -c conda-forge spyder']);
        if rv ~= 0
            info.Text = prefixtext;
            drawnow;
            error(sprintf('Could not install Spyder: Error message is: %s', out));
        end
    end

    info.Text = sprintf('%sPlease wait while the pace-python module is installed\n', prefixtext);
    drawnow;
    % Install pace_python itself using pip
    if ispc
        pip_exec = [inst_path '\envs\pace_python\Scripts\pip.exe'];
    else
        pip_exec = [inst_path '/envs/pace_python/bin/pip'];
    end
    [rv, out] = system([pip_exec ' install -i https://test.pypi.org/simple/ pace-python']);
    if rv ~= 0
        error(sprintf('Could not install pace-python module: Error message is: %s', out));
    end
    info.Text = 'Installation Complete';
    app.OKButton.Visible = 'on';
    drawnow;
end

function pyexec = get_python_folders()
    % Searches for Python installations
    
    if ispc
        whichexec = 'where';
    else
        whichexec = 'which';
    end
    
    % Accepted python executable names and versions
    pyname = {'python', 'python3'};
    pyver = {'3.6', '3.7'};  % We're using Matlab 2020a which only supports 3.6 and 3.7
    pyexec = {};
    
    % Search first on the path
    for ii = 1:numel(pyname)
        [rv, out] = system([whichexec ' ' pyname{ii}]);
        if rv == 0
            pyexec = cat(1, pyexec, split(out, sprintf('\n')));
        end
    end
    
    % If on Windows, try the registry
    if ispc
        rootkeys = {'HKEY_CURRENT_USER', 'HKEY_LOCAL_MACHINE'};
        for jj = 1:numel(rootkeys)
            py_in_reg = true;
            try
                regq = winqueryreg('name', rootkeys{jj}, 'Software\Python');
            catch
                py_in_reg = false;
            end
            if py_in_reg
                regsearch = {};
                for ii = 1:numel(pyver)
                    regsearch = cat(1, regsearch, {['Software\Python\PythonCore\' pyver{ii} '\InstallPath'];
                                                   ['Software\Python\PythonCore\' pyver{ii} '-32\InstallPath'];
                                                   ['Software\Python\PythonCore\' pyver{ii} '-64\InstallPath']});
                    ver = strrep(pyver{ii}, '.', '');
                    regsearch = cat(1, regsearch, {['Software\Python\ContinuumAnalytics\Anaconda' ver '-32\InstallPath'];
                                                   ['Software\Python\ContinuumAnalytics\Anaconda' ver '-64\InstallPath']});
                end
                for ii = 1:numel(regsearch)
                    try
                        regq = winqueryreg(rootkeys{jj}, regsearch{ii}, 'ExecutablePath');
                        pyexec = cat(1, pyexec, {regq});
                    catch
                        try
                            regq = winqueryreg(rootkeys{jj}, regsearch{ii});
                            if exist([regq '/python.exe'], 'file')
                                pyexec = cat(1, pyexec, {[regq '/python.exe']});
                            elseif exist([regq '/python3.exe'], 'file')
                                pyexec = cat(1, pyexec, {[regq '/python3.exe']});
                            end
                        end
                    end
                end
            end
        end
    end
    
    % Finally just search common locations
    if ispc
        c_dr = getenv('SystemDrive');
        home_dir = getenv('UserProfile');
        progfile = getenv('ProgramFiles');
        progfile86 = getenv('ProgramFiles(x86)');
        appdata = getenv('LocalAppData');
        if isempty(appdata)
            appdata = getenv('AppData');
        end
        progdata = getenv('ProgramData');
    
        conda_root_dirs = {[c_dr '\tools']; progdata; home_dir; [appdata '\Continuum']};
        condaroot = {};
        for jj = 1:numel(conda_root_dirs)
            if ~isempty(conda_root_dirs{jj})
                condaroot = cat(1, condaroot, {[conda_root_dirs{jj} '\miniconda3\envs']});
                condaroot = cat(1, condaroot, {[conda_root_dirs{jj} '\anaconda3\envs']});
            end
        end
    
        searchpath = {[c_dr '\MantidInstall\bin']; [c_dr '\MantidNightlyInstall\bin']};
        for jj = 1:numel(condaroot)
            if exist(condaroot{jj}, 'dir')
                dd = dir(condaroot{jj});
                for kk = 1:numel(dd)
                    if dd(kk).isdir && ~strcmp(dd(kk).name, '..')
                        searchpath = cat(1, searchpath, {[dd(kk).folder '\' dd(kk).name]});
                    end
                end
            end
        end
    
        for jj = 1:numel(pyver)
            ver_no_dot = strrep(pyver{jj}, '.', '');
            searchpath = cat(1, searchpath, [progfile '\Python' ver_no_dot]);
            searchpath = cat(1, searchpath, [progfile86 '\Python' ver_no_dot]);
            searchpath = cat(1, searchpath, [appdata 'Programs\Python\Python' ver_no_dot]);
        end
    
        for jj = 1:numel(searchpath)
            if exist([searchpath{jj} '\python.exe'], 'file')
                pyexec = cat(1, pyexec, {[searchpath{jj} '\python.exe']});
            end
        end
    else
        searchpath = {};
        home_dir = getenv('HOME');
    
        % Try to use `locate` to find all instances of the activate script
        [rva, activate_loc] = system('locate -b "\activate"');
        [rvp, pyexec_loc] = system('locate -r "bin/python$"');
        if rva == 0 && rvp == 0
            activate_loc = split(activate_loc, sprintf('\n'));
            l1 = {}; i1 = 1;
            for ii = 1:numel(activate_loc)
                if strfind(activate_loc{ii}, 'venv')
                    aa = split(activate_loc{ii}, '/');
                    l1(i1) = join(aa(1:end-6), '/');
                    i1 = i1 + 1;
                end
            end
            activate_loc = l1;
            pyexec_loc = split(pyexec_loc, sprintf('\n'));
            pyexec_loc = pyexec_loc(~cellfun(@isempty, pyexec_loc));
            for ii = 1:numel(pyexec_loc)
                aa = split(pyexec_loc{ii}, '/');
                pyexec_loc(ii) = join(aa(1:end-2), '/');
            end
            pyenv_loc = intersect(activate_loc, pyexec_loc);
            for ii = 1:numel(pyenv_loc)
                fname = [pyenv_loc{ii} '/bin/python'];
                if isempty(strfind(pyenv_loc{ii}, 'cpython')) && ...
                   isempty(strfind(pyenv_loc{ii}, 'containers/storage/vfs')) && ...
                   exist(fname, 'file')
                    pyexec = cat(1, pyexec, {fname});
                end
            end
        else
            % Just try to look in standard locations of miniconda / anaconda
            conda_root_dirs = {home_dir};
            condaroot = {};
            for jj = 1:numel(conda_root_dirs)
                if ~isempty(conda_root_dirs{jj})
                    condaroot = cat(1, condaroot, {[conda_root_dirs{jj} '/miniconda3/envs']});
                    condaroot = cat(1, condaroot, {[conda_root_dirs{jj} '/anaconda3/envs']});
                end
            end
            for jj = 1:numel(condaroot)
                if exist(condaroot{jj}, 'dir')
                    dd = dir(condaroot{jj});
                    for kk = 1:numel(dd)
                        if dd(kk).isdir && ~strcmp(dd(kk).name, '..')
                            searchpath = cat(1, searchpath, {[dd(kk).folder '/' dd(kk).name '/bin/python']});
                        end
                    end
                end
            end
        end
    
        searchpath = cat(1, searchpath, {'/usr/bin/python', '/usr/local/bin/python'});
        searchpath = cat(1, searchpath, {'/usr/bin/python3', '/usr/local/bin/python3'});
        for jj = 1:numel(pyver)
            searchpath = cat(1, searchpath, {['/usr/bin/python' pyver{jj}], ['/usr/local/bin/python' pyver{jj}]});
            if ismac
                searchpath = cat(1, searchpath, {[home_dir '/Library/Frameworks/Python.framework/Versions/' pyver{jj} '/bin/python']});
                searchpath = cat(1, searchpath, {['/usr/local/Frameworks/Python.framework/Versions/' pyver{jj} '/bin/python']});
            end
        end 
    
        for jj = 1:numel(searchpath)
            if exist(searchpath{jj}, 'file')
                pyexec = cat(1, pyexec, searchpath(jj));
            end
        end
    end
    
    % Sorts and remove duplicates
    pyexec = sort(unique(pyexec(~cellfun(@isempty, pyexec))));
    
end
