from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
import msg_processor
import cryptodriver
import time
import select


class WorkerSignals(QtCore.QObject):
    message_received = QtCore.pyqtSignal(str)


class SpeakServerWorker(QtCore.QThread):
    def __init__(self, role):
        super(SpeakServerWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.signals = WorkerSignals()
        self.role = role

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        
        while not self.role.end_call:
            print("while speak server loop")
            try:
                # Get data from mic
                data = self.role.input_stream.read(self.role.INPUT_BUFFER)

                # If there is data to be encoded then encode the data before sending
                if self.role.encode_data:

                    # Insert data
                    modified_data = b''
                    current_index = 0

                    if self.role.first_round:
                        # Set the start pattern (8 x 00001111)
                        for i in range(8):
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                        self.role.first_round = False

                    # Insert data until end of message binary or end of packet
                    while current_index < 4096 and self.role.message_counter < len(self.role.message_binary):
                        if self.role.message_binary[self.role.message_counter] == "1":
                            modified_data += bytes(
                                {data[current_index] | self.role.get_bitwise_data(1, self.role.key[self.role.key_counter_encode])})
                        else:
                            modified_data += bytes(
                                {data[current_index] & self.role.get_bitwise_data(0, self.role.key[self.role.key_counter_encode])})
                        self.role.key_counter_encode = (self.role.key_counter_encode + 1) % len(self.role.key)
                        self.role.message_counter += 1
                        current_index += 1

                    # If completed the message then start inserting the mid pattern
                    if self.role.message_counter == len(self.role.message_binary):

                        # insert 8 OR until end of packet
                        while current_index < 4096 and self.role.mid_counter_encode < 8:
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                            self.role.mid_counter_encode += 1

                            self.role.key_counter_encode = 0

                    # If the mid pattern is completed then start sending message digest
                    if self.role.mid_counter_encode == 8:
                        while current_index < 4096 and self.role.message_digest_counter < len(self.role.message_digest_binary):
                            if self.role.message_digest_binary[self.role.message_digest_counter] == "1":
                                modified_data += bytes(
                                    {data[current_index] | self.role.get_bitwise_data(1, self.role.key[self.role.key_counter_encode])})
                            else:
                                modified_data += bytes(
                                    {data[current_index] & self.role.get_bitwise_data(0, self.role.key[self.role.key_counter_encode])})
                            self.role.key_counter_encode = (self.role.key_counter_encode + 1) % len(self.role.key)
                            self.role.message_digest_counter += 1
                            current_index += 1

                    # If completed the message digest then start inserting the end pattern
                    if self.role.message_counter == len(self.role.message_binary):

                        # insert 8 OR until end of packet
                        while current_index < 4096 and self.role.end_counter_encode < 8:
                            modified_data += bytes({int('00001111', 2)})
                            current_index += 1
                            self.role.end_counter_encode += 1

                    # If end pattern is completed then end
                    if self.role.end_counter_encode == 8:
                        while current_index < 4096:
                            modified_data += bytes({data[current_index]})
                            current_index += 1
                        self.role.reset_global_variables_speak()

                    self.role.client.send(modified_data)
                    continue

                # Send normal data when no message
                self.role.client.send(data)
            except Exception as e:
                break

        # Close connection
        try:
            self.role.sock.shutdown(socket.SHUT_RDWR)
            self.role.sock.close()
            print("Call ended")

        except Exception as e:
            print("Call ended")

        self.role.reset_global_variables_speak()