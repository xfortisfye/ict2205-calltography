##### Imports #####
import pyaudio
import socket
import threading

# Global variables
message = ""
message_binary = ""
message_counter = 0

encode_data = False
first_round = True

key = [1, 5, 3, 4, 0, 4, 2, 2]
key_counter = 0

end_counter = 0


##### Get the bits to OR or AND with the data #####
def get_bitwise_data(value, position):
    if value==0:
        bitwise_str = "11111111"
        final_bitwise_str = bitwise_str[:2+position] + "0" + bitwise_str[3 + position:]
    else:
        bitwise_str = "00000000"
        final_bitwise_str = bitwise_str[:2 + position] + "1" + bitwise_str[3 + position:]
    return int(final_bitwise_str, 2)

def reset_global_variables():
    global message, message_binary, message_counter, key_counter, encode_data, first_round, end_counter
    message = ""
    message_binary = ""
    message_counter = 0

    encode_data = False
    first_round = True

    key_counter = 0
    end_counter = 0

##### Call function for sending (pick up mic data and send) ######
def sender(host, port):
    global message, message_binary, message_counter, key_counter, encode_data, first_round, end_counter
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
    # Call #
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    while True:
        # Get data from mic
        data = input_stream.read(BUFFER)

        # If there is data to be encoded then encode the data before sending
        if encode_data:

            # Insert data
            modified_data = b''
            current_index = 0

            if first_round:
                # Set the start pattern (8 x 00001111)
                for i in range(8):
                    modified_data += bytes({int('00001111', 2)})
                    current_index += 1
                first_round = False

            # Insert data until end of message binary or end of packet
            while current_index < 4096 and message_counter < len(message_binary):
                if message_binary[message_counter] == "1":
                    modified_data += bytes({data[current_index] | get_bitwise_data(1, key[key_counter])})
                else:
                    modified_data += bytes({data[current_index] & get_bitwise_data(0, key[key_counter])})
                key_counter = (key_counter + 1) % len(key)
                message_counter += 1
                current_index += 1

            # If completed the message then start inserting the end pattern
            if message_counter == len(message_binary):

                # insert 8 OR until end of packet
                while current_index < 4096 and end_counter < 8:
                    modified_data += bytes({int('00001111', 2)})
                    current_index += 1
                    end_counter += 1

            # If the end pattern is completed then done
            if end_counter == 8:
                while current_index < 4096:
                    modified_data += bytes({data[current_index]})
                    current_index += 1
                reset_global_variables()

            s.send(modified_data)
            continue

        # Send normal data when no message
        s.send(data)


if __name__ == '__main__':
    host = '192.168.0.111'
    port = 10001

    sender_thread = threading.Thread(target=sender, args=(host, port,))
    sender_thread.start()

    while True:
        print("Please enter a message: ")
        message = str(input())
        message_binary = bin(int.from_bytes(bytes(message, 'utf-8'), byteorder='little'))[2:]

        if len(message_binary) % 8 != 0:
            for i in range(8-(len(message_binary) % 8)):
                message_binary = "0"+message_binary

        encode_data = True