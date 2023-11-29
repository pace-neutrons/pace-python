classdef create_grid < pyclasswrapper
    % pyHorace version of a brillem class
    methods
        % Constructor
        function obj = create_grid(varargin)
            obj.pyObjectString = call('_call_python', 'create_grid', varargin{:}); 
            obj.overrides = [obj.overrides {'fill', 'ir_interpolate_at'}];
        end
        function out = fill(obj, varargin)
            % Ensures inputs are the correct type and shape.
            call('_call_python', 'brille_grid_fill', obj.pyObjectString, varargin{:});
            out = [];
        end
        function [eigval, eigvec] = ir_interpolate_at(obj, varargin)
            [eigval, eigvec] = call('_call_python', 'brille_ir_interpolate_at', obj.pyObjectString, varargin{:});
        end
    end
end
