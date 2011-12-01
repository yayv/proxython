

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

def parseCommand(command):
    if command in commands:
        print "[",command,"]\n"
    else:
        print 'unknown command\n'
    pass

#eventlet.spawn(checkConsole)
#checkProxy()
try:
    while True:
        console_client,address = console_server.accept()
        print console_client
        console_writer = console_client.makefile('w')
        console_reader = console_client.makefile('r')
        line = console_reader.readline()
        while line:
            print "console:", line.strip()
            try:
                parseCommand(line);
                console_writer.write('copy that\n')
                console_writer.flush()
            except socket.error, e:
                # ignore broken pipes, they just mean the participant
                # closed its connection already
                if e[0] != 32:
                    raise
            line = console_reader.readline()

except (KeyboardInterrupt, SystemExit):
    print "ChatServer exiting."                

