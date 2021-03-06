#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import division, with_statement
'''
Copyright 2013, 陈同 (chentong_biology@163.com).  
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
desc = '''
Functional description:
    This is designed to generate plot for output of clusterProfileGO.sh.

'''

import sys
import os
from json import dumps as json_dumps
import json
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
#from multiprocessing.dummy import Pool as ThreadPool
from math import log

debug = 0

def fprint(content):
    print json_dumps(content,indent=1)

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "%prog -i file"
    parser = OP(usage=usages)
    parser.add_option("-i", "--input-file", dest="filein",
        metavar="FILEIN", help="file given to clusterProfileSelf.sh.")
    parser.add_option("-t", "--tag", dest="tag",
        metavar="FILEIN", help="tag given to clusterProfileSelf.sh.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-d", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------
def readGO2(go_xls, factor, count, condA, cmp, condB, summaryD):
    if debug:
        print >>sys.stderr, "Processing "+go_xls
    cnt = 0
    header = 1
    output = go_xls + '.for_dvplot310.tmp'
    fh_out = open(output, 'w')
    for line in open(go_xls):
        lineL = line.rstrip().split('\t')
        if debug:
            print >>sys.stderr, lineL
        if len(lineL) <= 8:
            print >>sys.stderr, "No enrichment data for "+go_xls
            fh_out.close()
            os.system('/bin/rm -f '+output)
            return
        if header:
            tmpL = [lineL[1][:70],'neg_log10padjust',lineL[8], "Sample"]
            print >>fh_out, '\t'.join(tmpL)
            header -= 1
            continue
        #if len(lineL) < 4:
        #    print >>sys.stderr, "lineL"
        #    break
        padjust = str((-1)*log(float(lineL[5]), 10))
        tmpL = [lineL[1][:70], padjust, lineL[8], factor]
        print >>fh_out, '\t'.join(tmpL)
        cnt+=1
        if cnt == count:
            break
    fh_out.close()
    #if cnt == 0:
    #    print >>sys.stderr, "No enrichment data for "+go_xls
    #    return
    cmd = ['s-plot scatterplotDoubleVariable -f', output, "-t 'KEGG enrichment'", 
        '-o Sample -v Description -c neg_log10padjust -s Count -E pdf']
    os.system(' '.join(cmd))
    os.system('/bin/mv -f '+output+".scatterplot.dv.pdf "+go_xls[:-3]+'scatterplot.dv.pdf')
    convert = ['convert -density 150 -quality 90',
            go_xls[:-4]+'.scatterplot.dv.pdf',
            go_xls[:-4]+'.scatterplot.dv.png']
    os.system(' '.join(convert))
    os.system('/bin/rm -f '+output)
#----------------------------------------------

def readGO(go_xls, factor, tag, count=30):
    if debug:
        print >>sys.stderr, "Processing "+go_xls
    cnt = 0
    header = 1
    output = go_xls + '.for_dvplot310.tmp'
    fh_out = open(output, 'w')
    for line in open(go_xls):
        lineL = line.rstrip().split('\t')
        if debug:
            print >>sys.stderr, lineL
        if len(lineL) <= 8:
            print >>sys.stderr, "No enrichment data for "+go_xls
            fh_out.close()
            os.system('/bin/rm -f '+output)
            return
        if header:
            tmpL = [lineL[1][:70],'neg_log10padjust',lineL[8], "Sample"]
            print >>fh_out, '\t'.join(tmpL)
            header -= 1
            continue
        #if len(lineL) < 4:
        #    print >>sys.stderr, "lineL"
        #    break
        padjust = str((-1)*log(float(lineL[5]), 10))
        tmpL = [lineL[1][:70], padjust, lineL[8], factor]
        print >>fh_out, '\t'.join(tmpL)
        cnt+=1
        if cnt == count:
            break
    fh_out.close()
    #if cnt == 0:
    #    print >>sys.stderr, "No enrichment data for "+go_xls
    #    return
    cmd = ['s-plot scatterplotDoubleVariable -f', output, "-t '", tag, "enrichment'", 
        '-o Sample -v Description -c neg_log10padjust -s Count -E pdf']
    os.system(' '.join(cmd))
    os.system('/bin/mv -f '+output+".scatterplot.dv.pdf "+go_xls[:-3]+'scatterplot.dv.pdf')
    convert = ['convert -density 150 -quality 90',
            go_xls[:-4]+'.scatterplot.dv.pdf',
            go_xls[:-4]+'.scatterplot.dv.png']
    os.system(' '.join(convert))
    os.system('/bin/rm -f '+output)
#----------------------------------------------

def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    factor_labeling = options.filein
    tag = options.tag
    verbose = options.verbose
    global debug
    debug = options.debug
    #----------------------------------------------
    factorL = set([line.split()[1] for line in open(factor_labeling)])
    summary = factor_labeling + '.'+tag+'.summary.xls'
    summary_fh = open(summary, 'w')
    summaryD = {}
    #go_catL = ['MF', 'BP', 'CC']
    for factor in factorL:
        go_xls = factor_labeling+'.'+factor+'.'+tag+'.xls'    
        if factor.find('Than') != -1:
            first = factor.find('._')
            second = factor.find('_.')
            condA = factor[:first]
            cmp = factor[first+2:second]
            condB = factor[second+2:]
            key = '\t'.join([condA, condB])
            if key not in summaryD:
                summaryD[key] = {}
            subkey = cmp+'_'+tag
            summaryD[key][subkey] = {'file':go_xls, 
                    'pdf': go_xls[:-4]+'.scatterplot.dv.pdf'}
        if not os.path.exists(go_xls):
            print >>sys.stderr, "**<{}> un-exist**".format(go_xls)
            continue
        readGO(go_xls, factor, tag=tag)   
    json.dump(summaryD, open(summary, 'w'), indent=4, sort_keys=True)
    #----close factor_labeling handle for files-----
    #-----------end close fh-----------
    ###--------multi-process------------------
    #pool = ThreadPool(5) # 5 represents thread_num
    #result = pool.map(func, iterable_object)
    #pool.close()
    #pool.join()
    ###--------multi-process------------------
    if verbose:
        print >>sys.stderr,\
            "--Successful %s" % strftime(timeformat, localtime())

if __name__ == '__main__':
    startTime = strftime(timeformat, localtime())
    main()
    endTime = strftime(timeformat, localtime())
    fh = open('python.log', 'a')
    print >>fh, "%s\n\tRun time : %s - %s " % \
        (' '.join(sys.argv), startTime, endTime)
    fh.close()
    ###---------procompare_pair the program---------
    #import procompare_pair
    #procompare_pair_output = sys.argv[0]+".prof.txt")
    #procompare_pair.run("main()", profile_output)
    #import pstats
    #p = pstats.Stats(procompare_pair_output)
    #p.sort_stats("time").print_stats()
    ###---------procompare_pair the program---------


