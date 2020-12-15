import socket
import sys
import re
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
        self.client_public_key = "TEST"
        self.client_private_key = "TEST"
        self.chat_partner_key = "PARTNERKEY"
        self.chat_partner_port = 0
        self.chat_partner_username = ""

    def tuple_to_string(self, tpl):
        return ",".join(list(map(lambda x: str(x), tpl)))

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

        self.client_socket.bind(('0.0.0.0', int(self.client_port)))
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
            self.chat_partner_port = data_from_server[1]
            self.chat_partner_key = data_from_server[2]
            print("Your partner %s can be found on port %s with key %s"%(self.chat_partner_username, self.chat_partner_port, self.chat_partner_key))

    def do_send_message(self):
        print("Send")

    def do_exit(self):
        print("Thank you for using CryptoChat!")
        self.client_socket.close()
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


