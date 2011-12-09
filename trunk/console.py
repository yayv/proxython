import eventlet

class console:
    def __init__(self):
        self.commands = ['exit','help','ls','view','']
        self.command_maps = {'exit':'exit',
                         '?':'help', 'help':'help',
                         'view':'view'}


    def parseCommandLine(self,cmdline):
        return 'exit','ok'

    def startListen(self):
        try:
            self.console_server = eventlet.listen(('0.0.0.0', 4444))
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
                        command,params = self.parseCommandLine(line)
                        if('exit'==command):
                            console_client.close()
                            self.console_server.close()
                            return 
                        else:
                            print command
                    except eventlet.greenio.socket.error, e:
                        # ignore broken pipes, they just mean the participant
                        # closed its connection already
                        if e[0] != 32:
                            raise
                    line = console_reader.readline()

        except (KeyboardInterrupt, SystemExit):
            print "proxython Stopped"

