from unittest import TestCase
import socket

def tuple_to_string(tpl):
        return ",".join(list(map(lambda x: str(x), tpl)))

# Run with: python -m unittest discover

class ServerTest(TestCase):
    def test_register(self):
        """
        Registers a 'testuser' client successfully.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost",  9999))

        public_key = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        message = "register#testuser#10000#" + tuple_to_string(public_key)
        client.send(message.encode())

        response_from_server = client.recv(1024).decode()

        self.assertEqual("done#Registered successfully!", response_from_server)

        client.send("exit#".encode())
        client.close()

    def test_register_username_taken_error(self):
        """
        Registers a 'testuser' client and another one with the same name.
        Error is recieved as response.
        """
        client_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_1.connect(("localhost",  9999))
        client_2.connect(("localhost",  9999))

        public_key_1 = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        public_key_2 = (1156, 1445, 565, 1117, 776, 68, 1089, 509)
        
        message = "register#testuser#10000#" + tuple_to_string(public_key_1)
        client_1.send(message.encode())
        response_from_server = client_1.recv(1024).decode()

        message = "register#testuser#10001#" + tuple_to_string(public_key_2)
        client_2.send(message.encode())
        response_from_server = client_2.recv(1024).decode()

        self.assertEqual("error#Username already taken!", response_from_server)

        client_1.send("exit#".encode())
        client_2.send("exit#".encode())
        client_1.close()
        client_2.close()

    def test_register_port_taken_error(self):
        """
        Registers a client with port 10000 and another one with the same port.
        Error is recieved as response.
        """
        client_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_1.connect(("localhost",  9999))
        client_2.connect(("localhost",  9999))

        public_key_1 = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        public_key_2 = (1156, 1445, 565, 1117, 776, 68, 1089, 509)
        
        message = "register#testuser1#10000#" + tuple_to_string(public_key_1)
        client_1.send(message.encode())
        response_from_server = client_1.recv(1024).decode()

        message = "register#testuser2#10000#" + tuple_to_string(public_key_2)
        client_2.send(message.encode())
        response_from_server = client_2.recv(1024).decode()

        self.assertEqual("error#Port already taken!", response_from_server)

        client_1.send("exit#".encode())
        client_2.send("exit#".encode())
        client_1.close()
        client_2.close()

    def test_get_public_key(self):
        """
        Registers a user with a public key and gets that key successfully.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost",  9999))

        public_key = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        message = "register#testuser#10000#" + tuple_to_string(public_key)
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        message = "getkey#testuser"
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        expected_response = "done#10000#" + tuple_to_string(public_key)
        self.assertEqual(expected_response, response_from_server)

        client.send("exit#".encode())
        client.close()

    def test_get_public_key_error(self):
        """
        Registers a user and tries to get the key of an unregistered user.
        Error is recieved as response.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost",  9999))

        public_key = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        message = "register#testuser#10000#" + tuple_to_string(public_key)
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        message = "getkey#nonexistantuser"
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        expected_response = "error#No such user!"
        self.assertEqual(expected_response, response_from_server)

        client.send("exit#".encode())
        client.close()

    def test_exit_client(self):
        """
        Client exits, server removes it from the dict and closes connection.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost",  9999))

        public_key = (909, 1212, 1435, 892, 1258, 298, 174, 98)
        message = "register#testuser#10000#" + tuple_to_string(public_key)
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        message = "exit#"
        client.send(message.encode())
        response_from_server = client.recv(1024).decode()

        expected_response = "done#Unregistered from the server."
        self.assertEqual(expected_response, response_from_server)

        client.close()
