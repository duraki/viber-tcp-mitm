import socket
from threading import Thread

class Proxy2Server(Thread):

    def __init__(self):
        super(Viber2Proxy, self).__init__()
        self.viber = None
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    # run in thread
    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                print("[{}] <- {}".format(self.port, data[:100].encode('hex')))
                # forward to client
                self.server.sendall(data)

class Viber2Proxy(Thread):

    def __init__(self, host, port):
        super(Viber2Proxy, self).__init__()
        self.server = None # real server socket not known yet
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        # waiting for a connection
        self.viber, addr = sock.accept()

    def run(self):
        while True:
            data = self.viber.recv(4096)
            if data:
                print("[{} -> {}".format(self.port, data[:100].encode('hex')))
                # forward to server
                self.server.sendall(data)


class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("[proxy]({}) viber2proxy setting up".format(self.port))
            self.v2p = Viber2Proxy(self.from_host, self.port) # waiting for a client
            print("[proxy]({}) proxy2server setting up".format(self.port))
            self.p2s = Proxy2Server(self.to_host, self.port)
            print("[proxy]({}) connection established".format(self.port))
            self.v2p.server = self.p2s.server
            self.p2s.viber = self.v2p.viber

            self.v2p.start()
            self.p2s.start()

#master_server = Proxy('0.0.0.0', '52.0.253.194', 52952)
master_server = Proxy('0.0.0.0', '52.0.253.194', 3333)
master_server.start()

viber_servers = []

viber_servers.append(Proxy('0.0.0.0', '52.0.253.194', 443))
viber_servers.append(Proxy('0.0.0.0', '52.0.253.194', 52952))

for srv in viber_servers:
    srv.start()
