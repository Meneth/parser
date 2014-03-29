def main(fileName):
    global titles
    inputFile = structureFile(fileName, path, "common\landed_titles") #Transcribes game file to more parseable format
    #print(inputFile)
    for line in inputFile:
        if line[:2] == "d_" or line[:2] == "c_" or line[:2] == "k_" or line[:2] == "e_" or line[:2] == "b_":
            titles.append(getValues(line)[0].lower())

from common import *
import os

settings = readStatements("settings")
path = settings["path"].replace("\\", "/")

flags = []
for fileName in os.listdir("%s\gfx\\flags" % (path)):
    flags.append(fileName.lower())

history = []
for fileName in os.listdir("%s\history\\titles" % (path)):
    history.append(fileName.lower())

titles = []
for fileName in os.listdir("%s\common\landed_titles" % (path)):
    main(fileName)

if not os.path.exists("%s\gfx\\archive" % path):
    os.makedirs("%s\gfx\\archive" % path)

if not os.path.exists("%s\history\\archive" % path):
    os.makedirs("%s\history\\archive" % path)

for flag in flags:
    if not flag[:len(flag)-4] in titles:
        print(flag)
        os.rename("%s\gfx\\flags\%s" % (path, flag), "%s\gfx\\archive\%s" % (path, flag))

for title in history:
    if not title[:len(title)-4] in titles:
        print(title)
        os.rename("%s\history\\titles\%s" % (path, title), "%s\history\\archive\%s" % (path, title))