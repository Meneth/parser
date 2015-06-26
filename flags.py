def main(fileName):
    global titles
    with open("E:/Meneth/Downloads/Cities in Motion 1/pages/_file_list.txt") as inputFile:
        for line in inputFile:
            titles.append(line.rstrip()[0:-4].lower())

from common import *
import os

settings = readStatements("settings")
path = settings["path"].replace("\\", "/")

titles = []

main("nah")


history = []
for fileName in os.listdir("E:\\Meneth\\Downloads\\Cities in Motion 1\\pics"):
    history.append(fileName)

if not os.path.exists("E:\\Meneth\\Downloads\\Cities in Motion 1\\archive"):
    os.makedirs("E:\\Meneth\\Downloads\\Cities in Motion 1\\archive")

for title in history:
    if not title[0:-4].lower() in titles:
        print(title)
        os.rename("E:\\Meneth\\Downloads\\Cities in Motion 1\\pics\\%s" % (title), "E:\\Meneth\\Downloads\\Cities in Motion 1\\archive\\%s" % (title))
