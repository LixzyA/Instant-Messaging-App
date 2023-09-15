#imports
import socket 
import threading
from database import *

class Client():
    name: str = None
    def __init__(self, ip, port, socket):
        self.ip = ip
        self.port = port
        self.so = socket
    

class ChatServer:
    
    clients_list = []

    last_received_message = ""
    mydb = DB()

    def __init__(self):
        self.server_socket = None
        self.create_listening_server()

    #listen for incoming connection
    def create_listening_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket using TCP port and ipv4
        local_ip = '127.0.0.1'
        local_port = 10319
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("Listening for incoming messages..")
        self.server_socket.listen(5) #
        self.receive_messages_in_a_new_thread()

    def receive_messages(self, client: Client):

        while True:
            incoming_buffer = client.so.recv(2048) #initialize the buffer
            if incoming_buffer:
                message = incoming_buffer.decode('utf-8')
                if 'CREATE USER' in incoming_buffer.decode('utf-8'):
                    result = self.mydb.create_user(message.split()[2], None)
                    if result:
                        client.so.sendall('SIGNUP SUCCESS'.encode('utf-8'))
                        client.name = message.split()[2]
                    else:
                        client.so.sendall('FAILED SIGNUP'.encode('utf-8'))
                elif 'LOGIN ' in message:
                    result = self.mydb.check_username_if_exists(message.split()[1])
                    if result:
                        client.so.sendall('LOGIN SUCCESS'.encode('utf-8'))
                        client.name = message.split()[1]
                    else:
                        client.so.sendall('FAILED Username doesn\'t exist'.encode('utf-8'))
                elif 'CHANGE USERNAME' in message:
                    result = self.mydb.change_username(message.split()[2], message.split()[3])
                    if result:
                        client.so.sendall('CHANGE USERNAME SUCCESS'.encode('utf-8'))
                        client.name = message.split()[3]
                    else:
                        client.so.sendall('FAILED CHANGE USERNAME'.encode('utf-8'))
                elif 'INIT FRIEND' in message:
                    result = self.mydb.list_friend(message.split()[2])
                    if result not in [None, ' ', []]:
                        client.so.sendall(' '.join(result).encode('utf-8'))
                    else:
                        client.so.sendall('empty'.encode('utf-8'))
                elif 'ADD FRIEND' in message:
                    result = self.mydb.add_friend(message.split()[2], message.split()[3])
                    print(result)
                    if result:
                        client.so.sendall('Friend add success'.encode('utf-8'))
                    else:
                        client.so.sendall('Friend add failed'.encode('utf-8'))
                elif 'GET PROFILE' in message:
                    result = self.mydb.get_profile(message.split()[2])
                    if result:
                        client.so.sendall(result)
                    else:
                        client.so.sendall('None'.encode('utf-8'))
                elif 'CHANGE PROFILE' in message:
                    incoming_buffer = client.so.recv(16777215)
                    result = self.mydb.change_profile(message.split()[2], incoming_buffer)
                    if result:
                        client.so.sendall('CHANGE PROFILE SUCCESS'.encode('utf-8'))
                    else:
                        client.so.sendall('CHANGE PROFILE FAILED'.encode('utf-8'))
                elif 'CREATE GROUP' in message:
                    result = self.mydb.create_chatroom(room_type= 1, participants= message[2:].split(), room_name = '')
                else:
                    self.last_received_message = message
                    self.send_message_to_client(client)
            else:
                break
        client.so.close()

    #broadcast the message to all clients 
    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket is not senders_socket:
                socket.sendall(self.last_received_message.encode('utf-8'))

    def send_message_to_client(self, target_client: Client):
        #send a message directly to the client if client is in
        #self.clients_list
        sliced = self.last_received_message.split()
        sender = sliced[0]
        message = sliced[1:-1]
        receiver = sliced[-1]

        print(target_client.name)

        for client in self.clients_list:
            if receiver in target_client.name:
                client.so.sendall(' '.join(message).encode('utf-8'))
            
    def receive_messages_in_a_new_thread(self):
        while True:
            client = so, (ip, port) = self.server_socket.accept()
            print('Connected to ', ip, ':', str(port))
            client = Client(ip, port, so)
            self.add_to_clients_list(client)

            #should pass client instead of a socket
            t = threading.Thread(target=self.receive_messages, args=(client,))
            t.start()

    #add a new client 
    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)


if __name__ == "__main__":
    ChatServer()
