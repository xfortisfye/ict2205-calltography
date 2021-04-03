import socket
import client_class




host = '127.0.0.1'
port = 8888

connection = socket.socket()


print('Waiting for connection response')

try:
    connection.connect((host, port))
except socket.error as e:
    print(str(e))

res = connection.recv(1024)

print(res.decode('utf-8'))
if res:

    proceed = True

    client = client_class.Client(connection)
    print("\n")
    print("=================================")
    print("Performing server authentication")
    print("=================================")

    if(client.auth_server()):
        print("Server authentication successful\n\n")
    else:
        proceed = False



    if proceed:
        print("=================================")
        print("Performing ECDH exchange")
        print("=================================")
        if(client.exchange_ecdh()):
            print("ECDH exchange successful\n\n")
        else:
            proceed = False



    if proceed:
        print("=================================")
        print("wait user enter username communication")
        print("=================================")
        if(client.set_username()):
            print("Username successfully set\n\n")
        else:
            proceed = False

    if proceed:
        if(client.idle()):
            print("waiting.....")

connection.close()
