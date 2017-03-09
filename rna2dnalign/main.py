#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Driver
"""

import sys
import os
import tempfile
from collections import namedtuple

# third party imports

# local application imports
from version import VERSION
from mgpcutils import optparse_gui
from mgpcutils import exonicFilter
import readCounts

__author__ = 'Matthew L. Bendall'

''' Check whether wx is available '''
try:
    import wx
    print >>sys.stderr, "WX was imported"
    HAS_WX = True
except ImportError:
    print >> sys.stderr, "WX was not imported"
    HAS_WX = False

class OptValues:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
    def __str__(self):
        return str(self.__dict__)

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

    ''' Exon filtering group '''
    exfilt_og = optparse_gui.OptionGroup(parser, "Filtering")
    exfilt_og.add_option("-e", "--exoncoords", type="file", dest="exoncoords",
                         default=None,
                         help="Exon coordinates for SNV filtering. Optional.",
                         name="Exon Coords.",
                         remember=True,
                         filetypes=[("Exonic Coordinates", "*.txt")])
    parser.add_option_group(exfilt_og)

    ''' Regex group '''
    regexs_og = optparse_gui.OptionGroup(parser, "Filename Matching")
    regexs_og.add_option("--normaldnare", type="str", dest="normaldnare",
                         default='GDNA',
                         help="Germline/Normal DNA filename regular expression. Default: GDNA.",
                         remember=True, name="Germline DNA")
    regexs_og.add_option("--normaltransre", type="str", dest="normaltransre",
                         default='NRNA',
                         help="Normal transcriptome filename regular expression. Default: NRNA.",
                         remember=True, name="Normal Transcr.")
    regexs_og.add_option("--tumordnare", type="str", dest="tumordnare",
                         default='SDNA',
                         help="Somatic/Tumor DNA filename regular expression. Default: SDNA.",
                         remember=True, name="Somatic DNA")
    regexs_og.add_option("--tumortransre", type="str", dest="tumortransre",
                         default='TRNA',
                         help="Tumor transcriptome filename regular expression. Default: TRNA.",
                         remember=True, name="Tumor Transcr.")
    parser.add_option_group(regexs_og)

    ''' Readcounts group '''
    readcounts_og = optparse_gui.OptionGroup(parser, "Read Counting")
    readcounts_og.add_option("-m", "--minreads", type="int", dest="minreads",
                             default=10, remember=True,
                             help="Minimum number of good reads at SNV locus per alignment file. Default=10.",
                             name="Min. Reads")
    readcounts_og.add_option("-M", "--maxreads", type="float", dest="maxreads",
                             default=None, remember=True,
                             help="Scale read counts at high-coverage loci to ensure at most this many good reads at SNV locus per alignment file. Values greater than 1 indicate absolute read counts, otherwise the value indicates the coverage distribution percentile. Default=No maximum.",
                             name="Max. Reads")
    readcounts_og.add_option("-f", "--alignmentfilter", action="store_false",
                             dest="filter", default=True, remember=True,
                             help="(Turn off) alignment filtering by length, edits, etc.",
                             name="Filter Alignments")
    readcounts_og.add_option("-U", "--uniquereads", action="store_true",
                             dest="unique", default=False, remember=True,
                             help="Consider only distinct reads.",
                             name="Unique Reads")
    readcounts_og.add_option("-t", "--threadsperbam", type="int", dest="tpb",
                             default=1, remember=True,
                             help="Worker threads per alignment file. Indicate no threading with 0. Default=1.",
                             name="Threads/BAM")
    readcounts_og.add_option("-q", "--quiet", action="store_true", dest="quiet",
                             default=False, remember=True,
                             help="Quiet.", name="Quiet")
    parser.add_option_group(readcounts_og)

    if gui:
        try:
            opt, args = parser.parse_args(opts=None)
        except optparse_gui.UserCancelledError:
            sys.exit(0)
    else:
        opt, args = parser.parse_args()

    print >>sys.stderr, opt
    ''' Setup output '''
    outtemp = './tmpd' # tempfile.mkdtemp()

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

    ''' Set up and apply snv_computation '''



"""
python rna2dnalign/main.py -h
python rna2dnalign/main.py\
  -s /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf\
  -r /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.sorted.bam\
  -o .

python rna2dnalign/main.py\
  -s /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf\
  -r /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.sorted.bam\
  -e /Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt\
  -o .

python rna2dnalign/readCounts.py\
  -s /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf\
  -r /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.sorted.bam\
  -o ./tmpd/testfile.tsv

python mgpcutils/exonicFilter.py\
  --exons /Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt\
  --input /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf\
  --output tmp.vcf

python rna2dnalign/main.py\
  -s rna2dnalign/data/example-GDNA.vcf\
  -r rna2dnalign/data/example-GDNA.bam\
  -o .


python rna2dnalign/main.py\
  -s rna2dnalign/data/example-*.vcf\
  -r rna2dnalign/data/example-*.bam\
  -o .



"""

"""
from pysam import VariantFile
vcfin = '/Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf'
exonin = '/Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt'
out = 'tmp2.txt'

vcf_fh = VariantFile(vcfin)
vcf_outh = VariantFile(out, 'w', header=vcf_fh.header)

for l in lines:
    for rec in vcf_fh.fetch(l[0], int(l[1]), int(l[2])):
        vcf_outh.write(rec)

vcf_outh.close()

bgzip -i /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf |\
bcftools view -R /Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt

bgzip /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf
tabix /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf.gz
bcftools view -R /Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf.gz



"""