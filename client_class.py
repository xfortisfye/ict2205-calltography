import msg_processor
import cryptodriver
import time
import select


class Client:

    def __init__(self, socket_obj):

        self.socket = socket_obj
        self.shared_key = ""
        self.client_server_aes_key = ""
        self.server_client_enc = False

        self.ip = self.socket.getsockname()[0]
        self.port = self.socket.getsockname()[1]

        self.listen_call = True



    def send_msg(self, msg):
        self.socket.send(str.encode(msg))

    def send_enc_msg(self, msg):
        msg = self.encrypt_content(msg)
        self.send_msg(msg)

    def recv_msg(self):
        return self.socket.recv(5120).decode('utf-8')

    def recv_enc_msg(self):
        msg = self.recv_msg()
        return self.decrypt_content(msg)

    def encrypt_content(self, data):
        return cryptodriver.encrypt_aes_gcm(self.client_server_aes_key, data)

    def decrypt_content(self, data):
        return cryptodriver.decrypt_aes_gcm(self.client_server_aes_key, data)

    def derive_aeskey(self):
        self.client_server_aes_key = cryptodriver.hkdf(16, self.shared_key.encode())

    def auth_server(self):
        retries = 0
        while True:

            if retries > 5:
                self.socket.close()
                print("socket closed")
                return False

            keypair = cryptodriver.get_rsa_keypair()
            own_private_key = keypair[0]
            own_public_key = keypair[1]

            response = "header: SE_AUTH_REQ content: " + own_public_key.decode(
                "ISO-8859-1") + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
            self.send_msg(response)

            msg = self.recv_msg()

            if msg_processor.get_header_field(msg) == "SE_AUTH_REQ_RES":
                if msg_processor.get_content_field(msg) == "ok":
                    print("SE_AUTH_REQ successfully sent")
                    # receive server sig & key encrypted with own public key
                    msg = self.recv_msg()

                    if msg_processor.get_header_field(msg) == "SE_AUTH_SIG_KEY":
                        encrypted_data = msg_processor.get_content_field(msg)
                        if encrypted_data:
                            key_sig = cryptodriver.decrypt_rsa_aes(own_private_key, encrypted_data).decode(
                                "utf-8").split("{\n}")
                            server_key = key_sig[0].encode("ISO-8859-1")
                            server_sig = key_sig[1].encode("ISO-8859-1")
                            server_auth = cryptodriver.verify_rsa_sig(server_key, "place holder", server_sig)
                            if server_auth:
                                print("server verification success")
                                return True
                            else:
                                print("server verification failed retrying..")
                                retries += 1

    def exchange_ecdh(self):
        while True:

            key_obj = cryptodriver.make_dhe_key_obj()
            own_public_key = cryptodriver.make_dhe_keypair(key_obj)

            response = "header: US_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

            self.send_msg(response)

            msg = self.recv_msg()

            if msg_processor.get_header_field(msg) == "SE_PUB_KEY":
                recipient_public_key = msg_processor.get_content_field(msg)

                self.shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_public_key)
                print("Server pub key is " + recipient_public_key)
                print("Client pub key is: " + own_public_key)
                print("Client shared key is: " + self.shared_key)
                self.server_client_enc = True
                self.derive_aeskey()
                return True
            else:
                return False

    def set_username(self, username):
        if self.server_client_enc:
            # send nickname to server

            response = "header: US_NICKNAME content: " + username + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

            self.send_enc_msg(response)

            # receive response
            msg = self.recv_enc_msg()

            # check if username is accepted by the server
            if msg and msg_processor.get_header_field(msg) == "US_NICKNAME_STATUS":
                if msg_processor.get_content_field(msg) == "ok":
                    return True
                else:
                    return False

    def get_online_users(self):

        if self.server_client_enc:
            # get online users from server

            response = "header: SE_AVAIL_USERS_REQ content: ok [EOM]"  # msg structure smt like header=purpose of msg
            self.send_enc_msg(response)

            # receive response
            msg = self.recv_enc_msg()

            # check if username is accepted by the server
            if msg and msg_processor.get_header_field(msg) == "SE_AVAIL_USERS":
                avail_user_list = msg_processor.get_content_field(msg).split("{\n}")
                return avail_user_list
            else:
                return None
        else:
            return None


    def initiate_call_req(self, call_target):
        print("calling....")

        response = "header: CALL_REQ content: " + call_target + " [EOM]"  # msg structure smt like header=purpose of msg
        response = self.encrypt_content(response)
        self.send_msg(response)




    def send_call_ack(self):
        response = "header: INC_CALL_REQ_RES content: ack [EOM]"  # msg structure smt like header=purpose of msg
        response = self.encrypt_content(response)

        self.send_msg(response)

        msg = self.recv_msg()
        msg = self.decrypt_content(msg)

        print(msg)
        if msg and msg_processor.get_header_field(msg) == "CALLER_IP":
            caller_ip = msg_processor.get_content_field(msg)
            print(caller_ip)

            key_obj = cryptodriver.make_dhe_key_obj()
            own_public_key = cryptodriver.make_dhe_keypair(key_obj)

            response = "header: CALL_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
            response = self.encrypt_content(response)
            self.send_msg(response)

            msg = self.recv_msg()
            msg = self.decrypt_content(msg)
            if msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
                recipient_public_key = msg_processor.get_content_field(msg)
                shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_public_key)
                print("Shared: key is: " + shared_key)
        return None

    def send_call_dec(self):
        response = "header: INC_CALL_REQ_RES content: dec [EOM]"  # msg structure smt like header=purpose of msg
        response = self.encrypt_content(response)

        self.send_msg(response)
        print("called declined")