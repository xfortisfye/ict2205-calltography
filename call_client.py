##### Imports #####
import pyaudio
import socket
import threading
import time
import hashlib


class Sender():
    ##### Socket Variables #####
    host = ''
    port = ''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    end_call = False

    ##### Key Variables #####
    key = []

    ##### LISTEN VARIABLES #####
    blank_counter = 0
    mid_counter_decode = 0
    end_counter_decode = 0
    key_counter_decode = 0
    message_bytes = b''
    message_digest_bytes = b''
    collecting_data = False
    finished_message = False
    message_gathering = False
    finished_all = False

    ##### SPEAK VARIABLES #####
    message_binary = ""
    message_digest_binary = ""
    message_counter = 0
    message_digest_counter = 0
    mid_counter_encode = 0
    end_counter_encode = 0
    key_counter_encode = 0
    encode_data = False
    first_round = True

    ##### Pyaudio Variables #####
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    INPUT_BUFFER = 1024
    OUTPUT_BUFFER = 4096
    input_stream = None
    output_stream = None


    def __init__(self, host, port, key):
        self.host = host
        self.port = port
        self.key = key


    def get_bitwise_data(self, value, position):
        if value==0:
            bitwise_str = "11111111"
            final_bitwise_str = bitwise_str[:position] + "0" + bitwise_str[1 + position:]
        else:
            bitwise_str = "00000000"
            final_bitwise_str = bitwise_str[:position] + "1" + bitwise_str[1 + position:]
        return int(final_bitwise_str, 2)


    def reset_global_variables_listen(self):
        self.key_counter_decode = 0
        self.blank_counter = 0
        self.mid_counter_decode = 0
        self.end_counter_decode = 0

        self.message_bytes = b''
        self.message_digest_bytes = b''

        self.collecting_data = False
        self.finished_message = False
        self.message_gathering = False
        self.finished_all = False


    def reset_global_variables_speak(self):
        self.message_binary = ""
        self.message_digest_binary = ""
        self.message_counter = 0
        self.message_digest_counter = 0

        self.encode_data = False
        self.first_round = True

        self.key_counter_encode = 0
        self.mid_counter_encode = 0
        self.end_counter_encode = 0


    def call(self):
        self.sock.connect((self.host, self.port))

        ##### Pyaudio Initialization #####
        p = pyaudio.PyAudio()
        self.input_stream = p.open(format=self.FORMAT,
                              input=True, rate=self.RATE, channels=self.CHANNELS,
                              frames_per_buffer=self.INPUT_BUFFER)
        self.output_stream = p.open(format=self.FORMAT,
                               output=True, rate=self.RATE, channels=self.CHANNELS,
                               frames_per_buffer=self.OUTPUT_BUFFER)

        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

        speak_thread = threading.Thread(target=self.speak)
        speak_thread.start()


    def listen(self):
        while not self.end_call:
            try:
                data = self.sock.recv(self.OUTPUT_BUFFER)
                if data:
                    self.output_stream.write(data)
                    current_index = 0

                    # Not currently collecting data then...
                    if not self.collecting_data:

                        # Search for 00001111 to signify start of message
                        for i in range(8):
                            if data[i] == int('00001111', 2):
                                self.blank_counter += 1
                                current_index += 1
                            else:
                                self.blank_counter = 0
                                current_index += 1
                        if self.blank_counter == 8:
                            self.collecting_data = True

                    # if collecting data
                    if self.collecting_data:

                        # keep collecting data until finding 8 x 00001111 or until end of packet
                        while self.mid_counter_decode < 8 and current_index < 4096:
                            if data[current_index] == int('00001111', 2):
                                self.message_bytes += bytes({data[current_index]})
                                self.mid_counter_decode += 1
                            else:
                                self.message_bytes += bytes({data[current_index]})
                                self.mid_counter_decode = 0

                            current_index += 1

                        # if end pattern is found then stop collecting data
                        if self.mid_counter_decode == 8:
                            self.finished_message = True

                        if self.finished_message:

                            # keep collecting data until finding 8 x 00001111 or until end of packet
                            while self.end_counter_decode < 8 and current_index < 4096:
                                if data[current_index] == int('00001111', 2):
                                    self.message_digest_bytes += bytes({data[current_index]})
                                    self.end_counter_decode += 1
                                else:
                                    self.message_digest_bytes += bytes({data[current_index]})
                                    self.end_counter_decode = 0

                                current_index += 1

                        # if end pattern is found then stop collecting data
                        if self.end_counter_decode == 8:
                            self.finished_all = True

                    if self.finished_all:
                        #### MESSAGE #####
                        # Convert bytes to string binary
                        message_bin = ""
                        for byte in self.message_bytes:
                            bin_str = bin(byte)[2:]
                            for i in range(8 - len(bin_str)):
                                bin_str = "0" + bin_str

                            message_bin += bin_str[self.key[self.key_counter_decode]]
                            self.key_counter_decode = (self.key_counter_decode + 1) % len(self.key)

                        # Convert string binary to string
                        message = ""
                        message_bin = message_bin[:-8]
                        for i in range(0, len(message_bin), 8):
                            message = bytes({int(message_bin[i:i + 8], 2)}).decode("utf-8") + message

                        self.key_counter_decode = 0
                        ##### MESSAGE DIGEST #####
                        # Convert bytes to string binary
                        message_digest_bin = ""
                        for byte in self.message_digest_bytes:
                            bin_str = bin(byte)[2:]
                            for i in range(8 - len(bin_str)):
                                bin_str = "0" + bin_str

                            message_digest_bin += bin_str[self.key[self.key_counter_decode]]
                            self.key_counter_decode = (self.key_counter_decode + 1) % len(self.key)

                        # Convert string binary to string
                        message_digest = ""
                        message_digest_bin = message_digest_bin[:-8]
                        for i in range(0, len(message_digest_bin), 8):
                            message_digest = bytes({int(message_digest_bin[i:i + 8], 2)}).decode("utf-8") + message_digest

                        # print
                        if message_digest == hashlib.sha512(message.encode("utf-8")).hexdigest():
                            print(message) #TODO do whatever you want with the message

                        self.reset_global_variables_listen()
            except Exception as e:
                break

        # Close connection
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

        self.reset_global_variables_listen()


    def speak(self):
        while not self.end_call:
            try:
                # Get data from mic
                data = self.input_stream.read(self.INPUT_BUFFER)

                # If there is data to be encoded then encode the data before sending
                if self.encode_data:

                    # Insert data
                    modified_data = b''
                    current_index = 0

                    if self.first_round:
                        # Set the start pattern (8 x 00001111)
                        for i in range(8):
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                        self.first_round = False

                    # Insert data until end of message binary or end of packet
                    while current_index < 4096 and self.message_counter < len(self.message_binary):
                        if self.message_binary[self.message_counter] == "1":
                            modified_data += bytes({data[current_index] | self.get_bitwise_data(1, self.key[self.key_counter_encode])})
                        else:
                            modified_data += bytes({data[current_index] & self.get_bitwise_data(0, self.key[self.key_counter_encode])})
                        self.key_counter_encode = (self.key_counter_encode + 1) % len(self.key)
                        self.message_counter += 1
                        current_index += 1

                    # If completed the message then start inserting the mid pattern
                    if self.message_counter == len(self.message_binary):

                        # insert 8 OR until end of packet
                        while current_index < 4096 and self.mid_counter_encode < 8:
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                            self.mid_counter_encode += 1

                            self.key_counter_encode = 0

                    # If the mid pattern is completed then start sending message digest
                    if self.mid_counter_encode == 8:
                        while current_index < 4096 and self.message_digest_counter < len(self.message_digest_binary):
                            if self.message_digest_binary[self.message_digest_counter] == "1":
                                modified_data += bytes({data[current_index] | self.get_bitwise_data(1, self.key[self.key_counter_encode])})
                            else:
                                modified_data += bytes({data[current_index] & self.get_bitwise_data(0, self.key[self.key_counter_encode])})
                            self.key_counter_encode = (self.key_counter_encode + 1) % len(self.key)
                            self.message_digest_counter += 1
                            current_index += 1

                    # If completed the message digest then start inserting the end pattern
                    if self.message_counter == len(self.message_binary):

                        # insert 8 OR until end of packet
                        while current_index < 4096 and self.end_counter_encode < 8:
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                            self.end_counter_encode += 1

                    # If end pattern is completed then end
                    if self.end_counter_encode == 8:
                        while current_index < 4096:
                            modified_data += bytes({data[current_index]})
                            current_index += 1
                        self.reset_global_variables_speak()

                    self.sock.send(modified_data)
                    continue

                # Send normal data when no message
                self.sock.send(data)
            except Exception as e:
                break

        # Close connection
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print("Call ended")

        except Exception as e:
            print("Call ended")

        self.reset_global_variables_speak()


    def send_message(self, message):
        self.message_binary = bin(int.from_bytes(bytes(message, 'utf-8'), byteorder='little'))[2:]

        message_digest = hashlib.sha512(message.encode("utf-8")).hexdigest()
        self.message_digest_binary = bin(int.from_bytes(bytes(message_digest, 'utf-8'), byteorder='little'))[2:]

        if len(self.message_binary) % 8 != 0:
            for i in range(8 - (len(self.message_binary) % 8)):
                self.message_binary = "0" + self.message_binary

        if len(self.message_digest_binary) % 8 != 0:
            for i in range(8 - (len(self.message_digest_binary) % 8)):
                self.message_digest_binary = "0" + self.message_digest_binary

        self.encode_data = True


    def end(self):
        self.end_call = True







if __name__ == '__main__':
    host = '192.168.0.111'
    port = 10001

    s = Sender(host, port, [1, 5, 3, 4, 0, 7, 2, 6])
    s.call()


    # Send a message after 3 seconds (For testing)
    time.sleep(1)
    s.send_message("Wild potato species, originating in modern-day Peru, can be found throughout the Americas, from Canada to southern Chile.[3] The potato was originally believed to have been domesticated by indigenous peoples of the Americas independently in multiple locations,[4] but later genetic testing of the wide variety of cultivars and wild species traced a single origin for potatoes. In the area of present-day southern Peru and extreme northwestern Bolivia, from a species in the Solanum brevicaule complex, potatoes were domesticated approximately 7,000-10,000 years ago.[5][6][7] In the Andes region of South America, where the species is indigenous, some close relatives of the potato are cultivated.")
    # Send a message after 3 seconds (For testing)
    time.sleep(10)
    s.send_message("Hello this is a message 2")

    # End call (for testing)
    time.sleep(10)
    s.end()













# # Global variables
# message = ""
# message_binary = ""
# message_counter = 0
# end_counter = 0
#
# encode_data = False
# first_round = True
#
# key = [1, 5, 3, 4, 0, 4, 2, 2]
# key_counter = 0
#
#
#
#
# ##### Get the bits to OR or AND with the data #####
# def get_bitwise_data(value, position):
#     if value==0:
#         bitwise_str = "11111111"
#         final_bitwise_str = bitwise_str[:2 + position] + "0" + bitwise_str[3 + position:]
#     else:
#         bitwise_str = "00000000"
#         final_bitwise_str = bitwise_str[:2 + position] + "1" + bitwise_str[3 + position:]
#     return int(final_bitwise_str, 2)
#
# def reset_global_variables():
#     global message, message_binary, message_counter, key_counter, encode_data, first_round, end_counter
#     message = ""
#     message_binary = ""
#     message_counter = 0
#
#     encode_data = False
#     first_round = True
#
#     key_counter = 0
#     end_counter = 0
#
# ##### Call function for sending (pick up mic data and send) ######
# def sender(host, port):
#     global message, message_binary, message_counter, key_counter, encode_data, first_round, end_counter
#
#
#     ##### Socket Initialization #####
#     # Call #
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((host, port))
#
#     ##### Pyaudio Initialization #####
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 2
#     RATE = 44100
#     BUFFER = 1024
#
#     p = pyaudio.PyAudio()
#     input_stream = p.open(format=FORMAT,
#                           input=True, rate=RATE, channels=CHANNELS,
#                           frames_per_buffer=BUFFER)
#     output_stream = p.open(format=FORMAT,
#                            output=True, rate=RATE, channels=CHANNELS,
#                            frames_per_buffer=BUFFER)
#
#     while True:
#         # Get data from mic
#         data = input_stream.read(BUFFER)
#
#         # If there is data to be encoded then encode the data before sending
#         if encode_data:
#
#             # Insert data
#             modified_data = b''
#             current_index = 0
#
#             if first_round:
#                 # Set the start pattern (8 x 00001111)
#                 for i in range(8):
#                     modified_data += bytes({int('00001111', 2)})
#                     current_index += 1
#                 first_round = False
#
#             # Insert data until end of message binary or end of packet
#             while current_index < 4096 and message_counter < len(message_binary):
#                 if message_binary[message_counter] == "1":
#                     modified_data += bytes({data[current_index] | get_bitwise_data(1, key[key_counter])})
#                 else:
#                     modified_data += bytes({data[current_index] & get_bitwise_data(0, key[key_counter])})
#                 key_counter = (key_counter + 1) % len(key)
#                 message_counter += 1
#                 current_index += 1
#
#             # If completed the message then start inserting the end pattern
#             if message_counter == len(message_binary):
#
#                 # insert 8 OR until end of packet
#                 while current_index < 4096 and end_counter < 8:
#                     modified_data += bytes({int('00001111', 2)})
#                     current_index += 1
#                     end_counter += 1
#
#             # If the end pattern is completed then done
#             if end_counter == 8:
#                 while current_index < 4096:
#                     modified_data += bytes({data[current_index]})
#                     current_index += 1
#                 reset_global_variables()
#
#             s.send(modified_data)
#             continue
#
#         # Send normal data when no message
#         s.send(data)
#
#         # Recieve data
#         # data_recv = s.recv(BUFFER)
#         # if data_recv:
#         #     output_stream.write(data_recv)
#
#
# if __name__ == '__main__':
#     host = '192.168.0.111'
#     port = 10001
#
#     sender_thread = threading.Thread(target=sender, args=(host, port,))
#     sender_thread.start()
#
#     while True:
#         print("Please enter a message: ")
#         message = str(input())
#         message_binary = bin(int.from_bytes(bytes(message, 'utf-8'), byteorder='little'))[2:]
#
#         if len(message_binary) % 8 != 0:
#             for i in range(8-(len(message_binary) % 8)):
#                 message_binary = "0"+message_binary
#
#         encode_data = True