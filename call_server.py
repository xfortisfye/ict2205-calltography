##### Imports #####
import pyaudio
import socket

##### Socket Initialization #####
host = '192.168.108.6'
port = 10001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen()

client, address = sock.accept()


##### Pyaudio Initialization #####
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
BUFFER=1024
p = pyaudio.PyAudio()
output_stream = p.open(format=pyaudio.paInt16,
                              output=True, rate=44100, channels=2,
                              frames_per_buffer=BUFFER)

print("Server is now running\n=======================")

while True:
    data = client.recv(BUFFER)
    if data:
        print(data)
        output_stream.write(data)

