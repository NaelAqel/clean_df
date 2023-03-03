#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'missingno>=0.4.1',
    'numpy>=1.19.3',
    'pandas>=0.25.3',
    'IPython>=7.10',
    'matplotlib>=3.0.3'
]

test_requirements = ['pytest>=3', ]

setup(
    author="Nael Aqel",
    author_email='dev@naelaqel.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="Python module to report, clean, and optimize Pandas Dataframes effectively",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['clean_df', 'cleaning', 'data analysis', 'data science', 'wrangling', 'reporting',
              'optimization', 'outliers', 'missing'],
    name='clean_df',
    packages=find_packages(include=['clean_df', 'clean_df.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/naelaqel/clean_df',
    version='0.2.2',
    zip_safe=False,
)
