#! /usr/bin/env python3
import os, re, sys
from final_match import *
from collections import defaultdict

def get_interesting_info(path):
    with open(path) as stream:
        start = True
        for line in stream:
            line = line.replace('\n', '')
            if start:
                start = False
                continue
            items = line.split('\t')
            delta, name, score = items[10], items[11], items[15]
            yield name, int(score), int(delta)


def main():
    path = sys.argv[1]
    output = sys.argv[2]

    tweetos_score = defaultdict(int)
    tweetos_delta = defaultdict(list)
    for no_ext_file in walk(path, '.tsv'):
        if not no_ext_file.endswith('.out'):
            continue

        my_input_file = no_ext_file + ".tsv"
        for name, score, delta in get_interesting_info(my_input_file):
            tweetos_score[name] += score
            tweetos_delta[name].append(delta)

    for name in tweetos_delta:
        tweetos_delta[name] = int( sum(tweetos_delta[name]) / len(tweetos_delta[name]) )

    with open(output, 'w') as ostream:
        end_twittos = []
        for name in tweetos_score:
            delta = tweetos_delta[name]
            score = tweetos_score[name]
            end_twittos.append( (name, score, delta) )

        end_twittos = sorted(end_twittos, key = lambda k: k[1], reverse = True)
        for name, score, delta in end_twittos:
            print("%s\t%i\t%i" % (name, score, delta), file = ostream)


if __name__ == "__main__":
    main()
