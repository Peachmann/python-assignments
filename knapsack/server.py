import socket
import threading

class User:
    def __init__(self, username, port, public_key):
        self.username = username
        self.port = port
        self.public_key = public_key

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.userlist = {}
        self.running = True

    def listen(self):
        """
        Driver funtion.
        Listens to all incoming clients and assigns them a separate thread.
        """
        print("[INFO] CryptoChat server started.")
        self.sock.listen(10)
        while (self.running == True):
            client, address = self.sock.accept()
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def do_register(self, client, parsed_data):
        """
        Handles the registration process.
        If the username/port is not taken, adds the user to the dictionary.
        """
        error = False
        client_username = parsed_data[1]
        client_port = parsed_data[2]
        client_public_key = parsed_data[3]

        if (client_username in self.userlist):
            client.send("error#Username already taken!".encode())
            error = True

        if (error == False):
            for i in self.userlist.values():
                if (i.port == client_port):
                    client.send("error#Port already taken!".encode())
                    error = True

        if (error == False):
            self.userlist[client_username] = User(client_username, client_port, client_public_key)

            print("[REGISTER] Registered user '%s' with port '%s' and public key '%s'"%(client_username, client_port, client_public_key))
            client.send("done#Registered successfully!".encode())
            return client_username, client_port

        return '', 0

    def do_get_public_key(self, client, client_username, client_port, parsed_data):
        """
        Handles the public key requst.
        If the username is not present, responds with an error.
        Otherwise, it sends the public key and port of the user.
        """
        user_to_find = parsed_data[1]
        print("[GETKEY] User '%s' with port '%s' requested the public key of '%s'"%(client_username, client_port, user_to_find))
        if(user_to_find in self.userlist):
            user = self.userlist[user_to_find]
            user_port_and_key = "done#" + user.port + "#" + user.public_key
            client.send(user_port_and_key.encode())
        else:
            client.send("error#No such user!".encode())

    def do_exit(self, client, client_username):
        """
        Handles the exit request.
        Removes the user from the dictionary.
        """
        self.userlist.pop(client_username)
        client.send("done#Unregistered from the server.".encode())
        print("[DELETE] Client '%s' removed from list."%(client_username))
        client.close()

    def do_kill(self, client, client_username):
        """
        Kills the server.
        Only implemented for testing purposes, it should not be used.
        """
        print("[KILL] Client '%s' stopped the server."%(client_username))
        client.close()
        self.running = False
        self.sock.close()

    def listenToClient(self, client, address):
        """
        Handles clients.
        Starts the functions which correspond to the request.
        """
        print("[INFO] Client connected from %s:%s."%(address[0], address[1]))
        size = 1024
        client_username = ''
        client_port = 0

        while True:
            try:
                data = client.recv(size)
                if data:
                    parsed_data = data.decode().split("#")
                    request_type = parsed_data[0]

                    if (request_type == "register"):
                        client_username, client_port = self.do_register(client, parsed_data)

                    if (request_type == "getkey"):
                        self.do_get_public_key(client, client_username, client_port, parsed_data)
                
                    if (request_type == "exit"):
                        self.do_exit(client, client_username)
                        return False

                    if (request_type == "kill"):
                        self.do_kill(client, client_username)
                        return False
                else:
                    raise NameError("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
            except:
                print("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
                client.close()
                return False

if __name__ == "__main__":
    ThreadedServer("localhost", 9999).listen()