def main(file):
    global outputText
    parseFile = structureFile(file) #Transcribes game file to more parseable format
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
                    name = statementLookup(line, lookup, getCommand(line)+"_title", 0) #Finds just the name identifier
                    output(name, 2)
            elif "title" in line:
                name = statementLookup(line, events, getValue(line), 0) #Finds just the title identifier
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
                    line = statementLookup(line, statements, "factor", getValue(line))
                    output(line, 1)
                else:
                    line = statementLookup(line, statements, "factor_base", getValue(line))
                    base_chance = 0
                    output(line, 0)
                continue #Nothing more to do here
            elif option == 1 and "name" in line:
                line = "Option: "+valueLookup(getValue(line), "name")[0]+":" #Shows clearly that it is an option
                output(line, 1)
                option = 0
                continue #Nothing more to do here
        if printSection == 0:
            continue #Nothing more to do this iteration
        #These commands span multiple lines, so they need special handling
        if '"%s"' % getCommand(line) in exceptions["specialCommands"]:
            specialSection = 1
            specialType = getCommand(line)
            continue #Nothing more to do this iteration
        elif specialSection == 1 and nestingIncrement != -1:
            command = getCommand(line)
            #Assign the correct values
            if '"%s"' % command in exceptions["value1"]:
                value1 = valueLookup(getValue(line), specialType)[0]
                if command == "name":
                    modifier = getValue(line)
            elif '"%s"' % command in exceptions["value2"]:
                value2 = valueLookup(getValue(line), specialType)[0]
                if command == "duration":
                    if value2 == "-1":
                        value2 = "the rest of the campaign"
                    else: #Convert to years
                        value2 = str(int(value2)/365)
                        if re.search("\.", value2):
                            value2 = value2.rstrip("0").rstrip(".")
                        value2 = value2  + " years"
            elif specialType == "religion_years" and getCommand(line) != "":
                value1 = valueLookup(getCommand(line), specialType)[0]
                value2 = getValue(line)
            continue #Nothing more to do this iteration
        if specialSection == 0:
            line, negative = formatLine(line, negative) #Looks up the command and value, and formats the string
            if line != "":
                output(line, negative)
        elif nestingIncrement == -1:
            specialSection = 0
            #Outputs commands that span multiple lines
            if negative == 1:
                specialType = specialType+"_false"
            if value2 != "":
                if specialType == "spawn_rebels":
                    line = special[specialType] % (value2, value1)
                elif specialType in special:
                    line = special[specialType] % (value1, value2)
            elif specialType in statements:
                line = statements[specialType] % (value1)
            output(line, negative+1)
            if specialType == "add_country_modifier" or specialType == "add_province_modifier" or specialType == "add_ruler_modifier":
                getModifier(modifier) #Looks up the effects of the actual modifier
            value1 = ""
            value2 = ""
    outputFile = open("output/%s" % file, "w", encoding="utf-8")
    outputFile.write(outputText)
    outputFile.close()
 
#Reads in a statement file as a dictionary
def read_statements(type):
    statements = {}
    with open('%s.txt' % type) as effects_file:
        for line in effects_file.readlines():
            if not ":" in line:
                continue
            line = line.strip()
            statement_name, format_string = line.split(':', 1)
            statements[statement_name.strip()] = format_string.strip()
         
    return statements
 
#Reads in a definition file as a dictionary
def read_definitions(name):
    definitions = {}
    with open(path+"/localisation/%s_l_english.yml" % name, encoding="utf-8") as definitions_file:
        lines = definitions_file.readlines()
        language_def = lines[0].strip()
        line_number = 1
        for line in lines[1:]:
            if line.strip():
                try:
                    id, value = line.split(':', 1)
                except ValueError(e):
                    print ("%d -> %s, e : %s" % (line_number, line, e))
            definitions[id.strip()] = value.strip().strip('"')
            line_number += 1
   
    return definitions
 
#Splits the file at every bracket to ensure proper parsing
def structureFile(name):
    output = []

    with open('%s/%s/%s' % (path, folder, name), encoding="Windows-1252") as file:
        for line in file.readlines():
            if line.startswith("#"):
                continue
            line = line.strip().replace("{", "{\n").replace("}", "\n}") #Splits line at brackets
            line = re.sub("(=[ ]*[\w]*) ([\w]*[ ]*=)", "\g<1>\n\g<2>", line).strip() #Splits lines with more than one statement in two
            if line != "":
                if "\n" in line:
                    parts = line.split("\n")
                    for p in parts:
                        output.append(p)
                else:
                    output.append(line)
    return output
 
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
        line = re.sub("NOT[ ]*=[ ]*{", "", line)
    elif negativeNesting == nesting:
        negative = 0
    return (negative, line, negativeNesting)
 
def formatLine(line, negative):
    command = getCommand(line)
    value = getValue(line)
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
            command = command+"_country"
    elif value == "capital":
        value = "the capital"
 
    #Negation
    if negative == 1 and localNegation == 0 or negative == 0 and localNegation == 1:
        if value != "":
            command = command+"_false" #Unique lookup string for false version
        elif "any_" in command:
            command = command+"_false"
            negative = 0 #Contents of a "none of the following" scope don't need to be negated
   
    #Fallback code in case the lookups fail
    if value != "":
        line = "%s = %s" % (command, value)
    else:
        line = command
 
    #Lookup of human-readable string
    if len(command) == 3 and re.match("[A-Z]{3}", command):
        line = statementLookup(line, countries, command, value)
        line = statementLookup(line, lookup, command, value)+":"
    elif command != "" and value == "":
        line = statementLookup(line, lookup, command, value)+":"
        if not re.search("[a-zA-Z]", command):
            line = statementLookup(line, provinces, "PROV"+command, value)+":"
    line = statementLookup(line, statements, command, value)
    return(line, negative)
 
def getCommand(line):
    if re.search("[\w]*[ ]*=", line): #Looks for the string before the equals sign
        command = re.search("[\w]*[ ]*=", line).group(0)
        return re.sub("[ ]*=", "", command).strip()
    else:
        return ""
 
def getValue(line):
    if re.search("=[ ]*[-.\w]*", line): #Looks for the string after  the equals sign
        if '"' in line: #These strings may have spaces in them
            value = re.search('=[ ]*(".*")', line).group(1)
        else:
            value = re.search("=[ ]*[-.\w\"]*", line).group(0)
        return re.sub("=[ ]*", "", value).strip('"').strip()
    else:
        return ""
 
def valueLookup(value, command):
    valueType = "other"
 
    #Root
    if value == "ROOT" or value == "root":
        return "our country", "country"
    if value == "FROM" or value == "from":
        return "our country", "country"
   
    #Assign country. 3 capitalized letters in a row is a country tag
    elif len(value) == 3 and re.match("[A-Z]{3}", value):
        if value in countries:
            return countries[value], "country"
        elif value in lookup: #For some reason, not all countries are in country localisation
            return lookup[value], "country"
   
    #Assign province
    if command in exceptions["provinceCommands"]: #List of statements that check provinces
        if "PROV"+value in provinces:
            return provinces["PROV"+value], "province"
   
    #Attempt to look up
    if value != "" and re.match("[a-zA-Z]", value): #Numbers that aren't provinces are just regular numbers
        if value in lookup:
            return lookup[value], "other"
        elif "building_"+value in lookup:
            return lookup["building_"+value], "other"
        elif value+"_title" in lookup:
            return lookup[value+"_title"], "other"
        if folder == "events":
            if value in events:
                return events[value], "event"
    return(value, valueType)
 
#Lookup of human-readable string
def statementLookup(line, check, command, value):
    if command in check:
        if "%s" in check[command]:
            return check[command] % value
        else:
            return check[command]
    return(line)
 
#Looks up the actual effects of modifiers
def getModifier(modifier):
    modifierFound = False
    #Rare enough that going line by line is efficient enough
    for line in modifiers:
        if modifierFound == False:
            if modifier in line:
                modifierFound = True
            continue
        if modifierFound == True and not "icon" in line:
            if "}" in line:
                break #End of modifier found
            line = formatLine(line, 0)[0]
            if re.match("[0-9]", line):
                line = "+" + line
            if line.strip() != "":
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
settings = read_statements("settings")
path = settings["path"].replace("\\", "/").strip()
folder = settings["folder"]
specificFile = settings["file"]
if folder == "decisions":
    nesting, nestingIncrement = 0, 0
elif folder == "missions" or folder == "events":
    nesting, nestingIncrement = 1, 0 #One less level of irrelevant nesting
 
#Dictionaries of known statements
special = read_statements("statements/special")
statements = read_statements("statements/statements")
exceptions = read_statements("statements/exceptions")
 
try:
    #Dictionaries of relevant values
    provinces = read_definitions("prov_names")
    countries = read_definitions("countries")
    lookup = read_definitions("eu4")
    lookup.update(read_definitions("text"))
    lookup.update(read_definitions("opinions"))
    lookup.update(read_definitions("powers_and_ideas"))
    lookup.update(read_definitions("decisions"))
    lookup.update(read_definitions("modifers"))
    lookup.update(read_definitions("muslim_dlc"))
    lookup.update(read_definitions("Purple_Phoenix"))
    lookup.update(read_definitions("core"))
    lookup.update(read_definitions("missions"))
    events = read_definitions("generic_events")
    events.update(read_definitions("flavor_events"))
    events.update(read_definitions("EU4"))
    events.update(read_definitions("muslim_dlc"))
    events.update(read_definitions("Purple_Phoenix"))
    with open(path+"/common/event_modifiers/00_event_modifiers.txt") as f:
        modifiers = f.readlines()
   
    if specificFile == "no":
        for file in os.listdir("%s/%s" % (path, folder)):
            print("Parsing file %s" % file)
            main(file)
    else:
        file = specificFile+".txt"
        main(file)
except FileNotFoundError:
    print("File not found error: Make sure you've set the file path in settings.txt")
elapsed = time.clock() - start
print("Parsing the files took %.3f seconds" %elapsed)
pr.disable()
sortby = 'tottime'
ps = pstats.Stats(pr).sort_stats(sortby)
ps.print_stats()
