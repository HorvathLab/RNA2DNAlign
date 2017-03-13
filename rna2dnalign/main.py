#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Driver
"""

import sys
import os
import tempfile
import shutil
import atexit

# third party imports

# local application imports
from version import VERSION
from mgpcutils import optparse_gui
import optgroups
from optgroups import OptValues
from mgpcutils import exonicFilter
import readCounts
import snv_computation
import summary_analysis
import allelic_maps

__author__ = 'Matthew L. Bendall'

''' Check whether wx is available '''
try:
    import wx
    HAS_WX = True
except ImportError:
    HAS_WX = False

if __name__=='__main__':
    if len(sys.argv) == 1 and HAS_WX:
        # Using the GUI
        parser = optparse_gui.OptionParserGUI(version=VERSION)
        error_kwargs = {'exit': False}
        sys.excepthook = optparse_gui.excepthook
        gui = True
    else:
        # Using command line
        parser = optparse_gui.OptionParser(version=VERSION)
        error_kwargs = {}
        gui = False

    parser.add_option("-s", "--snvs", type="files", dest="snvs", default=None,
                      help="Single-Nucleotide-Variant files. Required.",
                      name="SNV Files",
                      notNone=True, remember=True,
                      filetypes=[
                          ("SNV Files", "*.vcf;*.csv;*.tsv;*.xls;*.xlsx;*.txt")])
    parser.add_option("-r", "--readalignments", type="files", dest="alignments",
                      default=None,
                      help="Read alignment files in indexed BAM format. Required.",
                      name="Read Alignment Files",
                      notNone=True, remember=True,
                      filetypes=[("Read Alignment Files (Indexed BAM)", "*.bam")])
    parser.add_option("-o", "--output", type="savedir", dest="output",
                      remember=True,
                      help="Output folder. Required.", default=None, notNone=True,
                      name="Output Folder")

    ''' Exon filtering group '''
    parser.add_option_group(optgroups.get_exonfilt_optgroup(parser))
    ''' Readcounts group '''
    parser.add_option_group(optgroups.get_readcounts_optgroup(parser))
    ''' Regex group '''
    parser.add_option_group(optgroups.get_regex_optgroup(parser))
    ''' SNV annotation group'''
    parser.add_option_group(optgroups.get_snvannot_optgroup(parser))
    ''' Allelic maps group '''
    parser.add_option("--make_maps", action="store_true",
                      dest="make_maps", default=False, remember=True,
                      help='''Create allelic maps?
                              Default: Do not create allelic maps.''',
                     )
    parser.add_option_group(optgroups.get_allelicmaps_optgroup(parser))

    if gui:
        try:
            opt, args = parser.parse_args(opts=None)
        except optparse_gui.UserCancelledError:
            sys.exit(0)
    else:
        opt, args = parser.parse_args()

    ''' Setup output '''
    outtemp = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, path=outtemp)

    ''' Apply exonic filter on SNVs '''
    if opt.exoncoords:
        snvfiles = []
        for snvfile in opt.snvs:
            dirname, basename = os.path.split(snvfile)
            prefix, ext = os.path.splitext(basename)
            outfile = os.path.join(outtemp, '%s.filtered%s' % (prefix, ext))
            ef_opts = OptValues(
                exons=opt.exoncoords,
                input=snvfile,
                output=outfile
            )
            try:
                exonicFilter.main(ef_opts)
                snvfiles.append(outfile)
            except Exception as e:
                print >>sys.stderr, 'ERROR in exonicFilter, using unfiltered file'
                print >>sys.stderr, str(e)
                snvfiles.append(snvfile)
    else:
        snvfiles = opt.snvs

    print >> sys.stderr, '\n'.join(snvfiles)

    ''' Apply readCounts to SNVs and aligned reads '''
    rc_outfile = os.path.join(outtemp, "readCounts.tsv")
    rc_opts = OptValues(
        full=True,
        snvs=snvfiles,
        alignments=opt.alignments,
        output=rc_outfile,
        minreads=opt.minreads,
        maxreads=opt.maxreads,
        tpb=opt.tpb,
        filter=opt.filter,
        unique=opt.unique,
        quiet=opt.quiet,
        debug=False,
    )
    readCounts.main(rc_opts)
    # Copy readCounts.tsv
    if os.path.isfile(rc_outfile):
        shutil.copy(rc_outfile, opt.output)

    ''' Set up and apply snv_computation '''
    sc_opts = OptValues(
        counts=rc_outfile,
        cosmic=opt.cosmic,
        darned=opt.darned,
        normaldnare=opt.normaldnare,
        normaltransre=opt.normaltransre,
        tumordnare=opt.tumordnare,
        tumortransre=opt.tumortransre,
        output=outtemp,
    )
    snv_computation.main(sc_opts)

    ''' Summarize events '''
    outsum = os.path.join(opt.output, 'summary_result.txt')
    if os.path.exists(outsum):
        os.unlink(outsum)
    for event in "RNAed T-RNAed VSE T-VSE VSL T-VSL LOH SOM SOM-E SOM-L".split():
        evfile = os.path.join(outtemp, "Events_%s.tsv" % (event,))
        if os.path.isfile(evfile):
            shutil.copy(evfile, opt.output)
            summary_analysis.read_events(evfile, outsum)

    ''' Allelic maps '''
    if opt.make_maps:
        am_opts = OptValues(
            counts=rc_outfile,
            normaldnare=opt.normaldnare,
            normaltransre=opt.normaltransre,
            tumordnare=opt.tumordnare,
            tumortransre=opt.tumortransre,
            save_conf=opt.save_conf,
            circos_path=opt.circos_path,
            sample_name=opt.sample_name,
            output=opt.output,
        )
        allelic_maps.main(am_opts)

"""
python rna2dnalign/main.py\
  -s "rna2dnalign/data/example-*.vcf"\
  -r "rna2dnalign/data/example-*.bam"\
  -o ../testing4
"""