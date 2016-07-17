#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, sys

def options():
    import argparse
    parser = argparse.ArgumentParser(prog="entities matching")
    parser.add_argument('-i', '--input', required=True, help='Input file (normalized)')
    parser.add_argument('-s', '--suffix', required=True, help='Suffix to replace in file')
    parser.add_argument('-r', '--replace', required=True, help='Replacement')
    parser.add_argument('-e', '--entities', required=True, help='Entities data directory')
    return parser

def main():
    args = options().parse_args()
    cols_number = []
    input = args.input
    output	= args.input.replace(args.suffix, args.replace)
    entityDataDir = args.entities

    dictEntities = LoadDictGeneralMethod(entityDataDir)
    dictPlayers  = LoadPlayersDict(entityDataDir)

    print("Recognizing in %s" % args.input, file = sys.stderr)
    with open(args.input) as stream, open(output, "w") as ostream:
        for i,line in enumerate(stream):
            if i == 0:
                print("id\tlang\tname\ttimestamp_ms\tentities\tplayers",file=ostream);
                continue

            line = line.replace('\n','')
            newline = MatchEntities(line,dictEntities,dictPlayers)
            if newline != "":
                print(newline,file = ostream)
            #print(i)

def MatchEntities(line,dictEntities,dictPlayers):
    newline = ""
    colomns = line.split('\t')
    lang = colomns[5]
    id = colomns[4]
    name = colomns[6]
    text = colomns[11]
    timestamp = colomns[12]
    dicoLang = {}
    entities = []
    players = []

    if lang in dictEntities:
        dicoLang = dictEntities[lang]
        dictPlayers = dictPlayers

    for label in dicoLang:
        if Annotate(text,dicoLang[label]):
            entities.append(label)

    players = AnnotatePlayers(text,dictPlayers)

    if len(entities) != 0 or len(players) != 0:
        strEntities = ",".join(entities)
        strPlayer   = ",".join(players)
        newline     = id+"\t"+lang+"\t"+name+"\t"+timestamp+"\t"+strEntities+"\t"+strPlayer
    return newline



def AnnotatePlayers(twitter,dict):
    twitter = str.lower(twitter)
    words = set(twitter.split(" "))
    players = []
    for entry in dict:
        if entry in twitter:
            players.append(entry)
            continue
        name = str.split(entry," ")[0]
        if name in words:
            players.append(name)
    #TODO distinct players
    return players

def Annotate(twitter, dict):
    twitter = str.lower(twitter)
    words = set(twitter.split(" "))

    for entry in dict:
        if " " in entry:
            if entry in twitter:
                return True
        else:
            if entry in words:
                return True
    return False

def LoadDictGeneralMethod(fileDir):
    filepathAr = os.path.join(fileDir,"ar")
    filepathEn = os.path.join(fileDir,"en")
    filepathFr = os.path.join(fileDir,"fr")
    dict={}
    LoadDictForEachLang("ar",filepathAr,dict)
    LoadDictForEachLang("en", filepathEn,dict)
    LoadDictForEachLang("fr",filepathFr,dict)
    return dict

def LoadDictForEachLang(lang,fileDir,dict):
    dict[lang] ={}
    for file in os.listdir(fileDir):
        if file.endswith(".txt"):
            label = file.replace(".txt","")
            if lang == "ar":
                if file.endswith("norm.txt"):
                    file = os.path.join(fileDir,file)
                    label = label.replace('.norm', '').upper()
                    try:
                        dict[lang][label] = open(file).readlines()
                        dict[lang][label] = [x.strip().lower() for x in dict[lang][label] if x.strip() != ""]
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise
            else:
                file = os.path.join(fileDir, file)
                try:
                    dict[lang][label] = open(file).readlines()
                    dict[lang][label] = [x.strip().lower() for x in dict[lang][label] if x.strip() != ""]
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
    return dict

def LoadPlayersDict(fileDir):
    ls =[]
    for file in os.listdir(fileDir):
        if file.endswith("_norm.txt") and file.startswith("PLAYERS") and not file.endswith("_not_norm.txt"):
            file = os.path.join(fileDir,file)
            if(os.path.exists(file)):
                country = os.path.basename(file).replace("_norm.txt","").replace("PLAYERS_","")
                if(country !=""):
                    dataPlayers = open(file).readlines()
                    dataPlayers =[x.strip().lower() for x in dataPlayers]
                    ls=ls+dataPlayers
    return ls

if __name__ == "__main__":
    main()
