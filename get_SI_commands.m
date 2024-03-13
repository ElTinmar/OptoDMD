function get_SI_commands(ipc)
    while ipc.keep_listening
        msg = ipc.receiver.recv()
        disp(msg)
    end
end