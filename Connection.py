
import sys

from threading import Thread

# Check For Paramiko Dependency
try:
    from paramiko import SSHClient
    from paramiko import AutoAddPolicy
except ImportError:
    print('Missing Paramiko Dependency.')
    sys.exit(0)


class Connection(Thread):
    '''
    This is the class that checks if a specific
    Username and password combination was successful.
    '''

    def __init__(self, username, password, targetIp, portNumber, timeoutTime):

        super(Connection, self).__init__()

        self.username = username
        self.password = password
        self.targetIp = targetIp
        self.portNumber = portNumber
        self.timeoutTime = timeoutTime
        self.status = ""
        self.found=False
        self.fu=""
        self.fp=""

    def run(self):
        try:
            sshConnection = SSHClient()
            sshConnection.set_missing_host_key_policy(AutoAddPolicy())
        except:
            print("Some Error in Connection ssh")

        try:
            sshConnection.connect(self.targetIp, port=int(self.portNumber),
                                  username=self.username, password=self.password,
                                  timeout=int(self.timeoutTime), allow_agent=False, look_for_keys=False,banner_timeout=200)

            self.status = 'Succeeded'
            self.found=True
            self.fu=self.username
            self.fp=self.password
            print("---------------------------------Connection Stablised----------------------------------------------------------")
            sshConnection.close()
        except:
            self.status = 'Failed'

