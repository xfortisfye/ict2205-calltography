##### Imports #####
import pyaudio
import socket
import sys

##### Pyaudio Initialization #####
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
BUFFER=1024

p = pyaudio.PyAudio()
input_stream = p.open(format=FORMAT,
                            input=True, rate=RATE, channels=CHANNELS,
                            frames_per_buffer=BUFFER)


##### Socket Initialization #####
host = '192.168.108.6'
port = 10001
size = 1024

# Call #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

###### EXAMPLE OF KEY #######
key = [1, 5, 3, 4, 0, 4, 2, 2]
count = 0

while True:
    data = input_stream.read(BUFFER)
    ######## MODIFY BITS HERE #########

    s.send(data)



