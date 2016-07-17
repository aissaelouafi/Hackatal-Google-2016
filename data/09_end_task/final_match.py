#! /usr/bin/env python3

import os, re, sys
import json, datetime
from collections import defaultdict
from unidecode import unidecode

list_of_events = ["D1P", "D2P", "F1P", "F2P", "CJA", "CRO", "CGT", "BUT", "TIR", "PEN"]

def filter(collection, predicate):
    nc = []
    for c in collection:
        if predicate(c):
            continue
        nc.append(c)
    return nc

def normalize(string):
    return unidecode(string).lower()

def arab2latin(tweet):
    dic ={"ل":"l","ە":"h","م":"m","ر":"r","ت":"t","ز":"z","ن":"n","ش":"ch","ق":"k","ف":"f","و":"w","ي":"y","ط":"t","ك":"k","د":"d","ذ":"d","ب":"b","خ":"kh","ح":"h","ج":"j","ظ":"d","ع":"3","ه":"h","غ":"r","ث":"t","ص":"s","إ":"i","ة":"a","ض":"d","أ":"a","ى":"a","آ":"a","ئ":"a","ء":"2","ا":"a","ّ":"","ْ":"","ٌ":"","ْ":"","ُ":"","ٍ":"","ِ":"","ً":"","َ":"","س":"s","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9","٠":"0"}
    for i, j in dic.items():
        tweet = tweet.replace(i, j)
    return tweet

def convert_to_unix(iso):
    utc_dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    # convert UTC datetime to seconds since the Epoch
    timestamp = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(timestamp * 1000)

def extract_date(path):
    items = path.split('_')
    idx = -3
    if items[-1] == "SO":
        idx = -4
    return items[idx]

def read_json(filepath):
    with open(filepath) as stream:
        for line in stream:
            line = line.strip()
            yield json.loads(line)

def extract_text_from_tweet(tweet):
    lang = tweet['lang']
    text = tweet['text']
    text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    if lang != "fr" and lang != "en":
        return arab2latin(text)
    else:
        return normalize(text)

def extract_timestamp_from_tweet(tweet):
    return tweet['timestamp_ms']

def extract_name_from_tweet(tweet):
    return tweet['user']['screen_name']

def between_interval(timestamp, start, end):
    if int(timestamp) >= int(start) and int(timestamp) <= int(end):
        return True
    else:
        return False

def read_match(date, filepath):
    matrix = []
    tpldate = date + "T%sZ"
    with open(filepath) as stream:
        start = True
        for line in stream:
            line = line.replace('\n', '')
            items = line.split('\t')

            if start:
                matrix.append(items)
                start = False
                continue

            h,m,s = items[0].split(':')
            h = int(h) - 2
            iso = tpldate % ("%i:%s:%s" % (h,m,s),)
            unix = convert_to_unix(iso)

            items[0] = str(unix)
            matrix.append(items)
    return matrix

def keep_tweet(tweet, event):
    elapsed = 120 * 1000
    unix = extract_timestamp_from_tweet(tweet)
    text = extract_text_from_tweet(tweet)
    name = extract_name_from_tweet(tweet)
    tp, action, info = event

    if between_interval(unix, tp, tp + elapsed):
        return unix, text, name, action
    else:
        return None

def read_dict_by_lang(path, lang, info):
    for file in os.listdir(path):
        if file.endswith(".txt"):
            label = file.replace(".txt","")
            if lang == "ar":
                if file.endswith("norm.txt"):
                    file = os.path.join(path,file)
                    label = label.replace('.norm', '').upper()
                    try:
                        info[lang][label] = open(file).readlines()
                        info[lang][label] = [x.strip().lower() for x in info[lang][label] if x.strip() != ""]
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise
            else:
                file = os.path.join(path, file)
                try:
                    info[lang][label] = open(file).readlines()
                    info[lang][label] = [x.strip().lower() for x in info[lang][label] if x.strip() != ""]
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
    return info

def read_dict_for_players(path, info):
    with open(path) as stream:
        for line in stream:
            line = line.strip()
            items = line.split(' ')
            info['players'].add(line)
            info['players'].add(items[0])
            if len(items) > 1:
                info['players'].add(items[1])
    return info

def read_dict_for_countries(path, info):
    with open(path) as stream:
        for line in stream:
            line = line.strip()
            info['countries'].add(line)
    return info

def read_dict_for_hashtags(path, info):
    with open(path) as stream:
        for line in stream:
            line = line.strip()
            items = line.split('\t')

            if len(items) == 3:
                hasht, lang, c1 = items
                info['hashtags'][hasht] = set([c1])
            elif len(items) > 3:
                hasht, lang, c1, c2 = items[:4]
                info['hashtags'][hasht] = set([c1, c2])
    return info

def read_dicts(path):
    info = {
        'en': {},
        'fr': {},
        'ar': {},
        'countries': set([]),
        'players': set([]),
        'hashtags': {}
    }
    filepathAr = os.path.join(path,"ar")
    filepathEn = os.path.join(path,"en")
    filepathFr = os.path.join(path,"fr")
    country    = os.path.join(path, "PAYS_norm.txt")
    players    = os.path.join(path, "PLAYERS_norm.txt")
    hashtags   = os.path.join(path, "hashtag_pays.txt")

    info = read_dict_by_lang(filepathAr, "ar", info)
    info = read_dict_by_lang(filepathEn, "en", info)
    info = read_dict_by_lang(filepathFr, "fr", info)
    info = read_dict_for_players(players, info)
    info = read_dict_for_countries(country, info)
    info = read_dict_for_hashtags(hashtags, info)
    return info

def extract_most_probable_action(dictionary, tweet):
    actions = set([])
    for action in dictionary:
        for entity in dictionary[action]:
            if entity in tweet:
                actions.add(action)
    return actions

def extract_players(dictionary, tweet):
    players = set([])
    words = set(tweet.split(' '))
    for player in dictionary:
        if " " in player and player in tweet:
            players.add(player)
        else:
            if player in words:
                players.add(player)
    return players

def extract_countries(dictionary, tweet):
    countries = set([])
    for country in dictionary:
        if country in tweet:
            countries.add(country)
    return countries

def extract_countries_from_hashtags(dictionary, tweet):
    countries = set([])
    for hashtag in dictionary:
        if "#"+hashtag in tweet:
            countries |= dictionary[hashtag]
    return countries

def extract_entities(tweet, dictionaries):
    actions = set([])
    players = set([])
    countries = set([])
    for key in dictionaries:
        if key in set(['ar', 'en', 'fr']):
            d = dictionaries[key]
            actions |= extract_most_probable_action(d, tweet)
        elif key == "players":
            d = dictionaries[key]
            players |= extract_players(d, tweet)
        elif key == "countries":
            d = dictionaries[key]
            countries |= extract_countries(d, tweet)
        elif key == "hashtags":
            d = dictionaries[key]
            countries |= extract_countries_from_hashtags(d, tweet)

    return actions, players, countries

def walk(path, extension):
    for root, dirs, files in os.walk(path):
        for f in files:
            fullfile = os.path.join(root, f)
            no_ext, ext = os.path.splitext(fullfile)
            if ext == extension:
                yield no_ext

def uppermain(tweets_file, match_file, entities_file, output_file, acc_score, acc_delta):
    date = extract_date(match_file)
    match = read_match(date, match_file)
    headers = ["timestamp_ms", "text", "name", "true_info", "pred_players", "pred_actions", "pred_countries", "delta", "score"] + list_of_events
    headers = sorted(headers)
    matrix = [headers]
    dictionaries = read_dicts(entities_file)

    for jq in read_json(tweets_file):
        if 'limit' in jq:
            continue

        row = {}
        for h in headers:
            row[h] = ""

        for e in list_of_events:
            row[e] = 0

        row['score'] = 0
        row['delta'] = []
        row['pred_actions'] = set([])
        row['pred_players'] = set([])
        row['pred_countries'] = set([])

        text = extract_text_from_tweet(jq)
        unix = extract_timestamp_from_tweet(jq)
        name = extract_name_from_tweet(jq)
        pred_actions, pred_players, pred_countries = extract_entities(text, dictionaries)

        row["timestamp_ms"] = unix
        row["text"] = text
        row["name"] = name

        row['pred_actions'] = pred_actions
        row['pred_players'] = pred_players
        row['pred_countries'] = pred_countries

        for i in range( len(match) ):
            if i == 0:
                continue
            items = match[i]
            items = items[:3]
            tp, action, info = items
            tp = int(tp)

            row["true_info"] = info
            retour = keep_tweet(jq, (tp, action, info))
            if retour is None:
                continue

            for e in list_of_events:
                if e == action:
                    row[e] = 1
                    break

            row['score'] += action in pred_actions
            row['delta'].append( abs(int(unix) - int(tp)) )


        if row['score'] == 0:
            continue

        acc_score[row['name']] += row['score']
        acc_delta[row['name']] += row['delta']

        row['delta'] = str( int( sum(row['delta']) / len(row['delta']) ) )
        row['pred_actions'] = ",".join(row['pred_actions'])
        row['pred_players'] = ",".join(row['pred_players'])
        row['pred_countries'] = ",".join(row['pred_countries'])
        _row = [str(v) for k,v in sorted(row.items())]
        matrix.append(_row)

    with open(output_file, 'w') as ostream:
        for row in matrix:
            r = "\t".join(row)
            print(r, file = ostream)

def main():
    path = sys.argv[1]
    entities = sys.argv[2]
    out_tweetos = sys.argv[3]
    acc_score = defaultdict(int)
    acc_delta = defaultdict(list)

    for no_ext_file in walk(path, ".json"):
        print("Analyzing %s" % no_ext_file, file = sys.stderr)
        my_tsv_file = no_ext_file.replace('ar', 'fr').replace('en', 'fr') + ".tsv"
        my_tweet_file = no_ext_file + ".json"
        my_output_file = no_ext_file + ".out.tsv"
        uppermain(my_tweet_file, my_tsv_file, entities, my_output_file, acc_score, acc_delta)

    tweetos = sorted(acc_score.items(), key= lambda k: k[1], reverse = True)
    tweetos = tweetos[:1000]
    finals = []

    for name in acc_delta:
        acc_delta[name] = int( sum(acc_delta[name]) / len(acc_delta[name]) )
    for name, score in tweetos:
        finals.append( "%s\t%i\t%i" % (name, score, acc_delta[name]) )

    with open(out_tweetos, "w") as ostream:
        print("\n".join(finals), file = ostream)

if __name__ == "__main__":
    main()
