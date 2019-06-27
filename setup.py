from setuptools import setup, find_packages

setup(name='quality_made_xlsx',
    version='0.0.1',
    url='https://github.com/csm-adapt/citrine-quality-made',
    description='This converts a Quality Made Excel metadata file to PIF.',
    author='This converter was written by Branden Kappes',
    author_email='bkappes@mines.edu',
    packages=find_packages(),
    install_requires=[
        'pypif',
    ],
    entry_points={
        'citrine.dice.converter': [
            'quality_made_xlsx = quality_made_xlsx.converter',
        ],
    },
)
