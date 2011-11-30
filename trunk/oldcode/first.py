# -*: coding: UTF-8 *-


#TODO: 1. 进行 内部的 host 查询
#TODO: 2. 转发请求
#TODO: 3. 对于



urls = ["http://www.google.com/intl/en_ALL/images/logo.gif",
     "https://wiki.secondlife.com/w/images/secondlife.jpg",
     "http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif"]

import re
import eventlet
from eventlet.green import urllib2  

def loadHostList():
	# TODO: 1. read /etc/hosts
	# TODO: 2. read ./hosts
	# TODO: 3. do host by url


def fetch(url):
  print "opening", url
  body = urllib2.urlopen(url).read()
  print "done with", url
  return url, body

def get():
	pool = eventlet.GreenPool(200)
	for url, body in pool.imap(fetch, urls):
	  print "got body from", url, "of length", len(body)

def parseCommandLine(commandline):
	re.compile('(GET|POST) .* HTTP/1.[01]');
	print re.match(commandline);

def getHostIp(host):
	pass

def handle(fd):
    print "client connected"
	
	command = fd.readline()
	parseCommandLIne(command)

	# TODO: 1. dohost
	# TODO: transfer request
    while True:
        # pass through every non-eof line
        x = fd.readline()
        if not x: break
        
		#fd.write(x)
        fd.flush()
        print "echoed", x,
    print "client disconnected"

def start():
	print "server socket listening on port 8888"
	server = eventlet.listen(('0.0.0.0', 8888))
	pool = eventlet.GreenPool()
	while True:
		try:
		    new_sock, address = server.accept()
		    print "accepted", address
		    pool.spawn_n(handle, new_sock.makefile('rw'))
		except (SystemExit, KeyboardInterrupt):
		    break


start()

