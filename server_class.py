import msg_processor
import cryptodriver
import time



online_users = []
user_ip_dict = {}

call_requests = {}
call_requests_status = {}


class Server_socket:


    def __init__(self, socket_obj):

        self.socket = socket_obj
        self.shared_key = ""
        self.client_server_aes_key = ""
        self.server_client_enc = False

        self.username = None

        self.ip = self.socket.getsockname()[0]
        self.port = self.socket.getsockname()[1]

    def send_msg(self, msg):
        self.socket.send(str.encode(msg))

    def recv_msg(self):
        return self.socket.recv(5120).decode('utf-8')


    def encrypt_content(self, data):
        return cryptodriver.encrypt_aes_gcm(self.client_server_aes_key, data)

    def decrypt_content(self, data):
        return cryptodriver.decrypt_aes_gcm(self.client_server_aes_key, data)


    def derive_aeskey(self):
        self.client_server_aes_key = cryptodriver.hkdf(16, self.shared_key.encode())

    def wait_auth(self):
        while True:
            msg = self.recv_msg()
            if msg_processor.get_header_field(msg) == "SE_AUTH_REQ":
                print("\n\n")
                print("=================================")
                print("Received AUTH request")
                print("=================================")

                recipient_key = msg_processor.get_content_field(msg).encode("ISO-8859-1")

                if recipient_key:
                    response = "header: SE_AUTH_REQ_RES content: ok [EOM]"
                    self.send_msg(response)

                    keypair = cryptodriver.get_rsa_keypair()
                    own_private_key = keypair[0]
                    own_public_key = keypair[1]
                    message = "place holder"
                    signature = cryptodriver.make_rsa_sig(own_private_key, message)
                    payload = own_public_key.decode("ISO-8859-1") + "{\n}" + signature.decode("ISO-8859-1")

                    encrypted_payload = cryptodriver.encrypt_rsa_aes(recipient_key, payload)
                    response = "header: SE_AUTH_SIG_KEY content: "+encrypted_payload+" [EOM]"
                    self.send_msg(response)
                    print("Sent encrypted pubkey and sig\n\n")
                    return True

    def wait_exchange_ecdh(self):
        while True:
            msg = self.recv_msg()
            if msg_processor.get_header_field(msg) == "US_PUB_KEY":
                print("=================================")
                print("Performing ECDH exchange")
                print("=================================")

                recipient_public_key = msg_processor.get_content_field(msg)
                key_obj = cryptodriver.make_dhe_key_obj()
                own_public_key = cryptodriver.make_dhe_keypair(key_obj)
                response = "header: SE_PUB_KEY content: "+own_public_key+" [EOM]"
                self.send_msg(response)

                self.shared_key = cryptodriver.make_dhe_sharedkey(key_obj,recipient_public_key)
                print("Client pub key is " + recipient_public_key)
                print("Server pub key is: " + own_public_key)
                print("Server shared key is: " + self.shared_key)
                self.server_client_enc = True
                self.derive_aeskey()

                print("ECDH exchange successful\n\n")
                return True

    def wait_username_check(self):
        while True:
            msg = self.recv_msg()
            if self.server_client_enc:
                msg = self.decrypt_content(msg)
                if msg and msg_processor.get_header_field(msg) == "US_NICKNAME":
                    self.username = msg_processor.get_content_field(msg)
                    if self.username and self.username not in online_users:
                        print("adding " + self.username + " to list of online users")

                        online_users.append(self.username)

                        user_ip_dict[self.username] = [self.ip, self.port]
                        call_requests[self.username] = False
                        call_requests_status[self.username] = False

                        response = "header: US_NICKNAME_STATUS content: ok [EOM]"
                        response = self.encrypt_content(response)
                        self.send_msg(response)
                        return True

                    else:
                        print("username: " + self.username + " is taken")
                        response = "header: US_NICKNAME_STATUS content: no [EOM]"
                        response = self.encrypt_content(response)
                        self.send_msg(response)


    def wait_call_select(self):
        while True:

            if self.server_client_enc:
                msg = self.recv_msg()
                msg = self.decrypt_content(msg)
                print("msg recieve")
                if msg and msg_processor.get_header_field(msg) == "SE_AVAIL_USERS_REQ":

                    username_list = '{\n}'.join(online_users)

                    response = "header: SE_AVAIL_USERS content: " + username_list + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                    response = self.encrypt_content(response)
                    self.send_msg(response)

                    # return True

                #response to client listener
                if msg and msg_processor.get_header_field(msg) == "CHECK_INC_CALL_REQ":
                    if call_requests[self.username] != False:

                        caller = call_requests[self.username]

                        response = "header: INC_CALL_REQ content: " + caller + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

                        response = self.encrypt_content(response)
                        self.send_msg(response)

                        msg = self.recv_msg()

                        if msg and msg_processor.get_header_field(msg) == "INC_CALL_REQ_RES":
                            call_response = msg_processor.get_content_field(msg)

                            if call_response == "ack":
                                call_requests_status[self.username] = "ack"
                            elif call_response == "dec":
                                call_requests_status[self.username] = "dec"

                        call_requests[self.username] = False
                    else:
                        response = "header: INC_CALL_REQ content: none [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        response = self.encrypt_content(response)
                        self.send_msg(response)


                #client wants to call someone
                if msg and msg_processor.get_header_field(msg) == "CALL_REQ":
                    call_target = msg_processor.get_content_field(msg)
                    if call_target in online_users:
                        call_requests_status[call_target]= "wait"

                        #todo implement checking to see if the value is filled
                        #if filled means someone 'calling this user'
                        call_requests[call_target] = self.username

                        time_elapsed=0

                        call_status = "waiting"

                        while True:
                            if time_elapsed >= 30:
                                break

                            if call_requests_status[call_target] == "ack":
                                call_status = "ack"
                                break

                            elif call_requests_status[call_target] == "dec":
                                call_status = "dec"
                                break

                            time.sleep(0.5)
                            time_elapsed +=0.5

                        if call_status == "ack":
                            response = "header: CALL_REQ_RES content: ack [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                            response = self.encrypt_content(response)
                            self.send_msg(response)

                        elif call_status == "waiting":
                            response = "header: CALL_REQ_RES content: timeout [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                            response = self.encrypt_content(response)
                            self.send_msg(response)

                        elif call_status == "dec":
                            response = "header: CALL_REQ_RES content: dec [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                            response = self.encrypt_content(response)
                            self.send_msg(response)


    def listen_call_req(self):
        while True:
            if call_requests[self.username] != False:

                caller = call_requests[self.username]

                response = "header: INC_CALL_REQ content: "+caller+" [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

                response = self.encrypt_content(response)
                self.send_msg(response)

                msg = self.recv_msg()

                if msg and msg_processor.get_header_field(msg) == "INC_CALL_REQ_RES":
                    call_response = msg_processor.get_content_field(msg)

                    if call_response == "ack":
                        call_requests_status[self.username] = "ack"
                    elif call_response == "dec":
                        call_requests_status[self.username] = "dec"

                call_requests[self.username] = False

