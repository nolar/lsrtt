#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lsrtt',
    version='0.0.1',

    author='Sergey Vasilyev',
    author_email='nolar@nolar.info',
    url='http://github.com/nolar/lsrtt/',

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        'dill',
        'numpy',
        'click',
        'flask',
    ],
    extras_require={
        'dev': ['pdbpp', 'ipython'],
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'convert = lsrtt.scripts.convert:convert',
            'refresh = lsrtt.scripts.refresh:refresh',
            'predict = lsrtt.scripts.predict:predict',
        ],
    }
)
