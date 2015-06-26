def main(fileName):
    global outputDict
    inputFile = structureFile(fileName, path, "history/countries/") #Transcribes game file to more parseable format
    outputDict = {}
    for line in inputFile:
        #Determines how deeply nested the current line is
        nestingCheck(line, nesting)
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
    #for trigger in ideas.values():
    #    if "tag = %s" % fileName[:3] in trigger:
    #        outputText += " || Unique"
    #        break
    #if not "Unique" in outputText:
    #    outputText += " || "
    try:
        return outputText +"\n|-\n"
    except UnboundLocalError:
        return ""


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


def parseCultures():
    global nesting
    cultures = {}
    inputFile = structureFile("00_cultures.txt", path, "common/cultures/")
    for line in inputFile:
        nesting, nestingIncrement = nestingCheck(line, nesting)
        if nestingIncrement == 1:
            if nesting == 1:
                group = valueLookup(getValues(line)[0])
            elif nesting == 2:
                culture = valueLookup(getValues(line)[0])
                cultures[culture] = "%s (%s)" % (culture, group)
    nesting = 0
    return cultures


def parseGovernments():
    global nesting
    governments = {}
    inputFile = structureFile("00_governments.txt", path, "common/governments/")
    for line in inputFile:
        nesting, nestingIncrement = nestingCheck(line, nesting)
        if nesting == 1:
            if nestingIncrement == 1:
                government = valueLookup(getValues(line)[0])
            else:
                command = getValues(line)[0]
                if command in govTypes.keys():
                    governments[government] = govTypes[command]
    nesting = 0
    return governments


def output(command, value): #Outputs line to a temp variable. Written to output file when input file is parsed
    global outputDict
    if command in outputDict:
        return
    if command == "religion" or command == "technology_group":
        value = "[[File:%s.png]]%s" % (value, value)
    elif command == "primary_culture":
        value = cultures[value]
    elif command == "government":
        value = "[[File:Government %s.png]]%s" % (governments[value], value)
    outputDict[command] = value

if __name__ == "__main__":
    import cProfile, pstats
    pr = cProfile.Profile()
    pr.enable()

    from common import *
    import time #Used for timing the parser
    start = time.clock()
    import os #Used to grab the list of files
    settings = readStatements("settings")
    path = settings["path"].replace("\\", "/")

    #Dictionaries of known statements
    countryStatements = readStatements("statements/countryStatements")
    countryCommands = countryStatements["commands"].split()
    nesting, nestingIncrement = 0, 0
    finalOutput = []
    #ideas = {}
    #unformattedIdeas = structureFile("common/ideas/00_country_ideas.txt")
    #triggerFound = False
    #for line in unformattedIdeas:
    #    nestingCheck(line)
    #    if triggerFound:
    #        if nesting == 1:
    #            triggerFound = False
    #        else:
    #            ideas[token].append(line)
    #    if nesting == 1 and nestingIncrement == 1:
    #        token = getValues(line)[0]
    #        ideas[token] = []
    #    elif "trigger" in line:
    #        triggerFound = True

    try:
        #Dictionaries of relevant values
        provinces = readDefinitions("prov_names", path)
        countries = readDefinitions("countries", path)
        countries.update(readDefinitions("text", path))
        countries.update(readDefinitions("EU4", path))
        countries.update(readDefinitions("tags_phase4", path))
        countries.update(readDefinitions("eldorado", path))
        lookup = readDefinitions("EU4", path)
        lookup.update(readDefinitions("nw", path))
        lookup.update(readDefinitions("text", path))
        lookup.update(readDefinitions("opinions", path))
        lookup.update(readDefinitions("powers_and_ideas", path))
        lookup.update(readDefinitions("decisions", path))
        lookup.update(readDefinitions("modifers", path))
        lookup.update(readDefinitions("muslim_dlc", path))
        lookup.update(readDefinitions("Purple_Phoenix", path))
        lookup.update(readDefinitions("core", path))
        lookup.update(readDefinitions("missions", path))
        lookup.update(readDefinitions("diplomacy", path))
        lookup.update(readDefinitions("nw2", path))
        lookup.update(readDefinitions("aow", path))
        lookup.update(readDefinitions("cultures_phase4", path))
        lookup.update(readDefinitions("religion", path))
        cultures = parseCultures()
        govTypes = {
            "monarchy": "monarchy", "republic": "republic", "dictatorship": "republic",
            "nomad": "steppe horde", "tribal": "tribal", "native_mechanic": "tribal", "religion": "theocracy"
        }
        governments = parseGovernments()

        for fileName in os.listdir("%s/history/countries" % path):
            print("Parsing file %s" % fileName)
            finalOutput.append(main(fileName))
        with open("output/countryOutput.txt", "w", encoding="utf-8") as outputFile:
            outputFile.write("".join(finalOutput))
    except FileNotFoundError:
        print("File not found error: Make sure you've set the file path in settings.txt")
    elapsed = time.clock() - start
    print("Parsing the files took %.3f seconds" %elapsed)
    pr.disable()
    sortby = 'tottime'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()
