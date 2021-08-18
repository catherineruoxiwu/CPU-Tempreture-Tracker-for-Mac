# gem install iStats
# 0-2 fans

# Visulize cpu tempreture, battery tempreture, fan speed

import os, re, time, subprocess
from datetime import datetime
from tempfile import TemporaryFile
import matplotlib.pyplot as plt


CPU_TEMP_REG = r"CPU temp:\s+[0-9]*\.[0-9]+"
BATTERY_TEMP_REG = r"Battery temp:\s+[0-9]*\.[0-9]+"
FAN_SPEED_REG = r"Fan 0 speed:\s+[0-9]+ RPM"
DEC_REG = r"[0-9]*\.[0-9]+"
INT_REG = r"[0-9]+"

CPU_TEMP_ARR = []
BATERRY_TEMP_ARR = []
FAN_SPEED_ARR = []
TIME_ARR = []
BATTERY_PERCENTAGE_ARR = []

ROOT_DIR = os.path.dirname(__file__)
DIR_NAME = "Out"

# def init():
    

def get_info(file):
    process = subprocess.Popen("istats all", stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    output_string = output.decode("utf-8")
    file.write(output_string)

def process_info(file):
    file.seek(0)
    filecontent = file.read()
    cpu_temp_stringlist = re.findall(CPU_TEMP_REG, filecontent)
    battery_temp_stringlist = re.findall(BATTERY_TEMP_REG, filecontent)
    fan_speed_stringlist = re.findall(FAN_SPEED_REG, filecontent)
    if len(cpu_temp_stringlist) == 0 or len(battery_temp_stringlist) == 0 or len(fan_speed_stringlist) == 0:
        print("Oops. Your device is not supported.")
        exit()
    cpu_temp = float(re.findall(DEC_REG, cpu_temp_stringlist[0])[0])
    check_cpu_temp(cpu_temp)
    battery_temp = float(re.findall(DEC_REG, battery_temp_stringlist[0])[0])
    fan_speed = int(re.findall(INT_REG, fan_speed_stringlist[0])[1])
    battery_percentage = get_battery_percentage(file)
    CPU_TEMP_ARR.append(cpu_temp)
    BATERRY_TEMP_ARR.append(battery_temp)
    FAN_SPEED_ARR.append(fan_speed)
    BATTERY_PERCENTAGE_ARR.append(battery_percentage)
    TIME_ARR.append(datetime.now().strftime("%H:%M:%S"))

def get_battery_percentage(file):
    file.seek(0)
    lines = file.readlines()
    for line in lines:
        if "Current charge:" not in line:
            continue
        percentage_sign_idx = line.index('%')
        battery_percentage = int(line[percentage_sign_idx-3:percentage_sign_idx])
        if battery_percentage >= 100:
            return 100
        return battery_percentage

def check_cpu_temp(cpu_temp):
    cmd = "osascript -e \'Tell application \"System Events\" to display dialog \"Your CPU tempreture is now above 80°C.\" with title \"Warning\"\'"
    if cpu_temp >= 80:
        os.popen(cmd)
        os.close()


#TODO：store png
def graph_data():
    plt.figure(figsize=(10,7.5), constrained_layout=True)
    graph1 = plt.subplot(221)
    graph2 = plt.subplot(222)
    graph3 = plt.subplot(223)
    graph4 = plt.subplot(224)
    graph_battery_vs_time(graph1)
    graph_speed_vs_time(graph2)
    graph_temp_vs_time(graph3)
    graph_temp_vs_speed(graph4)
    plt.savefig("today.png", bbox_inches="tight", dpi=600, pad_inches=0.5)
    plt.show()

def graph_battery_vs_time(plt):
    plt.plot(TIME_ARR, BATTERY_PERCENTAGE_ARR, color="g")
    plt.set_xlabel('Time')
    plt.set_ylabel('Battery Percentage')
    plt.set_ylim(ymin=0, ymax=102)
    plt.fill_between(TIME_ARR, BATTERY_PERCENTAGE_ARR, interpolate=True, color='palegreen', alpha=0.5)

def graph_speed_vs_time(plt):
    plt.plot(TIME_ARR, FAN_SPEED_ARR, color="c")
    plt.set_xlabel('Time')
    plt.set_ylabel('Fan Speed (Unit: RPM)')
    plt.set_ylim(ymin=0, ymax=max(FAN_SPEED_ARR) * 1.2)

def graph_temp_vs_time(plt):
    plt.plot(TIME_ARR, CPU_TEMP_ARR, color="r", label="CPU")
    plt.plot(TIME_ARR, BATERRY_TEMP_ARR, color="b", label="Battery")
    plt.legend()
    plt.set_xlabel('Time')
    plt.set_ylabel('Tempreture (Unit: °C)')
    plt.set_ylim(ymin=0, ymax=max(max(CPU_TEMP_ARR), max(BATERRY_TEMP_ARR)) * 1.35)

def graph_temp_vs_speed(plt):
    plt.scatter(FAN_SPEED_ARR, CPU_TEMP_ARR, marker="^", color="r", label="CPU")
    plt.scatter(FAN_SPEED_ARR, BATERRY_TEMP_ARR, marker="o", color="b", label="Battery")
    plt.legend()
    plt.set_xlabel('Fan Speed (Unit: RPM)')
    plt.set_ylabel('Tempreture (Unit: °C)')
    plt.set_ylim(ymin=0, ymax=max(max(CPU_TEMP_ARR), max(BATERRY_TEMP_ARR)) * 1.35)

#TODO: 判断有没有安装iStats，init
#TODO: 画图before exit: close os; save graph
#TODO：判断画图时机
#TODO：文件路径正确
#TODO: 在背景运行
#TODO: support devices with 0 or more fans
if __name__ == '__main__':
    # init()
    count = 0
    while count < 20:
        temp_log = TemporaryFile("w+t")
        temp_log.write("jajaj")
        temp_log.seek(0)
        get_info(temp_log)
        process_info(temp_log)
        temp_log.close()
        time.sleep(100)
        count = count + 1
    graph_data()