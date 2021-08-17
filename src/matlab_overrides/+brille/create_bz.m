classdef create_bz < pyclasswrapper
    % pyHorace version of a brillem class
    methods
        % Constructor
        function obj = create_bz(varargin)
            obj.pyObjectString = call_python_m('create_bz', varargin{:}); 
        end
    end
end
