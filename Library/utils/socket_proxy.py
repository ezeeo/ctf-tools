import socket



class socket_proxy:
    def __init__(self,port):
        #self._raw_sock=sock

        self._port_server=port
        self._server_sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.bind(('127.0.0.1', self._port_server))
        self._server_sock.listen(50)
        # sock.setblocking(False)
        self._server_sock.settimeout(3)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



    def _ioloop(self):
        pass


    def proxy(self):

        

        try:
            self._server_sock.settimeout(3)
            conn, addr = self.sock.accept()
            self.sock.settimeout(None)


        except socket.timeout as ex:
            pass
        

        return conn