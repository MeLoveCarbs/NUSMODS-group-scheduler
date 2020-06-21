from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from API import *
from PIL import Image
from io import BytesIO
import logging
from imageTest import *

LINKS = ["https://nusmods.com/timetable/sem-2/share?CG2023=LAB:03,PLEC:03,PTUT:03&CG2028=LAB:01,TUT:03,LEC:01&CS2107=LEC:1,TUT:06&CS2113T=LEC:C03&EG2401=TUT:201,LEC:2&EG2401A=TUT:308,LEC:1"]
WEEKS = 12
schedule = []
for elem in LINKS:
    modulesAndSemester = timetableParser(elem)
    userLessons = lessonsGenerator(modulesAndSemester)
    lessonsInWeek = dataStructureOrganizer(userLessons)[str(WEEKS)]
    schedule.append(lessonsInWeek)

earliestAndLatestTime = findEarliestAndLatestTime(schedule[0])
# timetableWithDays: 1 hr slot, timetableWhiteBlack: 2hr slot
images = dynamicImager(earliestAndLatestTime)
widths, heights = zip(*(i.size for i in images))

total_width = sum(widths)
max_height = max(heights)

new_im = Image.new('RGB', (total_width, max_height))

x_offset = 0
for im in images:
    new_im.paste(im, (x_offset, 0))
    x_offset += im.size[0]

pixels = new_im.load()
imageSizeW, imageSizeH = new_im.size

tempList = schedule[0].split('+')
for elem in tempList:
    print(elem)
    auxList = elem.split(':')  # [0] = startTime-endTime, [1] = day
    startEndTime = auxList[0].split('-')  # [0] = startTime, [1] = endTime

    day = auxList[1]
    timetableStartTime = earliestAndLatestTime[0]
    print("DEBUG2: ", startEndTime, " ", timetableStartTime, " ", day)
    pixelList = timeToPixelConverter(startEndTime, timetableStartTime, day)
    widthPixelList = pixelList[0]
    heightPixelList = pixelList[1]

    for i in range(widthPixelList[0], widthPixelList[1]):
        for j in range(heightPixelList[0], heightPixelList[1]):
            pixels[i, j] = (200, 0, 0)
