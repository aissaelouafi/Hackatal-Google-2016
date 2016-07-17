#! /usr/bin/env python
import pandas as pd
import datetime
import re, sys, os
import numpy as np
from collections import defaultdict

def between_interval(timestamp, start, end):
    if timestamp >= start and timestamp <= end:
        return True
    else:
        return False

def convert_to_unix(iso):
    utc_dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    # convert UTC datetime to seconds since the Epoch
    timestamp = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(timestamp * 1000)

def timeTrueLabels(path_tsv_train):
    """
        input: path_tsv_train
        output: [(timestamp:event),...]
    """
    date=re.search(r'[0-9]+-[0-9]+-[0-9]+',path_tsv_train).group(0)

    df_train=pd.read_csv(path_tsv_train, sep='\t',index_col=False, encoding='utf-8')
    filledLines=[df_train["TEMPS ABSOLU (HH:MIN)"][i] for i in range(len(df_train["TEMPS ABSOLU (HH:MIN)"])) if not pd.isnull(df_train["TEMPS ABSOLU (HH:MIN)"])[i]]

    timeTrueLabels=[]
    for id_event in range(len(filledLines)):
        time=df_train["TEMPS ABSOLU (HH:MIN)"][id_event].split(':')
        time[0] = str( int(time[0]) - 2 )
        time = ":".join(time)
        iso_true = date+'T'+time+'Z'
        timestamp_true = convert_to_unix(iso_true)

        players = df_train["ANNOTATION COMPLEMENTAIRE"][id_event]
        if pd.isnull(df_train["ANNOTATION COMPLEMENTAIRE"])[id_event]:
            players = ""

        players = players.split(',')
        final_players = []
        for p in players:
            p = p.split(';')
            final_players.extend(p)

        timeTrueLabels.append( (timestamp_true, df_train["EVENEMENT"][id_event], final_players) )

    return timeTrueLabels


def annotate_norm_by_trueLabel(path_tsv_norm, path_tsv_norm_annoted, listTimeTrueLabels, tweetos_file):
    """
        input:
            path_in
            path_out
            timeTrueLabels

        output:
            generate a file annoted with "true_label", "true_players", "scores"
    """

    tweetos = defaultdict(dict)
    end_dict = {}

    df_norm=pd.read_csv(path_tsv_norm, sep='\t',index_col=False, encoding='utf-8')
    filledLines=[df_norm["id"][i] for i in xrange(len(df_norm["id"])) if not pd.isnull(df_norm["id"])[i]]
    df_norm['relevance_score']=pd.Series(np.nan,index=df_norm.index)
    df_norm['delta']=pd.Series(np.nan,index=df_norm.index)

    elapsed = 120 * 1000
    for id_tw in xrange( len(filledLines) ):
        timestamp_tw = df_norm['timestamp_ms'][id_tw]
        deltas = []
        true_events = []
        true_players = []
        for real_time, action, annotation in listTimeTrueLabels:
            if between_interval(timestamp_tw, real_time - elapsed, real_time + elapsed):
                true_events.append(action)
                true_players.extend(annotation)
            deltas.append( abs(timestamp_tw - real_time) )

        delta = int( sum(deltas) / len(deltas) )
        true_events = set(true_events)
        true_players = set(true_players)
        pred_events = str( df_norm['entities'][id_tw] )
        pred_event = [ event.strip() for event in pred_events.split(',') ]
        pred_players = str( df_norm['players'][id_tw] )
        pred_player = [ p.strip() for p in pred_players.split(',') ]


        # count relevance score
        score=0
        for e in pred_event:
            if e in true_events:
                score += 1

        if score > 0:
            for p in pred_player:
                if p in true_players:
                    score += 1

        if 'score' in tweetos[df_norm['name'][id_tw]]:
            tweetos[df_norm['name'][id_tw]]['score'] += score
        else:
            tweetos[df_norm['name'][id_tw]]['score'] = score

        if 'delta' not in tweetos[df_norm['name'][id_tw]]:
            tweetos[df_norm['name'][id_tw]]['delta'] = delta
        else:
            tweetos[df_norm['name'][id_tw]]['delta'] += delta

        if 'ndelta' not in tweetos[df_norm['name'][id_tw]]:
            tweetos[df_norm['name'][id_tw]]['ndelta'] = 1
        else:
            tweetos[df_norm['name'][id_tw]]['ndelta'] += 1

        df_norm['relevance_score'][id_tw] = score
        df_norm['delta'][id_tw] = delta

    # output
    df_norm.to_csv(path_tsv_norm_annoted, sep='\t', encoding='utf-8')
    sorted_tweetos = sorted(tweetos.iteritems(), key= lambda k: k[1]['score'], reverse = True)
    for tname in tweetos:
        tweetos[tname]['delta'] = int( tweetos[tname]['delta'] / tweetos[tname]['ndelta'] )
        delta, score = tweetos[tname]['delta'], tweetos[tname]['score']
        tweetos[tname]['all'] = "%s\t%s\t%s" % (tname, delta, score)
    with open(tweetos_file, 'w') as ostream:
        print >> ostream, "\n".join( [v['all'] for k,v in sorted_tweetos] )


def options():
    import argparse
    parser = argparse.ArgumentParser(prog="Hackatal Relevance score")
    parser.add_argument('-i', '--input', required=True, help='Input file')
    parser.add_argument('-m', '--match', required=True, help='Match file')
    parser.add_argument('-s', '--suffix', required=True, help='Suffix to replace in file')
    parser.add_argument('-r', '--replace', required=True, help='Replacement')
    parser.add_argument('-t', '--tweetos', required=True, help='Tweetos output file')
    return parser

def main():
    args = options().parse_args()
    path_tsv_train = args.match
    path_tsv_norm  = args.input
    path_tsv_norm_annoted = args.input.replace(args.suffix, args.replace)
    listTimeTrueLabels = timeTrueLabels(path_tsv_train)
    annotate_norm_by_trueLabel(path_tsv_norm, path_tsv_norm_annoted, listTimeTrueLabels, args.tweetos)

if __name__ == "__main__":
    main()
