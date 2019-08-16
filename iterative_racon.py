#!/usr/bin/env python3

'''
Run racon iterativily. Will detect finished runs.

Require:
    racon
    minimap2
'''

import sys
import os
import re
import argparse
import subprocess as sp

parser = argparse.ArgumentParser(description='Run racon iterativily with nanopore reads. Will detect finished runs.')
parser.add_argument('fasta')
parser.add_argument('fq')
parser.add_argument('-p', type=str, help='output prefix (input basename)', default=None)
parser.add_argument('-i', type=int, help='number of iterations (%(default)s)', default=4)
parser.add_argument('-t', type=int, help='threads (%(default)s)', default=20)
parser.add_argument('--racon', type=str, help='racon executable if not in $PATH', default='racon')
parser.add_argument('--minimap2', type=str, help='minimap2 executable if not in $PATH', default='minimap2')
args = parser.parse_args()

RACON = args.racon
MINIMAP = args.minimap2
mapper = 'map-ont'

fa_base = args.fasta
fq = args.fq
if not args.p:
    prefix = re.sub('.fa$|.fasta$', '', os.path.basename(fa_base)) + '_racon'
else:
    prefix = args.p
iter_n = args.i
threads = args.t

fa_out = fa_base
for n in range(iter_n):
    fa_in = fa_out
    fa_out = '{}_{}'.format(prefix, n + 1) + '.fasta'
    if os.path.isfile(fa_out) and os.path.getsize(fa_out) > 0:
        print('Found iteration {} result, skip.'.format(n + 1), file=sys.stderr)
        continue

    aln = 'reads{}.sam'.format(n + 1)
    print('Iteration {} start...'.format(n + 1), file=sys.stderr)
    if not os.path.isfile(aln) or os.path.getsize(aln) == 0:
        with open(aln, 'w') as OUT, open('minimap.{}.err'.format(n + 1), 'w') as ERR:
            # '-c' or '-a' is crucial in minimap2 mapping approach!
            # https://github.com/lh3/minimap2/blob/master/FAQ.md#1-alignment-different-with-option--a-or--c
            sp.run([MINIMAP, '-a', '-x', mapper, '-t', str(threads), fa_in, fq], stdout=OUT, stderr=ERR, check=True)

    with open(fa_out, 'w') as OUT, open('racon.{}.err'.format(n + 1), 'w') as ERR:
        sp.run([RACON, '-t', str(threads), fq, aln, fa_in], stdout=OUT, stderr=ERR, check=True)
    print('Iteration {} finish!'.format(n + 1), file=sys.stderr)
