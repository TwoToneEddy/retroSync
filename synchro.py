#!/usr/bin/env python2.7
#f = open("/home/lee/demofile2.txt", "a")
#f.write("Now the file has more content!\n")
#f.close()

import os
import time
import sys
from subprocess import Popen, PIPE
from datetime import datetime
import smtplib
import urllib2

class BackupHelper:
    def __init__(self,repoLocation,logFileDir,errLogDir,pollPeriod):
        self.repoLocation = repoLocation
        self.logFileDir = logFileDir
        self.pollPeriod = pollPeriod
        self.repoName = self.repoLocation.split('/')[-1]
        self.errLogFlile = errLogDir + "/" + self.repoName + "_err.txt"

    def logMessage(self,message):
        now = datetime.now()
        fileName = self.logFileDir+"/log_"+now.strftime("%d_%m_%Y") + ".txt"
        f = open(fileName, "a")
        f.write(os.uname()[1] + " " + now.strftime("%d/%m/%Y/ %H:%M:%S") + "\n" + "\t" +message)
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
            self.logMessage("Email sent")
            return 0
        except:
            self.logError("Unable to send email")
            return 1


    # If an error logfile exists send the contents of that file as an email.
    # If the email suceeds then move the error log file.
    def clearLogFile(self):
        now = datetime.now()
        message = ""

        try:
            file = open(self.errLogFlile,"r+")
            for line in file.readlines():
                message+=line
            file.close()
            if self.sendEmail(os.uname()[1]+" Logfile contents",message) == 0:
                os.system("mv "+self.errLogFlile+" "+self.errLogFlile+"_"+now.strftime("%d_%m_%Y__%H_%M_%S"))
        except:
            return


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
        message += mergeConflictBranch + " created and pushed\n"+"\t"
        message += "This means something had changed before a pull was done\n"
        self.sendEmail(subject,message)

    # Basic commit
    def commit(self, files):

        os.chdir(self.repoLocation)

        mergeMessage = "Auto commit @TwoToneEddy " + os.uname()[1]

        # Git add
        for file in files:
            result =  Popen(['/usr/bin/git', 'add', file],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = result.communicate()
            if len(out) > 1:
                self.logMessage("commit() performing git add *\n"+"\t" +out)
            if len(error) > 1:
                self.logMessage("commit() performing git add *\n"+"\t" +error)

        # Git commit
        result = Popen(['/usr/bin/git', 'commit', '-m',mergeMessage],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()
        if len(out) > 1:
            self.logMessage("commit() performing git commit\n"+"\t" +out)
        if len(error) > 1:
            self.logMessage("commit() performing git commit\n"+"\t" +error)

        # Git push
        result = Popen(['/usr/bin/git', 'push', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()
        if len(out) > 1:
            self.logMessage("commit() performing git push origin master \n"+"\t" +out)
        if len(error) > 1:
            self.logMessage("commit() performing git push origin master \n"+"\t" +error)
        
        if error.find("Could not resolve hostname") != -1:
            self.logError("Git push failed in BackupHelper.commit(), no connection")


    def push(self):

        os.chdir(self.repoLocation)
        success = False
        try:
            result = Popen(['/usr/bin/git', 'push', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = result.communicate()
            if len(out) > 1:
                self.logMessage("push() performing git push origin master \n"+"\t" +out)
            if len(error) > 1:
                self.logMessage("push() performing git push origin master \n"+"\t" +error)
                

            if error.find("Could not resolve hostname") != -1:
                self.logError("Git push failed in BackupHelper.push(), no connection")
                
        except Exception as e:
            self.logError(e)

    def smartPull(self):

        os.chdir(self.repoLocation)
        success = False
        try:
            result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = result.communicate()
            if len(out) > 1:
                self.logMessage("smartPull() performing git pull origin master \n" +"\t"+out)
            else:
                if len(error) > 1:
                    self.logMessage("smartPull() performing git pull origin master \n"+"\t" +error)
                

            if error.find("Could not resolve hostname") != -1:
                self.logError("Git pull failed in BackupHelper.smartPull(), no connection")
                return

            if error.find("overwritten by merge") != -1:
                self.mergeConflict()
                
            # If we have succeeded in the pull it means we have a connection, clear the log file. 
            self.clearLogFile()

        except Exception as e:
            self.logError(e)

    def run(self):
        os.chdir(self.repoLocation)
        while(1):    
            gitStatus = Popen(['/usr/bin/git', 'status', '-s'],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = gitStatus.communicate()

            # Get a list from the git status command
            gitStatusOutput = out.split('\n')
            gitStatusOutput.pop()
            gitStatusOutputClean = list()
            gitStatusOutputReallyClean = list()
            # Go through and remove any bin files

            for index, change in enumerate(gitStatusOutput):
                if change.find(".smc") != -1:
                    gitStatusOutput[index] = ''
            
            for change in gitStatusOutput:
                if len(change) > 0:
                    gitStatusOutputClean.append(change[3:])

            # Convert spaces for linux
            for index, change in enumerate(gitStatusOutputClean):
                gitStatusOutputClean[index] = gitStatusOutputClean[index].replace('"','')
                gitStatusOutputClean[index] = gitStatusOutputClean[index].replace(' ',"\\ ")

            # If the length of the git status list is > 0 after removing the bin
            # files then we have something we want
            gitStatusLength = len(gitStatusOutputClean)
            if(gitStatusLength > 0):
                time.sleep(1)
                self.smartPull()
                self.commit(gitStatusOutputClean)
            time.sleep(self.pollPeriod)


def wait_for_internet_connection():
    while True:
        try:
            response = urllib2.urlopen('http://www.github.com',timeout=1)
            return
        except urllib2.URLError:
            pass
# Args
# 0 Repository location
# 1 Path to log directory 
# 2 Path to error log directory
def main():

    helper = BackupHelper(sys.argv[1],sys.argv[2],sys.argv[3],5)

    helper.logMessage("Device powered up, waiting for connection\n")
    wait_for_internet_connection()
    helper.logMessage("Connection successful\n")
    
    helper.clearLogFile()


    helper.smartPull()
    helper.push()

    time.sleep(1)

    helper.run()



if __name__ == "__main__":
    main()




