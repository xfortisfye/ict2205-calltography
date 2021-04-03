import socket
import client_class

server_pub_key =    "-----BEGIN PUBLIC KEY-----\n" \
                    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAj/Lc8hNnwdVdpEjnIGAD\n" \
                    "qUiViWp+xrEdCjun/Ds2lHErQlvdZj8bcSvkEZkgmMRgNQMqfS3PDQoY/7I1Ffok\n" \
                    "0+wCsIXdEzFvuAh23i/0yLXBItjz2NbhUQlfw+hdtupfBcfbBxwNjYSxuvo58KJi\n" \
                    "lwDF86N0l96+dVyDoWqPrHzhLdGe9J71/o8KGdNtc1KPbtsglkg6Bo9ikjLioR+y\n" \
                    "MO3D36T3cYTVfRQInEqIk69GZkLsiUjUkP4ZL5Vb2E7zvuhMcnxEPNgQOcQv+op+\n" \
                    "amT0evCw//t4LOi36apyzvDlBj7Q4GPIrR/CyEhg8Ou4y+bonXW1WSUGsP3+/tF9\n" \
                    "5QIDAQAB\n" \
                    "-----END PUBLIC KEY-----" \




ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 8888


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


print('Waiting for connection response')

try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

res = ClientMultiSocket.recv(1024)

print(res.decode('utf-8'))
if res:

    proceed = True

    client = client_class.Client(ClientMultiSocket)
    print("\n\n")
    print("=================================")
    print("Performing server authentication")
    print("=================================")

    if(client.auth_server()):
        print("Server authentication successful\n\n")
    else:
        proceed = False

    print("=================================")
    print("Performing ECDH exchange")
    print("=================================")

    if proceed:
        if(client.exchange_ecdh()):
            print("ECDH exchange successful\n\n")
        else:
            proceed = False

    print("=================================")
    print("Performing aes-gcm communication")
    print("=================================")

    if proceed:
        if(client.set_username()):
            print("aes-gcm message decrypt successful\n\n")
            pass
            #print("Username set")


ClientMultiSocket.close()
