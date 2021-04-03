import msg_processor
import cryptodriver
import time



online_users = []
user_ip_dict = {}

class Server_socket:


    def __init__(self, socket_obj):

        self.socket = socket_obj
        self.shared_key = ""
        self.client_server_aes_key = ""
        self.server_client_enc = False

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
                    username = msg_processor.get_content_field(msg)
                    if username and username not in online_users:
                        print("adding " + username + " to list of online users")
                        online_users.append(username)

                        user_ip_dict[username] = [self.ip, self.port]
                        response = "header: US_NICKNAME_STATUS content: ok [EOM]"
                        response = self.encrypt_content(response)
                        self.send_msg(response)
                        return True

                    else:
                        print("username: " + username + " is taken")
                        response = "header: US_NICKNAME_STATUS content: no [EOM]"
                        response = self.encrypt_content(response)
                        self.send_msg(response)


    def wait_call_select(self):
        while True:
            username_list = '{\n}'.join(online_users)

            response = "header: SE_AVAIL_USERS content: " + username_list + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
            response = self.encrypt_content(response)
            self.send_msg(response)
            time.sleep(10)