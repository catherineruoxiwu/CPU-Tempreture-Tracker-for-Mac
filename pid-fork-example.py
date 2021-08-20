import os
import time

print ("Before fork process pid=%s, ppid=%s" % (os.getpid(), os.getppid()))

pid = os.fork()
if pid == 0:
    print ("I am child process pid=%s, ppid=%s" % (os.getpid(), os.getppid()))
    time.sleep(5)
else:
    # parent's pid = child's ppid
    print ("I am parent process pid=%s, ppid=%s" % (os.getpid(), os.getppid()))
    time.sleep(5)

# Printed twice: once in the parent thread and once in the child thread
print ("After fork process pid=%s, ppid=%s" % (os.getpid(), os.getppid()))
