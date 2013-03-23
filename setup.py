import sys

from setuptools import setup

import hueman


requires, extra = ['requests', 'PyYAML'], {}
if sys.version_info < (2, 7):
    requires.append('argparse')
elif sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='hueman',
    version=hueman.__version__,
    description='A human interface for managing your hues.',
    author='Will Boyce',
    author_email='me@willboyce.com',
    url='https://www.github.com/wrboyce/hueman',
    license='BSD',
    install_requires=requires,
    packages=['hueman'],
    package_data={'': ['LICENCE'], 'hueman': ['hueman.yml']},
    package_dir={'hueman': 'hueman'},
    entry_points={'console_scripts': ['hueman = hueman.util:cli']},
    zip_safe=False,
    **extra
)
