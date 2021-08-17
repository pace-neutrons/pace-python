classdef create_grid < pyclasswrapper
    % pyHorace version of a brillem class
    methods
        % Constructor
        function obj = create_grid(varargin)
            obj.pyObjectString = call_python_m('create_grid', varargin{:}); 
            obj.overrides = [obj.overrides {'fill', 'ir_interpolate_at'}];
        end
        function out = fill(obj, varargin)
            % Ensures inputs are the correct type and shape.
            call_python('brille_grid_fill', obj.pyObjectString, varargin{:});
            out = [];
        end
        function [eigval, eigvec] = ir_interpolate_at(obj, varargin)
            out = call_python('brille_ir_interpolate_at', obj.pyObjectString, varargin{:});
            eigval = out{1}{1};
            eigvec = out{2}{1};
        end
    end
end
