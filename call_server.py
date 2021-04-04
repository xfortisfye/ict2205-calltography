##### Imports #####
import pyaudio
import socket
import sys
import threading

message_gathering = False

key = [1, 5, 3, 4, 0, 4, 2, 2]
key_counter = 0
blank_counter = 0
end_counter = 0
message_bytes = b''

collecting_data = False
finished_message = False


def reset_global_variables():
    global key_counter, collecting_data, blank_counter, end_counter, message_bytes, finished_message

    key_counter = 0
    collecting_data = False
    blank_counter = 0
    end_counter = 0
    message_bytes = b''
    finished_message = False


def receiver(host, port):
    global key_counter, collecting_data, blank_counter, end_counter, message_bytes, finished_message

    ##### Socket Initialization #####
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()

    client, address = sock.accept()


    ##### Pyaudio Initialization #####
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    BUFFER=4096
    p = pyaudio.PyAudio()
    output_stream = p.open(format=FORMAT,
                                  output=True, rate=RATE, channels=CHANNELS,
                                  frames_per_buffer=BUFFER)

    print("Server is now running\n=======================")

    while True:
        data = client.recv(BUFFER)
        if data:
            output_stream.write(data)
            current_index = 0

            # Not currently collecting data then...
            if not collecting_data:

                # Search for 00001111 to signify start of message
                for i in range(8):
                    if data[i] == int('00001111', 2):
                        blank_counter += 1
                        current_index += 1
                    else:
                        blank_counter = 0
                        current_index += 1
                if blank_counter == 8:
                    collecting_data = True

            # if collecting data
            if collecting_data:
                end_counter = 0
                print("here")
                # keep collecting data until finding 8 x 00001111 or until end of packet
                while end_counter < 8 and current_index < 4096:
                    if data[current_index] == int('00001111', 2):
                        end_counter += 1
                    else:
                        message_bytes += bytes({data[current_index]})
                        end_counter = 0

                    current_index += 1

                # if end pattern is found then stop collecting data
                if end_counter == 8:
                    finished_message = True

            if finished_message:
                # Convert bytes to string binary
                message_bin = ""
                for byte in message_bytes:
                    bin_str = bin(byte)[2:]
                    for i in range(8 - len(bin_str)):
                        bin_str = "0" + bin_str

                    message_bin += bin_str[key[key_counter] + 2]
                    key_counter = (key_counter + 1) % len(key)

                # Convert string binary to string
                message = ""
                print(message_bin)
                for i in range(0, len(message_bin), 8):
                    print(bytes({int(message_bin[i:i + 8], 2)}).decode("utf-8"))
                    message = bytes({int(message_bin[i:i + 8], 2)}).decode("utf-8") + message

                # print
                print(message)
                reset_global_variables()




if __name__ == '__main__':
    host = '192.168.0.111'
    port = 10001

    receiver(host, port)