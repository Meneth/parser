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
def readDefinitions(name, path):
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
def structureFile(name, path, folder):
    functionOutput = []

    with open('%s/%s/%s' % (path, folder, name), encoding="Windows-1252") as file:
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
def nestingCheck(line, nesting):
    nestingIncrement = 0
    #Thanks to file restructuring, it is impossible for there to be multiple brackets on a line
    if "{" in line:
        nesting += 1
        nestingIncrement = 1
    elif "}" in line:
        nesting -= 1
        nestingIncrement = -1
    return nesting, nestingIncrement

def getValues(line):
    line = line.split("=")
    line[0] = line[0].strip()
    try: #Checks if the command has a value
        line[1] = line[1].strip().strip('{}"')
        return line[0], line[1]
    except IndexError:
        return line[0], ""

import re