#!/usr/bin/env python
#f = open("/home/lee/demofile2.txt", "a")
#f.write("Now the file has more content!\n")
#f.close()

import os
import time
from subprocess import Popen, PIPE
from datetime import datetime
import smtplib


def logError(error):
    print "Running logError"
    print error


# If merge conflict we have to create a branch with the stuff that conflicts and deal with it later
def mergeConflict():
    now = datetime.now()
    mergeConflictBranch = now.strftime("%d_%m_%Y__%H_%M_%S")

    result = Popen(['/usr/bin/git', 'checkout', '-b', mergeConflictBranch ],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'add', '*'],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'commit', '-m','"Merge conflict 351ELEC"'],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'push', '-u', 'origin', mergeConflictBranch],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'checkout', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
    result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)


server = smtplib.SMTP("smtp.mail.yahoo.com",587)
server.starttls()

server.login("tim.smith361@yahoo.com",'nysvfvgmjwiktrog')
SUBJECT = "Testing"
TEXT = "Text"
message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

server.sendmail("tim.smith361@yahoo.com","lee.hudson1384@gmail.com",message)
server.quit()
os.chdir("/home/lee/del/testRepo")



try:
    print"Doing git pull"
    result = Popen(['/usr/bin/git', 'pull', 'origin', 'master'],stdout=PIPE,stderr=PIPE,shell=False)
    (out, error) = result.communicate()

    if error.find("Could not resolve hostname") != -1:
        logError("No connection error")
    

    if error.find("overwritten by merge") != -1:
        mergeConflict()

    print"Git pull complete"
except Exception as e:
    logError(e)



