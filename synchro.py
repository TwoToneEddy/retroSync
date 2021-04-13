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


class BackupHelper:
    def __init__(self,errLogFlile,repoLocation,logFileDir,pollPeriod):
        self.errLogFlile = errLogFlile
        self.repoLocation = repoLocation
        self.logFileDir = logFileDir
        self.pollPeriod = pollPeriod

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
        message += mergeConflictBranch + " created and pushed\n"+"\t"
        message += "This means something had changed before a pull was done\n"
        self.sendEmail(subject,message)

    # Basic commitlogFileDir
    def commit(self):

        os.chdir(self.repoLocation)

        mergeMessage = "Auto commit " + os.uname()[1]

        # Git add
        result =  Popen(['/usr/bin/git', 'add', '*'],stdout=PIPE,stderr=PIPE,shell=False)
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
        
        while(1):    
            gitStatus = Popen(['/usr/bin/git', 'status', '-s'],stdout=PIPE,stderr=PIPE,shell=False)
            (out, error) = gitStatus.communicate()
            gitStatusLength = len(out)
            if(gitStatusLength > 1):
                time.sleep(1)
                self.smartPull()
                self.commit()
            time.sleep(self.pollPeriod)



# Args
# 0 Error log file
# 1 Repository location
# 2 Path to log directory  
def main():

    helper = BackupHelper(sys.argv[1],sys.argv[2],sys.argv[3],1)

    helper.logMessage("Device powered up\n")
    helper.clearLogFile()

    helper.smartPull()
    helper.push()

    time.sleep(1)

    helper.run()



if __name__ == "__main__":
    main()




