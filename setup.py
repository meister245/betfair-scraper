#!/usr/bin/env python3

import re
from setuptools import setup


with open('./betfair_scraper/__init__.py', 'r') as f:
    version = re.search(r'(?<=__version__ = .)([\d\.]*)', f.read()).group(1)

with open('./README.md', 'r') as f:
    readme = f.read()


if __name__ == '__main__':
    setup(
        name='betfair-scraper',
        version=version,
        author='Zsolt Mester',
        author_email='',
        description='Betfair website scraper library',
        long_description=readme,
        license='MIT',
        url='https://github.com/meister245/betfair-scraper',
        project_urls={
            "Code": "https://github.com/meister245/betfair-scraper",
            "Issue tracker": "https://github.com/meister245/betfair-scraper/issues",
        },
        packages=[
            'betfair_scraper'
        ],
        install_requires=[
            'robobrowser',
            'html5lib'
        ],
        python_requires='>=3.8',
        include_package_data=False
    )
