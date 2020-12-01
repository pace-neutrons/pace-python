function varargout = call_function_m(varargin)
    % Convert row vectors to column vectors for better conversion to numpy
    for ii = 1:numel(varargin)
        if size(varargin{ii}, 1) == 1
            varargin{ii} = varargin{ii}';
        end
    end
    varargout = call_python(varargin{:});
    if ~iscell(varargout)
        varargout = {varargout};
    else
        varargout = unwrap_single(varargout);
    end
    if nargout < 2
        varargout = {varargout};
    end
end

function input = unwrap_single(input)
    if iscell(input) 
        if numel(input) == 1
            input = input{1};
        else
            for ii = 1:numel(input)
                input{ii} = unwrap_single(input{ii});
            end
        end
    end
end
