#! /usr/bin/env python3

import json, os, re, sys, datetime

keep = set(["id", "source", "place", "text", "lang", "geo", "created_at", "possibly_sensitive", "timestamp_ms", "entities", "user"])
keep_in_entities = set(['hashtags', 'urls', 'symbols', 'user_mentions'])
keep_in_subentities = {
    'hashtags': set(['text']),
    'urls': set(['expanded_url']),
    'symbols': set([]),
    'user_mentions': set(['name']),
}
keep_in_user = set(['name'])


def should_keep_tweet(timestamp, real_intervals):
    for start, end in real_intervals:
        if int(timestamp) >= start and int(timestamp) <= end:
            return True
    return False

def filter_by_timestamp(tweets, tid, real_timestamps, span):
    new_tweets = []
    first, end = span
    first = first * 1000
    end   = end * 1000

    real_intervals = []
    for timestamp in real_timestamps:
        interval = [int(timestamp) - first, int(timestamp) + end]
        real_intervals.append(interval)

    for tweet in tweets:
        timestamp = tweet[tid]
        if should_keep_tweet(timestamp, real_intervals):
            new_tweets.append(tweet)
    return new_tweets

def handle_subentities(json, entity, keep, info):
    info_sub = []
    for jq in json:
        k = keep[entity]
        for key in jq:
            if key not in k:
                continue
            info_sub.append(jq[key])
    info[entity] = ",".join([str(s).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ') for s in info_sub])

def handle_entities(json, keep, info):
    for pkey in json:
        if pkey not in keep:
            continue
        handle_subentities(json[pkey], pkey, keep_in_subentities, info)

def handle_user(json, keep, info):
    for pkey in json:
        if pkey not in keep:
            continue
        info[pkey] = json[pkey].replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')

def tabularize(path):
    keys = []
    tweets = []

    with open(path) as stream:
        for i, line in enumerate(stream):
            line = line.strip()
            jq = json.loads(line)

            if 'limit' in jq:
                continue

            info = {}
            for k in keep:
                info[k] = ""
            for k in keep_in_entities:
                info[k] = ""
            for k in keep_in_user:
                info[k] = ""

            for key in jq:
                if key in keep:
                    if key == "entities":
                        handle_entities(jq[key], keep_in_entities, info)
                    elif key == "user":
                        handle_user(jq[key], keep_in_user, info)
                    else:
                        if key == "text":
                            info[key] = jq[key].replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
                        else:
                            info[key] = str(jq[key])
            sort = sorted(info.items())
            values = []
            for k,v in sort:
                if i == 0:
                    keys.append(k)
                values.append(v)
            tweets.append(values)
    return keys, tweets

def parse_real_time(path):
    times = []
    with open(path) as stream:
        for i, line in enumerate(stream):
            line = line.strip()

            if i == 0:
                continue
            items = line.split("\t")
            items = [i for i in items if i.strip() != ""]
            if len(items) > 0:
                times.append( items[0] )
    return times

def convert_to_unix(iso):
    utc_dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    # convert UTC datetime to seconds since the Epoch
    timestamp = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(timestamp * 1000)

def walk(path, extension):
    for root, dirs, files in os.walk(path):
        for f in files:
            fullfile = os.path.join(root, f)
            no_ext, ext = os.path.splitext(fullfile)
            if ext == extension:
                yield no_ext

def extract_date(path):
    items = path.split('_')
    idx = -3
    if items[-1] == "SO":
        idx = -4
    return items[idx]

def resort_by_timestamp(tid, tweets):
    return sorted(tweets, key=lambda k: k[tid])

def options():
    import argparse
    parser = argparse.ArgumentParser(prog="Hackatal Filtering")
    parser.add_argument('-b', '--before', type=int, default=120, help='Min interval (in sec)')
    parser.add_argument('-a', '--after', type=int, default=120, help='Max interval (in sec)')
    #parser.add_argument('-d', '--date', required=True, help='Date of the match')
    #parser.add_argument('-m', '--match', required=True, help='Match file')
    #parser.add_argument('-j', '--json', required=True, help='Tweets')
    parser.add_argument('-p', '--path', required=True, help='Path to jsons')
    parser.add_argument('-n', '--no-filter', action="store_false", help='Don\'t filter out on events (for test data)')

    return parser

def main():
    args = options().parse_args()

    gmt_times_files = {}
    for no_ext_file in walk(args.path, ".tsv"):
        if ".filtered" in no_ext_file:
            continue

        print("Analyzing %s" % no_ext_file+".tsv", file=sys.stderr)
        date = extract_date(no_ext_file)
        tpldate = date + "T%s"
        times = parse_real_time(no_ext_file+".tsv")
        gmt_times = []
        for time in times:
            h,m,s = time.split(':')
            h = int(h) - 2
            gmt = tpldate % ("%i:%s:%sZ" % (h,m,s),)
            unix = convert_to_unix(gmt)
            gmt_times.append(unix)
        gmt_times_files[no_ext_file] = gmt_times

    for no_ext_file in walk(args.path, ".json"):
        my_tsv_file = no_ext_file.replace('ar', 'fr').replace('en', 'fr')
        span = [args.before, args.after]
        tid = 12
        keys, tweets = tabularize(no_ext_file+".json")
        print("Analyzing %s" % no_ext_file+".json", file=sys.stderr)
        print("Number of tweets before filtering: %i" % len(tweets), file=sys.stderr)

        if args.no_filter:
            tweets = filter_by_timestamp(tweets, tid, gmt_times_files[my_tsv_file], span)
            print("Number of tweets after filtering: %i" % len(tweets), file=sys.stderr)

        with open(no_ext_file+".filtered.tsv", "w") as stream:
            print( "\t".join(keys), file=stream )
            print( "\n".join(["\t".join(t) for t in resort_by_timestamp(tid, tweets)]), file=stream )

if __name__ == "__main__":
    main()
