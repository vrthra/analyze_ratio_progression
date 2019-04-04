#!/usr/bin/env python3
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import argparse
import sys
import datetime
import time

import random
random.seed(0)
#from scipy.stats import norm

M_UPTO = 1 # generate upto nfaulty bits per mutant
M_EXACT = 2 # generate exactly nfaulty bits per mutant
M_NUM_FAULTS = M_UPTO

T_UPTO = 1 # generate upto nfaulty bits per test
T_EXACT = 2 # generate exactly nfaulty bits per test
T_NUM_FAULTS = T_UPTO

def random_number(start, end):
    return random.randrange(start, end)

def genmutant(mutantlen, nfaulty):
    """Generate a mutant mutantlen long with nfaulty faulty bits"""
    faulty_bits = nfaulty if M_NUM_FAULTS == M_EXACT else random_number(1, nfaulty+1)
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
    faulty_bits = nchecks if T_NUM_FAULTS == T_EXACT else random_number(1, nchecks+1)
    m = 0
    for i in range(0, faulty_bits):
        pos = random.randrange(0, mutantlen)
        fault = 1 << pos
        m = m | fault
    assert m != 0
    return m

def gen_mutants(nmutants, mutantlen, nfaulty):
    """ Generate n mutants """
    return [genmutant(mutantlen, nfaulty) for i in range(0, nmutants)]

def gen_tests(ntests, mutantlen, nchecks):
    """ Generate n tests """
    return [gentest(mutantlen, nchecks) for i in range(0, ntests)]

def kills(test, mutant):
    # A test kills a mutant if any of the bits match.
    return mutant & test

def mutant_killmatrix(opts, mutants, equivalents, my_tests):
    mutant_kills = []
    nmutants = int(opts['nmutants'])
    start = time.monotonic()
    for j,m in enumerate(mutants + equivalents):
        end = time.monotonic()
        mutant_kills.append(['1' if kills(t,m) else '0' for t in my_tests])
    return mutant_kills

def mutant_killscore(opts, mutants, equivalents, my_tests):
    mutant_kills = {}
    nmutants = int(opts['nmutants'])
    cent = nmutants // 100
    start = time.monotonic()
    for j,m in enumerate(mutants + equivalents):
        mutant_kills[j] = sum(1 for t in my_tests if kills(t, m))
    return mutant_kills

def main(nmutants=1000, nequivalents=0, mutantlen=100, nfaulty=100, ntests=1000, nchecks=10):
    opts = {'nmutants':nmutants,
       'mutantlen':mutantlen,
       'nfaulty':nfaulty,
       'ntests':ntests,
       'nchecks':nchecks,
       'nequivalents':nequivalents}
    # first generate our tests
    my_tests = gen_tests(ntests=ntests, mutantlen=mutantlen, nchecks=nchecks)

    # Now generate n mutants
    mutants = gen_mutants(nmutants=nmutants, mutantlen=mutantlen, nfaulty=nfaulty)

    equivalents = [0 for i in range(0, nequivalents)]
    opts['nequivalents'] = len(equivalents)

    # how many tests killed this mutant?
    mutant_kill_matrix = mutant_killmatrix(opts, mutants, equivalents, my_tests)
    mutant_kills = mutant_killscore(opts, mutants, equivalents, my_tests)
    for i,mutant in enumerate(mutant_kill_matrix):
        print(i+1,','.join(mutant), sep='')
    score = len([i for i in mutant_kills if mutant_kills[i] > 0])/len(mutant_kills)
    print("score=%f" % score, file=sys.stderr)

parser = argparse.ArgumentParser()
parser.add_argument('--nmutants', type=int, default=1000, help='the number of mutants')
parser.add_argument('--nequivalents', type=int, default=0, help='the number of equivalents')
parser.add_argument('--mutantlen', type=int, default=100, help='the size (in bits) of a single mutant')
parser.add_argument('--nfaulty', type=int, default=100, help='the maximum number of faults in a single mutant')
parser.add_argument('--ntests', type=int, default=1000, help='the number of tests to use')
parser.add_argument('--nchecks', type=int, default=10, help='the maximum number of bits checked per test')
args = parser.parse_args()
main(args.nmutants, args.nequivalents, args.mutantlen, args.nfaulty, args.ntests, args.nchecks)
