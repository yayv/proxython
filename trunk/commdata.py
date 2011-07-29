#! /usr/bin/env python
# -* coding:utf-8 *-
#############################################################################
#                                                                           #
#   File: commdata.py                                                       #
#   Author: liuce                                                           #
#   email: yayv.cn@gmail.com                                                #
#   Home: http://www.pyapp.com                                              #
#   Blog: http://www.liuce.cn                                               #
#   用来存储数据的结构                                                      #
#   每一个记录包括 request(header body), response(header body)              #
#############################################################################

__version__ = "0.1"

__all__ = ["commdata"]

import time
import thread

class CommData:
	""" save http communication data """
	def __init__(self):
		self.data = {}
		self.count = 0
		self.lock  = thread.allocate_lock()

	def append(self,request):
		""" append a couple of request and response """
		self.lock.acquire()
		self.data[self.count+1] = {'url':request['u'],'status':'-','request':request}
		self.lock.release()
		self.count = self.count + 1
		
		return self.count
		
	def updateData(self, id, args):
		""" update response data for a request"""
		self.lock.acquire()
		for i in args:
			self.data[id][i]=args[i]
		self.lock.release()
		pass
	
	def remove(self, id):
		""" remove a couple of request and response  by id"""
		pass

	def clear(self):
		del self.data
		self.data = {}

		
	def getRawRequest(self, id):
		#print 'h:',self.data[id]['request']['h']
		#print 's:',self.data[id]['request']['s']
		l = ""
		l = l + str(self.data[id]['request']['s'])
		l = l + str(self.data[id]['request']['h'])
		l = l + '\n'
		l = l + self.data[id]['request']['b']
		return l
		
	def getRawResponse(self,id):
		l = ''
		if 'response' in self.data[id]:
			l = l + str(self.data[id]['response']['s'])
			l = l + str(self.data[id]['response']['h'])
			l = l + '\n'
			l = l + self.data[id]['response']['b']
		return l
				
	def getData(self,id):
		""" get request data and response data """
		raw = self.getRawRequest(id)
		raw = raw + '\n-------【 我是孤独的分割线 】---------------\n'
		raw = raw + self.getRawResponse(id)
				
		return raw
		
	def getInfo(self, id):
		return {'id':id,'status':self.data[id]['status'],'url':self.data[id]['url']}
		
	
	def getList(self):
		l = []
		self.lock.acquire()
		for i in self.data:
			l.append(self.getInfo(i))
		self.lock.release()
		return l
		
commdata = CommData()
			
if(__name__=='__main__'):
	a = CommData()
	a.append(1)
	print a.getData(1)
	
