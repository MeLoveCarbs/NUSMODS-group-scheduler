from datetime import datetime

time1 = "0930"
time2 = "1800"
FMT = "%H%M"
delta = datetime.strptime(time2, FMT) - datetime.strptime(time1, FMT)
deltaList = str(delta).split(':')
unit = int(deltaList[0]) * 2
if (int(deltaList[1]) == 30):
    unit += 1
print(unit)