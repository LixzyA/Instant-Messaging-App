#imports
import socket 
import threading
from database import *

class Client():
    def __init__(self, ip, port, name, client):
        self.ip = ip
        self.port = port
        self.name = name
        self.client = client

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

    def receive_messages(self, so):

        while True:
            incoming_buffer = so.recv(2048) #initialize the buffer
            if incoming_buffer:
                message = incoming_buffer.decode('utf-8')
                if 'CREATE USER' in message:
                    result = self.mydb.create_user(message.split()[2], None)
                    if result:
                        so.sendall('SINGUP SUCCESS'.encode('utf-8'))
                    else:
                        so.sendall('FAILED SIGNUP'.encode('utf-8'))
                elif 'LOGIN ' in message:
                    result = self.mydb.check_username_if_exists(message.split()[1])
                    if result:
                        so.sendall('LOGIN SUCCESS'.encode('utf-8'))
                    else:
                        so.sendall('FAILED Username doesn\'t exist'.encode('utf-8'))
                elif 'CHANGE USERNAME' in message:
                    result = self.mydb.change_username(message.split()[2], message.split()[3])
                    if result:
                        so.sendall('CHANGE USERNAME SUCCESS'.encode('utf-8'))
                    else:
                        so.sendall('FAILED CHANGE USERNAME'.encode('utf-8'))
                elif 'INIT FRIEND' in message:
                    result = self.mydb.list_friend(message.split()[2])
                    so.sendall(' '.join(result).encode('utf-8'))
                elif 'GET PROFILE' in message:
                    result = self.mydb.get_profile(message.split()[2])
                    if result:
                        so.sendall(result.encode('utf-8'))
                    else:
                        so.sendall('None'.encode('utf-8'))
                elif 'CHANGE PROFILE' in message:
                    result = self.mydb.change_profile(message.split()[2], message.split()[3])
                    if result:
                        so.sendall('CHANGE PROFILE SUCCESS'.encode('utf-8'))
                    else:
                        so.sendall('CHANGE PROFILE FAILED'.encode('utf-8'))
                else:
                    self.last_received_message = message
            else:
                break
        so.close()

    #broadcast the message to all clients 
    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket is not senders_socket:
                socket.sendall(self.last_received_message.encode('utf-8'))

    def send_message_to_client(self, target_client: Client):
        mydb.send_message(self.last_received_message, target= target_client , user_id= self.name)
        #send a message directly to the client if client is in
        #self.clients_list
        if target_client in self.clients_list:
            target_client.client.sendall(self.last_received_message.encode('utf-8'))
            
    def receive_messages_in_a_new_thread(self):
        while True:
            client = so, (ip, port) = self.server_socket.accept()
            print('Connected to ', ip, ':', str(port))
            client = Client(ip, port, self.last_received_message, so)
            self.add_to_clients_list(client)
            t = threading.Thread(target=self.receive_messages, args=(so,))
            t.start()

    #add a new client 
    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)


if __name__ == "__main__":
    ChatServer()
