import msg_processor
import cryptodriver


class Client:

    def __init__(self, socket_obj):

        self.socket = socket_obj
        self.shared_key = ""
        self.client_server_aes_key = ""
        self.server_client_enc = False

    def send_msg(self, msg):
        self.socket.send(str.encode(msg))

    def recv_msg(self):
        return self.socket.recv(5120).decode('utf-8')

    def encrypt_content(self, msg):
        pass

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

            msg = "header: SE_AUTH_REQ content: " + own_public_key.decode(
                "ISO-8859-1") + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
            self.send_msg(msg)

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
                                # msg = "header: SE_AUTH_SIG_KEY_RES content: ok [EOM]"
                                # self.send_msg(msg)
                                return True
                            else:
                                print("server verification failed retrying..")
                                retries += 1

    def exchange_ecdh(self):
        while True:

            key_obj = cryptodriver.make_dhe_key_obj()
            own_public_key = cryptodriver.make_dhe_keypair(key_obj)

            msg = "header: US_PUB_KEY content: " + own_public_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

            self.send_msg(msg)

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

    def set_username(self):
        if self.server_client_enc:
            while True:
                # send nickname to server
                # username = input("Enter Username: ")
                # msg = "header: US_NICKNAME content: " + username + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                msg = "Hi this is client"
                print("\n\nAES KEY:")
                print(self.client_server_aes_key)
                msg = cryptodriver.encrypt_aes_gcm(self.client_server_aes_key, msg)


                self.send_msg(msg)

                # receive response
                msg = self.recv_msg()
                cryptodriver.decrypt_aes_gcm(self.client_server_aes_key, msg)
                return True
                # # check if username is accepted by the server
                # if msg_processor.get_header_field(msg) == "US_NICKNAME_STATUS":
                #     if msg_processor.get_content_field(msg) == "ok":
                #         return True
                #     else:
                #         print("username taken pls try again")
