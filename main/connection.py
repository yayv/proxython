import socket
import signal
import weakref
import errno
import logging
import pyev
import getopt

class Connection(object):

    def __init__(self, sock, address, loop):
        self.sock = sock
        self.address = address
        self.sock.setblocking(0)
        self.buf = ""
        self.watcher = pyev.Io(self.sock._sock, pyev.EV_READ, loop, self.io_cb)
        self.watcher.start()
        logging.debug("{0}: ready".format(self))

    def reset(self, events):
        self.watcher.stop()
        self.watcher.set(self.sock, events)
        self.watcher.start()

    def handle_error(self, msg, level=logging.ERROR, exc_info=True):
        logging.log(level, "{0}: {1} --> closing".format(self, msg),
                    exc_info=exc_info)
        self.close()

    def handle_read(self):
        try:
            buf = self.sock.recv(1024)
        except socket.error as err:
            if err.args[0] not in NONBLOCKING:
                self.handle_error("error reading from {0}".format(self.sock))
        if buf:
            self.read(buf)
            self.reset(pyev.EV_READ | pyev.EV_WRITE)
        else:
            self.handle_error("connection closed by peer", logging.DEBUG, False)

    def handle_write(self):
        try:
            sent = self.sock.send(self.buf)
        except socket.error as err:
            if err.args[0] not in NONBLOCKING:
                self.handle_error("error writing to {0}".format(self.sock))
        else :
            self.buf = self.buf[sent:]
            if not self.buf:
                self.reset(pyev.EV_READ)

    def io_cb(self, watcher, revents):
        if revents & pyev.EV_READ:
            self.handle_read()
        else:
            self.handle_write()

    def close(self):
        self.sock.close()
        self.watcher.stop()
        self.watcher = None
        logging.debug("{0}: closed".format(self))

class Proxy(Connection):

    def __init__(self, sock, address, loop):
        super(Proxy, self).__init__(sock, address, loop)

    def read(buf):
        self.cmdbuf += buf
        l = self.cmdbuf.index("\n")

    def write():
        pass

class Console(Connection):

    def __init__(self, sock, address, loop):
        super(Console,self).__init__(sock, address, loop)
        self.cmdbuf = ""
        self.sock.send("Proxython>")
        logging.debug("{0}: ready".format(self))

    def read(self,buf):

        self.cmdbuf += buf

        commands = self.cmdbuf.split("\r\n")

        options  = "abcde:"
        for command in commands:
            if command != "":
                argv = command.split()
                opts,args = getopt.getopt(argv[1:],options)

        self.sock.send("Proxython>")


    def write(self):
        self.sock.send("Proxython>")

