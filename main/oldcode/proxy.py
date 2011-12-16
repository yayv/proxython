"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

TODO: 要把这个BaseServer实现的Proxy使用 curl 的实现替换
"""


__version__ = "0.6"

__all__ = ["ProxyHTTPRequestHandler"]

import os
import sys
import posixpath
import SocketServer
import BaseHTTPServer
import urllib
import urllib2
import urlparse
import cgi
import zlib
import time
import shutil
import mimetypes
import curl
from commdata import commdata 

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ProxyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
    PostDataLimit = 0x100000

    server_version = "SimpleHTTP/" + __version__

    DEBUG = False

    def cli_output(self, headers, body):
        if self.DEBUG:
            print time.time()
            print '--------------------------'
            print headers
            print body


    def doCallback(self, status):
        if not hasattr(self.server,'callbacks'):
            return 
        
        for i in self.server.callbacks:
            i(status)

    def log_object(self, obj):
    	if not self.DEBUG :
    		return
    		
        print '-----[ ';
        try:
        	print obj.__name__;
        except:
        	pass
        print ' ]-----------'
        print obj.__dict__
        print '------------------------'

    def do_PROXY(self):
        global commdata
        
        postData = ''
        try:
            if self.headers.has_key('Content-Length'):
                postDataLen = int(self.headers['Content-Length'])
                postData = self.rfile.read(postDataLen)
        except:
        	postData = ''
        requestid = commdata.append(
        		{'r':self.command,
        		 'u':self.path,
        		 's':self.raw_requestline,
        		 'h':self.headers,
        		 'b':postData})
        self.doCallback('-')
        
        # check http method and post data
        method = self.command
        if method == 'GET' or method == 'HEAD':
            # no post data
            postDataLen = 0
        elif method == 'POST':
            # get length of post data
            postDataLen = 0
            if self.headers.has_key('Content-Length'):
                postDataLen = int(self.headers['Content-Length'])
            # exceed limit?
            if postDataLen > self.PostDataLimit:
                self.send_error(403)
                self.connection.close()
                return
        else:
            # unsupported method
            self.send_error(501)
            self.connection.close()
            return

        # get post data
        if postDataLen > 0:
            if len(postData) != postDataLen:
                # bad request
                self.send_error(400)
                self.connection.close()
                return

        scm, netloc, path, params, query, frag = urlparse.urlparse(self.path)
        if scm != 'http' or not netloc:
            self.send_error(400)
            self.connection.close()
            return

        # create new path
        path = urlparse.urlunparse((scm, netloc, path, params, query, ''))

        # create request for GAppProxy
        params = urllib.urlencode({'method': method, 
                                   'path': path, 
                                   #'headers': self.headers, 
                                   'encodeResponse': 'compress', 
                                   'postdata': postData})

        request = urllib2.Request(self.path)
        for h in self.headers:
        	request.add_header(h,self.headers[h])
        
        request.add_header('Host',netloc)
        request.add_header('Connection', 'close')
        
        # create new opener
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        # set the opener as the default opener
        urllib2.install_opener(opener)
        self.log_object(request)

        resp = urllib2.urlopen(request, params)

        # parse resp
        textContent = True
        # for status line
        print resp.geturl()
        header = str( resp.info() )
        body = resp.read()        
        
        self.cli_output(header, body)
        self.send_response(resp.code)
        self.wfile.write( header )
        self.end_headers()

        self.wfile.write( body )
		
        # for headers
        #while True:
        #    line = resp.readline()
        #    line = line.strip()
        #    # end header?
        #    if line == '':
        #        break
        #    # header
        #    name, sep, value = line.partition(':')
        #    name = name.strip()
        #    value = value.strip()
        #    self.send_header(name, value)
        #    # check Content-Type
        #    if name.lower() == 'content-type':
        #        if value.lower().find('text') == -1:
        #            # not text
        #            textContent = False
        
        # for page
        #if textContent:
        #    self.wfile.write(zlib.decompress(resp.read()))
        #else:
        self.wfile.write(resp.read())


        self.connection.close()
		        
        commdata.updateData(requestid,{'status':resp.code})
        commdata.updateData(requestid,{'response':{
        						's':str(resp.code)+' '+resp.msg+'\n',
        						'h':header,
        						'b':body,
        						}})
        self.doCallback(resp.code)
        
        # end do_Proxy
    	
    def log_message(self, format, *args):
    	pass

    do_GET=do_PROXY
    do_POST=do_PROXY
    do_HEAD=do_PROXY

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	def addCallback(self, callback):
		if not hasattr(self,'callbacks'):
			self.callbacks = []
			
		self.callbacks.append(callback)
	
	
def callbacktest(status):
	print status

def test(port,
		 HandlerClass = ProxyHTTPRequestHandler,
         ServerClass = ThreadingHTTPServer, 
         protocol="HTTP/1.0"):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the first command line
    argument).

    """
    server_address = ('', port)

    
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)
    httpd.addCallback(callbacktest)
    
    #print httpd.__class__.__bases__
    #return 
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == '__main__':
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000
    test(port)
