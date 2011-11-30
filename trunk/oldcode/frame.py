#!/usr/bin/env python

#-* coding:UTF-8 *-
# example test frame.py

import pygtk
pygtk.require('2.0')
import time
import gtk
import gobject
import thread
import proxy 
import socket
from commdata import commdata
from threading import Thread
from commdata import commdata 

LOG = True
myserver = None

def test(callbackfunction):
    port = 8888
    HandlerClass = proxy.ProxyHTTPRequestHandler
    ServerClass = proxy.ThreadingHTTPServer
    protocol="HTTP/1.0"
    
    server_address = ('', port)
    
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)
    httpd.addCallback(callbackfunction)
    
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()


class Frame:
	def debugLog(self, info):
		if(self.debug_log):
			print info
		else:
			pass

	def getMainMenuBar(self):
		# append menu
		self.menu = gtk.Menu()
		self.menu.show()
		self.menu_open = gtk.MenuItem('Open')
		self.menu_line = gtk.MenuItem()
		self.menu_exit = gtk.MenuItem('Exit')
		self.menu_open.show()
		self.menu_line.show()
		self.menu_exit.show()
		self.menu.append(self.menu_open)
		self.menu.append(self.menu_line)
		self.menu.append(self.menu_exit)

		self.menubar = gtk.MenuBar()
		self.menubar.show()
		self.menu_file = gtk.MenuItem('File')
		self.menu_file.show()
		self.menu_file.set_submenu(self.menu)
		
		self.menubar.append(self.menu_file)

		return self.menubar		

	def getMainStatusBar(self):
		self.statusbar = gtk.Statusbar()
		self.statusbar.push(1,'test')
		self.statusbar.show()
		
		return self.statusbar

	def getMainBody(self):
	
		self.bodyview = gtk.TextView()
		self.buffer = self.bodyview.get_buffer()
		self.body   = gtk.ScrolledWindow()
		self.body.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.body.add(self.bodyview)
		#self.insert_text(self.buffer)
		iter = self.buffer.get_iter_at_offset(0)
		self.buffer.insert(iter,'test string\n test test')
		self.body.show_all()

		return self.body
	
	def getMainList(self):
		self.list = gtk.ScrolledWindow()
		self.list.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		self.store = gtk.ListStore(int,str,str,str)
		self.store.append([0,'test','test','test'])

		self.listview = gtk.TreeView(self.store)
		self.listview.show()

		cell = gtk.CellRendererText()
		self.tvcolumn = gtk.TreeViewColumn('id',gtk.CellRendererText(), text=0)
		self.tvcolumn1 = gtk.TreeViewColumn('url',gtk.CellRendererText(), text=1)
		self.tvcolumn2 = gtk.TreeViewColumn('status',gtk.CellRendererText(), text=2)
		
		self.listview.append_column(self.tvcolumn)
		self.listview.append_column(self.tvcolumn1)
		self.listview.append_column(self.tvcolumn2)

		self.list.add(self.listview)

		self.list.show_all()
		
		return self.list

	def refreshList(self,status):
		global commdata
		
		cl = commdata.getList()
		gtk.gdk.threads_enter()
		self.store.clear()
		if cl:
			for i in cl:
				self.store.append([i['id'], i['status'],i['url'],'test'])

		gtk.gdk.threads_leave()
		return True


	def __init__(self):
		global LOG
		self.count = 0
		self.debug_log = LOG
		self.liststorelock = thread.allocate_lock()
		
		# create form
		self.frame = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.frame.set_title('test')
				
		self.box1 = gtk.VBox()
		
		self.box1.pack_start(self.getMainMenuBar(),False,False,0)
		
		self.hpaned = gtk.HPaned()
		self.hpaned.show()
		
		self.hpaned.add1(self.getMainList())
		self.hpaned.add2(self.getMainBody())
				
		self.box1.pack_start(self.hpaned, True, True,1)
		self.box1.pack_start(self.getMainStatusBar(), False,False,0)		
		self.box1.show()

		self.frame.set_border_width(5)
		self.frame.set_size_request(450, 400)
		self.frame.add(self.box1)
		self.frame.connect('destroy',self.destroy, '')
		self.frame.show()
		
		# bind to event
		self.bindEvent()
		
	def showCommData(self,treeview,path,viewcolumn,up):
		global commdata
		
		l = treeview.get_model()
		itor = l.get_iter(path)
		
		id = l.get_value(itor,0)
		raw_data = commdata.getData(id)
		
		self.buffer.set_text(raw_data)
		
	def bindEvent(self):
		self.menu_exit.connect('activate', self.destroy, '111')
		self.menu_open.connect('activate', self.debug, '111')
		self.listview.connect('row-activated', self.showCommData,'')

	def debug(self,widget,Data):
		global commdata
		
		print widget
		print Data
		for i in  commdata.data:
			print i,':',commdata.data[i]
	
	def destroy(self,widget,Data):
		self.debugLog('window destroy')
		gtk.main_quit()


	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()

if(__name__=='__main__'):
	#thread.start_new_thread(MyServer,(1,))
	f = Frame()
	
	gtk.gdk.threads_init();
	thread.start_new_thread(test,(f.refreshList,))
	

	f.main()


	
