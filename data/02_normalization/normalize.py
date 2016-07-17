#! /usr/bin/env python3

import os, re, sys
from unidecode import unidecode

normalizing_cols = set(['text', 'hashtags', 'user_mentions', 'name'])

def normalize(string):
    return unidecode(string).lower()

def options():
    import argparse
    parser = argparse.ArgumentParser(prog="Hackatal Normalization")
    parser.add_argument('-i', '--input', required=True, help='Input file (not normalized)')
    parser.add_argument('-t', '--tweet', action='store_true', help='File is a filtered TSV file of tweets')
    parser.add_argument('-s', '--suffix', default='not_norm', help='String to find in file')
    parser.add_argument('-r', '--replace', default='norm', help='Replace found string by this one')
    return parser

def main():
    args = options().parse_args()
    cols_number = []
    output = args.input.replace(args.suffix, args.replace)

    with open(args.input) as stream, open(output, "w") as ostream:
        for i, line in enumerate(stream):
            line = line.replace('\n', '')
            if args.tweet:
                items = line.split('\t')
                if i == 0:
                    for j, k in enumerate(items):
                        if k in normalizing_cols:
                            cols_number.append(j)
                    cols_number = sorted(cols_number)
                    print("\t".join(items), file = ostream)
                    continue

                for j  in cols_number:
                    try:
                        items[j] = normalize(items[j])
                    except IndexError:
                        print(items, j, cols_number, file=sys.stderr)
                print("\t".join(items), file = ostream)
            else:
                line = normalize(line)
                print(line, file = ostream)

if __name__ == "__main__":
    main()
