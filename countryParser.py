def main(fileName):
    global outputDict
    inputFile = structureFile(fileName) #Transcribes game file to more parseable format
    outputDict = {}
    for line in inputFile:
        #Determines how deeply nested the current line is
        nestingCheck(line)
        if nesting > 0:
            continue
        command, value = getValues(line)
        if not '"%s"' % command in countryCommands:
            continue
        value = valueLookup(value)
        output(command, value)
    outputText = "| [[File:%s.png|100px|border]] '''[[%s]]''' || '''%s'''" % (countries[fileName[:3]], countries[fileName[:3]], fileName[:3])
    for token in countryCommands:
        try:
            outputText += " || " + outputDict[token.strip('"')]
        except KeyError:
            outputText += " || "
    try:
        return outputText +"\n|-\n"
    except UnboundLocalError:
        return ""



#Reads in a statement file as a dictionary
def readStatements(localisationName):
    localisation = {}
    with open('%s.txt' % localisationName) as effectsFile:
        for line in effectsFile.readlines():
            if not ":" in line: #Not a statement string
                continue
            StatementName, formatString = line.split(':', 1)
            localisation[StatementName.strip()] = formatString.strip()

    return localisation

#Reads in a definition file as a dictionary
def readDefinitions(name):
    definitions = {}
    with open(path+"/localisation/%s_l_english.yml" % name, encoding="utf-8") as definitionsFile:
        lines = definitionsFile.readlines()
        lineNumber = 1
        for line in lines[1:]:
            if not ":" in line:
                continue
            try:
                identifier, value = line.split(':', 1)
                definitions[identifier.strip()] = value.strip('" \n')
            except ValueError:
                print ("%d -> %s" % (lineNumber, line))
            lineNumber += 1

    return definitions

#Splits the file at every bracket to ensure proper parsing
def structureFile(name):
    functionOutput = []

    with open('%s/history/countries/%s' % (path, name), encoding="Windows-1252") as file:
        for line in file:
            if "#" in line:
                line = line.split("#")[0]
            if line == "":
                continue
            line = line.replace("{", "{\n").replace("}", "\n}").strip() #Splits line at brackets
            if line == "":
                continue
            if "=" in line:
                count = line.count("=")
                if count > 1:
                    for values in range(count):
                        line = re.sub("(=[\s]*[\w\.]*) ([\w\.]*[\s]*=)", "\g<1>\n\g<2>", line) #Splits lines with more than one statement in two
            if "\n" in line:
                parts = line.split("\n")
                for p in parts:
                    functionOutput.append(p)
            else:
                functionOutput.append(line)
    return functionOutput

#Determines the current level of nesting
def nestingCheck(line):
    global nesting
    global nestingIncrement
    nestingIncrement = 0
    #Thanks to file restructuring, it is impossible for there to be multiple brackets on a line
    if "{" in line:
        nesting += 1
        nestingIncrement = 1
    elif "}" in line:
        nesting -= 1
        nestingIncrement = -1

def getValues(line):
    line = line.split("=")
    line[0] = line[0].strip()
    try: #Checks if the command has a value
        line[1] = line[1].strip().strip('{}"')
        return line[0], line[1]
    except IndexError:
        return line[0], ""

def valueLookup(value):
    try:
        return provinces["PROV"+value]
    except KeyError:
        try:
            int(value)
            print("Could not look up province with value %s" % value)
        except ValueError:
            pass
    try:
        return lookup[value]
    except KeyError:
        pass
    return value

def output(command, value): #Outputs line to a temp variable. Written to output file when input file is parsed
    global outputDict
    outputDict[command] = value

import cProfile, pstats
pr = cProfile.Profile()
pr.enable()

import time #Used for timing the parser
start = time.clock()
import re #Needed for various string handling
import os #Used to grab the list of files
settings = readStatements("settings")
path = settings["path"].replace("\\", "/")

#Dictionaries of known statements
countryStatements = readStatements("statements/countryStatements")
countryCommands = countryStatements["commands"].split()
nesting, nestingIncrement = 0, 0
finalOutput = ""

try:
    #Dictionaries of relevant values
    provinces = readDefinitions("prov_names")
    countries = readDefinitions("countries")
    countries.update(readDefinitions("text"))
    countries.update(readDefinitions("eu4"))
    lookup = readDefinitions("eu4")
    lookup.update(readDefinitions("text"))
    lookup.update(readDefinitions("opinions"))
    lookup.update(readDefinitions("powers_and_ideas"))
    lookup.update(readDefinitions("decisions"))
    lookup.update(readDefinitions("modifers"))
    lookup.update(readDefinitions("muslim_dlc"))
    lookup.update(readDefinitions("Purple_Phoenix"))
    lookup.update(readDefinitions("core"))
    lookup.update(readDefinitions("missions"))
    lookup.update(readDefinitions("diplomacy"))
    for fileName in os.listdir("%s/history/countries" % path):
        print("Parsing file %s" % fileName)
        finalOutput += main(fileName)
    with open("output/countryOutput.txt", "w", encoding="utf-8") as outputFile:
        outputFile.write(finalOutput)
except FileNotFoundError:
    print("File not found error: Make sure you've set the file path in settings.txt")
elapsed = time.clock() - start
print("Parsing the files took %.3f seconds" %elapsed)
pr.disable()
sortby = 'tottime'
ps = pstats.Stats(pr).sort_stats(sortby)
ps.print_stats()