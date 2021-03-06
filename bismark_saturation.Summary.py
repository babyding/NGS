#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division, with_statement
'''
Copyright 2015, 陈同 (chentong_biology@163.com).  
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
desc = '''
Program description:
    This is designed to summarize results output by `bismark_saturation.py`.


'''

import sys
import os
from json import dumps as json_dumps
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
import re
from tools import *
#from multiprocessing.dummy import Pool as ThreadPool

#from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

debug = 0

def fprint(content):
    """ 
    This is a Google style docs.

    Args:
        param1(str): this is the first param
        param2(int, optional): this is a second param
            
    Returns:
        bool: This is a description of what is returned
            
    Raises:
        KeyError: raises an exception))
    """
    print json_dumps(content,indent=1)

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "%prog -f file"
    parser = OP(usage=usages)
    parser.add_option("-f", "--files", dest="filein",
        metavar="FILEIN", help="`,` or ` ` separated a list of files. *.Log.final.out generated by `STAR` during mapping")
    parser.add_option("-l", "--labels", dest="label",
        metavar="LABEL", help="`,` or ` ` separated a list of labels to label each file. It must have same order as files.")
    parser.add_option("-o", "--output-prefix", dest="out_prefix",
        help="The prefix of output files. UNUSED")
    parser.add_option("-r", "--report-dir", dest="report_dir",
        default='report', help="Directory for report files. Default 'report'.")
    parser.add_option("-R", "--report-sub-dir", dest="report_sub_dir",
        default='2_mapping_quality', help="Directory for saving report figures and tables. This dir will put under <report_dir>,  so only dir name is needed. Default '2_mapping_quality'.")
    parser.add_option("-d", "--doc-only", dest="doc_only",
        default=False, action="store_true", help="Specify to only generate doc.")
    parser.add_option("-n", "--number", dest="number", type="int", 
        default=40, help="Set the maximum allowed samples for barplot. Default 40.\
 If more than this number of samples are given, heatmap will be used instead. UNUSED.")
    parser.add_option("-v", "--verbose", dest="verbose",
        action="store_true", help="Show process information")
    parser.add_option("-D", "--debug", dest="debug",
        default=False, action="store_true", help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------


#---------------------------------------
def plot(subF, subL):
    for file, label in zip(subF, subL): 
        cmd = ['s-plot lines -m TRUE -a Per', 
           '-y "Number of covered sites" -x "Number of available sequencing reads"', 
           '-f', file, '-P none', 
           '-t \"'+ label+' sequencing saturation analysis\"', 
           "-w 15 -u 20 -F \"+facet_wrap(~variable, ncol=1, scale=\'free_y\')\""]
        if os.path.exists(file) and os.stat(file).st_size>0:
            #print >>sys.stderr, ' '.join(cmd)
            os.system(' '.join(cmd))
        else:
            print >>sys.stderr, file + " not available"
#-----------------------------------------------------

def generateDoc(report_dir, report_sub_dir, fileL, labelL, curation_label):
    dest_dir = report_dir+'/'+report_sub_dir+'/'
    os.system('mkdir -p '+dest_dir)

    print "\n## Sequencing saturation estimation for all samples\n"

    knitr_read_txt(report_dir,  curation_label)
    
    print """样品测序饱和度评估。

从比对结果中随机抽取5%, 10%, 15%, ..., 90%, 95%, 100%的reads，分别计算检测到的甲基化位点的数目, 并绘制变化检测到的甲基化位点数目相对于测序深度的变化曲线，以评估测序饱和度。 当曲线变化趋于平缓时，说明测序量已接近或达到饱和。

"""
    
    fileL, labelL = skipUnExistedOrEmptyFile(fileL[:], labelL[:])

    len_fileL = len(fileL)
    group = 3
    
    for i in range(0, len_fileL, 3):
        subF = fileL[i:i+3]
        subL = labelL[i:i+3]
        plot(subF, subL)
        pdfL = [j+'.lines.pdf' for j in subF]
        copy(dest_dir, *subF)
        copypdf(dest_dir, *pdfL)
        len_subF = len(subF)
        pdfL = [report_sub_dir+'/'+os.path.split(j)[-1] for j in pdfL]
        pngL = [j.replace('pdf', 'png') for j in pdfL]

        #pdf_link = []  #[label_pdf](pdf), [label_pdf](pdf)
        #for pdf, label in zip(pdfL, subL):
        #    tmp_155 = '['+label+'_pdf]'+'('+pdf+')'
        #    pdf_link.append(tmp_155)

        #pdf_link = ' '.join(pdf_link)
        pdf_link = generateLink(pdfL, subL, 'pdf', '', join_symbol=" / ")
        xls_link = generateLink(subF, subL, 'xls', report_sub_dir, join_symbol=" / ")


        print "(ref:read-saturation-fig-{}) Summary sequencing saturation of each samples. From left to right, the samples are **{}**。 纵轴表示检测到的基因组位点数目，值越高越好。横轴表示测序可用的READs数。曲线越早趋于平稳说明测序越早达到饱和。 PDF结果下载 {} 原始数据结果下载 {}\n".format(i, ', '.join(subL), pdf_link, xls_link)
        
        #pngFileL = []  #"png1", "png2", "png3"
        #for png in pngL:
        #    tmp_164 = "'"+png+"'"
        #    pngFileL.append(tmp_164)
        #pngFileL = ', '.join(pngFileL)
        pngFileL = grenerateQuotedLists(pngL)
        print '''```{{r read-saturation-fig-{label}, out.width="{width}%", fig.cap="(ref:read-saturation-fig-{label})"}}
knitr::include_graphics(c({png}))
```
'''.format(label=i, png=pngFileL, width=int(100/len_subF))

#--------------------------------


def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    file = options.filein
    fileL = re.split(r'[, ]*', file.strip())
    sample_readin = len(fileL)
    label = options.label
    labelL = re.split(r'[, ]*', label.strip())
    verbose = options.verbose
    op = options.out_prefix
    report_dir = options.report_dir
    report_sub_dir = options.report_sub_dir
    global debug
    debug = options.debug
    doc_only = options.doc_only
    num_samples_each_grp = options.number
    melt = 0
    if sample_readin <= num_samples_each_grp:
        melt = 1
    #-----------------------------------
    aDict = {}
    curation_label = os.path.split(sys.argv[0])[-1].replace('.', '_')
    if doc_only:
        generateDoc(report_dir, report_sub_dir, fileL[:], labelL[:], curation_label)
        return 0

    generateDoc(report_dir, report_sub_dir, fileL[:], labelL[:], curation_label)
    ###--------multi-process------------------

if __name__ == '__main__':
    startTime = strftime(timeformat, localtime())
    main()
    endTime = strftime(timeformat, localtime())
    fh = open('python.log', 'a')
    print >>fh, "%s\n\tRun time : %s - %s " % \
        (' '.join(sys.argv), startTime, endTime)
    fh.close()
    ###---------profile the program---------
    #import profile
    #profile_output = sys.argv[0]+".prof.txt")
    #profile.run("main()", profile_output)
    #import pstats
    #p = pstats.Stats(profile_output)
    #p.sort_stats("time").print_stats()
    ###---------profile the program---------


