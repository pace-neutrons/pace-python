classdef thinwrapper < handle
    properties
        ObjectString
    end
    methods
        % Constructor
        function obj = thinwrapper(input_obj)
            obj.ObjectString = ['obj' replace(char(java.util.UUID.randomUUID), '-', '')];
            assignin('base', obj.ObjectString, input_obj);
        end
    end
end
