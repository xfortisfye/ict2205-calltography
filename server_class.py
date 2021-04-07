import msg_processor
import cryptodriver
import time

online_users = []
user_ip_dict = {}

call_requests = {}
call_requests_status = {}
call_key_exchange = {}


class Server_socket:

    def __init__(self, socket_obj):

        self.socket = socket_obj
        self.shared_key = ""
        self.client_server_aes_key = ""
        self.server_client_enc = False

        self.username = None
        self.caller = None
        self.call_target = None

        self.ip = self.socket.getpeername()[0]
        self.port = self.socket.getpeername()[1]

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

    # removes user from the list of online users
    def remove_user(self):
        try:
            online_users.remove(self.username)
        except:
            print("failed to remove username")

    def wait_auth(self):
        while True:
            msg = self.recv_msg()

            msg = cryptodriver.decrypt_rsa_aes(open('server_rsa_priv_key.pem').read(), msg).decode('utf-8')

            if msg_processor.get_header_field(msg) == "SE_AUTH_REQ":
                print("\n\n")
                print("=================================")
                print("Received AUTH request")
                print("=================================")

                content = msg_processor.get_content_field(msg).split("{\n}")

                recipient_key = content[0].encode("ISO-8859-1")

                recipient_ecdh = content[1]

                if recipient_key:
                    response = "header: SE_AUTH_REQ_RES content: ok [EOM]"
                    self.send_msg(response)

                    # gen rsa keypair
                    keypair = cryptodriver.get_rsa_keypair()
                    own_rsa_private_key = keypair[0]
                    own_rsa_public_key = keypair[1]
                    message = "place holder"

                    key_obj = cryptodriver.make_dhe_key_obj()
                    own_dhe_public_key = cryptodriver.make_dhe_keypair(key_obj)

                    signature = cryptodriver.make_rsa_sig(own_rsa_private_key, message)
                    payload = own_rsa_public_key.decode("ISO-8859-1") + "{\n}" + signature.decode(
                        "ISO-8859-1") + "{\n}" + own_dhe_public_key

                    encrypted_payload = cryptodriver.encrypt_rsa_aes(recipient_key, payload)
                    response = "header: SE_AUTH_SIG_KEY content: " + encrypted_payload + " [EOM]"
                    self.send_msg(response)

                    self.shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_ecdh)
                    print("Client pub key is " + recipient_ecdh)
                    print("Server pub key is: " + own_dhe_public_key)
                    print("Server shared key is: " + self.shared_key)
                    self.server_client_enc = True
                    self.derive_aeskey()

                    print("Auth done\n\n")

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
                response = "header: SE_PUB_KEY content: " + own_public_key + " [EOM]"
                self.send_msg(response)

                self.shared_key = cryptodriver.make_dhe_sharedkey(key_obj, recipient_public_key)
                print("Client pub key is " + recipient_public_key)
                print("Server pub key is: " + own_public_key)
                print("Server shared key is: " + self.shared_key)
                self.server_client_enc = True
                self.derive_aeskey()

                print("ECDH exchange successful\n\n")
                return True

    # waits for user to enter username
    def wait_username_check(self):
        while True:
            if self.server_client_enc:
                msg = self.recv_enc_msg()
                if msg and msg_processor.get_header_field(msg) == "US_NICKNAME":
                    self.username = msg_processor.get_content_field(msg)
                    if self.username and self.username not in online_users:
                        print("adding " + self.username + " to list of online users")

                        online_users.append(self.username)

                        user_ip_dict[self.username] = [self.ip, self.port]
                        call_requests[self.username] = False
                        call_requests_status[self.username] = False

                        response = "header: US_NICKNAME_STATUS content: ok [EOM]"
                        self.send_enc_msg(response)

                        return True

                    else:
                        print("username: " + self.username + " is taken")
                        response = "header: US_NICKNAME_STATUS content: no [EOM]"
                        self.send_enc_msg(response)

    def wait_call_select(self):
        while True:

            if self.server_client_enc:

                msg = self.recv_enc_msg()

                if msg and msg_processor.get_header_field(msg) == "SE_AVAIL_USERS_REQ":
                    username_list = '{\n}'.join(online_users)

                    response = "header: SE_AVAIL_USERS content: " + username_list + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                    self.send_enc_msg(response)

                # response to client listener
                elif msg and msg_processor.get_header_field(msg) == "CHECK_INC_CALL_REQ":
                    self.incoming_call_request(msg)

                elif msg and msg_processor.get_header_field(msg) == "INC_CALL_STATUS":

                    self.call_status_check()

                elif msg and msg_processor.get_header_field(msg) == "INC_CALL_REQ_RES":
                    self.incoming_call_response_check(msg)

                # client wants to call someone
                elif msg and msg_processor.get_header_field(msg) == "CALL_REQ":
                    self.send_call_request(msg)

    def call_status_check(self):

        if call_requests_status[self.username] == "canc":
            response = "header: INC_CALL_STATUS_RES content: canc [EOM]"
            # call_requests_status.pop(self.caller)
            call_requests_status[self.caller] = False
            call_requests[self.username] = False


        elif call_requests_status[self.username] == "timeout":
            response = "header: INC_CALL_STATUS_RES content: timeout [EOM]"
            # call_requests_status.pop(self.caller)
            call_requests_status[self.caller] = False
            call_requests[self.username] = False

        else:
            response = "header: INC_CALL_STATUS_RES content: waiting [EOM]"
        print("sending : " + response)
        self.send_enc_msg(response)

    def incoming_call_request(self, msg):
        # checks if call_request has been set (aka check if there is anyone wanting to call the user)
        if call_requests[self.username]:
            # if call_request has been set

            # get the caller username
            self.caller = call_requests[self.username]

            # build incoming call request
            response = "header: INC_CALL_REQ content: " + self.caller + " [EOM]"

            # send response
            self.send_enc_msg(response)

        else:
            response = "header: INC_CALL_REQ content: none [EOM]"
            self.send_enc_msg(response)

    def incoming_call_response_check(self, msg):
        # checks if msg is a incoming call request response

        # get the user response
        call_response = msg_processor.get_content_field(msg)

        # if user acknowledges the call
        if call_response == "ack" and self.caller:
            call_requests_status[self.username] = "ack"
            self.call_target_exchange_ip_ecdh()

        # if user declines the call
        elif call_response == "dec":
            call_requests_status[self.username] = "dec"
            print("call declined")

        # if call is cancelled
        elif call_response == "canc":
            call_requests_status[self.call_target] = "canc"
            print("call cancelled")

        call_requests[self.username] = False

    def send_call_request(self, msg):
        # get call_target
        self.call_target = msg_processor.get_content_field(msg)
        print("call request recieved")

        # check if call_target is in the available list of users
        if self.call_target in online_users:
            call_requests_status[self.call_target] = "wait"

            # todo implement checking to see if the value is filled
            # set call_requests (aka indicate to calltarget server socket this user wants to call the call target)
            call_requests[self.call_target] = self.username

            # check shared memory for call status timeout 30 seconds
            time_elapsed = 0

            while True:

                msg = self.recv_enc_msg()
                if msg and msg_processor.get_header_field(msg) == "CALL_REQ_STATUS":
                    status = msg_processor.get_content_field(msg)
                    # check call status
                    if status == "ok":
                        pass  # continue loopuing as per usual
                    # elif status is cancelled
                    elif status == "canc":
                        call_requests_status[self.call_target] = "canc"
                        print("call cancelled")
                        #
                        break

                    # if timeout
                    if time_elapsed >= 30:
                        response = "header: CALL_REQ_RES content: timeout [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        self.send_enc_msg(response)
                        call_requests_status[self.call_target] = 'timeout'
                        break

                    # if call_target has acknowledged
                    elif call_requests_status[self.call_target] == "ack":
                        # build
                        print("acked")
                        response = "header: CALL_REQ_RES content: ack [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        self.send_enc_msg(response)
                        self.caller_exchange_ip_ecdh()
                        # call_requests_status.pop(self.call_target)
                        call_requests_status[self.call_target] = False
                        break

                    # else if call_target has declined
                    elif call_requests_status[self.call_target] == "dec":
                        response = "header: CALL_REQ_RES content: dec [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        self.send_enc_msg(response)

                        # call_requests_status.pop(self.call_target)
                        break


                    else:
                        response = "header: CALL_REQ_RES content: waiting [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag
                        self.send_enc_msg(response)

                    time.sleep(0.5)
                    time_elapsed += 0.5
                    print("time left" + str(30 - time_elapsed))

        else:
            # send user not found
            pass

    def call_target_exchange_ip_ecdh(self):

        # set status of call request to ack
        # this lets the server socket on the caller side know the user has accepted the call

        # =============== EXCHANGE IP =============== #
        # get caller ip (to send to the user)
        caller_ip = str(user_ip_dict[self.caller][0])

        # build ip response
        response = "header: CALLER_IP content: " + caller_ip + " [EOM]"

        # send response
        self.send_enc_msg(response)

        # =============== EXCHANGE ECDH =============== #
        # get user response
        msg = self.recv_enc_msg()
        print("Client manage to send the message: " + msg)

        # checks if msg is for public key exchange
        if msg and msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
            # get the public key in the msg
            recipient_public_key = msg_processor.get_content_field(msg)

            # loads public key 'shared' memory
            call_key_exchange[self.username] = recipient_public_key

            # waits for caller public key
            call_target_key = self.wait_for_user_pub_key(self.caller)

            # build caller public response
            response = "header: CALL_PUB_KEY content: " + call_target_key + " [EOM]"

            # send response
            self.send_enc_msg(response)
            print("sending to client" + response)

    def caller_exchange_ip_ecdh(self):
        # =============== EXCHANGE IP =============== #
        # get call_target ip (to send to the user)
        call_target_ip = str(user_ip_dict[self.call_target][0])
        
        print("L call target ip" + call_target_ip)
        # build ip response
        response = "header: CALLER_IP content: " + call_target_ip + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

        # send response
        self.send_enc_msg(response)
        print("L call target response " + response)
        # =============== EXCHANGE ECDH =============== #
        # waits for call_target public key
        call_target_key = self.wait_for_user_pub_key(self.call_target)

        # build call_target public response
        response = "header: CALL_PUB_KEY content: " + call_target_key + " [EOM]"  # msg structure smt like header=purpose of msg                                                    #contents== msg contents (e.g audio data, or nickname in this case                                                        #[EOM] signifies end of messag

        # send response
        self.send_enc_msg(response)

        msg = self.recv_enc_msg()

        # checks if msg is for public key exchange
        if msg and msg_processor.get_header_field(msg) == "CALL_PUB_KEY":
            # get the public key in the msg
            recipient_public_key = msg_processor.get_content_field(msg)

            # loads public key 'shared' memory
            call_key_exchange[self.username] = recipient_public_key

    def wait_for_user_pub_key(self, usr):
        while True:
            # if caller public key is found
            if usr in call_key_exchange:
                print(usr + " key is: " + call_key_exchange[usr])

                # get caller public key
                call_target_key = call_key_exchange[usr]

                # clean up 'shared' memory
                call_key_exchange.pop(usr)

                return call_target_key
