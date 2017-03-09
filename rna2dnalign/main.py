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
    exfilt = optparse_gui.OptionGroup(parser, "Filtering")
    exfilt.add_option("-e", "--exoncoords", type="file", dest="exoncoords",
                      default=None,
                      help="Exon coordinates for SNV filtering. Optional.",
                      name="Exon Coords.",
                      remember=True,
                      filetypes=[("Exonic Coordinates", "*.txt")])
    parser.add_option_group(exfilt)

    ''' Regex group '''
    regexs = optparse_gui.OptionGroup(parser, "Filename Matching")
    regexs.add_option("--normaldnare", type="str", dest="normaldnare",
                      default='GDNA',
                      help="Germline/Normal DNA filename regular expression. Default: GDNA.",
                      remember=True, name="Germline DNA")
    regexs.add_option("--normaltransre", type="str", dest="normaltransre",
                      default='NRNA',
                      help="Normal transcriptome filename regular expression. Default: NRNA.",
                      remember=True, name="Normal Transcr.")
    regexs.add_option("--tumordnare", type="str", dest="tumordnare",
                      default='SDNA',
                      help="Somatic/Tumor DNA filename regular expression. Default: SDNA.",
                      remember=True, name="Somatic DNA")
    regexs.add_option("--tumortransre", type="str", dest="tumortransre",
                      default='TRNA',
                      help="Tumor transcriptome filename regular expression. Default: TRNA.",
                      remember=True, name="Tumor Transcr.")
    parser.add_option_group(regexs)

    if gui:
        try:
            opt, args = parser.parse_args(opts=None)
        except optparse_gui.UserCancelledError:
            sys.exit(0)
    else:
        opt, args = parser.parse_args()

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

    ''' Apply readCounts to SNVs and aligned reads. '''


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


python mgpcutils/exonicFilter.py\
  --exons /Volumes/CBI_GRAY/testR2D/UCSC_Human_hg19_RefSeq_CDS_exon_coordinates.txt\
  --input /Volumes/CBI_GRAY/testR2D/022NTex-TCGA-BH-A0E0-11A-13W-A10F-09_HOLD_QC_PENDING_IlluminaGA-DNASeq_exome.var.flt.vcf\
  --output tmp.vcf
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