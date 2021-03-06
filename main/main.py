import socket
import signal
import errno
import logging
import pyev
from connection import Connection,Console,Proxy


logging.basicConfig(level=logging.DEBUG)

STOPSIGNALS = (signal.SIGINT, signal.SIGTERM)
NONBLOCKING = (errno.EAGAIN, errno.EWOULDBLOCK)

PROXYPORT   = ("",8888)
CONSOLEPORT = ("",9876)

class Server(object):

    def __init__(self, address=("",8888), console=("",9876)):

        # init proxy socket
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(address)
        self.sock.setblocking(0)
        self.proxyaddress = self.sock.getsockname()
 
        # init console socket
        self.console = socket.socket()
        self.console.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.console.bind(console)
        self.console.setblocking(0)
        self.consoleaddress = self.console.getsockname()
 
        self.loop = pyev.default_loop()
        self.watchers = [pyev.Signal(sig, self.loop, self.signal_cb)
                         for sig in STOPSIGNALS]
        self.watchers.append(pyev.Io(self.sock._sock, pyev.EV_READ, self.loop,
                                    self.io_cb))

        self.watchers.append(pyev.Io(self.console._sock, pyev.EV_READ, self.loop,
                                     self.console_cb))

        self.connection_count = 0
        self.conns = {}

    def handle_error(self, msg, level=logging.ERROR, exc_info=True):
        logging.log(level, "{0}: {1} --> stopping".format(self, msg),
                    exc_info=exc_info)
        self.stop()

    def signal_cb(self, watcher, revents):
        self.stop()

    def console_cb(self, watcher, revents):
        self.connection_count += 1
        try:
            while True:
                try:
                    sock, address = self.console.accept()
                except socket.error as err:
                    if err.args[0] in NONBLOCKING:
                        break
                    else:
                        raise
                else:
                    self.conns["%d" % self.connection_count] = Console(self.connection_count, sock, address, self.loop, self.conns)
                    logging.debug("{0}".format(sock))
        except Exception:
            self.handle_error("error accepting a connection")


    def io_cb(self, watcher, revents):
        self.connection_count += 1
        try:
            while True:
                try:
                    sock, address = self.sock.accept()
                except socket.error as err:
                    if err.args[0] in NONBLOCKING:
                        break
                    else:
                        raise
                else:
                    self.conns["%d" % self.connection_count] = Proxy(self.connection_count, sock, address, self.loop)
                    logging.debug("{0}: proxy on {0.proxyaddress} and console on {0.consoleaddress}".format(self))
        except Exception:
            self.handle_error("error accepting a connection")

    def start(self):
        self.sock.listen(socket.SOMAXCONN)
        self.console.listen(socket.SOMAXCONN)
        for watcher in self.watchers:
            watcher.start()

        logging.debug("{0}: started on {0.proxyaddress} and {0.consoleaddress}".format(self))
        self.loop.start()

    def stop(self):
        self.loop.stop(pyev.EVBREAK_ALL)
        self.sock.close()
        self.console.close()
        while self.watchers:
            self.watchers.pop().stop()
        for conn in self.conns.values():
            conn.close()
        logging.debug("{0}: stopped".format(self))


if __name__ == "__main__":
    server = Server(PROXYPORT,CONSOLEPORT)
    server.start()


