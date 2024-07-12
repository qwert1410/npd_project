from setuptools import setup, find_packages
import os

long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='movie_analyzer',
    version='0.1.0',
    packages=find_packages(where='NPD_project'),
    package_dir={'': 'NPD_project'},
    include_package_data=True,
    install_requires=[
        'numpy', 'pandas', 'matplotlib', 'argparse', 'IPython'
    ],
    entry_points={
        'console_scripts': [
            'movie_analyzer=movie_analyzer.main:main',
        ],
    },
    author='Kacper Zieniuk',
    author_email='kz430642@students.mimum.edu.pl',
    description='NPD project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qwert1410/npd_project/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
