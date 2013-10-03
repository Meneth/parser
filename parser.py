def main(fileName):
    global outputText
    parseFile = structureFile(fileName) #Transcribes game file to more parseable format
    #parseFile = open("temp.txt", "r") #The restructured file
    specialSection, negative, negativeNesting, printSection, base_chance, option = 0, 0, 0, 0, 0, 0
    value1, value2 = "", ""
    outputText = ""
    for line in parseFile:
        nestingCheck(line) #Determines how deeply nested the current line is
        if nesting <= 1:
            continue #Nothing relevant is nested this low
        if nesting == 2:
            if folder != "events":
                if nestingIncrement == 1: #At these values the name is encountered
                    name = statementLookup(line, lookup, getValues(line)[0]+"_title", 0) #Finds just the name identifier
                    output(name, 2)
            elif "title" in line:
                name = statementLookup(line, events, getValues(line)[1], 0) #Finds just the title identifier
                output(name, 2)
                if specialSection == "province_event":
                    output("Province event", -1)
                    specialSection = 0
            elif "province_event" in line:  #This should be printed after the name of the event
                specialSection = "province_event"
            elif "fire_only_once" in line:  #One of the few instances of relevant info that isn't a title on this nesting level
                output("Can only fire once", -1)
            elif nestingIncrement == -1: #End of relevant section
                printSection = 0
            continue #Nothing more to do this iteration
        else:
            negative, line, negativeNesting = negationCheck(negative, line, negativeNesting)
        if folder == "decisions":
            if "potential" in line or "allow" in line or "effect" in line:
                printSection = 1 #Only these sections are relevant
        elif folder == "missions":
            if "allow" in line or "success" in line or "abort" in line or "effect" in line:
                if not "abort_effect" in line:
                    printSection = 1 #Only these sections are relevant
        elif folder == "events":
            if "trigger" in line or "mean_time_to_happen" in line or "option" in line or "immediate" in line:
                printSection = 1 #Only these sections are relevant
                if "option" in line:
                    option = 1
                    continue #This is handled by the "name" attribute instead
            elif "ai_chance" in line:
                base_chance = 1 #Tells the parser to look for the base chance
            elif "factor" in line:
                if base_chance == 0:
                    line = statementLookup(line, statements, "factor", getValues(line)[1])
                    output(line, 1)
                else:
                    line = statementLookup(line, statements, "factor_base", getValues(line)[1])
                    base_chance = 0
                    output(line, 0)
                continue #Nothing more to do here
            elif option == 1 and "name" in line:
                line = "Option: "+valueLookup(getValues(line)[1], "name")[0]+":" #Shows clearly that it is an option
                output(line, 1)
                option = 0
                continue #Nothing more to do here
        if printSection == 0:
            continue #Nothing more to do this iteration
        #These commands span multiple lines, so they need special handling
        if '"%s"' % getValues(line)[0] in exceptions["specialCommands"]:
            specialSection = 1
            specialType = getValues(line)[0]
            continue #Nothing more to do this iteration
        elif specialSection == 1 and nestingIncrement != -1:
            command = getValues(line)[0]
            #Assign the correct values
            if '"%s"' % command in exceptions["value1"]:
                value1 = valueLookup(getValues(line)[1], specialType)[0]
                if command == "name":
                    modifier = getValues(line)[1]
            elif '"%s"' % command in exceptions["value2"]:
                value2 = valueLookup(getValues(line)[1], specialType)[0]
                if command == "duration":
                    if value2 == "-1":
                        value2 = "the rest of the campaign"
                    else: #Convert to years
                        value2 = str(int(value2)/365)
                        if "." in value2:
                            value2 = value2.rstrip("0").rstrip(".")
                        value2 += " years"
            elif specialType == "religion_years" and getValues(line)[0] != "":
                value1 = valueLookup(getValues(line)[0], specialType)[0]
                value2 = getValues(line)[1]
            continue #Nothing more to do this iteration
        if specialSection == 0:
            line, negative = formatLine(line, negative) #Looks up the command and value, and formats the string
            if line != "":
                output(line, negative)
        elif nestingIncrement == -1:
            specialSection = 0
            #Outputs commands that span multiple lines
            if negative == 1:
                specialType += "_false"
            if value2 != "":
                if specialType == "spawn_rebels":
                    line = special[specialType] % (value2, value1)
                elif specialType in special:
                    line = special[specialType] % (value1, value2)
            elif specialType in statements:
                line = statements[specialType] % value1
            output(line, negative+1)
            if specialType == "add_country_modifier" or specialType == "add_province_modifier" or specialType == "add_ruler_modifier":
                getModifier(modifier) #Looks up the effects of the actual modifier
            value1 = ""
            value2 = ""
    outputFile = open("output/%s" % fileName, "w", encoding="utf-8")
    outputFile.write(outputText)
    outputFile.close()
 
#Reads in a statement file as a dictionary
def readStatements(localisationName):
    localisation = {}
    with open('%s.txt' % localisationName) as effectsFile:
        for line in effectsFile.readlines():
            if not ":" in line:
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
                definitions[identifier.strip()] = value.strip().strip('"')
            except ValueError:
                print ("%d -> %s" % (lineNumber, line))
            lineNumber += 1
   
    return definitions
 
#Splits the file at every bracket to ensure proper parsing
def structureFile(name):
    functionOutput = []

    with open('%s/%s/%s' % (path, folder, name), encoding="Windows-1252") as file:
        for line in file:
            if "#" in line:
                line = line.split("#")[0]
            if line == "":
                continue
            line = line.strip().replace("{", "{\n").replace("}", "\n}") #Splits line at brackets
            if "=" in line:
                count = line.count("=")
                if count > 1:
                    for values in range(count):
                        line = re.sub("(=[\s]*[\w]*) ([\w]*[\s]*=)", "\g<1>\n\g<2>", line) #Splits lines with more than one statement in two
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
 
def negationCheck(negative, line, negativeNesting):
    #Negation via NOT
    if "NOT" in line:
        negative = 1
        negativeNesting = nesting-1
        line = line.lstrip("NOT =")
    elif negativeNesting == nesting:
        negative = 0
    return negative, line, negativeNesting
 
def formatLine(line, negative):
    if line == "}" or line == "{":
        return "", negative
    command, value = getValues(line)
    if command in statements and "%%" in statements[command]: #Percentage values should be multiplied
        value = str(round(100*float(value), 1)).rstrip("0").rstrip(".")
   
    #Local negation
    if value == "no":
        localNegation = 1
    else:
        localNegation = 0
 
    value, valueType = valueLookup(value, command)
 
    #Special exceptions
    if valueType == "country":
        if command in exceptions["countryCommands"]:
            command += "_country"
    elif value == "capital":
        value = "the capital"
 
    #Negation
    if negative == 1 and localNegation == 0 or negative == 0 and localNegation == 1:
        if value != "":
            command += "_false" #Unique lookup string for false version
        elif "any_" in command:
            command += "_false"
            negative = 0 #Contents of a "none of the following" scope don't need to be negated
   
    #Fallback code in case the lookups fail
    if value != "":
        line = "%s = %s" % (command, value)
    else:
        line = command
 
    #Lookup of human-readable string
    if len(command) == 3 and re.match("[A-Z]{3}", command):
        line = statementLookup(line, countries, command, value)
        return statementLookup(line, lookup, command, value)+":", negative
    elif command != "" and value == "":
        line = statementLookup(line, lookup, command, value)+":"
        try:
            command = str(int(command))
            line = statementLookup(line, provinces, "PROV"+command, value)+":"
        except ValueError:
            pass
    line = statementLookup(line, statements, command, value)
    return line, negative

def getValues(line):
    line = line.split("=")
    line[0] = line[0].strip()
    try: #Looks for the string before the equals sign
        return line[0], line[1].strip().strip('{}"')
    except IndexError:
        return line[0], ""
 
def valueLookup(value, command):
    valueType = "other"

    if value == "":
        return value, valueType

    #Root
    if value == "ROOT" or value == "root":
        return "our country", "country"
    if value == "FROM" or value == "from":
        return "our country", "country"
   
    #Assign country. 3 capitalized letters in a row is a country tag
    elif len(value) == 3 and re.match("[A-Z]{3}", value):
        try:
            return countries[value], "country"
        except KeyError:
            try:
                return lookup[value], "country"
            except KeyError:
                print("Could not look up country with value %s" % value)
   
    #Assign province
    if command in exceptions["provinceCommands"]: #List of statements that check provinces
        try:
            return provinces["PROV"+value], "province"
        except KeyError:
            try:
                int(value)
                print("Could not look up province with value %s" % value)
            except ValueError:
                pass

    #Attempt to look up
    if value != "" and re.match("[a-zA-Z]", value): #Numbers that aren't provinces are just regular numbers
        #if value in lookup:
        try:
            return lookup[value], "other"
        except KeyError:
            try:
                return lookup["building_"+value], "other"
            except KeyError:
                try:
                    return lookup[value+"_title"], "other"
                except KeyError:
                    if folder == "events":
                        try:
                            return events[value], "event"
                        except KeyError:
                            return value, valueType
    return value, valueType
 
#Lookup of human-readable string
def statementLookup(line, check, command, value):
    #if command in check:
    try:
        return check[command] % value
    except TypeError:
        return check[command]
    except (KeyError, ValueError):
        return line
 
#Looks up the actual effects of modifiers
def getModifier(modifier):
    modifierFound = False
    #Rare enough that going line by line is efficient enough
    for line in modifiers:
        if not modifierFound:
            if modifier in line:
                modifierFound = True
            continue
        elif not "icon" in line:
            if "}" in line:
                break #End of modifier found
            line = formatLine(line, 0)[0]
            if re.match("[0-9]", line):
                line = "+" + line
            if line != "":
                output(line, 0)
 
#Output line
def output(line, negative):
    global outputText
    indent = "*"*(nesting-nestingIncrement-negative-2)
    if indent != "":
        line = "%s %s" % (indent, line)
    elif negative == 2:
        line = "\n=== %s ===" %line
    else:
        line = "\n'''%s'''\n" %line
    #if specificFile != "no":
        #print(line)
    outputText += line + "\n"
 
import cProfile, pstats
pr = cProfile.Profile()
pr.enable()
 
import time #Used for timing the parser
start = time.clock()
import re #Needed for various string handling
import os #Used to grab the list of files
settings = readStatements("settings")
path = settings["path"].replace("\\", "/")
folder = settings["folder"]
specificFile = settings["file"]
if folder == "decisions":
    nesting, nestingIncrement = 0, 0
elif folder == "missions" or folder == "events":
    nesting, nestingIncrement = 1, 0 #One less level of irrelevant nesting
 
#Dictionaries of known statements
special = readStatements("statements/special")
statements = readStatements("statements/statements")
exceptions = readStatements("statements/exceptions")
 
try:
    #Dictionaries of relevant values
    provinces = readDefinitions("prov_names")
    countries = readDefinitions("countries")
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
    events = readDefinitions("generic_events")
    events.update(readDefinitions("flavor_events"))
    events.update(readDefinitions("EU4"))
    events.update(readDefinitions("muslim_dlc"))
    events.update(readDefinitions("Purple_Phoenix"))
    with open(path+"/common/event_modifiers/00_event_modifiers.txt") as f:
        modifiers = f.readlines()
   
    if specificFile == "no":
        for fileName in os.listdir("%s/%s" % (path, folder)):
            print("Parsing file %s" % fileName)
            main(fileName)
    else:
        fileName = specificFile+".txt"
        main(fileName)
except FileNotFoundError:
    print("File not found error: Make sure you've set the file path in settings.txt")
elapsed = time.clock() - start
print("Parsing the files took %.3f seconds" %elapsed)
pr.disable()
sortby = 'tottime'
ps = pstats.Stats(pr).sort_stats(sortby)
ps.print_stats()
