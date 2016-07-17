#! /usr/bin/env python3

import os, re, sys
from final_match import *

def read_tweetos(path, keep = 50):
    tweetos = {}
    with open(path) as stream:
        for line in stream:
            if len(tweetos) == keep:
                break
            line = line.strip()
            items = line.split('\t')
            tweetos[items[0]] = [int(items[1]), int(items[2])]
    return tweetos

def has_tweetos(tweetos, tweet):
    if tweet['user']['name'] in tweetos:
        return True
    return False

def uppermain(tweets_file, tweetos_file, entities_file, output_file):

    dictionaries = read_dicts(entities_file)
    tweetos = read_tweetos(tweetos_file)

    headers = ["timestamp_ms", "text", "name", "pred_players", "pred_actions", "pred_countries", "expected_timestamp"]
    headers = sorted(headers)
    matrix = [headers]

    row = {}
    for jq in read_json(tweets_file):
        if 'limit' in jq:
            continue

        if not has_tweetos(tweetos, jq):
            continue


        text = extract_text_from_tweet(jq)
        unix = extract_timestamp_from_tweet(jq)
        name = extract_name_from_tweet(jq)
        pred_actions, pred_players, pred_countries = extract_entities(text, dictionaries)

        if len(pred_actions) == 0:
            continue

        row["timestamp_ms"] = unix
        row["text"] = text
        row["name"] = name
        row['pred_actions'] = ",".join(pred_actions)
        row['pred_players'] = ",".join(pred_players)
        row['pred_countries'] = ",".join(pred_countries)
        row['expected_timestamp'] = int(unix) - tweetos[name][1]

        _row = [str(v) for k,v in sorted(row.items())]
        matrix.append(_row)
        row = {}

    with open(output_file, 'w') as ostream:
        for row in matrix:
            print("\t".join(row), file = ostream)

def main():
    path = sys.argv[1]
    tweetos_file = sys.argv[2]
    entities_file = sys.argv[3]

    for no_ext_file in walk(path, '.json'):
        print("Analyzing %s" % no_ext_file+".json", file = sys.stderr)
        my_tweet_file = no_ext_file + ".json"
        my_output_file = no_ext_file + ".predicted.tsv"
        uppermain(my_tweet_file, tweetos_file, entities_file, my_output_file)

if __name__ == "__main__":
    main()
