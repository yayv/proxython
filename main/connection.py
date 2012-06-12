import socket
import signal
import errno
import logging
import pyev
import getopt

NONBLOCKING = (errno.EAGAIN, errno.EWOULDBLOCK)

class Connection(object):

    def __init__(self, sock, address, loop):
        self.sock = sock
        self.address = address
        self.sock.setblocking(0)
        self.status = 'connected'
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
            return

        if buf:
            ret = self.read(buf)
            if ret:
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
        self.status = 'stopped'
        self.watcher = None
        logging.debug("{0}: closed".format(self))

class Proxy(Connection):

    def __init__(self, sock, address, loop):
        super(Proxy, self).__init__(sock, address, loop)

    def read(self, buf):
        pass

    def write(self, buf):
        pass

class Console(Connection):

    def __init__(self, sock, address, loop, conns):
        super(Console,self).__init__(sock, address, loop)
        self.commands = {
                "exit":self.exit,
                "help":self.help,
                "ls":self.listconns,
                }
        self.cmdbuf = ""
        self.conns = conns
        self.sock.send("Proxython>")

    def read(self,buf):

        self.cmdbuf += buf

        commands = self.cmdbuf.split("\r\n")

        options  = "abcde:"
        for command in commands:
            if command != "":
                argv = command.split()
                opts,args = getopt.getopt(argv[1:],options)
                if command in self.commands:
                    self.commands[command](opts,args)
                else:
                    self.nocmd(argv[0])

        self.cmdbuf = ""

        if self.watcher:
            self.sock.send("Proxython>")
            return True


    def write(self):
        self.sock.send("Proxython>")

    def nocmd(self,command):
        print "command %s is not support" % command
        self.sock.send("command '%s' is not support\n" % command);

    def exit(self,opts,args):
        self.sock.send("Bye-bye\n")
        self.close()
        
    def listconns(self,opts,args):
        for i in self.conns:
            self.sock.send( "%s:%d status:%s\n" % (i[0],i[1], self.conns[i].status ) )

    def help(self,opts,args):
        for i in self.commands.keys():
            self.sock.send(i)
            self.sock.send(" ")

        self.sock.send("\n")

