classdef create_bz < pyclasswrapper
    % pyHorace version of a brillem class
    methods
        % Constructor
        function obj = create_bz(varargin)
            obj.pyObjectString = call('_call_python', 'create_bz', varargin{:}); 
        end
    end
end
