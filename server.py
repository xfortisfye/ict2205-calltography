import socket
from _thread import *
import server_class
online_users = []
user_ip_dict = {}




def multi_threaded_controller(connection):


    proceed = True

    connection.send(str.encode('Connected to server'))

    server = server_class.Server_socket(connection)

    print("\n\n")
    print("=================================")
    print("Wait for client server authentication request")
    print("=================================")

    if (server.wait_auth()):
        print("Server authentication successful\n\n")
    else:
        proceed = False


    if proceed:
        print("=================================")
        print("Wait for client to start ECDH exchange")
        print("=================================")
        if(server.wait_exchange_ecdh()):
            print("ECDH exchange successful\n\n")
        else:
            proceed = False

    if proceed:
        print("=================================")
        print("Wait for client to provide a username")
        print("=================================")
        if(server.wait_username_check()):
            print("Client selected username\n\n")
        else:
            proceed = False

    if proceed:
        if(server.wait_call_select()):
            pass

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
    start_new_thread(multi_threaded_controller, (Client,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
serverSocket.close()
