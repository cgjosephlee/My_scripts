#!/usr/bin/env python3

'''
Bin and trim the fastqs according to `barcoding_summary.txt` generated by guppy_barcoder.
Unclassified reads are not trimmed.

TODO:
    require both front and rear barocode?
    tunable quality criteria?
'''

import sys
import os
from glob import glob
import pysam

if len(sys.argv[1:]) != 2:
    print('Usage: {} <dir_fq> <dir_barcode>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

dir_fq = sys.argv[1]
dir_barcode = sys.argv[2]

ids = {}
barcodes = set()
with open(os.path.join(dir_barcode, 'barcoding_summary.txt')) as f:
    next(f)  # skip first line
    for line in f:
        line = line.strip().split()
        st = int(line[10]) + int(line[11])
        ed = (int(line[16]) + int(line[17])) * -1
        # score_F = float(line[7])
        # score_R = float(line[13])
        ids[line[0]] = [line[1], [st, ed]]
        barcodes.add(line[1])

# barcodes = set([ids[x][0] for x in ids.keys()])
# barcodes.discard('unclassified')

file_outs = {}
for i in barcodes:
    file_outs[i] = open(os.path.join(dir_barcode, i + '.fastq'), 'w')

file_fqs = glob(os.path.join(dir_fq, '*fastq'))
# print(file_fqs)
if len(file_fqs) > 0:
    print('Found {} fastq files.'.format(len(file_fqs)), file=sys.stderr)
else:
    print('No fastq file was found!', file=sys.stderr)
    sys.exit(1)

for f in file_fqs:
    with pysam.FastxFile(f) as fh:
        for entry in fh:
            # v = ids[entry.name]
            v = ids.pop(entry.name)  # get value and remove key
            if v[0] != 'unclassified':
                entry.sequence = entry.sequence[v[1][0]:v[1][1]]
                entry.quality = entry.quality[v[1][0]:v[1][1]]
            print(str(entry), file=file_outs[v[0]])

for f in file_outs.values():
    f.close()

if len(ids.keys()) != 0:
    print('Something wrong!', file=sys.stderr)
    sys.exit(1)
