# -*- coding: utf-8 -*-
""" Option groups
"""
from mgpcutils import optparse_gui

class OptValues:
    """ Object with kwargs as attributes

        Behaves like optparse.Values
    """
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
    def __str__(self):
        return str(self.__dict__)

def get_regex_optgroup(parser):
    ''' Regex group '''
    optgrp = optparse_gui.OptionGroup(parser, "Filename Matching")
    optgrp.add_option("--normaldnare", type="str", dest="normaldnare",
                      default=r'NTex',
                      help='''Germline/Normal DNA filename regular expression.
                              Default: NTex.''',
                      remember=True, name="Germline DNA RE")
    optgrp.add_option("--normaltransre", type="str", dest="normaltransre",
                      default=r'NTtr',
                      help='''Normal transcriptome filename regular expression.
                              Default: NTtr.''',
                      remember=True, name="Normal Transcr. RE")
    optgrp.add_option("--tumordnare", type="str", dest="tumordnare",
                      default=r'TPex',
                      help='''Somatic/Tumor DNA filename regular expression.
                              Default: TPex.''',
                      remember=True, name="Somatic DNA RE")
    optgrp.add_option("--tumortransre", type="str", dest="tumortransre",
                      default=r'TPtr',
                      help='''Tumor transcriptome filename regular expression.
                              Default: TPtr.''',
                      remember=True, name="Tumor Transcr. RE")
    return optgrp

def get_allelicmaps_optgroup(parser):
    ''' Allelic maps group '''
    optgrp = optparse_gui.OptionGroup(parser, "Allelic Maps")
    optgrp.add_option("--sample_name", type="str", dest="sample_name",
                      default='example',
                      help="Prefix for output files. Default: example.",
                      remember=True, name="Output prefix")
    optgrp.add_option("--save_conf", action="store_true",
                      dest="save_conf", default=False, remember=True,
                      help='''Save configuration files to output directory.
                              Default: Files are removed.''',
                      name="Save Circos configuration?")
    optgrp.add_option("--circos_path", type="file",
                      dest="circos_path", remember=True,
                      help="Path to circos executable.",
                      name="Circos path")
    return optgrp

def get_readcounts_optgroup(parser):
    ''' Readcounts group '''
    optgrp = optparse_gui.OptionGroup(parser, "Read Counting")
    optgrp.add_option("-m", "--minreads", type="int", dest="minreads",
                      default=10, remember=True,
                      help='''Minimum number of good reads at SNV locus
                              per alignment file. Default=10.''',
                      name="Min. Reads")
    optgrp.add_option("-M", "--maxreads", type="float", dest="maxreads",
                      default=None, remember=True,
                      help='''Scale read counts at high-coverage loci to ensure
                              at most this many good reads at SNV locus per
                              alignment file. Values greater than 1 indicate
                              absolute read counts, otherwise the value
                              indicates the coverage distribution percentile.
                              Default=No maximum.''',
                      name="Max. Reads")
    optgrp.add_option("-f", "--alignmentfilter", action="store_false",
                      dest="filter", default=True, remember=True,
                      help='''(Turn off) alignment filtering by length, edits,
                              etc.''',
                      name="Filter Alignments")
    optgrp.add_option("-U", "--uniquereads", action="store_true",
                      dest="unique", default=False, remember=True,
                      help='''Consider only distinct reads.''',
                      name="Unique Reads")
    optgrp.add_option("-t", "--threadsperbam", type="int", dest="tpb",
                      default=1, remember=True,
                      help='''Worker threads per alignment file. Indicate no
                              threading with 0. Default=1.''',
                      name="Threads/BAM")
    optgrp.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      default=False, remember=True,
                      help="Quiet.", name="Quiet")
    return optgrp

def get_snvannot_optgroup(parser):
    ''' SNV annotation group'''
    optgrp = optparse_gui.OptionGroup(parser, "SNV Annotation")
    optgrp.add_option("-d", "--darned", type="file", dest="darned",
                      default="",remember=True,
                      help="DARNED Annotations. Optional.",
                      filetypes=[("DARNED Annotations", "*.txt")],
                      )
    optgrp.add_option("-c", "--cosmic", type="file", dest="cosmic",
                      default="",remember=True,
                      help="COSMIC Annotations. Optional.",
                      filetypes=[("COSMIC Annotations", "*.tsv;*.tsv.gz")],
                      )
    return optgrp

def get_exonfilt_optgroup(parser):
    ''' Exon filtering group '''
    optgrp = optparse_gui.OptionGroup(parser, "Filtering")
    optgrp.add_option("-e", "--exoncoords", type="file", dest="exoncoords",
                      default=None, remember=True,
                      help="Exon coordinates for SNV filtering. Optional.",
                      name="Exon Coords.",
                      filetypes=[("Exonic Coordinates", "*.txt")],
                      )
    return optgrp