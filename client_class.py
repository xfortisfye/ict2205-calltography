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

            # gen rsa keypair
            keypair = cryptodriver.get_rsa_keypair()
            own_rsa_private_key = keypair[0]
            own_rsa_public_key = keypair[1]

            # ecdh
            key_obj = cryptodriver.make_edhe_key_obj()
            own_edhe_public_key = cryptodriver.make_edhe_keypair(key_obj)

            # build response
            response = "header: SE_AUTH_REQ content: " + own_rsa_public_key.decode(
                "ISO-8859-1") + "{\n}" + own_edhe_public_key + " [EOM]"

            # encrypt with server public key
            response = cryptodriver.encrypt_rsa_aes(open('server_rsa_pub_key.pem').read(), response)

            self.send_msg(response)

            msg = self.recv_msg()

            if msg_processor.get_header_field(msg) == "SE_AUTH_REQ_RES":
                if msg_processor.get_content_field(msg) == "ok":
                    print("SE_AUTH_REQ successfully sent")
                    # receive server sig & pub rsa key & ecdh key encrypted with own public key
                    msg = self.recv_msg()

                    if msg_processor.get_header_field(msg) == "SE_AUTH_SIG_KEY":
                        encrypted_data = msg_processor.get_content_field(msg)
                        if encrypted_data:
                            key_sig = cryptodriver.decrypt_rsa_aes(own_rsa_private_key, encrypted_data).decode(
                                "utf-8").split("{\n}")

                            server_key = key_sig[0]
                            recipient_public_key = key_sig[1]
                            server_sig = key_sig[2]

                            sig_message = server_key+"{\n}"+recipient_public_key
                            hashed_sig_message = cryptodriver.sha512(sig_message)

                            server_auth = cryptodriver.verify_rsa_sig(server_key.encode("ISO-8859-1"),hashed_sig_message , server_sig.encode("ISO-8859-1"))
                            if server_auth:

                                self.shared_key = cryptodriver.make_edhe_sharedkey(key_obj, recipient_public_key)
                                print("Server pub key is " + recipient_public_key)
                                print("Client pub key is: " + own_edhe_public_key)
                                print("Client shared key is: " + self.shared_key)
                                self.server_client_enc = True
                                self.derive_aeskey()

                                print("Server auth done")

                                return True
                            else:
                                print("server verification failed retrying..")
                                retries += 1


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

    def send_call_dec(self):
        response = "header: INC_CALL_REQ_RES content: dec [EOM]"  # msg structure smt like header=purpose of msg
        response = self.encrypt_content(response)

        self.send_msg(response)

    def get_ip(self):
        return self.ip