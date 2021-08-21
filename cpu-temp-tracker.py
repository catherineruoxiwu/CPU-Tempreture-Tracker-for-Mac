# gem install iStats
# 0-2 fans
# Visulize cpu tempreture, battery tempreture, fan speed

import os, re, time, subprocess, atexit, json
from datetime import datetime
from tempfile import TemporaryFile
import matplotlib.pyplot as plt



############### GLOBAL VARIABLES ###############

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
DATE = datetime.today().strftime("%Y-%m-%d")
OUT_PATH = os.path.join(ROOT_DIR, DATE)
LOG_PATH = os.path.join(OUT_PATH, "Log.json")
GRAPH_PATH = os.path.join(OUT_PATH, "Graph.png")
print(OUT_PATH)



############### INITIALIZATION ###############

def get_prev_log():
    global CPU_TEMP_ARR, BATERRY_TEMP_ARR, FAN_SPEED_ARR, TIME_ARR, BATTERY_PERCENTAGE_ARR
    if not os.path.exists(OUT_PATH):
        os.mkdir(OUT_PATH)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as logfile:
            logdata = json.load(logfile)  
        CPU_TEMP_ARR += logdata["cpu temp"]
        BATERRY_TEMP_ARR += logdata["battery temp"]
        FAN_SPEED_ARR += logdata["fan speed"]
        TIME_ARR += logdata["time"]
        BATTERY_PERCENTAGE_ARR += logdata["battery percentage"]



############### GET AND PROCESS COMPUTER STATS ###############

def get_info(file):
    file.seek(0)
    process = subprocess.Popen("istats all", stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    output_string = output.decode("utf-8")
    file.write(output_string)

def process_info(file):
    global CPU_TEMP_ARR, BATERRY_TEMP_ARR, FAN_SPEED_ARR, TIME_ARR, BATTERY_PERCENTAGE_ARR
    file.seek(0)
    filecontent = file.read()
    cpu_temp_stringlist = re.findall(CPU_TEMP_REG, filecontent)
    battery_temp_stringlist = re.findall(BATTERY_TEMP_REG, filecontent)
    fan_speed_stringlist = re.findall(FAN_SPEED_REG, filecontent)
    if len(cpu_temp_stringlist) == 0 or len(battery_temp_stringlist) == 0 or len(fan_speed_stringlist) != 1:
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
    TIME_ARR.append(datetime.now().strftime("%H:%M"))

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



############### GRAPHING AND STORING DATA ###############

def manage_exit():
    graph_data()
    store_data()

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
    plt.savefig(GRAPH_PATH, bbox_inches="tight", dpi=600, pad_inches=0.5)

def store_data():
    global CPU_TEMP_ARR, BATERRY_TEMP_ARR, FAN_SPEED_ARR, TIME_ARR, BATTERY_PERCENTAGE_ARR
    effective_arr_len = min(len(CPU_TEMP_ARR), len(BATERRY_TEMP_ARR), len(FAN_SPEED_ARR), len(TIME_ARR), len(BATTERY_PERCENTAGE_ARR))
    CPU_TEMP_ARR = CPU_TEMP_ARR[0:effective_arr_len]
    BATERRY_TEMP_ARR = BATERRY_TEMP_ARR[0:effective_arr_len]
    FAN_SPEED_ARR = FAN_SPEED_ARR[0:effective_arr_len]
    TIME_ARR = TIME_ARR[0:effective_arr_len]
    BATTERY_PERCENTAGE_ARR = BATTERY_PERCENTAGE_ARR[0:effective_arr_len]
    log = {"cpu temp": CPU_TEMP_ARR,
           "battery temp": BATERRY_TEMP_ARR,
           "fan speed": FAN_SPEED_ARR,
           "time": TIME_ARR,
           "battery percentage": BATTERY_PERCENTAGE_ARR}
    with open(LOG_PATH, "w") as logfile:
        json.dump(log, logfile, indent=4)

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



############### MAIN ###############
#TODO: 横轴日期
#TODO: 跨日期
#TODO：图虚线实线
#TODO: support devices with 0 or more fans
if __name__ == '__main__':
    get_prev_log()
    atexit.register(manage_exit)
    while True:
        temp_log = TemporaryFile("w+t")
        get_info(temp_log)
        process_info(temp_log)
        temp_log.close()
        time.sleep(300)
