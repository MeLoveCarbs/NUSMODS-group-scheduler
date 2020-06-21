import requests
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from io import BytesIO
import sys
from math import ceil
from datetime import datetime
from API import *

#global vars
timetableWidth = [109]
timetableWidthDiff = 117  # half a block ie, 30minutes per widthDiff
timestampWidthDiff = 234
timetableHeight = [2, 116]
timetableHeightDiff = 117
dayToDigit = {"Monday": 0, "Tuesday": 1,
              "Wednesday": 2, "Thursday": 3, "Friday": 4}
timeString = ["0700", "0800", "0900", "1000", "1100", "1200", "1300", "1400",
              "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300"]
timeStringIndex = {"07": 0, "08": 1, "09": 2, "10": 3, "11": 4, "12": 5, "13": 6, "14": 7,
                   "15": 8, "16": 9, "17": 10, "18": 11, "19": 12, "20": 13, "21": 14, "22": 15, "23": 16}
RGBshade = {0.1: (255, 240, 0), 0.2: (255, 224, 0), 0.3: (255, 208, 0), 0.4: (255, 192, 0), 0.5: (
    255, 176, 0), 0.6: (255, 160, 0), 0.7: (255, 128, 0), 0.8: (255, 96, 0), 0.9: (255, 80, 0), 1: (255, 0, 0)}


def timeToUnit(diffTime, timetableStartTime):
    FMT = "%H%M"
    delta = datetime.strptime(str(diffTime), FMT) - \
        datetime.strptime(str(timetableStartTime), FMT)
    deltaList = str(delta).split(':')
    unit = int(deltaList[0]) * 2
    if (int(deltaList[1]) == 30):
        unit += 1
    return unit


# startEndTime: ["0900-1200"], timetableStartTime: "0900", day= "Monday"
def timeToPixelConverter(startEndTime, timetableStartTime, day):
    # units of 30mins
    # find difference between timetableStartTime and blocked time
    widthStart = timeToUnit(startEndTime[0], timetableStartTime)
    widthEnd = timeToUnit(startEndTime[1], timetableStartTime)
    widthStartPixel = timetableWidth[0] + (widthStart*timetableWidthDiff)
    widthEndPixel = timetableWidth[0] + (widthEnd*timetableWidthDiff)
    heightStartPixel = timetableHeight[0] + dayToDigit[day]*timetableHeightDiff
    heightEndPixel = timetableHeight[1] + dayToDigit[day]*timetableHeightDiff
    return [[widthStartPixel, widthEndPixel], [heightStartPixel, heightEndPixel]]


# earliestAndLatestTime: ["0900", "1800"]
def dynamicImager(earliestAndLatestTime, timestampOrtimetable):
    start = earliestAndLatestTime[0][0:2]
    end = earliestAndLatestTime[1][0:2]
    timeDiff = int(end) - int(start)
    timetableWhiteBlackCount = ceil(timeDiff/2)
    toAppend = None
    if timestampOrtimetable == "timetable":
        imageToOpen = ["./timetableImage/timetableWithDays.png"]
        toAppend = "./timetableImage/timetableWhiteBlack.png"
    elif timestampOrtimetable == "timestamp":
        imageToOpen = ["./timetableImage/timestampStart.jpg"]
        toAppend = "./timetableImage/timestampWhiteBlack.jpg"

    for elem in range(timetableWhiteBlackCount):
        imageToOpen.append(toAppend)

    images = [Image.open(x) for x in imageToOpen]

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    return new_im


def timestampDrawer(img, earliestAndLatestTime):
    start = timeStringIndex[earliestAndLatestTime[0][0:2]]
    end = timeStringIndex[earliestAndLatestTime[1][0:2]]
    draw = ImageDraw.Draw(img)
    widthIndex = 0
    extra = None
    if ((end-start) % 2 != 0):
        extra = 2
    else:
        extra = 1
    for elem in range(start, end+extra):
        draw.text((75+timestampWidthDiff*widthIndex, 85), timeString[elem], font=ImageFont.truetype(
            "arial.ttf", 30), fill=(255, 0, 0))
        widthIndex += 1
