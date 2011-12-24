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

    def executeCommand(params, writer):
        pass

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


                while True:
                    try:
                        console_writer.write(">")                    
                        console_writer.flush()

                        line = console_reader.readline().strip()
                        params = self.parseCommandLine(line)

                        if len(params)<1:
                            continue;

                        if('shutdown'==params[0]):
                            console_writer.write('Server Shuting Down.\n')
                            console_writer.close()
                            console_reader.close()
                            console_client.close()
                            self.console_server.close()
                            return 
                        elif('exit'  ==params[0]):
                        	console_writer.write('Close current client\n')
                        	console_writer.close()
                        	console_reader.close()
                        	console_client.close()
                        	break
                        else:
                            ret = self.executeCommand(params,console_writer)

                    except eventlet.greenio.socket.error, e:
                        # ignore broken pipes, they just mean the participant
                        # closed its connection already
                        if e[0] != 32:
                            raise
                        else:
                            console_reader.close()
                            console_client.close()
                            break
                    
            
            print "proxython server stopped" 
            
        except (KeyboardInterrupt, SystemExit):
            print "proxython console fault"

