import eventlet
import console
import config
from eventlet.green import socket

connections = set()
logs        = set()

try:
    proxy_server   = eventlet.listen(('0.0.0.0', 8888))
except:
    print "error: proxy\n"

def parseRequestLine(line):
    pass

def getHeader(reader):
    header = []
    line = reader.readline().strip()
    while line!="":
        header.append(line)
        line = reader.readline().strip()

    return header    

def response(writer):
    writer.write("HTTP/1.1 200 OK\n")
    writer.write("Date: Sun, 04 Dec 2011 16:44:12 GMT\n")
    writer.write("Server: Apache/2.2.14 (Unix)\n")
    writer.write("Expires: Thu, 19 Nov 1981 08:52:00 GMT\n")
    writer.write("Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0\n")
    writer.write("Pragma: no-cache\n")
    writer.write("Content-Length: 3084\n")
    writer.write("Keep-Alive: timeout=5, max=100\n")
    writer.write("Connection: Keep-Alive\n")
    writer.write("Content-Type: text/html;charset=UTF-8\n")
    writer.write("\n\n")
    writer.write('Hi, Body. I"m here.')
    writer.flush()


def proxyAConnection(connection):
    reader = connection.makefile('r')
    
    header = getHeader(reader)
    print header

    # read the request, and choose the target host: localhost, a virtualHost within a special ip, or a realhost

    # parseRequestLine()

    # server = new httpclient()
    # server.connect()
    # server.send_request()
    # response = server.receive_response()
    # server.disconnect()
    # writer.writer( response )
    writer = connection.makefile('w')
    response(writer)

    connection.close()
    

def doProxyServer():
    while True:
        try:
            new_connection, address = proxy_server.accept()
            eventlet.spawn_n(proxyAConnection,new_connection)
        except :
            print "Proxy Server Closed"
            break

def parseCommandLine(commandline):
    return 'exit','exitit'


def main():
    eventlet.spawn(doProxyServer)

    console_server = console.console()
    console_server.start()
	

if __name__=="__main__":
    main()


