from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from API import *
from PIL import Image
from io import BytesIO
import logging
from timetableBuilder import *
import os

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# global vars:
MEMBERS = None
LINKS = []
WEEKS = None

MEMBERCOUNT, WEEKCOUNT, LINKCOUNT, SHOWIMAGE = range(4)


def start(update, context):
    keyboard = [['3', '4', '5', '6', '/cancel']]

    global MEMBERS, LINKS, WEEKS
    MEMBERS = None
    LINKS = []
    WEEKS = None
    message = "Welcome, how many members are there on your group?"
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text(message, reply_markup=reply_markup)
    return MEMBERCOUNT


def member(update, context):
    global MEMBERS
    MEMBERS = update.message.text
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Please input " + MEMBERS +
                             " NUSMODS link\nThe NUSMODS link can be retrieve as seen below, or /cancel to restart")
    context.bot.send_photo(chat_id=chat_id, photo=open(
        "./miscImage/guider.png", "rb"))
    return LINKCOUNT


def link(update, context):
    # Feature not implemented: reset all links stored.
    keyboard_ongoing = [['/cancel']]
    reply_markup_ongoing = ReplyKeyboardMarkup(keyboard_ongoing,
                                               one_time_keyboard=True,
                                               resize_keyboard=True)

    keyboard_done = [['/complete', '/cancel']]
    reply_markup_done = ReplyKeyboardMarkup(keyboard_done,
                                            one_time_keyboard=True,
                                            resize_keyboard=True)
    global LINKS
    global MEMBERS
    LINKS.append(update.message.text)
    logger.info("Appended")
    if (int(MEMBERS) > len(LINKS)):
        remaining = int(MEMBERS) - len(LINKS)
        update.message.reply_text("{0} link/s remaining".format(remaining))
        return LINKCOUNT
    else:
        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id=chat_id, text="Successfully stored all NUSMODS links. /complete to move on, /cancel to restart", reply_markup=reply_markup_done)
        return WEEKCOUNT


def week(update, context):
    keyboard = [['3', '4', '5', '6', '7', '8',
                 '9', '10']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, text="Please choose which week to show. For eg, \"12\" means week 12. /cancel to restart", reply_markup=reply_markup)

    return SHOWIMAGE


def show(update, context):
    keyboard = [['/showanother', '/cancel']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    global WEEKS
    WEEKS = update.message.text
    index = 0
    scheduleAndMemberList = []
    totalUnformatted = []
    for elem in LINKS:
        modulesAndSemesterAndUnformatted = timetableParser(elem)
        modulesAndSemester = modulesAndSemesterAndUnformatted[0]
        unformatted = modulesAndSemesterAndUnformatted[1]
        totalUnformatted.append(unformatted)
        userLessons = lessonsGenerator(modulesAndSemester)
        lessonsInWeek = dataStructureOrganizer(userLessons)[str(WEEKS)]
        scheduleAndMemberList.append(lessonsInWeek + "@" + str(index))
        index += 1

    chat_id = update.message.chat_id
    update.message.reply_text(
        "Here is week " + WEEKS + " schedule for your group, darker shade of red represents more people are unavailable, /showanother to see another week, or /cancel to restart\nPlease wait while your timetable is loading.", reply_markup=reply_markup)

    unformattedInList = []
    for userUnformatted in totalUnformatted:
        for unformatted in userUnformatted:
            if unformatted not in unformattedInList:
                unformattedInList.append(unformatted)
    if len(unformattedInList) != 0:
        unformattedInString = " ".join(unformattedInList)
        context.bot.send_message(
            chat_id=chat_id, text="TAKE NOTE\nThe following module\s doesn't follow the standard 13 weeks per semester convention, and cannot be displayed: " + unformattedInString)

    earliestAndLatestTime = findEarliestAndLatestTime(scheduleAndMemberList)
    # timetableWithDays: 1 hr slot, timetableWhiteBlack: 2hr slot
    new_im = dynamicImager(earliestAndLatestTime, "timetable")
    imageTimestamp = dynamicImager(earliestAndLatestTime, "timestamp")
    timestampDrawer(imageTimestamp, earliestAndLatestTime)

    pixels = new_im.load()
    pixelDict = {}
    pixelMemberSet = set()

    for scheduleAndMember in scheduleAndMemberList:
        scheduleAndMemberArr = scheduleAndMember.split("@")
        schedule = scheduleAndMemberArr[0]
        member = scheduleAndMemberArr[1]
        tempList = schedule.split('+')
        for elem in tempList:
            auxList = elem.split(':')  # [0] = startTime-endTime, [1] = day
            # [0] = startTime, [1] = endTime
            startEndTime = auxList[0].split('-')

            day = auxList[1]
            timetableStartTime = earliestAndLatestTime[0]
            pixelList = timeToPixelConverter(
                startEndTime, timetableStartTime, day)
            widthPixelList = pixelList[0]
            heightPixelList = pixelList[1]

            for i in range(widthPixelList[0], widthPixelList[1]):
                for j in range(heightPixelList[0], heightPixelList[1]):
                    key = str(i)+":" + str(j)
                    keyWithMember = str(i) + ":"+str(j)+"@"+member
                    # If pixel belongs to same member, skip. Because it means the user has 2 mods in 1 timeslot
                    if keyWithMember not in pixelMemberSet:
                        if key in pixelDict:
                            pixelDict[key] += 1
                        else:
                            pixelDict[key] = 1
                    pixelMemberSet.add(keyWithMember)

    for key, value in pixelDict.items():
        ijArr = key.split(":")
        i = int(ijArr[0])
        j = int(ijArr[1])
        fraction = round(value/int(MEMBERS), 1)
        if fraction == 0:
            fraction = 0.1
        RGB = RGBshade[fraction]
        pixels[i, j] = RGB

    dst = Image.new(
        'RGB', (new_im.width, new_im.height+imageTimestamp.height-60))
    dst.paste(imageTimestamp, (0, -60))
    dst.paste(new_im, (0, imageTimestamp.height-60))

    bio = BytesIO()
    bio.name = 'image.png'
    dst.save(bio, 'png')
    bio.seek(0)

    context.bot.send_photo(chat_id=chat_id, photo=bio)
    return WEEKCOUNT


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! /start to begin again',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    authToken = None
    with open("authToken.txt") as reader:
        authToken = reader.read()
    updater = Updater(authToken, use_context=True)
    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MEMBERCOUNT: [MessageHandler(Filters.regex('1|2|3|4|5|6|7|8|9|10'), member)],

            LINKCOUNT: [MessageHandler(Filters.regex('https://nusmods\.com/timetable/sem-./share\?.*'), link)],

            WEEKCOUNT: [MessageHandler(Filters.regex('/complete'), week),
                        MessageHandler(Filters.regex('/showanother'), week)],

            SHOWIMAGE: [MessageHandler(
                Filters.regex('^([1-9]|1[0-3])$'), show)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=False
    )

    dp.add_handler(conv_handler)

    # Log all errors:
    dp.add_error_handler(error)
    # Start bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=authToken)
    updater.bot.setWebhook(
        'https://serene-reaches-64631.herokuapp.com/' + authToken)
    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    main()
