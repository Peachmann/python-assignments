import socket
import sys
import re
import threading
from knapsack import Merkle_Hellman
from clientMenu import get_choice
from clientMenu import get_yes_or_no
from clientMenu import get_input

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_username = ""
        self.client_port = 0
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_public_key = ""
        self.client_private_key = ""
        self.chat_partner_key = ""
        self.chat_partner_port = 0
        self.chat_partner_username = ""
        self.running = True
        self.recieve_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mh = Merkle_Hellman()

    def tuple_to_string(self, tpl):
        return ",".join(list(map(lambda x: str(x), tpl)))

    def string_to_tuple(self, string):
        return tuple(map(lambda x: int(x), string.split(',')))

    def list_to_string(self, lst):
        return ",".join(map(lambda x: str(x), lst))

    def string_to_list(self, string):
        return list(map(lambda x: int(x), string.split(',')))

    def listen_to_peer(self, peer, address):
        print("[INFO] Client connected from %s:%s."%(address[0], address[1]))
        size = 1024

        while True:
            try:
                data = peer.recv(size)
                if data:
                    parsed_data = data.decode().split("#")
                    request_type = parsed_data[0]
                    
                    if (request_type == "hello"):
                        decrypted_message = self.mh.decrypt_mh(self.string_to_list(parsed_data[1]), self.client_private_key).split("#")
                        print("[INFO] User '%s' from port '%s' sent a 'hello' request. Grabbing public key and sending ACK response."%(decrypted_message[0], decrypted_message[1]))
                        
                        key_request = "getkey#" + decrypted_message[0]
                        self.client_socket.send(key_request.encode())
                        
                        data_from_server = self.client_socket.recv(1024).decode().split("#")
                        ack_port = int(data_from_server[1])
                        ack_public_key = self.string_to_list(data_from_server[2])
                        ack_response = "ack#" + self.list_to_string(self.mh.encrypt_mh("Hello recieved. You can send messages.", ack_public_key))
                        
                        peer.send(ack_response.encode())

                    if (request_type == "ack"):
                        decrypted_message = self.mh.decrypt_mh(self.string_to_list(parsed_data[1]), self.client_private_key)
                        print("[INFO] I recieved ACK from '%s' on port '%s'"%(self.chat_partner_username, self.chat_partner_port))

                    if (request_type == "msg"):
                        print("Message from '%s': %s"%(parsed_data[1], parsed_data[2]))

                else:
                    raise NameError("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
            except:
                print("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
                peer.close()
                return False

    def accept_messages_thread(self):
        self.recieve_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recieve_socket.bind(('0.0.0.0', int(self.client_port)))
        self.recieve_socket.listen()
        while (self.running == True):
            peer, address = self.recieve_socket.accept()
            t1 = threading.Thread(target = self.listen_to_peer,args = (peer, address))
            t1.daemon = True
            t1.start()

    def do_register(self):
        if (self.client_port != 0):
            print("You can register only once per client!")
            return

        print("\nBeginning registration process\n")

        self.client_username = get_input("Username: ")
        while not re.match("^[A-Za-z]*$", self.client_username):
            print ("Error! Make sure you only use letters in your name")
            self.client_username = get_input("Username: ")

        self.client_port = get_input("Port (in range 10000-10999): ")
        while not re.match("^10[0-9]{3}$", self.client_port):
            print ("Error! Port must be in range 10000-10999!")
            self.client_port = get_input("Port: ")

        self.client_socket.connect((self.server_ip, self.server_port))

        # Generate public key with Knapsack
        self.client_private_key = Merkle_Hellman().generate_private_key()
        self.client_public_key = Merkle_Hellman().generate_public_key(self.client_private_key)

        data = "register#" + self.client_username + "#" + self.client_port + "#" + self.tuple_to_string(self.client_public_key)
        self.client_socket.send(data.encode())

        data_from_server = self.client_socket.recv(1024).decode().split("#")
        response_type = data_from_server[0]

        if (response_type == "error"):
            print(data_from_server[1])
            self.client_socket.close()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_username = ""
            self.client_port = 0
            self.do_register()
        else:
            print(data_from_server[1])
            t1 = threading.Thread(target=self.accept_messages_thread, args=())
            t1.daemon = True
            t1.start()

    def do_get_public_key(self):
        if (self.client_port == 0):
            print("You must be registered first!")
            return
        
        print("\nBeginning GetKey process\n")

        self.chat_partner_username = get_input("Chat partner username: ")
        while not re.match("^[A-Za-z]*$", self.chat_partner_username):
            print ("Error! The partner's name has only letters!")
            self.chat_partner_username = get_input("Username: ")

        data = "getkey#" + self.chat_partner_username
        self.client_socket.send(data.encode())

        data_from_server = self.client_socket.recv(1024).decode().split("#")
        response_type = data_from_server[0]

        if (response_type == "error"):
            self.chat_partner_username = ""
            print(data_from_server[1])
            print("Your partner's details are not set. Redo this section!")
        else:
            print("Partner's details set successfully. You can now send a message!")
            self.chat_partner_port = int(data_from_server[1])
            self.chat_partner_key = self.string_to_tuple(data_from_server[2])
            print("Your partner %s can be found on port %s with key %s"%(self.chat_partner_username, self.chat_partner_port, self.chat_partner_key))

    def do_send_message(self):
        if (self.chat_partner_key == "" or self.chat_partner_port == ""):
            print("You need to get a chat partner's details first!")
            return
        
        self.send_socket.close()
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.send_socket.connect((SERVER_IP, self.chat_partner_port))

        print ("\n[INFO] Starting chat process. Send '!end' as a message to return to the main menu.\n[INFO] Sending communication request.\n")
        request_type = "hello#"
        request_body = self.client_username + "#" + str(self.client_port)
        data = request_type + self.list_to_string(Merkle_Hellman().encrypt_mh(request_body, self.chat_partner_key))
        self.send_socket.send(data.encode())

        ack_response = self.send_socket.recv(1024).decode().split("#")
        print(ack_response)
        if (ack_response[0] != "ack"):
            return
        
        print(self.mh.decrypt_mh(self.string_to_list(ack_response[1]), self.client_private_key))

        message_text = "Enter message to send to '{}'".format(self.chat_partner_username)
        message = get_input(message_text)
        request_type = "msg#"
        while (message != "!end"):
            # Solitaire here
            data = request_type + self.client_username + "#" + message
            self.send_socket.send(data.encode())
            message = get_input(message_text)


    def do_exit(self):
        print("Thank you for using CryptoChat!")
        self.running = False
        self.client_socket.close()
        self.send_socket.close()
        self.recieve_socket.close()
        sys.exit()

    def do_kill(self):
        if (self.client_port == 0):
            print("You must register first!")
            return

        data = "kill#server"
        self.client_socket.send(data.encode())
        dataFromServer = self.client_socket.recv(1024)
        print(dataFromServer.decode())

    def run_client(self):
        command = int(get_choice("""
        1 - Register
        2 - Get public key of user
        3 - Send message
        4 - Exit client
        9 - Kill server

        Please choose a command's number! 
        """, "12349"))

        if command == 1:
            self.do_register()

        if command == 2:
            self.do_get_public_key()

        if command == 3:
            self.do_send_message()

        if command == 4:
            self.do_exit()
        
        if command == 9:
            self.do_kill()

client = Client(SERVER_IP, SERVER_PORT)

print("CryptoChat Client v0.1")
while True:
    client.run_client()
print("Goodbye!")


