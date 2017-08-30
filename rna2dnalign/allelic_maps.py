#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Create allelic maps
"""

import sys
import os
import re
from collections import defaultdict
from subprocess import Popen, PIPE

import tempfile
import shutil
import atexit

import circosutils
from mgpcutils import optparse_gui
import optgroups

__author__ = 'Matthew L. Bendall'

from version import VERSION
VERSION = '1.0.7 (%s)' % (VERSION,)

CHROMSORT = {str(c): i for i, c in enumerate(range(1, 23) + ['X', 'Y', 'M'])}


def which(file):
    ''' Search path for file

    Cross platform version of 'which'

    :param file:
    :return:
    '''
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
                return os.path.join(path, file)
    return None

def find_circos():
    p = which('circos')
    if p is not None:
        return p
    # If circos not in path, we'll look in the current directory
    # Downloaded circos directory has a version number so glob for it
    f = glob(os.path.join('circos*', 'bin', 'circos'))
    return f[0] if len(f) == 1 else None

def make_tracks(infile, outdir, prefix, dt_regex, chromsort=CHROMSORT):
    """ Create data files for each track
    """
    datatypes = dt_regex.keys()
    lines = (l.strip('\n').split('\t') for l in open(infile, 'rU'))
    header = lines.next()

    # Dictionary mapping (chrom, pos, ref, alt) to a dictionary with MAF values
    # each datatype
    allvals = defaultdict(dict)
    for l in lines:
        row_key = tuple(l[:4])
        dtype = [k for k, v in dt_regex.iteritems() if re.search(v, l[4])]
        assert len(dtype) == 1, "Error for data type in %s" % l[4]
        allvals[row_key][dtype[0]] = float(l[13])

    # Sort SNVs by chromosome and position
    snvs = allvals.keys()
    snvs.sort(key=lambda x: int(x[1]))
    snvs.sort(key=lambda x: chromsort[x[0].strip('chr')])

    # Output tab-delimited to data files (for circos)
    fhs = {}
    for dt in datatypes:
        fhs[dt] = open(os.path.join(outdir, '%s_%s.txt' % (prefix, dt)), 'w')

    for tup in snvs:
        for dt in datatypes:
            if dt in allvals[tup]:
                row = ['hs%s' % tup[0], tup[1], tup[1], allvals[tup][dt]]
                print >> fhs[dt], '\t'.join(map(str, row))

    # Close the files
    for f in fhs.values():
        f.close()

def main(opt):
    dt_regex = {
        'Nex': opt.normaldnare,
        'Ntr': opt.normaltransre,
        'Tex': opt.tumordnare,
        'Ttr': opt.tumortransre,
    }

    ''' Save configuration files? '''
    if opt.save_conf:
        outtemp = opt.output
    else:
        outtemp = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, path=outtemp)

    ''' Find path to circos '''
    if opt.circos_path is None:
        opt.circos_path = find_circos()

    if opt.circos_path is not None:
        opt.circos_path = os.path.abspath(opt.circos_path)

    ''' Create circos tracks from counts file'''
    make_tracks(opt.counts, outtemp, opt.sample_name, dt_regex)

    ''' Create circos configuration files '''
    config_files = circosutils.get_configurations()
    for fn, confstr in config_files.iteritems():
        with open(os.path.join(outtemp, fn), 'w') as outh:
            print >>outh, confstr

    ''' Output file '''
    # For some reason circos doesn't like absolute paths
    outrel = os.path.relpath(opt.output, os.getcwd())
    outf = os.path.join(outrel, '%s.AllelicMap' % opt.sample_name)
    # outsvg = os.path.join(outrel, '%s.AllelicMap.svg' % opt.sample_name)

    ''' Construct circos command '''
    if opt.circos_path is not None:
        cmd = ['perl', opt.circos_path, ]
    else:
        cmd = ['circos']

    cmd += [
        '-conf', os.path.join(outtemp, 'circos.conf'),
        '-param', 'sample_name=%s' % opt.sample_name,
        '-outputfile', outf,
    ]

    if opt.circos_path is None:
        print >>sys.stderr, 'Unable to locate circos. Circos command:'
        print >> sys.stderr, ' '.join(cmd)
    else:
        print >> sys.stderr, 'Running circos...'
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        o,e = p.communicate()

        if p.returncode == 0:
            print >>sys.stderr, 'Circos complete.'
            if os.path.exists('%s.png' % outf):
                print >> sys.stderr, '%s.png' % outf
            if os.path.exists('%s.svg' % outf):
                print >> sys.stderr, '%s.svg' % outf
        else:
            print >>sys.stderr, 'ERROR: Circos returned non-zero exit status %d.' % p.returncode
            print >>sys.stderr, 'Circos stdout:\n%s' % o
            print >>sys.stderr, 'Circos stderr:\n%s' % o

if __name__ == '__main__':
    if not optparse_gui.GUI() and len(sys.argv) == 2 and sys.argv[1] == '--GUI':
        from optparse_gui.needswx import *
        sys.exit(1)

    if optparse_gui.GUI() and len(sys.argv) == 1:
        parser = optparse_gui.OptionParserGUI(version=VERSION)
        error_kwargs = {'exit': False}
        sys.excepthook = optparse_gui.excepthook
    else:
        parser = optparse_gui.OptionParser(version=VERSION)
        error_kwargs = {}

    parser.add_option("--counts", type="file", dest="counts", default=None,
                      help="Output file from readCounts. Required.", notNone=True,
                      filetypes=[("readCount Output", "*.tsv")])
    parser.add_option("-o", "--output", type="savedir", dest="output",
                      remember=True,
                      help="Output folder. Required.", default=None,
                      name="Output Folder")

    parser.add_option_group(optgroups.get_allelicmaps_optgroup(parser))
    parser.add_option_group(optgroups.get_regex_optgroup(parser))

    opt = None
    while True:
        if 'exit' in error_kwargs:
            try:
                opt, args = parser.parse_args(opts=opt)
            except optparse_gui.UserCancelledError:
                sys.exit(0)
        else:
            opt, args = parser.parse_args()

        break

    main(opt)

"""
pythonw rna2dnalign/allelic_maps.py
python rna2dnalign/allelic_maps.py -h

python rna2dnalign/allelic_maps.py\
  --counts ../pipeline_circos_matlab/ESCAreadCounts5/001/001_ESCA_readCounts.tsv\
  --normaldnare Nex\
  --normaltransre Ntr\
  --tumordnare Tex\
  --tumortransre Ttr\
  -o ../testing4\
  --circos_path ../pipeline_circos_matlab/circos-0.69-2/bin/circos

"""