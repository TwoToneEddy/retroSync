#!/usr/bin/env python
#f = open("/home/lee/demofile2.txt", "a")
#f.write("Now the file has more content!\n")
#f.close()

import os
import time
import sys
from subprocess import Popen, PIPE
from datetime import datetime
import smtplib


class backupHelper:
    def __init__(self,errLogFlile,repoLocation,logFileDir,pollPeriod):
        self.errLogFlile = errLogFlile
        self.repoLocation = repoLocation
        self.logFileDir = logFileDir
        self.pollPeriod = pollPeriod

    def logMessage(self,message):
        now = datetime.now()
        fileName = self.logFileDir+"/log_"+now.strftime("%d_%m_%Y") + ".txt"
        f = open(fileName, "a")
        f.write(message + " " + os.uname()[1] + " " + now.strftime("%d/%m/%Y/ %H:%M:%S") + "\n")
        f.close()


    def logError(self,error):
        now = datetime.now()
        f = open(self.errLogFlile, "a")
        f.write(error + " " + os.uname()[1] + " " + now.strftime("%d/%m/%Y/ %H:%M:%S") + "\n")
        f.close()

    def sendEmail(self,subject, message):

        try:
            server = smtplib.SMTP("smtp.mail.yahoo.com",587)
            server.starttls()

            server.login("tim.smith361@yahoo.com",'nysvfvgmjwiktrog')
            message = 'Subject: {}\n\n{}'.format(subject, message)

            server.sendmail("tim.smith361@yahoo.com","lee.hudson1384@gmail.com",message)
            server.quit()
            logMessage(self.logFileDir,"Email sent ")
            return 0
        except:
            logError(self.errLogFlile,"Unable to send email")
            return 1


    # Moves logfile and sends email with contents
    def clearLogFile(self):
        now = datetime.now()
        message = ""

        try:
            file = open(self.errLogFlile,"r+")
            for line in file.readlines():
                message+=line
            file.close()
            if sendEmail(os.uname()[1]+" Logfile contents",message,self.errLogFlile,self.logFileDir) == 0:
                os.system("mv "+self.errLogFlile+" "+self.errLogFlile+"_"+now.strftime("%d_%m_%Y__%H_%M_%S"))
        except:
            print "No log file \n"


    # If merge conflict we have to create a branch with the stuff that conflicts and deal with it later
    def mergeConflict(self):
        now = datetime.now()
        mergeConflictBranch = now.strftime("%d_%m_%Y__%H_%M_%S")
        mergeMessage = "Merge conflict " + os.uname()[1]

        result = Popen(['/usr/bin/git', 'checkout', '-b', mergeConflictBranch ],stdout=PIPE,stderr=PIPE,shell=False)
        result = Popen(['/usr/bin/git', 'add', '*'],stdout=PIPE,stderr=PIPE,shell=False)
        result = Popen(['/usr/bin/git', 'commit', '-m',mergeMessage],stdout=PIPE,stderr=PIPE,shell=False)
        result = Popen(['/usr/bin/git', 'push', '-u', 'origin', mergeConflictBranch],stdout=PIPE,stderr=PIPE,shell=False)
        result = Popen(['/usr/bin/git', 'checkout', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
        result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)

        # Now send email
        subject = os.uname()[1]+" Merge confict!!"
        message = "mergeConflict() called by " + os.uname()[1] + "\n"
        message += mergeConflictBranch + " created and pushed\n"
        message += "This means something had changed before a pull was done\n"
        sendEmail(subject,message)

    # Basic commitlogFileDir
    def commit(self):

        os.chdir(self.repoLocation)

        mergeMessage = "Auto commit " + os.uname()[1]

        # Git add
        result =  Popen(['/usr/bin/git', 'add', '*'],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()
        if len(out) > 1:
            logMessage("commit() performing git add *\n" +out)
        if len(error) > 1:
            logMessage("commit() performing git add *\n" +error)

        # Git commit
        result = Popen(['/usr/bin/git', 'commit', '-m',mergeMessage],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()
        if len(out) > 1:
            logMessage("commit() performing git commit\n" +out)
        if len(error) > 1:
            logMessage("commit() performing git commit\n" +error)

        # Git push
        result = Popen(['/usr/bin/git', 'push', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()
        if len(out) > 1:
            logMessage("commit() performing git push origin master \n" +out)
        if len(error) > 1:
            logMessage("commit() performing git push origin master \n" +error)
        
        if error.find("Could not resolve hostname") != -1:
                logError("No connection")



    def smartPull(location,errLogFlile,logFileDir):

        os.chdir(location)
        try:
            result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = result.communicate()
            if len(out) > 1:
                logMessage(logFileDir,"smartPull() performing git pull origin master \n" +out)
            if len(error) > 1:
                logMessage(logFileDir,"smartPull() performing git pull origin master \n" +error)

            if error.find("Could not resolve hostname") != -1:
                logError(errLogFlile,"No connection")
            
            if error.find("overwritten by merge") != -1:
                mergeConflict(errLogFlile,logFileDir)

        except Exception as e:
            logError(errLogFlile,e)



def main():

    pollPeriod = 1
    errLogFlile = sys.argv[1]
    repoLocation = sys.argv[2]
    logFileDir = sys.argv[3]

    # Check if there are any errors logged, send email if there are
    clearLogFile(errLogFlile,logFileDir)

    smartPull(repoLocation,errLogFlile,logFileDir)

    time.sleep(1)

    # Get current state of directory without any hidden files
    oldState = Popen("ls -pla " +repoLocation+ " | grep -v /",shell=True,stdout=PIPE).stdout.read()

    while 1:
        currentState = Popen("ls -pla " +repoLocation+ " | grep -v /",shell=True,stdout=PIPE).stdout.read()
        if(currentState != oldState):
            time.sleep(2)
            smartPull(repoLocation,errLogFlile,logFileDir)
            commit(repoLocation,errLogFlile,logFileDir)
        oldState = currentState
        time.sleep(pollPeriod)


if __name__ == "__main__":
    main()




