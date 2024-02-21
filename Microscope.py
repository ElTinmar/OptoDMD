# Get images from scanimage 
# Use a scanimage "user function" and some form of IPC to send
# images to python
# Looks like ZMQ might not be a bad idea there (can be used 
# with MATLAB by using the java implementation, JeroMQ)

# https://stackoverflow.com/questions/38060320/how-to-use-jeromq-in-matlab
# https://stackoverflow.com/questions/39316544/getting-started-with-jeromq-in-matlab

import zmq
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5560")
message = socket.recv()
image = np.matrix(message.decode())
