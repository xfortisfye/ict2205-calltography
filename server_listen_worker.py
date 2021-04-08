from PyQt5 import QtCore

import traceback
import sys
from client_class import Client
from call_server import Receiver
import msg_processor
import cryptodriver
import hashlib
import time
import select


class WorkerSignals(QtCore.QObject):
    message_received = QtCore.pyqtSignal(str)


class ServerListenWorker(QtCore.QThread):
    def __init__(self, role):
        super(ServerListenWorker, self).__init__()

        self.signals = WorkerSignals()
        self.role = role

    @QtCore.pyqtSlot()
    def run(self):
        while not self.role.end_call:
            try:
                data = self.role.client.recv(self.role.OUTPUT_BUFFER)
                if data:
                    self.role.output_stream.write(data)
                    current_index = 0

                    # Not currently collecting data then...
                    if not self.role.collecting_data:

                        # Search for 00001111 to signify start of message
                        for i in range(8):
                            if data[i] == int('00001111', 2):
                                self.role.blank_counter += 1
                                current_index += 1
                            else:
                                self.role.blank_counter = 0
                                current_index += 1
                        if self.role.blank_counter == 8:
                            self.role.collecting_data = True

                    # if collecting data
                    if self.role.collecting_data:

                        # keep collecting data until finding 8 x 00001111 or until end of packet
                        while self.role.mid_counter_decode < 8 and current_index < 4096:
                            if data[current_index] == int('00001111', 2):
                                self.role.message_bytes += bytes({data[current_index]})
                                self.role.mid_counter_decode += 1
                            else:
                                self.role.message_bytes += bytes({data[current_index]})
                                self.role.mid_counter_decode = 0

                            current_index += 1

                        # if end pattern is found then stop collecting data
                        if self.role.mid_counter_decode == 8:
                            self.role.finished_message = True

                        if self.role.finished_message:
                            # keep collecting data until finding 8 x 00001111 or until end of packet
                            while self.role.end_counter_decode < 8 and current_index < 4096:
                                if data[current_index] == int('00001111', 2):
                                    self.role.message_digest_bytes += bytes({data[current_index]})
                                    self.role.end_counter_decode += 1
                                else:
                                    self.role.message_digest_bytes += bytes({data[current_index]})
                                    self.role.end_counter_decode = 0

                                current_index += 1

                        # if end pattern is found then stop collecting data
                        if self.role.end_counter_decode == 8:
                            self.role.finished_all = True

                    if self.role.finished_all:

                        #### MESSAGE #####
                        # Convert bytes to string binary
                        message_bin = ""
                        for byte in self.role.message_bytes:
                            bin_str = bin(byte)[2:]
                            for i in range(8 - len(bin_str)):
                                bin_str = "0" + bin_str

                            message_bin += bin_str[self.role.key[self.role.key_counter_decode]]
                            self.role.key_counter_decode = (self.role.key_counter_decode + 1) % len(self.role.key)

                        # Convert string binary to string
                        message = ""
                        message_bin = message_bin[:-8]

                        for i in range(0, len(message_bin), 8):
                            try:
                                message = bytes({int(message_bin[i:i + 8], 2)}).decode("utf-8") + message
                            except Exception as e:
                                print(e)

                        self.role.key_counter_decode = 0
                        ##### MESSAGE DIGEST #####
                        # Convert bytes to string binary
                        message_digest_bin = ""
                        for byte in self.role.message_digest_bytes:
                            bin_str = bin(byte)[2:]
                            for i in range(8 - len(bin_str)):
                                bin_str = "0" + bin_str

                            message_digest_bin += bin_str[self.role.key[self.role.key_counter_decode]]
                            self.role.key_counter_decode = (self.role.key_counter_decode + 1) % len(self.role.key)

                        # Convert string binary to string
                        message_digest = ""
                        message_digest_bin = message_digest_bin[:-8]
                        for i in range(0, len(message_digest_bin), 8):
                            message_digest = bytes({int(message_digest_bin[i:i + 8], 2)}).decode(
                                "utf-8") + message_digest

                        # print
                        if message_digest == hashlib.sha512(message.encode("utf-8")).hexdigest():
                            self.signals.message_received.emit(message)

                        self.role.reset_global_variables_listen()
            except Exception as e:
                break

        # Close connection
        try:
            #self.role.sock.shutdown(socket.SHUT_RDWR)
            self.role.sock.close()
            print("server listen: shutdown")
        except:
            print("server listen: shutdown" + str(e))
            pass

        self.role.reset_global_variables_listen()