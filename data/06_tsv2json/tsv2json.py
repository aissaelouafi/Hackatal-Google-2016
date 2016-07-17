#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, sys
import json as jq

# Replace special character by normal characeter (remove special character)
def normalize(string):
    liste = [("é", "e"), ("è","e"), ("â", "a"), ("ä", "a"), ("ù", "u"), ("à", "a"), ("~", "-")]
    for c, r in liste:
        string = string.replace(c, r)
    return string

# Extract first and second country, date and hour from the file name
def find_in_filename(filename):
    items = filename.split('_')
    first_country, second_country, date, hour, _ = items
    return first_country, second_country, date, hour

# Options to add support input, outpu file and options
def options():
    import argparse
    parser = argparse.ArgumentParser(prog="TSV To Json Parser")
    parser.add_argument('-i','--input',required=True,help='Input file (tsv file)')
    parser.add_argument('-o','--output',required=True,help='Output file (json file)')
    return parser

def filter(collection, predicate):
    new_col = []
    for c in collection:
        if not predicate(c):
            new_col.append(c)
    return new_col

def main():
    print os.path.basename(__file__) # print the file name
    args = options().parse_args() # get arguments of the script
    first, second, date, hour = find_in_filename(args.input)
    hour = hour[:-1] # remove the 'h' from the hour
    json = { # build the json object
        'header': {
            'eq1': first,
            'eq2': second,
            'date': date,
            'hour': hour
        }
    }
    with open(args.input) as tsv, open(args.output, 'w') as ostream:
        for i,line in enumerate(tsv):
            line = line.replace('\n', '')
            if i == 0:
                continue # dont take the first line

            items = line.split('\t') # split line by tabulation (return all items splited by tabulation )
            items = filter(items, predicate= lambda c: c.strip() == '')
            if len(items) == 0:
                continue

            items = items[:3]
            if len(items) < 3: items.append("")
            hour, action, annot = items
            json[i-1] = {
                'date': hour,
                'event': action,
                'info': annot
            }
        print >> ostream, ( "var %s = %s" % (normalize(first)+"_"+normalize(second), jq.dumps(json)) )

if __name__ == '__main__':
    main()
