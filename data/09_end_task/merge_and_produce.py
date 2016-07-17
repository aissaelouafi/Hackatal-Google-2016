#! /usr/bin/env python3
import os, re, sys, datetime
from collections import defaultdict
from final_match import *

def extract_players(pred_players):
    players = set(pred_players.split(','))
    keep = set()
    for p in players:
        if " " in p:
            keep.add(p)

    if len(keep) == 0:
        return " ; ".join(players)
    else:
        return " ; ".join(keep)


def do_merging(e1,  e2):
    actions_e1, actions_e2 = set(e1[2].split(',')), set(e2[2].split(','))
    players_e1, players_e2 = set(e1[4].split(',')), set(e2[4].split(','))

    e1[2] = ",".join( actions_e1 | actions_e2 )
    e1[4] = ",".join( players_e1 | players_e2 )

    return e1

def merge_events(lines):
    remove = []
    for i in range(1, len(lines)):
        event_1 = lines[i]
        actions = set(event_1[2].split(','))
        tp      = int(event_1[0])
        for j in range(i+1, len(lines)):
            event_next = lines[j]
            actions_next = set(event_next[2].split(','))
            tp_next = int(event_next[0])

            if abs(tp_next - tp) > 80 * 1000:
                break

            if len( actions & actions_next ) > 0:
                event_1 = do_merging(event_1, event_next)
                remove.append(j)
                actions = set(event_1[2].split(','))

    remove = reversed(remove)
    for i in remove:
        lines.pop(i)

def transform_timestamp_into_cest(tp):
    h = datetime.datetime.utcfromtimestamp(tp/1000).strftime('%H')
    m = datetime.datetime.utcfromtimestamp(tp/1000).strftime('%M')
    s = datetime.datetime.utcfromtimestamp(tp/1000).strftime('%S')
    h = int(h) + 2
    return "%i:%s:%s" % (h,m,s)

def keep_event_related_to_match(items, c1, c2):
    countries = set(items[3].split(','))
    if c1 in countries or c2 in countries:
        return True
    return False

def contains_country_or_player(items):
    countries = items[3].split(',')
    countries = filter(countries, lambda k: k.strip() == "")
    players   = items[4].split(',')
    players   = filter(players, lambda k: k.strip() == "")
    if len(countries) > 0 or len(players) > 0:
        return True
    else:
        return False


def main():
    path = sys.argv[1]
    output_path = sys.argv[2]

    commons = defaultdict(set)
    for no_ext_file in walk(path, '.tsv'):
        if not no_ext_file.endswith('.predicted'):
            continue
        basename = os.path.basename(no_ext_file)
        common = basename.replace('.predicted', '').replace('_fr', '').replace('_en', '').replace('_ar', '')
        commons[common].add(no_ext_file+".tsv")

    for common in commons:
        c1, c2, _ = common.split('_', 2)
        c1 = normalize(c1)
        c2 = normalize(c2)

        lines = []
        headers = []
        for path in commons[common]:
            with open(path) as stream:
                start = True
                for line in stream:
                    line = line.replace('\n', '')
                    items = line.split('\t')
                    if start:
                        headers = items
                        start = False
                        continue

                    if not contains_country_or_player(items):
                        continue

                    if not keep_event_related_to_match(items, c1, c2):
                        continue

                    lines.append(items)

        lines = sorted(lines, key = lambda k:k[0])
        merge_events(lines)

        with open(os.path.join(output_path, common+".predicted.tsv"), 'w') as ostream:
            headers = ["TEMPS ABSOLU (HH:MIN)", "EVENEMENT", "ANNOTATION COMPLEMENTAIRE"]
            print("\t".join(headers), file = ostream)
            for items in lines:
                items[0] = transform_timestamp_into_cest(int(items[0]))
                items[4] = extract_players(items[4])

                out = (items[0], items[2], items[4])
                l = "\t".join(out)
                print(l, file = ostream)


if __name__ == "__main__":
    main()
