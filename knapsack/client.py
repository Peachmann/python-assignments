import socket
import sys
import re
import random
import threading
import traceback
from knapsack import Merkle_Hellman
from solitaire import Solitaire
from clientMenu import get_choice
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
        self.mh = Merkle_Hellman()
        self.sol = Solitaire()
        self.cards = {}

    # Various helper functions for string management
    def tuple_to_string(self, tpl):
        return ",".join(list(map(lambda x: str(x), tpl)))

    def string_to_tuple(self, string):
        return tuple(map(lambda x: int(x), string.split(',')))

    def list_to_string(self, lst):
        return ",".join(map(lambda x: str(x), lst))

    def string_to_list(self, string):
        return list(map(lambda x: int(x), string.split(',')))

    def handle_hello(self, peer, decrypted_message):
        """
        Function which handles inital handshake (hello message).
        """
        peer_username = decrypted_message[1]
        print("[INFO] User '%s' from port '%s' sent a 'hello' request. Grabbing public key and sending ACK response."%(peer_username, decrypted_message[2]))
                        
        key_request = "getkey#" + decrypted_message[1]
        self.client_socket.send(key_request.encode())
                        
        data_from_server = self.client_socket.recv(1024).decode().split("#")
        peer_public_key = self.string_to_list(data_from_server[2])
        ack_response = self.list_to_string(self.mh.encrypt_mh("ack#Hello recieved. You can send messages.", peer_public_key))
        peer.send(ack_response.encode())

        return peer_username, peer_public_key

    def handle_firstkey(self, peer, peer_username, peer_public_key, decrypted_message):
        """
        Function which handles the key exchange and common card generation.
        """
        print("[INFO] User '%s' sent me his part of the common key: %s"%(peer_username, decrypted_message[2]))
        key_2 = self.generate_random_secret()
        self.cards[peer_username] = self.sol.generate_cards(self.generate_common_secret(decrypted_message[2], key_2))
        print("[INFO] Cards generated: %s"%(self.cards[peer_username]))

        key_response = "secondkey#" + key_2
        data = self.list_to_string(self.mh.encrypt_mh(key_response, peer_public_key))
        peer.send(data.encode())

    def listen_to_peer(self, peer, address):
        """
        Function which handles each inbound connection on a separate thread.
        """
        
        print("[INFO] Client connected from %s:%s."%(address[0], address[1]))
        size = 1024
        peer_username = ''
        peer_public_key = ''

        while True:
            try:
                data = peer.recv(size)

                # Handle pre-messaging state (hello, key exchange) -> Decrypt message with Merkle-Hellman
                if data and peer_username not in self.cards:
                    decrypted_message = self.mh.decrypt_mh(self.string_to_list(data.decode()), self.client_private_key).split("#")
                    request_type = decrypted_message[0]
                    
                    if (request_type == "hello"):
                        peer_username, peer_public_key = self.handle_hello(peer, decrypted_message)

                    if (request_type == "firstkey"):
                        self.handle_firstkey(peer, peer_username, peer_public_key, decrypted_message)
                
                # Handle messaging state (actual messages being sent) -> Decrypt message with Solitaire 
                elif data:
                    decrypted_message = self.sol.decrypt(self.cards[peer_username], data.decode())

                    # If message is "!bye", disconnect user 
                    if (decrypted_message == "!bye"):
                        print("[INFO] Peer '%s' said goodbye."%(peer_username))
                        peer.send(self.sol.encrypt(self.cards[peer_username], "!bye").encode())
                    print("[%s] -> me: %s"%(peer_username, decrypted_message))
                else:
                    print("[INFO] Peer disconnected at %s:%s."%(address[0], address[1]))
            
            # Any sudden socket closure is handled as a disconnect event
            except:
                traceback.print_exc()
                print("[INFO] Peer '%s' disconnected at %s:%s."%(peer_username, address[0], address[1]))
                peer.close()
                return False

    def accept_messages_thread(self):
        """
        Main thread which listens to inbound clients and assigns them a thread.
        """
        self.recieve_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recieve_socket.bind(('0.0.0.0', int(self.client_port)))
        self.recieve_socket.listen()
        while (self.running == True):
            peer, address = self.recieve_socket.accept()
            t1 = threading.Thread(target = self.listen_to_peer,args = (peer, address))
            t1.daemon = True
            t1.start()

    def do_register(self):
        """
        Function which handles the registration process.
        """
        if (self.client_port != 0):
            print("You can register only once per client!")
            return

        print("\nBeginning registration process\n")

        self.client_username = get_input("Username: ")
        while not re.match("^[A-Za-z]+$", self.client_username):
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

        # If any kind of error is responded from the server, restart the registartion process.
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
        """
        Function which handles the key acquiring process.
        """
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

        # If the specified user is not registered to the server, the client has to redo the query.
        if (response_type == "error"):
            self.chat_partner_username = ""
            print(data_from_server[1])
            print("Your partner's details are not set. Redo this section!")
        else:
            print("Partner's details set successfully. You can now send a message!")
            self.chat_partner_port = int(data_from_server[1])
            self.chat_partner_key = self.string_to_tuple(data_from_server[2])
            print("Your partner %s can be found on port %s with key %s"%(self.chat_partner_username, self.chat_partner_port, self.chat_partner_key))

    # Encryption helper functions
    def generate_random_secret(self):
        """
        Generates a key made up of 10 random 2 digit numbers joined as a string.
        """
        return ''.join(list(map(lambda x: str(random.randint(10, 99)), range(10))))

    def generate_common_secret(self, key_1, key_2):
        """
        Intertwines the two keys, creating a common secret.
        Ex. abc & 123 -> a1b2c3
        """
        return ''.join(map(''.join, zip(key_1, key_2)))

    def do_send_message(self):
        """
        Function which handles the messaging part.
        """
        if (self.chat_partner_key == "" or self.chat_partner_port == ""):
            print("[ERROR] You need to get a chat partner's details first!")
            return

        # As a client might change chat partners, always reinitialize a new socket (reuse port for optimal storage)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_socket.connect((SERVER_IP, self.chat_partner_port))

        # Encrypt the pre-messaging stages with Merkle-Hellman
        print ("\n[INFO] Starting chat process. Send '!bye' as a message to return to the main menu.\n[INFO] Sending communication request.\n")
        request_body = "hello#" + self.client_username + "#" + str(self.client_port)
        data = self.list_to_string(self.mh.encrypt_mh(request_body, self.chat_partner_key))
        send_socket.send(data.encode())

        ack_response = send_socket.recv(1024).decode()
        decrpyed_response = self.mh.decrypt_mh(self.string_to_list(ack_response), self.client_private_key).split('#')
        if (decrpyed_response[0] != "ack"):
            return

        print("[ACK] ACK recieved: %s"%(decrpyed_response[1]))
        cards_init = ''
        
        # If the current partner did not send the client a message yet (did not set its key),
        # start the key aquiring procedure
        if (self.chat_partner_username not in self.cards):
            key_1 = self.generate_random_secret()
            print("My key is: %s"%(key_1))
            request_body = "firstkey#" + self.client_username + "#" + key_1
            request = self.list_to_string(self.mh.encrypt_mh(request_body, self.chat_partner_key))
            send_socket.send(request.encode())

            key_response = send_socket.recv(1024).decode()
            decrpyed_response = self.mh.decrypt_mh(self.string_to_list(key_response), self.client_private_key).split('#')
        
            if (decrpyed_response[0] == "secondkey"):
                cards_init = self.sol.generate_cards(self.generate_common_secret(key_1, decrpyed_response[1]))
                self.cards[self.chat_partner_username] = cards_init
        # If they already communicated, simply read the saved initial card state.
        else:
            cards_init = self.cards[self.chat_partner_username]

        print("[INFO] Cards generated: %s"%(cards_init))

        # Encrypt the messages with Solitaire (based on the perviously acquired cards)
        message_text = "me -> [{}]: ".format(self.chat_partner_username)
        message = get_input(message_text)
        while (message != "!bye"):
            if not re.match("^[A-Za-z0-9 .,:!?]+$", message):
                print ("[ERROR] Only letters, digits, and punctuation is allowed!")
                message = get_input(message_text)
                continue

            data = self.sol.encrypt(cards_init, message)
            send_socket.send(data.encode())
            message = get_input(message_text)

        # If "!bye" is sent, send the bye message and disconnect from the partner.
        data = self.sol.encrypt(cards_init, "!bye")
        send_socket.send(data.encode())
        bye_response = self.sol.decrypt(cards_init, send_socket.recv(1024).decode())
        if bye_response == "!bye":
            print("[INFO] User '%s' responded to my goodbye."%(self.chat_partner_username))

        send_socket.close()

    def do_exit(self):
        """
        Function which handles the exit process.
        Sends an exit message, thus removing the user from to server and closing all sockets.
        """
        self.client_socket.send("exit#".encode())
        response = self.client_socket.recv(1024).decode().split('#')
        print(response[1])
        print("\nThank you for using CryptoChat!\n")
        self.running = False
        self.client_socket.close()
        self.recieve_socket.close()
        sys.exit()

    def do_kill(self):
        """
        Function which kills the server.
        Only implemented for testing reasons.
        Killing the server raises many issues and should not be available for clients.
        """
        if (self.client_port == 0):
            print("You must register first!")
            return

        data = "kill#server"
        self.client_socket.send(data.encode())
        dataFromServer = self.client_socket.recv(1024)
        print(dataFromServer.decode())

    def run_client(self):
        """
        Looped function which serves as the main GUI/menu for the user.
        Based on choices, it starts the correct handler functions.
        """
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