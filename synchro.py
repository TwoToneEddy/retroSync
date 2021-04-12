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

def logError(logfile,error):
    now = datetime.now()
    f = open(logfile, "a")
    f.write(error + " " + os.uname()[1] + " " + now.strftime("%d/%m/%Y/ %H:%M:%S") + "\n")
    f.close()

def sendEmail(subject, message):

    server = smtplib.SMTP("smtp.mail.yahoo.com",587)
    server.starttls()

    server.login("tim.smith361@yahoo.com",'nysvfvgmjwiktrog')
    message = 'Subject: {}\n\n{}'.format(subject, message)

    server.sendmail("tim.smith361@yahoo.com","lee.hudson1384@gmail.com",message)
    server.quit()

# Moves logfile and sends email with contents
def clearLogFile(logfile):
    now = datetime.now()
    message = ""

    try:
        file = open(logfile,"r+")
        for line in file.readlines():
            message+=line
        file.close()
        #sendEmail(os.uname()[1]+" Logfile contents",message)
        os.system("mv "+logfile+" "+logfile+"_"+now.strftime("%d_%m_%Y__%H_%M_%S"))
    except:
        print "No log file \n"


# If merge conflict we have to create a branch with the stuff that conflicts and deal with it later
def mergeConflict():
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

def commit(location):

    os.chdir(location)

    mergeMessage = "Auto commit " + os.uname()[1]

    result = Popen(['/usr/bin/git', 'add', '*'],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'commit', '-m',mergeMessage],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'push', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)



def updateRepos(location,logfile):

    os.chdir(location)
    try:
        result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
        (out, error) = result.communicate()

        if error.find("Could not resolve hostname") != -1:
            logError(logfile,"No connection")
        
        if error.find("overwritten by merge") != -1:
            mergeConflict()

    except Exception as e:
        logError(e)





def main():

    pollPeriod = 10
    logfile = sys.argv[1]
    repoLocation = sys.argv[2]
    clearLogFile(logfile)
    updateRepos(repoLocation,logfile)

    # Get current state of directory without any hidden files
    oldState = Popen("ls -pla " +repoLocation+ " | grep -v /",shell=True,stdout=PIPE).stdout.read()

    while 1:
        currentState = Popen("ls -pla " +repoLocation+ " | grep -v /",shell=True,stdout=PIPE).stdout.read()
        if(currentState != oldState):
            print "Changed!"
        oldState = currentState
        time.sleep(pollPeriod)





if __name__ == "__main__":
    main()




