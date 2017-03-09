#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Driver
"""

import sys

# third party imports

# local application imports
from version import VERSION
from mgpcutils import optparse_gui
# import readCounts

__author__ = 'Matthew L. Bendall'

''' Check whether wx is available '''
try:
    import wx
    print >>sys.stderr, "WX was imported"
    HAS_WX = True
except ImportError:
    print >> sys.stderr, "WX was not imported"
    HAS_WX = False

if __name__=='__main__':
    if len(sys.argv) == 1 and HAS_WX:
        # Using the GUI
        parser = optparse_gui.OptionParserGUI(version=VERSION)
        error_kwargs = {'exit': False}
        # sys.excepthook = excepthook
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
    if gui:
        try:
            opt, args = parser.parse_args(opts=None)
        except optparse_gui.UserCancelledError:
            sys.exit(0)
    else:
        opt, args = parser.parse_args()
