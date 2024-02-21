import zmq
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5560")
message = socket.recv()
image = np.matrix(message.decode())
