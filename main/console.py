import eventlet
from getopt import *

class console:
    def __init__(self):
        self.commands = ['exit','help','ls','view','shutdown']
        self.command_maps = {'exit':'exit',
                         '?':'help', 'help':'help',
                         'view':'view'}
        self.listenip  = '0.0.0.0'
        self.listenport= 4444


    def parseCommandLine(self,sCmdline):
        lCmdline = sCmdline.strip(' \t\r\n').replace('\t',' ').split(' ')
        while True:
            try:
                lCmdline.remove('')
            except:
                break
        print 'list:',lCmdline,"\n"
        return lCmdline

    def startListen(self):
        try:
            self.console_server = eventlet.listen((self.listenip, self.listenport))
            return True
        except:
            print 'error: console\n'
            return False

    def start(self):
        ret = self.startListen()
        if(not ret):
            return ret

        try:
            while True:
                console_client,address = self.console_server.accept()
                console_writer = console_client.makefile('w')
                console_reader = console_client.makefile('r')
                line = console_reader.readline()
                while line:
                    print "console:", line.strip()
                    try:
                    	print 'line:',line
                        params = self.parseCommandLine(line)
                        command = params[0]
                        if('shutdown'==command):
                            console_client.close()
                            self.console_server.close()
                            return 
                        elif('exit'==command):
                        	console_reader.close()
                        	console_writer.write('Close current client\n')
                        	console_writer.close()
                        	console_client.close()
                        	break
                        else:
                            print command
                    except eventlet.greenio.socket.error, e:
                        # ignore broken pipes, they just mean the participant
                        # closed its connection already
                        if e[0] != 32:
                            raise
                    line = console_reader.readline()
                    print "here\n"

            print "proxython server stopped" 
            
        except (KeyboardInterrupt, SystemExit):
            print "proxython console fault"

