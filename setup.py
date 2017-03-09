# -*- coding: utf-8 -*-
""" Setup configuration file
"""

from setuptools import setup

__author__ = 'Matthew L. Bendall'

setup(
    name='rna2dnalign',
    version='1.0.13',
    description='RNA2DNAlign evaluates evidence for asymmetric allele distribution in next-gen sequencing reads of DNA and RNA samples from the same individual',
    url='https://github.com/HorvathLab/RNA2DNAlign',
    author='Nathan Edwards',
    license='MIT',
    packages=[
        'rna2dnalign',
        'mgpcutils',
    ],
    zip_safe=False,
)
