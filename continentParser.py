def main(fileName):
    global provinces
    global continents

    inputFile = structureFile(fileName, path, "history/countries/") #Transcribes game file to more parseable format
    outputDict = {}
    for line in inputFile:
        command, value = getValues(line)
        if command == "capital":
            continent = provinces[value]
            continents[continent].append(countries[fileName[:3]])
            break


def parseContinents(continentFile):
    provDict = {}
    for line in open(continentFile):
        line = line.strip()
        if "=" in line:
            continent = line.split("=")[0].strip()
        else:
            line = line.split("#")[0]
            for province in line.split(" "):
                provDict[province] = continent
    return provDict

def output(command, value): #Outputs line to a temp variable. Written to output file when input file is parsed
    global outputDict
    if command == "religion" or command == "technology_group":
        value = "[[File:%s.png]]%s" % (value, value)
    if not command in outputDict:
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

    try:
        #Dictionaries of relevant values
        countries = readDefinitions("countries", path)
        countries.update(readDefinitions("text", path))
        countries.update(readDefinitions("EU4", path))
        countries.update(readDefinitions("tags_phase4", path))
        countries.update(readDefinitions("eldorado", path))
        provinces = parseContinents("%s/map/continent.txt" % path)
        continents = {"europe":[], "asia":[], "africa":[], "north_america":[], "south_america":[], "oceania":[]}
        for fileName in os.listdir("%s/history/countries" % path):
            print("Parsing file %s" % fileName)
            main(fileName)
        print(continents)
    except FileNotFoundError:
        print("File not found error: Make sure you've set the file path in settings.txt")
    elapsed = time.clock() - start
    print("Parsing the files took %.3f seconds" %elapsed)
    pr.disable()
    sortby = 'tottime'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()
