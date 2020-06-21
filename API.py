import requests
import json
from collections import defaultdict
from unformattedModules import unformattedModules

# global vars:

lessonTypeCodes = {'Design Lecture': "DLEC",  'Laboratory': "LAB",  'Lecture': "LEC",
                   'Packaged Lecture': "PLEC",  'Packaged Tutorial': "PTUT",
                   'Recitation': "REC",  'Sectional Teaching': "SEC",
                   'Seminar-Style Module Class': "SEM",  'Tutorial': "TUT",
                   'Tutorial Type 2': "TUT2"}


def moduleApiParser(moduleName):
    templateUrl = "https://api.nusmods.com/v2/2019-2020/modules/"
    apiUrl = templateUrl + moduleName + ".json"
    response = requests.get(apiUrl)
    array = json.loads(response.text)
    semesterData = array['semesterData']
    return semesterData


def timetableParser(timetableLink):
    myDict = {}
    modulesAndSemester = []
    unformatted = []
    index = timetableLink.index("share?")
    semester = timetableLink[34:index-1]
    unparsedModules = timetableLink[index+6:]
    semiParsedModules = unparsedModules.split('&')
    for elem in semiParsedModules:
        equalsIndex = elem.index("=")
        moduleCode = elem[:equalsIndex]
        lessonDetails = elem[equalsIndex+1:].split(',')
        if moduleCode in unformattedModules:
            unformatted.append(moduleCode)
        else:
            myDict[moduleCode] = lessonDetails

    modulesAndSemester.append(myDict)
    modulesAndSemester.append(semester)
    modulesAndSemesterAndUnformatted = []
    modulesAndSemesterAndUnformatted.append(modulesAndSemester)
    modulesAndSemesterAndUnformatted.append(unformatted)
    # first index contains modules and semester info, 2nd index contains unformatted modules info
    return modulesAndSemesterAndUnformatted


def lessonsGenerator(modulesAndSemester):
    userLessons = []
    semester = modulesAndSemester[1]
    for module, lesson in modulesAndSemester[0].items():
        rawModuleData = moduleApiParser(module)
        moduleData = None
        for elem in rawModuleData:
            if (elem['semester'] == int(semester)):
                moduleData = elem
        allLessonDict = defaultdict(list)
        for elem in moduleData['timetable']:
            # print(module, " ", elem)
            key = lessonTypeCodes[elem['lessonType']]+":"+elem['classNo']
            weeks = ','.join(map(str, elem['weeks']))
            value = elem['startTime'] + "-" + \
                elem['endTime'] + ":" + elem['day'] + ":" + weeks
            allLessonDict[key].append(value)
        # print(module, "\n", allLessonDict)
        for elem in lesson:
            userLessons.append(allLessonDict[elem])
    return userLessons


def dataStructureOrganizer(userLessons):
    # week1: "0900-1200:Friday+0800-1100:Thursday" week2: "1300-1500:Wednesday"
    lessonsPerWeek = {}
    for elem in userLessons:
        for subelem in elem:
            tempList = subelem.split(':')
            auxList = tempList[2].split(',')
            for weekCount in auxList:
                if weekCount in lessonsPerWeek:
                    toAdd = "+" + tempList[0] + ":" + tempList[1]
                    lessonsPerWeek[weekCount] += toAdd
                else:
                    toAdd = tempList[0] + ":" + tempList[1]
                    lessonsPerWeek[weekCount] = toAdd
    # for key, value in lessonsPerWeek.items():
    #     print(key, " ", value)
    return lessonsPerWeek


def getModules(modulesAndSemester):
    modules = []
    for elem in modulesAndSemester[0]:
        modules.append(elem)
    return modules


def findEarliestAndLatestTime(scheduleAndMemberList):
    earliest = 2330
    latest = 0
    for scheduleAndMember in scheduleAndMemberList:
        schedule = scheduleAndMember.split("@")
        tempList = schedule[0].split('+')
        for elem in tempList:
            tempTimeList = elem.split(':')
            tempTimeListSpecific = tempTimeList[0].split('-')
            for subelem in tempTimeListSpecific:
                # print(subelem)
                if int(subelem) > int(latest):
                    latest = subelem
                if int(subelem) < int(earliest):
                    earliest = subelem

    return [earliest, latest]


def main():
    modulesAndSemester = timetableParser(
        "https://nusmods.com/timetable/sem-2/share?CG2023=LAB:03,PLEC:03,PTUT:03&CG2028=LAB:01,TUT:03,LEC:01&CS2107=LEC:1,TUT:06&CS2113T=LEC:C03")
    userLessons = lessonsGenerator(modulesAndSemester)
    lessonsInWeek = dataStructureOrganizer(userLessons)
    for key, values in lessonsInWeek.items():
        print(key, " ", values)
    findEarliestAndLatestTime(lessonsInWeek, "9")


if __name__ == '__main__':
    main()
