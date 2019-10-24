#! /usr/bin/env python

# Given a two by two tableau:
#
#         | X        |   not X
#   ----------------------------------
#   Y     |   a      | b
#    ---------------------------------
#   not Y | c        | d
#
# ... calculate (variants of) the Fisher exact test.
#
# These functions use arbitrary-precision rational numbers and return *exact* results. For that reason, they are slow.
#
# FisherExactT(a, b, c, d) --> corresponds to R: fisher.test(matrix(c(a, b, c, d), nrow = 2, byrow = TRUE), alternative = "t")$p.value
# FisherExactG(a, b, c, d) --> corresponds to R: fisher.test(matrix(c(a, b, c, d), nrow = 2, byrow = TRUE), alternative = "g")$p.value
# FisherExactL(a, b, c, d) --> corresponds to R: fisher.test(matrix(c(a, b, c, d), nrow = 2, byrow = TRUE), alternative = "l")$p.value

from gmpy import mpq, bincoef
import math 
from math import log10

def CalculateProbability(a, b, c, d):
    return mpq(bincoef(a + b, a) * bincoef(c + d, c), bincoef(a + b + c + d, a + c))

def FisherExactT(a, b, c, d):

    pBase = CalculateProbability(a, b, c, d)

    pTotalMoreExtreme = 0

    min_aa = max(a - d,     0)
    max_aa = min(a + b, a + c)

    for aa in xrange(min_aa, max_aa + 1):

        bb = a + b - aa
        cc = a + c - aa
        dd = d - a + aa

        pNow = CalculateProbability(aa, bb, cc, dd)

        if pNow <= pBase:
            pTotalMoreExtreme += pNow

    return pTotalMoreExtreme

def FisherExactG(a, b, c, d):

    pTotalMoreExtreme = 0

    min_aa = a
    max_aa = min(a + b, a + c)

    for aa in xrange(min_aa, max_aa + 1):

        bb = a + b - aa
        cc = a + c - aa
        dd = d - a + aa

        pTotalMoreExtreme += CalculateProbability(aa, bb, cc, dd)

    return pTotalMoreExtreme

def FisherExactL(a, b, c, d):

    pTotalMoreExtreme = 0

    min_aa = max(a - d, 0)
    max_aa = a

    for aa in xrange(min_aa, max_aa + 1):

        bb = a + b - aa
        cc = a + c - aa
        dd = d - a + aa

        pTotalMoreExtreme += CalculateProbability(aa, bb, cc, dd)

    return pTotalMoreExtreme

def LogarithmOfFraction(p, base = None):
    if base is None:
        #WATCH VERSION
        #return math.log(p.numerator) - math.log(p.denominator)
        return math.log(p.numer()) - math.log(p.denom())
    else:
        #return math.log(p.numerator, base) - math.log(p.denominator, base)
        return math.log(p.numer(), base) - math.log(p.denom(), base)
#print(testcase, LogarithmOfFraction(testcase, 10))

def main():
    from math import log10
    from random import randint
    import rpy2.robjects.numpy2ri
    import numpy
    rpy2.robjects.numpy2ri.activate() # In the new version of RPy2 you need to activate that feature.
    import rpy2.robjects as robjects
    fisherR = robjects.r["fisher.test"]

    nFAIL = 0
    nMax = 1000

    for i in xrange(1000):

        a = randint(0, nMax)
        b = randint(0, nMax)
        c = randint(0, nMax)
        d = randint(0, nMax)

        table = numpy.array(([a, b], [c, d]))

        r_T = fisherR(table, alternative = "t").rx2("p.value")[0]
        r_G = fisherR(table, alternative = "g").rx2("p.value")[0]
        r_L = fisherR(table, alternative = "l").rx2("p.value")[0]

        if r_T == 0.0 or r_G == 0.0 or r_L == 0.0:
            print("Skipping case", a, b, c, d, " due to R yielding zero:", r_T, r_G, r_L)
            continue

        # This would yield an overflow in case of zero values.
        r_T = log10(r_T)
        r_G = log10(r_G)
        r_L = log10(r_L)

        myT = FisherExactT(a, b, c, d)
        myG = FisherExactG(a, b, c, d)
        myL = FisherExactL(a, b, c, d)

        # Probabilities will always be positive.
        myT = log10(myT)
        myG = log10(myG)
        myL = log10(myL)

        # the log10-p values should be the same to epsilon.

        errT = myT - r_T
        errG = myG - r_G
        errL = myL - r_L

        epsilon = 1e-12
        if abs(errT) > epsilon or abs(errG) > epsilon or abs(errL) > epsilon:
            nFAIL = nFAIL + 1
            print("T", a, b, c, d, r_T, myT)
            print("G", a, b, c, d, r_G, myG)
            print("L", a, b, c, d, r_L, myL)

    print("Number of test failures:",nFAIL)

if __name__ == "__main__":
    main()
