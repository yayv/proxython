import event
import socket

def myread(ev, fd, evtype, arg):
    print 'read handle...'
    h,addr = fd.accept()
    data = h.recv(1024)
    print data
   
    event.event(mywrite, handle=h, evtype=event.EV_WRITE, arg=fd).add()

def mywrite(ev, fd, evtype, arg):
    print 'write handle...'
    fd.send('hehe, ok!')
    fd.close()
    #event.event(myread, handle=arg, evtype=event.EV_READ).add()
   
   
svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind(('127.0.0.1', 10000))
svr.listen(5)

event.event(myread, handle=svr, evtype=event.EV_READ|event.EV_PERSIST).add()

event.dispatch()

svr.close()



