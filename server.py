import socket
from _thread import *
import cryptodriver
online_users = []
user_ip_dict = {}

def get_header_field(msg):
    if msg.startswith("header: ") and msg.endswith(" [EOM]"):
        start_index = 8
        end_index = msg.find(" content: ")

        # "carve" out the field in the header field
        return msg[start_index: end_index]


def get_content_field(msg):
    if msg.endswith(" [EOM]"):
        start_index = msg.find(" content: ") + 10

        end_index = msg.find(" [EOM]")

        # "carve" out the field in the contents field
        return msg[start_index: end_index]


def multi_threaded_controller(connection, address):
    connection.send(str.encode('Connected to server'))
    while True:
        data = connection.recv(5120)
        #print(data.decode('utf-8'))
        if get_header_field(data.decode('utf-8')) == "END_CONN":
            print("ending connection")
            response = "header: END_CONN content: ok [EOM]"
            connection.send(str.encode(response))
            break

        elif get_header_field(data.decode('utf-8')) == "SE_AUTH_REQ":
            print("\n\n")
            print("=================================")
            print("Recieved AUTH request")
            print("=================================")

            recipient_key = get_content_field(data.decode('utf-8')).encode("ISO-8859-1")

            if recipient_key:
                response = "header: SE_AUTH_REQ_RES content: ok [EOM]"
                connection.send(str.encode(response))


                keypair = cryptodriver.get_rsa_keypair()
                own_private_key = keypair[0]
                own_public_key = keypair[1]
                message = "place holder"
                signature = cryptodriver.make_rsa_sig(own_private_key, message)
                payload = own_public_key.decode("ISO-8859-1") + "{\n}" + signature.decode("ISO-8859-1")

                encrypted_payload = cryptodriver.encrypt_rsa_aes(recipient_key, payload)
                response = "header: SE_AUTH_SIG_KEY content: "+encrypted_payload+" [EOM]"
                print("Sent encrypted pubkey and sig\n\n")



        #ecdh exchange
        elif get_header_field(data.decode('utf-8')) == "US_PUB_KEY":
            print("=================================")
            print("Performing ECDH exchange")
            print("=================================")
            recipient_public_key = get_content_field(data.decode('utf-8'))
            key_obj = cryptodriver.make_dhe_key_obj()
            own_public_key = cryptodriver.make_dhe_keypair(key_obj)
            response = "header: SE_PUB_KEY content: "+own_public_key+" [EOM]"

            shared_key = cryptodriver.make_dhe_sharedkey(key_obj,recipient_public_key)
            print("Client pub key is " + recipient_public_key)
            print("Server pub key is: " + own_public_key)
            print("Server shared key is: " + shared_key)
            server_client_enc = True
            aes_key = cryptodriver.hkdf(16, shared_key.encode())
            print("ECDH exchange successful\n\n")

        elif server_client_enc:
            print("=================================")
            print("Performing aes-gcm communication")
            print("=================================")
            msg = "Hi this is server"
            response = cryptodriver.encrypt_aes_gcm(aes_key, msg)
            connection.send(str.encode(response))
            print("\n\nAES KEY:")
            print(aes_key)
            cryptodriver.decrypt_aes_gcm(aes_key, data.decode())
            print("aes-gcm message decrypt successful\n\n")
            break
            # if get_header_field(data.decode('utf-8')) == "US_NICKNAME":
            #     username = get_content_field(data.decode('utf-8'))
            #     if username not in online_users:
            #         print("adding "+username+" to list of online users")
            #         online_users.append(username)
            #         user_ip_dict[username]= [address[0],address[1]]
            #         response = "header: US_NICKNAME_STATUS content: ok [EOM]"
            #
            #     else:
            #         print("username: " + username + " is taken")
            #         response = "header: US_NICKNAME_STATUS content: no [EOM]"


        else:
            print("invalid header purpose")
            #maybe put invalid header so client can resend
            #response = "header: END_CONN content: ok [EOM]"
            #connection.send(str.encode(response))
            break


        connection.send(str.encode(response))
    connection.close()


HOST = '127.0.0.1'  # currently set to localhost

PORT = 8888  # temp port (pls choose good port like 6969 or 420)

ThreadCount = 0

serverSocket = socket.socket()



try:
    serverSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

print('Server is listening...')

serverSocket.listen(5)

while True:
    Client, address = serverSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_controller, (Client,address,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSideSocket.close()
