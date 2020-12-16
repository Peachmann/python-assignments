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
        print("[INFO] CryptoChat server started.")
        self.sock.listen(5)
        while (self.running == True):
            client, address = self.sock.accept()
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        print("[INFO] Client connected from %s:%s."%(address[0], address[1]))
        size = 1024
        client_username = ''
        client_port = 0
        client_public_key = 0

        while True:
            try:
                data = client.recv(size)
                if data:
                    parsed_data = data.decode().split("#")
                    request_type = parsed_data[0]
                    
                    if (request_type == "echo"):
                        client.send(data)

                    if (request_type == "register"):
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
                    
                    if (request_type == "getkey"):
                        user_to_find = parsed_data[1]
                        print("[GETKEY] User '%s' with port '%s' requested the public key of '%s'"%(client_username, client_port, user_to_find))
                        if(user_to_find in self.userlist):
                            user = self.userlist[user_to_find]
                            user_port_and_key = "done#" + user.port + "#" + user.public_key
                            client.send(user_port_and_key.encode())
                        else:
                            client.send("error#No such user!".encode())
                
                    if (request_type == "exit"):
                        self.userlist.pop(client_username)
                        print("[DELETE] Client '%s' removed from list."%(client_username))
                        client.close()
                        return False

                    if (request_type == "kill"):
                        print("[KILL] Client '%s' stopped the server."%(client_username))
                        client.close()
                        self.running = False
                        self.sock.close()
                        return False
                else:
                    raise NameError("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
            except:
                print("[INFO] Client disconnected at %s:%s."%(address[0], address[1]))
                client.close()
                return False

if __name__ == "__main__":
    ThreadedServer("localhost", 9999).listen()