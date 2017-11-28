# -*- coding: utf-8 -*-
"""Installer for the collective.excelexport package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='collective.excelexport',
    version='1.5',
    description="Export dexterity contents in an excel file, one column by field",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Export,Plone,Excel',
    author='Thomas Desvenain',
    author_email='thomas.desvenain@gmail.com',
    url='http://pypi.python.org/pypi/collective.excelexport',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'xlwt',
    ],
    extras_require={
        'test': [
            'collective.z3cform.datagridfield',
            'ecreall.helpers.testing',
            'plone.app.testing',
            'plone.app.dexterity',
            'plone.app.relationfield',
            'xlrd',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
