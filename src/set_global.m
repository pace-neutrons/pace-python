function ack = set_global(name, value)
    try
        assignin('base', name, value);
        ack = true;
    catch
        ack = false;
    end
end