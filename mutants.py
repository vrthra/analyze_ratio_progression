#!/usr/bin/env python3
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import argparse
import sys
import os
import datetime
import time

import ggplot as gg
import pandas as pd

import random
random.seed(0)


def genmutant(mutantlen, nfaulty):
    """Generate a mutant mutantlen long with nfaulty faulty bits"""
    faulty_bits = random.randrange(1, nfaulty+1)
    m = 0
    for i in range(0, faulty_bits):
        pos = random.randrange(0, mutantlen)
        fault = 1 << pos
        m = m | fault
    assert m != 0
    return m

def gentest(mutantlen, nchecks):
    """Generate a test that checks n faulty bits"""

    # This is exactly same as genmutant, but rewritten here just in
    # case we want to change the distribution.
    faulty_bits = random.randrange(1, nchecks+1)
    m = 0
    for i in range(0, faulty_bits):
        pos = random.randrange(0, mutantlen)
        fault = 1 << pos
        m = m | fault
    assert m != 0
    return m

def gen_mutants(nmutants, mutantlen, nfaulty):
    """ Generate n mutants """
    lst = []
    for i in range(0, nmutants):
        lst.append(genmutant(mutantlen, nfaulty))
    return lst

def gen_tests(ntests, mutantlen, nchecks):
    testline = []
    for i in range(0, ntests):
        testline.append(gentest(mutantlen, nchecks))
    return testline


def kills(test, mutant):
    # A test kills a mutant if any of the bits match.
    return mutant & test

def plot(mydata, opts):
    p = gg.ggplot(gg.aes(x=opts['x'], y=opts['y']), data=mydata) + gg.geom_line() +\
       gg.xlab(opts['x']) + gg.ylab(opts['y']) + gg.ggtitle(opts['title'])

    p.save(opts['file'])

def dname(opts):
  return "data/mutantlen={mutantlen}/nmutants={nmutants}/nequivalents={nequivalents}/nfaulty={nfaulty}".format(**opts) + \
  "/ntests={ntests}/nchecks={nchecks}".format(**opts)

def mutant_killscore(opts, mutants, equivalents, my_tests):
    mutant_kills = {}
    nmutants = int(opts['nmutants'])
    cent = nmutants // 100
    #start = datetime.datetime.now()
    start = time.monotonic()
    for j,m in enumerate(mutants + equivalents):
        end = time.monotonic()
        #end = datetime.datetime.now()
        if j % cent == 0: print("%3.0f%% (%0.0f sec)" % (j/nmutants * 100.0, end-start), end='', sep=' ', flush=True)
        #start = datetime.datetime.now()
        #start = time.monotonic()
        mutant_kills[j] = sum(1 for t in my_tests if kills(t, m))
    print(" 100%")
    return mutant_kills

def do_statistics(opts, mutant_kills):
    atleast_ntests = {}
    ntests = []
    with open(dname(opts) + '/atleast.csv', 'w+') as f:
        print('ntests, atleast, atmost, exactly',file=f)
        for i in range(0, 11):
            k = sum(1 for mi, killed in mutant_kills.items() if killed >= i)
            s = sum(1 for mi, killed in mutant_kills.items() if killed <= i)
            e = sum(1 for mi, killed in mutant_kills.items() if killed == i)
            atleast_ntests[i] = k
            ntests.append({'ntests':i, 'atleast':k, 'atmost':s, 'exactly':e})
            print("%d, %d, %d, %d" % (i, k, s, e), file=f)

    imax = max(i for i, k in atleast_ntests.items())

    mu_ratio = {}
    for i in range(2, imax + 1):
        if atleast_ntests[i] == 0: break
        mu_ratio[i - 1] = atleast_ntests[i] / atleast_ntests[i-1]

    with open(dname(opts) + '/ratios.csv', 'w+') as f:
        print('index, ratio',file=f)
        for i in sorted(mu_ratio.keys()):
            print("%f, %f" % (i, mu_ratio[i]), file=f)
            print(i, mu_ratio[i])
    print('plotting', file=sys.stderr)
    data = pd.DataFrame(ntests)
    print(data)
    plot(data, {'x':'ntests', 'y':'atleast', 'title':str(opts), 'file':dname(opts) + '/plot.png'})
    print('done', file=sys.stderr)

def main(nmutants=1000, nequivalents=1000, mutantlen=100, nfaulty=100, ntests=1000, nchecks=10):
    opts = {'nmutants':nmutants,
       'mutantlen':mutantlen,
       'nfaulty':nfaulty,
       'ntests':ntests,
       'nchecks':nchecks,
       'nequivalents':nequivalents}
    os.makedirs(dname(opts), exist_ok=True)
    # first generate our tests
    my_tests = gen_tests(ntests=ntests, mutantlen=mutantlen, nchecks=nchecks)

    # Now generate n mutants
    mutants = gen_mutants(nmutants=nmutants, mutantlen=mutantlen, nfaulty=nfaulty)

    equivalents = [0 for i in range(0, nequivalents)]
    opts['nequivalents'] = len(equivalents)

    # how many tests killed this mutant?
    mutant_kills = mutant_killscore(opts, mutants, equivalents, my_tests)

    do_statistics(opts, mutant_kills)

parser = argparse.ArgumentParser()
parser.add_argument('--nmutants', type=int, default=1000, help='the number of mutants')
parser.add_argument('--nequivalents', type=int, default=0, help='the number of equivalents')
parser.add_argument('--mutantlen', type=int, default=100, help='the size (in bits) of a single mutant')
parser.add_argument('--nfaulty', type=int, default=100, help='the maximum number of faults in a single mutant')
parser.add_argument('--ntests', type=int, default=1000, help='the number of tests to use')
parser.add_argument('--nchecks', type=int, default=10, help='the maximum number of bits checked per test')
args = parser.parse_args()
main(args.nmutants, args.nequivalents, args.mutantlen, args.nfaulty, args.ntests, args.nchecks)
