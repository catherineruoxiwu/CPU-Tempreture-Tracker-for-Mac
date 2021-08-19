import os
import time
import daemon
from datetime import datetime
# 首先进行一次fork，防止对原有进程产生干扰
pid = os.fork()
print(pid)
f = open("lalalla.txt", "w+t")

# 对于fork出的子进程，进入Daemon模式
with daemon.DaemonContext():
    while True:
        try:
            f.write("hahah")
            print(datetime.now())
        except ImportError as e:
            f.write("hehehe")
                # logger.warning("setproctitle module not found")
        time.sleep(3600)