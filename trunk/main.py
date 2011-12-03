
import eventlet
from eventlet.green import socket

connections = set()
logs        = set()

proxy_server   = eventlet.listen(('0.0.0.0', 8888))
console_server = eventlet.listen(('0.0.0.0', 4444))

commands       = ("help","list","exit")

def proxyAConnection(connection):
    pass

def checkProxy():
    while True:
        new_connection, address = proxy_server.accept()
        eventlet.spawn_n(proxyAConnection,new_connection)

def parseCommandLine(commandline):
    pass


def main():
    eventlet.spawn(checkProxy)

    try:
        while True:
            console_client,address = console_server.accept()
            console_writer = console_client.makefile('w')
            console_reader = console_client.makefile('r')
            line = console_reader.readline()
            while line:
                print "console:", line.strip()
                try:
                    command,params = parseCommandLine(line)
                    console_writer.flush()
                    if('close'==ret):
                        console_client.close()
                except socket.error, e:
                    # ignore broken pipes, they just mean the participant
                    # closed its connection already
                    if e[0] != 32:
                        raise
                line = console_reader.readline()

    except (KeyboardInterrupt, SystemExit):
        print "Proxy Server Stopped"


if __name__=="__main__":
    main()


