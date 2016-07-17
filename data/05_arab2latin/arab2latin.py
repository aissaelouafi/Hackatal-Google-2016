#!/usr/bin/env python3

def options():
    import argparse
    parser = argparse.ArgumentParser(prog="Hackatal Arab2Latin")
    parser.add_argument('-i', '--input', required=True, help='Input file to be transformed')
    parser.add_argument('-s', '--suffix', default='not_norm', help='String to find in file')
    parser.add_argument('-r', '--replace', default='norm', help='Replace found string by this one')
    parser.add_argument('-t', '--tweet', action="store_true", help='Output file')
    return parser

def arab2Latin(tweet):
    dic ={"ل":"l","ە":"h","م":"m","ر":"r","ت":"t","ز":"z","ن":"n","ش":"ch","ق":"k","ف":"f","و":"w","ي":"y","ط":"t","ك":"k","د":"d","ذ":"d","ب":"b","خ":"kh","ح":"h","ج":"j","ظ":"d","ع":"3","ه":"h","غ":"r","ث":"t","ص":"s","إ":"i","ة":"a","ض":"d","أ":"a","ى":"a","آ":"a","ئ":"a","ء":"2","ا":"a","ّ":"","ْ":"","ٌ":"","ْ":"","ُ":"","ٍ":"","ِ":"","ً":"","َ":"","س":"s","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9","٠":"0"}
    for i, j in dic.items():
        tweet = tweet.replace(i, j)
    return tweet

normalizing_cols = set(['text', 'hashtags', 'name'])
def main():
    cols_number = []
    args = options().parse_args()
    output = args.input.replace(args.suffix, args.replace)
    print("Normalizing (arab2Latin) %s" % args.input)
    with open(args.input) as stream, open(output, 'w') as ostream:
        for i, line in enumerate(stream):
            line = line.replace('\n', '')
            if args.tweet:
                items  = line.split('\t')
                if i == 0:
                    for j, k in enumerate(items):
                        if k in normalizing_cols:
                            cols_number.append(j)
                    cols_number = sorted(cols_number)
                    print("\t".join(items), file = ostream)
                    continue

                for j in cols_number:
                    items[j] = arab2Latin(items[j])
                print("\t".join(items), file = ostream)
            else:
                line = arab2Latin(line)
                print(line, file = ostream)

if __name__ == "__main__":
    main()
