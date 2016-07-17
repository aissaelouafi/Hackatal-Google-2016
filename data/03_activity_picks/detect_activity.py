#! /usr/bin/env python3

import os, re, sys
from collections import defaultdict

def find_timestamp_idx(tmp, items):
    for i, k in enumerate(items):
        if k == tmp:
            return i
    return None #Should never happen!

def find_right_bin(time, interval, binn, start_time):
    time = int(time)
    start_time = int(start_time)
    end_time   = start_time + interval
    if time >= start_time and time <= end_time:
        return binn, start_time
    else:
        return find_right_bin(time, interval, binn+1, end_time)

def options():
    import argparse
    parser = argparse.ArgumentParser(prog="Hackatal Activity Picks")
    parser.add_argument('-i', '--input', required=True, help='Input file')
    parser.add_argument('-I', '--interval', default=10, type=int, help='Interval in secs')
    return parser

def main():
    args = options().parse_args()
    timestamp_idx = 11
    start_time = None
    graph = defaultdict(int)
    bin_number = 0
    start_times = {}
    with open(args.input) as stream:
        for i, line in enumerate(stream):
            line = line.strip()
            items = line.split('\t')
            if i == 0:
                timestamp_idx = find_timestamp_idx('timestamp_ms', items)
                continue
            if i == 1:
                start_time = items[timestamp_idx]
                graph[bin_number] += 1
                start_times[bin_number] = start_time
                continue

            time = items[timestamp_idx]
            bin_number, start_time = find_right_bin(time, args.interval*1000, bin_number, start_time)
            graph[bin_number] += 1
            start_times[bin_number] = start_time
    print(start_times)
    print(graph)

if __name__ == "__main__":
    main()
